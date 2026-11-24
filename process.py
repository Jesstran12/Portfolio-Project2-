"""Project 2 - the decision pipeline: prices -> estimates -> baselines, constrained portfolio,
mandate verdicts, bridges, stress run, scenarios, out-of-sample test, stop condition.

Every calculation the app shows comes from here, portfolio.py, client_mandate.py or
signal_rule.py; app.py holds no copy of the math. Standard library only.

Conventions (all numbers in percent a year unless a label says otherwise):
  return estimate = arithmetic mean of monthly returns x 12 (a historical estimate, not a forecast)
  volatility      = sample standard deviation of monthly returns x sqrt(12)
  weights         = long-only, searched in 5-point steps, rebalanced back to target
Run: python3 process.py
"""

import csv
import hashlib
import math
import random
import statistics

import client_mandate as cm
import portfolio as p

# ---------------------------------------------------------------- editable inputs
PRICES_FILE = "prices.csv"
PRICES_DOWNLOADED = "2026-10-22"   # the day the Adj Close snapshot was taken from Yahoo Finance
LAST_COMPLETE_MONTH = "2026-09"    # rows after this month are partial and excluded (data card D3)
AS_OF = "2026-09-30"               # the decision uses nothing dated after this
TRADE_COST = 0.10                  # percent of the value traded (not the signal's switch cost)
STEP = 5                           # weight grid, points
ESTIMATE_SHOCK = 1.0               # stress: each return estimate moved by this many points
STABILITY_LIMIT = 10.0             # points: the most a weight may move in the stress run to adopt
TURNOVER_BUDGET = 25.0             # percent a year, one-way
OOS_ESTIMATION_MONTHS = 36         # out-of-sample test: estimate on these, hold for the rest
BOOTSTRAP_RUNS = 300               # estimation-error test: resamples of the monthly returns
BOOTSTRAP_SEED = 43900
# ---------------------------------------------------------------- end of inputs


# ---------------------------------------------------------------- data in
def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def read_rows(path=PRICES_FILE):
    with open(path, newline="") as f:
        return [r for r in csv.reader(f) if r]


def validate_rows(rows, required=cm.TICKERS):
    """Return rows with the columns in mandate order, or raise ValueError with a plain message."""
    if len(rows) < 2:
        raise ValueError("the file has no price rows")
    header = [h.strip().upper() for h in rows[0]]
    missing = [t for t in required if t not in header[1:]]
    if missing:
        raise ValueError("missing column(s) " + ", ".join(missing) +
                         "; the mandate universe is " + ", ".join(required))
    index = [header.index(t) for t in required]
    out, last_date = [["date"] + list(required)], ""
    for n, row in enumerate(rows[1:], start=2):
        if len(row) < len(header):
            raise ValueError(f"row {n} has {len(row)} values but the header has {len(header)}")
        date = row[0].strip()
        if len(date) < 7 or date <= last_date:
            raise ValueError(f"row {n}: dates must be YYYY-MM-DD, oldest first, no repeats (got '{date}')")
        last_date = date
        prices = []
        for i in index:
            try:
                value = float(row[i])
            except ValueError:
                raise ValueError(f"row {n}: '{row[i]}' is not a price") from None
            if not value > 0:
                raise ValueError(f"row {n}: prices must be above zero (got {row[i]})")
            prices.append(value)
        out.append([date] + prices)
    if len(out) - 1 < 25:
        raise ValueError(f"need at least 25 monthly prices, found {len(out) - 1}")
    return out


def complete_rows(rows, last_complete=LAST_COMPLETE_MONTH):
    """Drop rows dated after the last complete month. Returns (kept, dropped)."""
    kept = [rows[0]] + [r for r in rows[1:] if r[0][:7] <= last_complete]
    return kept, [r for r in rows[1:] if r[0][:7] > last_complete]


def monthly_returns(rows):
    """(month labels, returns): returns[t][i] is fund i's return in month labels[t], decimal."""
    data = rows[1:]
    labels = [data[t][0][:7] for t in range(1, len(data))]
    rets = [[float(now) / float(before) - 1 for now, before in zip(data[t][1:], data[t - 1][1:])]
            for t in range(1, len(data))]
    return labels, rets


