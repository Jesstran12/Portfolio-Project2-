"""Project 2 - the point-in-time signal: a frozen yield-trend rule on DGS10, tested on real funds.

The rule card is rule-card-dgs10.md, committed before this backtest was first run on real data.
The data card is docs/data-cards.md. Standard library only. Edit the inputs at the top;
everything below is computed from them.
Run: python3 signal_rule.py
"""

import csv
import random

import process as pr

# ---------------------------------------------------------------- editable inputs (the rule card)
DGS10_FILE = "data/dgs10.csv"      # FRED series DGS10, daily, percent a year
DGS10_DOWNLOADED = "2026-11-23"
VINTAGE_FILE = "data/dgs10_vintage_2026-09-30.csv"   # ALFRED: DGS10 as known on 2026-09-30
RISK_FUND = "IEF"                  # held next month when the 10-year yield fell this month
SAFE_FUND = "BIL"                  # held otherwise; the run starts here
LAG = 1                            # months: this month's signal decides the position LAG months later
COST = 0.10                        # percent, charged in any month the position switches
DEVELOPMENT = ("2021-12", "2024-12")
HOLDOUT = ("2025-01", "2026-09")   # run once, never tuned
PLACEBO_RUNS = 1000
PLACEBO_SEED = 43900
# ---------------------------------------------------------------- end of inputs

FROZEN = {"lag": LAG, "cost": COST}  # the values committed on the rule card; the app locks these


def read_dgs10(path=DGS10_FILE):
    """[(date, yield %)] from the FRED CSV, oldest first; days with no market are skipped."""
    out = []
    with open(path, newline="") as f:
        for row in list(csv.reader(f))[1:]:
            if len(row) >= 2 and row[1].strip() not in ("", "."):
                out.append((row[0].strip(), float(row[1])))
    return out


def known_at_month_end(observations):
    """{month: (date, yield)}: the latest value already published at each month's last close.

    DGS10 for day t is published on day t+1, so at the close of the month's last trading day the
    newest value in hand is the one for the trading day before it: the second-to-last observation
    of the month.
    """
    by_month = {}
    for date, value in observations:
        by_month.setdefault(date[:7], []).append((date, value))
    return {m: obs[-2] for m, obs in by_month.items() if len(obs) >= 2}


def signals(known):
    """{month: change in the known month-end yield from the month before, percentage points}."""
    months = sorted(known)
    return {m: known[m][1] - known[prev][1] for prev, m in zip(months, months[1:])
            if _next_month(prev) == m}


def _next_month(month):
    year, mon = int(month[:4]), int(month[5:7])
    return f"{year + (mon == 12)}-{mon % 12 + 1:02d}"


def _shift(month, back):
    year, mon = int(month[:4]), int(month[5:7])
    total = year * 12 + (mon - 1) - back
    return f"{total // 12}-{total % 12 + 1:02d}"


def fund_returns(rows=None):
    """{month: {ticker: return %}} from the complete months of prices.csv."""
    if rows is None:
        rows, _ = pr.complete_rows(pr.validate_rows(pr.read_rows()))
    labels, monthly = pr.monthly_returns(rows)
    tickers = rows[0][1:]
    return {m: {t: r * 100 for t, r in zip(tickers, row)} for m, row in zip(labels, monthly)}


def compound(rets):
    """Compounded return in percent from a list of monthly percent returns."""
    g = 1.0
    for r in rets:
        g *= 1 + r / 100
    return (g - 1) * 100