def estimate(rows, last_months=None, label=None):
    """Estimates and the monthly history they came from, as one dict."""
    tickers, returns, vols, corr = p.estimates_from_prices(rows, last_months)
    labels, monthly = monthly_returns(rows)
    if last_months:
        labels, monthly = labels[-last_months:], monthly[-last_months:]
    return {"tickers": tickers, "returns": returns, "vols": vols, "corr": corr,
            "cov": p.covariance_matrix(vols, corr), "months": labels, "monthly": monthly,
            "label": label or f"{labels[0]} to {labels[-1]} ({len(labels)} months)"}


def with_returns(est, returns):
    return {**est, "returns": list(returns)}


def with_corr(est, corr):
    return {**est, "corr": corr, "cov": p.covariance_matrix(est["vols"], corr)}


# ---------------------------------------------------------------- portfolios and verdicts
def judge(weights, est, rules=cm.RULES):
    """Measures, rule-by-rule checks and the verdict for one set of weights."""
    m = cm.measure(weights, est["tickers"], est["returns"], est["cov"], est["monthly"])
    checks = cm.check(m, rules)
    return {"weights": [round(w * 100, 2) for w in weights], "measures": m,
            "checks": checks, "verdict": cm.verdict(checks)}


def baselines(est):
    """The benchmark and the two transparent baselines, decimal weights in ticker order."""
    return {
        "Benchmark 60/40": cm.benchmark_weights(est["tickers"]),
        "Equal weight": p.equal_weights(len(est["tickers"])),
        "Inverse volatility": p.inverse_vol_weights(est["vols"]),
    }


def constrained_portfolio(est, rules=cm.RULES, cost_drag=0.0, step=STEP):
    """Lowest-volatility mix on the grid that passes every mandate rule, or None.

    cost_drag (percent a year) is taken off every mix's return before the objective is tested.
    """
    tickers, returns, cov = est["tickers"], est["returns"], est["cov"]
    net = [r - cost_drag for r in returns]
    reserve = [cm.UNIVERSE[t][2] for t in tickers]
    equity = [cm.UNIVERSE[t][3] for t in tickers]
    survivors = []
    for w in p.long_only_mixes(len(tickers), step):
        ret = p.expected_return(w, net)
        if ret < rules["objective"] - 1e-9:
            continue
        if sum(x for x, e in zip(w, reserve) if e) * 100 < rules["reserve_min"] - 1e-9:
            continue
        if sum(x for x, e in zip(w, equity) if e) * 100 > rules["equity_max"] + 1e-9:
            continue
        vol = p.volatility(w, cov)
        if cm.loss_estimate_95(ret, vol) > rules["loss_limit"] + 1e-9:
            continue
        survivors.append((vol, w))
    survivors.sort(key=lambda s: s[0])
    for _, w in survivors:   # the history rule is the slow one, so test it last, lowest risk first
        if cm.worst_12_month_return(w, est["monthly"]) >= -rules["loss_limit"] - 1e-9:
            return w
    return None


# ---------------------------------------------------------------- bridges, turnover, cost
def risk_contributions(weights, cov):
    """Each fund's share of portfolio volatility, in percent; the shares add up to the volatility."""
    n = len(weights)
    vol = p.volatility(weights, cov) / 100
    if vol == 0:
        return [0.0] * n
    return [weights[i] * sum(cov[i][j] * weights[j] for j in range(n)) / vol * 100 for i in range(n)]


def bridge(start, end, est):
    """Benchmark-to-portfolio bridge: per fund, the weight change and what it adds to return and risk."""
    rc_start, rc_end = risk_contributions(start, est["cov"]), risk_contributions(end, est["cov"])
    rows = []
    for i, t in enumerate(est["tickers"]):
        rows.append({"fund": t, "from": start[i] * 100, "to": end[i] * 100,
                     "change": (end[i] - start[i]) * 100,
                     "return_added": (end[i] - start[i]) * est["returns"][i],
                     "risk_added": rc_end[i] - rc_start[i]})
    return rows


def one_way_turnover(start, end):
    """Percent of the portfolio sold (= bought) to move from start to end."""
    return sum(abs(a - b) for a, b in zip(start, end)) / 2 * 100


def trading_cost(start, end, cost=TRADE_COST):
    """Percent of the portfolio: cost charged on everything sold and everything bought."""
    return 2 * one_way_turnover(start, end) * cost / 100


def rebalance_turnover(weights, monthly, every=12):
    """One-way turnover (percent) needed at each rebalance if weights drift for `every` months."""
    out, held = [], list(weights)
    for t, row in enumerate(monthly, start=1):
        grown = [h * (1 + r) for h, r in zip(held, row)]
        total = sum(grown)
        held = [g / total for g in grown]
        if t % every == 0:
            out.append(one_way_turnover(held, weights))
            held = list(weights)
    return out


# ---------------------------------------------------------------- stress run
def _run(group, label, est, rules=cm.RULES, cost_drag=0.0):
    w = constrained_portfolio(est, rules, cost_drag)
    return {"group": group, "label": label,
            "weights": None if w is None else [round(x * 100) for x in w]}


def stress_run(rows_all, rows, base_est, rules=cm.RULES):
    """The constrained search repeated with one thing changed each time.

    rows_all includes any partial month; rows are the complete months; base_est is the base-case
    estimate. Groups: estimates, window, costs, constraints.
    """
    runs = [_run("base", "Base case", base_est, rules)]
    for i, t in enumerate(base_est["tickers"]):
        for sign in (+1, -1):
            shocked = list(base_est["returns"])
            shocked[i] += sign * ESTIMATE_SHOCK
            runs.append(_run("estimates", f"{t} return {sign * ESTIMATE_SHOCK:+.0f} point",
                             with_returns(base_est, shocked), rules))
    n = len(base_est["monthly"])
    if n >= OOS_ESTIMATION_MONTHS + 12:
        runs.append(_run("window", "Last 36 months", estimate(rows, 36), rules))
        runs.append(_run("window", f"First {OOS_ESTIMATION_MONTHS} months",
                         estimate(rows[:OOS_ESTIMATION_MONTHS + 2]), rules))
    if len(rows_all) > len(rows):
        runs.append(_run("window", f"All {n + len(rows_all) - len(rows)} months, partial month included",
                         estimate(rows_all), rules))
    for drag in (0.10, 0.25):
        runs.append(_run("costs", f"All-in cost drag {drag:.2f}% a year", base_est, rules, drag))
    base = rules
    for key, value, label in (
            ("objective", base["objective"] - 0.5, "Objective {:.1f}%"),
            ("objective", base["objective"] + 0.5, "Objective {:.1f}%"),
            ("reserve_min", 10.0, "Reserve minimum {:.0f}%"),
            ("equity_max", 50.0, "Equity cap {:.0f}%"),
            ("loss_limit", 5.0, "Loss limit {:.0f}%"),
            ("loss_limit", 15.0, "Loss limit {:.0f}%")):
        runs.append(_run("constraints", label.format(value), base_est, {**base, key: value}))
    return runs


def weight_ranges(runs, tickers):
    """Lowest and highest weight each fund (and total equity) takes across the feasible runs."""
    feasible = [r["weights"] for r in runs if r["weights"] is not None]
    out = {t: (min(w[i] for w in feasible), max(w[i] for w in feasible))
           for i, t in enumerate(tickers)}
    eq = [sum(x for x, t in zip(w, tickers) if cm.UNIVERSE[t][3]) for w in feasible]
    out["Equity (VTI + VXUS)"] = (min(eq), max(eq))
    return out


def largest_move(runs):
    """(points, run label, fund index): the largest single-fund weight change from the base case."""
    base = runs[0]["weights"]
    best = (0, "none", 0)
    for r in runs[1:]:
        if r["weights"] is None or base is None:
            continue
        for i, (a, b) in enumerate(zip(base, r["weights"])):
            if abs(a - b) > best[0]:
                best = (abs(a - b), r["label"], i)
    return best