def run(signal, returns, lag=LAG, cost=COST, development=DEVELOPMENT, holdout=HOLDOUT,
        risk=RISK_FUND, safe=SAFE_FUND):
    """{'Development': {...}, 'Holdout': {...}, 'failure': bool}.

    The rule: signal below 0 (the yield fell) -> hold the risk fund; otherwise the safe fund.
    The holdout starts from the position held at the end of development.
    """
    held = safe
    out = {}
    for label, period in (("Development", development), ("Holdout", holdout)):
        gross, net, bh, safe_only, switches, in_risk, log = [], [], [], [], 0, 0, []
        for m in sorted(x for x in returns if period[0] <= x <= period[1]):
            source = _shift(m, lag)
            if source not in signal:
                raise ValueError(f"no signal for {source}, needed to decide {m}")
            position = risk if signal[source] < 0 else safe
            r = returns[m][position]
            switched = position != held
            switches += switched
            in_risk += position == risk
            held = position
            gross.append(r)
            net.append(r - cost if switched else r)
            bh.append(returns[m][risk])
            safe_only.append(returns[m][safe])
            log.append({"month": m, "signal_month": source, "signal": signal[source],
                        "position": position, "switched": switched, "return": r})
        out[label] = {"gross": compound(gross), "net": compound(net), "buy_and_hold": compound(bh),
                      "safe_only": compound(safe_only), "switches": switches,
                      "months": len(gross), "months_in_risk": in_risk, "log": log}
    out["failure"] = out["Holdout"]["net"] < out["Holdout"]["buy_and_hold"]
    return out


def placebo(signal, returns, runs=PLACEBO_RUNS, seed=PLACEBO_SEED, lag=LAG, cost=COST):
    """Shuffle the signal across months and rerun: how often does a meaningless signal do as well?

    Returns the placebo holdout net returns (sorted) and the share that match or beat the real rule.
    """
    rng = random.Random(seed)
    actual = run(signal, returns, lag, cost)["Holdout"]["net"]
    months, values = sorted(signal), [signal[m] for m in sorted(signal)]
    nets = []
    for _ in range(runs):
        shuffled = values[:]
        rng.shuffle(shuffled)
        nets.append(run(dict(zip(months, shuffled)), returns, lag, cost)["Holdout"]["net"])
    nets.sort()
    return {"runs": runs, "seed": seed, "actual": actual, "median": nets[len(nets) // 2],
            "p05": nets[int(0.05 * runs)], "p95": nets[int(0.95 * runs) - 1],
            "share_at_least_actual": sum(n >= actual for n in nets) / runs * 100}


def revision_check(today=DGS10_FILE, vintage=VINTAGE_FILE):
    """Compare today's download with the ALFRED vintage: values on the same dates that differ."""
    now, then = dict(read_dgs10(today)), dict(read_dgs10(vintage))
    shared = [d for d in then if d in now]
    return {"vintage_last_date": max(then), "shared_dates": len(shared),
            "revised": sum(abs(now[d] - then[d]) > 1e-9 for d in shared),
            "missing_today": len(then) - len(shared),
            "new_since": sum(d > max(then) for d in now)}


def load():
    """(signal by month, fund returns by month, known month-end yields) from the committed files."""
    known = known_at_month_end(read_dgs10())
    return signals(known), fund_returns(), known


def main():
    signal, returns, _ = load()
    res = run(signal, returns)
    print(f"Rule: 10-year yield fell over the month -> hold {RISK_FUND} next month, else {SAFE_FUND}")
    print(f"Lag {LAG} month(s), cost {COST:.2f}% a switch")
    print(f"{'Period':<13}{'Months':>7}{'Rule gross':>11}{'Rule net':>10}"
          f"{'Hold ' + RISK_FUND:>10}{'Hold ' + SAFE_FUND:>10}{'Switches':>10}")
    for label in ("Development", "Holdout"):
        r = res[label]
        print(f"{label:<13}{r['months']:>7}{r['gross']:>11.2f}{r['net']:>10.2f}"
              f"{r['buy_and_hold']:>10.2f}{r['safe_only']:>10.2f}{r['switches']:>10}")
    gap = res["Holdout"]["buy_and_hold"] - res["Holdout"]["net"]
    print(f"Failure rule (stop if holdout net trails buy-and-hold {RISK_FUND}): "
          f"{'TRIGGERED' if res['failure'] else 'not triggered'} ({gap:+.2f} points)")


if __name__ == "__main__":
    main()