# ---------------------------------------------------------------- named scenarios
def scenarios(portfolios, est, rows):
    """Named scenarios replayed on fixed weights. portfolios: {name: decimal weights}."""
    labels, monthly = monthly_returns(rows)
    tickers = est["tickers"]
    out = []

    year = [row for label, row in zip(labels, monthly) if label.startswith("2022")]
    if len(year) == 12:
        fund = [(_compound([r[i] for r in year])) for i in range(len(tickers))]
        out.append({"name": "2022 rate shock replayed",
                    "detail": "Each fund's actual 2022 return: " + ", ".join(
                        f"{t} {x:+.1f}%" for t, x in zip(tickers, fund)),
                    "results": {name: _compound(cm.portfolio_returns(w, year))
                                for name, w in portfolios.items()}, "unit": "12-month return %"})

    shock = {"BIL": 0.0, "IEF": 5.0, "LQD": -5.0, "VTI": -30.0, "VXUS": -30.0}
    out.append({"name": "Equity drawdown (hypothetical)",
                "detail": "One-off shock: " + ", ".join(f"{t} {shock[t]:+.0f}%" for t in tickers),
                "results": {name: sum(w * shock[t] for w, t in zip(weights, tickers))
                            for name, weights in portfolios.items()}, "unit": "return %"})

    high = 0.80
    corr = [row[:] for row in est["corr"]]
    for i, a in enumerate(tickers):
        for j, b in enumerate(tickers):
            bond_a = a in ("IEF", "LQD")
            bond_b = b in ("IEF", "LQD")
            if (bond_a and cm.UNIVERSE[b][3]) or (bond_b and cm.UNIVERSE[a][3]):
                corr[i][j] = max(corr[i][j], high)
    stressed = with_corr(est, corr)
    out.append({"name": "Stock-bond correlation at +0.80",
                "detail": "Every bond-equity correlation raised to at least +0.80; "
                          "returns and volatilities unchanged",
                "results": {name: cm.loss_estimate_95(p.expected_return(w, est["returns"]),
                                                      p.volatility(w, stressed["cov"]))
                            for name, w in portfolios.items()}, "unit": "one-year 95% loss estimate %"})
    return out


def _compound(decimal_returns):
    growth = 1.0
    for r in decimal_returns:
        growth *= 1 + r
    return (growth - 1) * 100


# ---------------------------------------------------------------- out-of-sample test
def realized(weights, monthly):
    """Realized result of holding fixed weights (rebalanced monthly) over `monthly`."""
    series = cm.portfolio_returns(weights, monthly)
    n = len(series)
    growth, peak, drawdown = 1.0, 1.0, 0.0
    for r in series:
        growth *= 1 + r
        peak = max(peak, growth)
        drawdown = min(drawdown, growth / peak - 1)
    mean = sum(series) / n
    var = sum((r - mean) ** 2 for r in series) / (n - 1)
    return {"months": n, "total_return": (growth - 1) * 100,
            "annual_return": (growth ** (12 / n) - 1) * 100,
            "volatility": var ** 0.5 * 12 ** 0.5 * 100, "max_drawdown": drawdown * 100}


def out_of_sample(rows, n_est=OOS_ESTIMATION_MONTHS, rules=cm.RULES):
    """Estimate on the first n_est monthly returns, hold for the rest, compare with the baselines.

    Returns None when the file is too short to leave 12 months to hold.
    """
    if len(rows) - 2 < n_est + 12:
        return None
    early = estimate(rows[:n_est + 2])
    labels, monthly = monthly_returns(rows)
    later, later_labels = monthly[n_est:], labels[n_est:]
    names = baselines(early)
    chosen = constrained_portfolio(early, rules)
    if chosen is not None:
        names = {"Constrained portfolio (estimated on the early window)": chosen, **names}
    return {"estimation": early["label"], "holding": f"{later_labels[0]} to {later_labels[-1]} "
            f"({len(later)} months)", "feasible": chosen is not None,
            "results": {name: {"weights": [round(w * 100, 1) for w in weights],
                               **realized(weights, later)} for name, weights in names.items()}}


# ---------------------------------------------------------------- stop condition and triggers
def trailing_12m(weights, monthly):
    return _compound(cm.portfolio_returns(weights, monthly)[-12:])


def stop_conditions(chosen, est, runs, signal_failed=None, rules=cm.RULES):
    """Each condition with its current value and whether it has fired."""
    base_feasible = chosen is not None
    move, where, i = largest_move(runs)
    infeasible = [r["label"] for r in runs if r["weights"] is None]
    limit = rules["loss_limit"]
    out = [
        {"id": "STOP-1", "kind": "stop",
         "condition": "No mix on the grid passes every mandate rule on the current estimates",
         "value": "a mix passes" if base_feasible else "no mix passes", "fired": not base_feasible},
        {"id": "STOP-2", "kind": "stop",
         "condition": f"The held portfolio's trailing 12-month return is below -{limit:.0f}%",
         "value": "n/a" if chosen is None else f"{trailing_12m(chosen, est['monthly']):+.2f}%",
         "fired": chosen is not None and trailing_12m(chosen, est["monthly"]) < -limit},
        {"id": "GATE-1", "kind": "adopt gate",
         "condition": f"No weight moves more than {STABILITY_LIMIT:.0f} points anywhere in the stress run",
         "value": f"{move:.0f} points ({est['tickers'][i]}, {where})", "fired": move > STABILITY_LIMIT},
        {"id": "GATE-2", "kind": "adopt gate",
         "condition": "Every stress run still finds a mix that passes the mandate",
         "value": "all feasible" if not infeasible else "no mix under: " + "; ".join(infeasible),
         "fired": bool(infeasible)},
    ]
    if signal_failed is not None:
        out.append({"id": "SIGNAL", "kind": "signal failure rule",
                    "condition": "The signal rule's holdout net return trails buy-and-hold",
                    "value": "trails" if signal_failed else "does not trail", "fired": signal_failed})
    return out


# ---------------------------------------------------------------- cross-checks beyond the base requirement
def grid_check(est, rules=cm.RULES, fine_step=2.5):
    """The same search on a finer grid: how much does the 5-point grid cost?"""
    coarse, fine = constrained_portfolio(est, rules), constrained_portfolio(est, rules, step=fine_step)
    if coarse is None or fine is None:
        return None
    return {"fine_step": fine_step,
            "coarse_weights": [round(w * 100, 1) for w in coarse],
            "fine_weights": [round(w * 100, 1) for w in fine],
            "coarse_volatility": p.volatility(coarse, est["cov"]),
            "fine_volatility": p.volatility(fine, est["cov"]),
            "largest_weight_gap": max(abs(a - b) for a, b in zip(coarse, fine)) * 100}


def estimate_from_monthly(tickers, monthly):
    """Estimates from a list of monthly return rows (decimal), same conventions as estimate()."""
    series = [[row[i] for row in monthly] for i in range(len(tickers))]
    returns = [statistics.mean(s) * 12 * 100 for s in series]
    vols = [statistics.stdev(s) * math.sqrt(12) * 100 for s in series]
    corr = [[1.0 if i == j else p.correlation(series[i], series[j]) for j in range(len(series))]
            for i in range(len(series))]
    return {"tickers": tickers, "returns": returns, "vols": vols, "corr": corr,
            "cov": p.covariance_matrix(vols, corr), "monthly": monthly, "months": [], "label": "resampled"}


def bootstrap(est, rules=cm.RULES, runs=BOOTSTRAP_RUNS, seed=BOOTSTRAP_SEED):
    """Estimation error: resample the months with replacement, rerun the search each time.

    Rule M7 is tested on the real history in every run, so only the estimates are resampled.
    Returns, per fund and for total equity, the 5th, 50th and 95th percentile weight.
    """
    rng = random.Random(seed)
    tickers, monthly = est["tickers"], est["monthly"]
    found = []
    for _ in range(runs):
        sample = [monthly[rng.randrange(len(monthly))] for _ in monthly]
        try:
            resampled = estimate_from_monthly(tickers, sample)
        except ZeroDivisionError:
            continue
        w = constrained_portfolio({**resampled, "monthly": monthly}, rules)
        if w is not None:
            found.append([round(x * 100) for x in w])
    if not found:
        return {"runs": runs, "seed": seed, "feasible": 0, "weights": {}}

    def pct(values, q):
        ordered = sorted(values)
        return ordered[min(len(ordered) - 1, int(q * len(ordered)))]

    columns = {t: [w[i] for w in found] for i, t in enumerate(tickers)}
    columns["Equity (VTI + VXUS)"] = [sum(x for x, t in zip(w, tickers) if cm.UNIVERSE[t][3]) for w in found]
    return {"runs": runs, "seed": seed, "feasible": len(found),
            "weights": {k: {"p05": pct(v, 0.05), "median": pct(v, 0.50), "p95": pct(v, 0.95)}
                        for k, v in columns.items()}}


def monitoring(b):
    """The memo's monitoring triggers with today's value and status."""
    est, chosen, rules = b["estimates"], b["chosen"], b["rules"]
    if chosen is None:
        return []
    tickers = est["tickers"]
    equity = sum(w for w, t in zip(chosen, tickers) if cm.UNIVERSE[t][3]) * 100
    low, high = b["ranges"]["Equity (VTI + VXUS)"]
    bil = est["returns"][tickers.index("BIL")] if "BIL" in tickers else None
    t12 = trailing_12m(chosen, est["monthly"])
    worst = cm.worst_12_month_return(chosen, est["monthly"])
    turn = max(b["turnover"]["rebalance"]) if b["turnover"]["rebalance"] else 0.0
    rows = [
        ("Trailing 12-month return", f"below -{rules['loss_limit']:.0f}% (stop)", f"{t12:+.2f}%",
         t12 < -rules["loss_limit"]),
        ("Trailing 12-month return, early warning", f"below -{rules['loss_limit'] / 2:.0f}% (review)",
         f"{t12:+.2f}%", t12 < -rules["loss_limit"] / 2),
        ("Equity weight (VTI + VXUS)", f"outside {low}% to {high}% (rebalance)", f"{equity:.0f}%",
         not low <= equity <= high),
        ("Worst 12 months in the sample at current weights", "below -8% (review)", f"{worst:+.2f}%",
         worst < -8.0),
        ("Largest yearly rebalance, one-way", f"above {TURNOVER_BUDGET:.0f}% (review)", f"{turn:.1f}%",
         turn > TURNOVER_BUDGET),
    ]
    if bil is not None:
        rows.insert(2, ("BIL return estimate", "one point below the value at approval (re-run)",
                        f"{bil:.2f}%", False))
    return [{"trigger": a, "fires when": c, "now": v, "fired": f} for a, c, v, f in rows]


# ---------------------------------------------------------------- the whole pipeline
def build(rows_all=None, signal_failed=None, rules=None, last_complete=LAST_COMPLETE_MONTH):
    """Everything the app and the visible output show for the portfolio side.

    rules: the mandate limits to test against (default: the mandate). last_complete: rows dated
    after this month are treated as partial and left out of the base case.
    """
    rules = dict(cm.RULES if rules is None else rules)
    rows_all = validate_rows(read_rows() if rows_all is None else rows_all)
    rows, dropped = complete_rows(rows_all, last_complete)
    if len(rows) - 1 < 25:
        raise ValueError(f"need at least 25 complete monthly prices, found {len(rows) - 1}")
    est = estimate(rows)
    names = baselines(est)
    chosen = constrained_portfolio(est, rules)
    portfolios = dict(names)
    if chosen is not None:
        portfolios["Constrained portfolio"] = chosen
    runs = stress_run(rows_all, rows, est, rules)
    bench = names["Benchmark 60/40"]
    result = {
        "rules": rules, "last_month": rows[-1][0][:7], "months": len(est["monthly"]), "window": est["label"],
        "dropped_rows": [r[0] for r in dropped],
        "estimates": est, "portfolios": portfolios,
        "judged": {name: judge(w, est, rules) for name, w in portfolios.items()},
        "chosen": chosen, "stress": runs,
        "ranges": weight_ranges(runs, est["tickers"]) if chosen is not None else {},
        "scenarios": scenarios(portfolios, est, rows),
        "out_of_sample": out_of_sample(rows, rules=rules),
        "stops": stop_conditions(chosen, est, runs, signal_failed, rules),
    }
    if chosen is not None:
        result["bridge"] = bridge(bench, chosen, est)
        result["turnover"] = {
            "from_benchmark": one_way_turnover(bench, chosen),
            "cost_from_benchmark": trading_cost(bench, chosen),
            "rebalance": rebalance_turnover(chosen, est["monthly"]),
            "budget": TURNOVER_BUDGET, "cost_rate": TRADE_COST,
        }
    return result


def main():
    b = build()
    est = b["estimates"]
    print(f"{cm.CLIENT}\nWindow: {b['window']}; rows excluded as partial: {b['dropped_rows'] or 'none'}\n")
    print(f"{'Estimate':<22}" + "".join(f"{t:>8}" for t in est["tickers"]))
    print(f"{'Return (estimate) %':<22}" + "".join(f"{x:>8.2f}" for x in est["returns"]))
    print(f"{'Volatility %':<22}" + "".join(f"{x:>8.2f}" for x in est["vols"]) + "\n")
    for name, j in b["judged"].items():
        m = j["measures"]
        print(f"{name:<24}" + " / ".join(f"{w:.0f}" for w in j["weights"]) +
              f"   return {m['return']:.2f}  vol {m['volatility']:.2f}  "
              f"95% loss {m['loss_95']:.2f}  worst 12m {m['worst_12m']:.2f}   {j['verdict']}")
    print("\nStress run")
    for r in b["stress"]:
        print(f"  {r['group']:<12}{r['label']:<44}"
              + ("no mix passes" if r["weights"] is None else " / ".join(str(w) for w in r["weights"])))
    for s in b["stops"]:
        print(f"  {s['id']:<7} {'FIRED' if s['fired'] else 'ok':<6} {s['condition']}: {s['value']}")


if __name__ == "__main__":
    main()
