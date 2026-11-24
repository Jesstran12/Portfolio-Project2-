"""Project 2 - the one command that regenerates everything in output/.

Writes output/decision-numbers.json (the single source of truth for every number quoted in the
memo and the README; a test compares them), output/decision-report.md (the same numbers as a
page a grader can read on GitHub), and the three lab outputs. Nothing here does any math: it
calls process.py and signal_rule.py and formats what they return.
Run: python3 make_output.py
"""

import json
import os
import subprocess
import sys

import client_mandate as cm
import process as pr
import signal_rule as sr

OUT = "output"
SIGNAL_COSTS = (0.00, 0.10, 0.25)   # cost sensitivity shown in the report; 0.10 is the frozen value
LAB_SCRIPTS = ("backtest.py", "portfolio.py", "mandate.py")


def r2(x):
    return round(x, 2)


def status(stops):
    fired = {s["id"] for s in stops if s["fired"]}
    if fired & {"STOP-1", "STOP-2"}:
        return "STOP"
    return "PILOT (adoption gates not met)" if fired & {"GATE-1", "GATE-2"} else "ADOPTION GATES MET"


def numbers():
    signal, returns, known = sr.load()
    locked = sr.run(signal, returns)
    b = pr.build(signal_failed=locked["failure"])
    est, tickers = b["estimates"], b["estimates"]["tickers"]
    move, where, i = pr.largest_move(b["stress"])

    def period(res, k):
        return {x: (r2(v) if isinstance(v, float) else v) for x, v in res[k].items() if x != "log"}

    portfolios = {}
    for name, j in b["judged"].items():
        m = j["measures"]
        portfolios[name] = {"weights": dict(zip(tickers, j["weights"])),
                            "return": r2(m["return"]), "volatility": r2(m["volatility"]),
                            "loss_95": r2(m["loss_95"]), "worst_12m": r2(m["worst_12m"]),
                            "reserve": r2(m["reserve"]), "equity": r2(m["equity"]),
                            "verdict": j["verdict"],
                            "checks": [{"rule": rid, "test": text, "measured": r2(v), "passed": ok}
                                       for rid, text, v, ok in j["checks"]]}
    leak = sr.run(signal, returns, lag=0)
    boot = pr.bootstrap(est)
    return {
        "as_of": pr.AS_OF, "client": cm.CLIENT,
        "inputs": {
            "prices": {"file": pr.PRICES_FILE, "source": "Yahoo Finance, monthly Adj Close",
                       "downloaded": pr.PRICES_DOWNLOADED, "sha256": pr.sha256(pr.PRICES_FILE),
                       "window": b["window"], "monthly_returns": b["months"],
                       "rows_excluded_as_partial": b["dropped_rows"]},
            "dgs10": {"file": sr.DGS10_FILE, "source": "FRED series DGS10",
                      "downloaded": sr.DGS10_DOWNLOADED, "sha256": pr.sha256(sr.DGS10_FILE)},
            "dgs10_vintage": {"file": sr.VINTAGE_FILE, "source": "ALFRED, DGS10 as known on 2026-09-30",
                              "sha256": pr.sha256(sr.VINTAGE_FILE)},
        },
        "mandate": {"rules": b["rules"], "spending_rate": cm.SPENDING_RATE,
                    "inflation_assumption": cm.INFLATION_ASSUMPTION, "benchmark": cm.BENCHMARK,
                    "grid_step": pr.STEP, "stability_limit": pr.STABILITY_LIMIT,
                    "turnover_budget": pr.TURNOVER_BUDGET, "trade_cost": pr.TRADE_COST},
        "estimates": {t: {"return": r2(est["returns"][k]), "volatility": r2(est["vols"][k])}
                      for k, t in enumerate(tickers)},
        "correlation": {t: {u: r2(est["corr"][k][n]) for n, u in enumerate(tickers)}
                        for k, t in enumerate(tickers)},
        "portfolios": portfolios,
        "bridge": [{k: (r2(v) if isinstance(v, float) else v) for k, v in row.items()}
                   for row in b["bridge"]],
        "bridge_total": {"return_added": r2(sum(row["return_added"] for row in b["bridge"])),
                         "risk_added": r2(sum(row["risk_added"] for row in b["bridge"]))},
        "turnover": {"from_benchmark": r2(b["turnover"]["from_benchmark"]),
                     "cost_from_benchmark": r2(b["turnover"]["cost_from_benchmark"]),
                     "yearly_rebalance": [r2(x) for x in b["turnover"]["rebalance"]]},
        "stress": [{"group": r["group"], "change": r["label"],
                    "weights": None if r["weights"] is None else dict(zip(tickers, r["weights"]))}
                   for r in b["stress"]],
        "allocation_range": {k: {"low": lo, "high": hi} for k, (lo, hi) in b["ranges"].items()},
        "largest_move": {"points": move, "fund": tickers[i], "run": where},
        "scenarios": [{"name": s["name"], "detail": s["detail"], "unit": s["unit"],
                       "results": {n: r2(v) for n, v in s["results"].items()}} for s in b["scenarios"]],
        "out_of_sample": {**{k: b["out_of_sample"][k] for k in ("estimation", "holding", "feasible")},
                          "results": {n: {k: (r2(v) if isinstance(v, float) else v) for k, v in res.items()}
                                      for n, res in b["out_of_sample"]["results"].items()}},
        "stops": b["stops"], "process_status": status(b["stops"]),
        "monitoring": pr.monitoring(b),
        "grid_check": {k: (r2(v) if isinstance(v, float) else v)
                       for k, v in pr.grid_check(est).items()},
        "bootstrap": {**boot, "infeasible_share": r2((boot["runs"] - boot["feasible"]) / boot["runs"] * 100)},
        "signal": {
            "rule": f"DGS10 fell over the month -> hold {sr.RISK_FUND} next month, else {sr.SAFE_FUND}",
            "lag": sr.LAG, "cost": sr.COST, "development_period": list(sr.DEVELOPMENT),
            "holdout_period": list(sr.HOLDOUT),
            "development": period(locked, "Development"), "holdout": period(locked, "Holdout"),
            "failure_rule_triggered": locked["failure"],
            "holdout_gap": r2(locked["Holdout"]["buy_and_hold"] - locked["Holdout"]["net"]),
            "lag_0_leak": {"development_net": r2(leak["Development"]["net"]),
                           "holdout_net": r2(leak["Holdout"]["net"])},
            "placebo": {k: (r2(v) if isinstance(v, float) else v)
                        for k, v in sr.placebo(signal, returns).items()},
            "cost_sensitivity": [
                {"cost": c, "holdout_net": r2(res["Holdout"]["net"]),
                 "development_net": r2(res["Development"]["net"]),
                 "failure_rule_triggered": res["failure"]}
                for c in SIGNAL_COSTS for res in [sr.run(signal, returns, cost=c)]],
            "revision_check": sr.revision_check(),
            "last_signal_used": {"month": "2026-08", "known_value": known["2026-08"][1],
                                 "known_date": known["2026-08"][0]},
        },
    }


# ---------------------------------------------------------------- the readable report
def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    return "\n".join(out + ["| " + " | ".join(str(c) for c in row) + " |" for row in rows])


def wtext(weights):
    return " / ".join(f"{w:.0f}" for w in weights.values())


def report(n):
    tickers = list(n["estimates"])
    sig, p = n["signal"], n["portfolios"]
    rules = n["mandate"]["rules"]
    parts = [
        "# Decision report (visible executed output)",
        "Generated by `python3 make_output.py`. Do not edit by hand: a test regenerates the numbers "
        "and fails if this file is stale. Every figure also appears in "
        "[`decision-numbers.json`](decision-numbers.json).",
        "Built with AI help (Claude Code); the analysis and the decision are the student's. "
        "Education, not investment advice.",
        f"**As of {n['as_of']}.** Client: {n['client']}.",
        "## Inputs",
        table(["Input", "File", "Source", "Downloaded", "SHA-256"],
              [[k, f"`{v['file']}`", v["source"], v.get("downloaded", "2026-11-23"), f"`{v['sha256']}`"]
               for k, v in n["inputs"].items()]),
        f"Estimation window: {n['inputs']['prices']['window']}. Rows excluded as partial months: "
        f"{', '.join(n['inputs']['prices']['rows_excluded_as_partial']) or 'none'}. "
        "Data cards: [`docs/data-cards.md`](../docs/data-cards.md).",
        "## Mandate limits",
        table(["Limit", "Value"],
              [["Return objective (M5)", f"{rules['objective']:.1f}% a year = "
                f"{n['mandate']['spending_rate']:.1f}% payout + {n['mandate']['inflation_assumption']:.1f}% inflation assumption"],
               ["Reserve minimum, BIL + IEF (M3)", f"{rules['reserve_min']:.1f}%"],
               ["Equity cap, VTI + VXUS (M4)", f"{rules['equity_max']:.0f}%"],
               ["Loss limit over twelve months (M6, M7)", f"{rules['loss_limit']:.0f}%"],
               ["Benchmark", " / ".join(f"{t} {w}" for t, w in n["mandate"]["benchmark"].items())]]),
        "## Estimates (percent a year; historical estimates, not forecasts)",
        table(["", *tickers],
              [["Return = mean monthly return × 12", *[f"{n['estimates'][t]['return']:.2f}" for t in tickers]],
               ["Volatility = monthly st. dev. × √12", *[f"{n['estimates'][t]['volatility']:.2f}" for t in tickers]]]),
        "Correlation of monthly returns:",
        table(["", *tickers], [[t, *[f"{n['correlation'][t][u]:.2f}" for u in tickers]] for t in tickers]),
        "## Decision numbers: the portfolios and their mandate verdicts",
        table(["Portfolio", "BIL / IEF / LQD / VTI / VXUS", "Return", "Volatility", "95% loss estimate",
               "Worst 12 months", "Verdict"],
              [[name, wtext(v["weights"]), f"{v['return']:.2f}", f"{v['volatility']:.2f}",
                f"{v['loss_95']:.2f}", f"{v['worst_12m']:.2f}", f"**{v['verdict']}**"] for name, v in p.items()]),
        "95% loss estimate = 1.645 × volatility − return. Weights are long-only in 5-point steps. "
        "Failed rules:",
        "\n".join(f"- {name}: " + "; ".join(f"{c['rule']} {c['test']} (measured {c['measured']:.2f}%)"
                                            for c in v["checks"] if not c["passed"])
                  for name, v in p.items() if v["verdict"] != "PASS"),
        "Rule by rule for the constrained portfolio:",
        table(["Rule", "Test", "Measured (%)", "Result"],
              [[c["rule"], c["test"], f"{c['measured']:.2f}", "PASS" if c["passed"] else "FAIL"]
               for c in p["Constrained portfolio"]["checks"]]),
        "## Bridge: benchmark to constrained portfolio",
        table(["Fund", "Benchmark %", "Portfolio %", "Change", "Adds to return", "Adds to volatility"],
              [[b["fund"], f"{b['from']:.0f}", f"{b['to']:.0f}", f"{b['change']:+.0f}",
                f"{b['return_added']:+.2f}", f"{b['risk_added']:+.2f}"] for b in n["bridge"]]
              + [["Total", "100", "100", "0", f"{n['bridge_total']['return_added']:+.2f}",
                  f"{n['bridge_total']['risk_added']:+.2f}"]]),
        f"One-way turnover to move from the benchmark: {n['turnover']['from_benchmark']:.0f}%, costing "
        f"{n['turnover']['cost_from_benchmark']:.2f}% of the portfolio at {n['mandate']['trade_cost']:.2f}% of "
        f"value traded. Yearly rebalance turnover in the sample: "
        f"{', '.join(f'{x:.1f}%' for x in n['turnover']['yearly_rebalance'])} "
        f"(budget {n['mandate']['turnover_budget']:.0f}%).",
        "## Stress run: the search repeated with one thing changed",
        table(["Group", "Change", "BIL / IEF / LQD / VTI / VXUS"],
              [[s["group"], s["change"], "no mix passes" if s["weights"] is None else wtext(s["weights"])]
               for s in n["stress"]]),
        f"Largest single move from the base case: {n['largest_move']['points']:.0f} points "
        f"({n['largest_move']['fund']}, {n['largest_move']['run']}).",
        "### Allocation range: lowest and highest weight across the feasible stress runs",
        table(["Fund", "Low %", "High %"], [[k, v["low"], v["high"]] for k, v in n["allocation_range"].items()]),
        "### Named scenarios on fixed weights",
        "\n\n".join(f"**{s['name']}** ({s['unit']}). {s['detail']}.\n\n" +
                    table(["Portfolio", s["unit"]], [[k, f"{v:.2f}"] for k, v in s["results"].items()])
                    for s in n["scenarios"]),
        "### Out-of-sample test",
        f"Estimated on {n['out_of_sample']['estimation']}, held unchanged over {n['out_of_sample']['holding']}.",
        table(["Portfolio", "Weights", "Realized return % a year", "Realized volatility %", "Largest drawdown %"],
              [[k, " / ".join(f"{w:.0f}" for w in v["weights"]), f"{v['annual_return']:.2f}",
                f"{v['volatility']:.2f}", f"{v['max_drawdown']:.2f}"]
               for k, v in n["out_of_sample"]["results"].items()]),
        "### Cross-checks on the search",
        f"**Finer grid.** The same search in {n['grid_check']['fine_step']}-point steps gives "
        f"{' / '.join(f'{w:g}' for w in n['grid_check']['fine_weights'])} at {n['grid_check']['fine_volatility']:.2f}% "
        f"volatility, against {n['grid_check']['coarse_volatility']:.2f}% on the 5-point grid. Largest weight "
        f"difference: {n['grid_check']['largest_weight_gap']:g} points.",
        f"**Estimation error (bootstrap).** The {n['inputs']['prices']['monthly_returns']} months were resampled with "
        f"replacement {n['bootstrap']['runs']} times (seed {n['bootstrap']['seed']}) and the search rerun on each. "
        f"A passing mix was found in {n['bootstrap']['feasible']} of them; in {n['bootstrap']['infeasible_share']:.1f}% "
        "no mix passed. Weights across the feasible resamples:",
        table(["Fund", "5th percentile %", "Median %", "95th percentile %"],
              [[k, v["p05"], v["median"], v["p95"]] for k, v in n["bootstrap"]["weights"].items()]),
        "## Monitoring triggers, evaluated now",
        table(["Trigger", "Fires when", "Now", "Status"],
              [[t["trigger"], t["fires when"], t["now"], "**FIRED**" if t["fired"] else "not fired"]
               for t in n["monitoring"]]),
        "## Stop conditions and adoption gates",
        table(["ID", "Type", "Condition", "Current value", "Status"],
              [[s["id"], s["kind"], s["condition"], s["value"], "**FIRED**" if s["fired"] else "not fired"]
               for s in n["stops"]]),
        f"**Process status: {n['process_status']}.**",
        "## The signal: frozen DGS10 rule",
        f"Rule: {sig['rule']}. Lag {sig['lag']} month, cost {sig['cost']:.2f}% a switch. "
        "Rule card: [`rule-card-dgs10.md`](../rule-card-dgs10.md).",
        table(["Period", "Months", "Rule gross %", "Rule net %", "Hold IEF %", "Hold BIL %", "Switches"],
              [[k.capitalize(), v["months"], f"{v['gross']:.2f}", f"{v['net']:.2f}", f"{v['buy_and_hold']:.2f}",
                f"{v['safe_only']:.2f}", v["switches"]]
               for k, v in (("development", sig["development"]), ("holdout", sig["holdout"]))]),
        f"**Failure rule: {'TRIGGERED' if sig['failure_rule_triggered'] else 'not triggered'}.** Holdout net "
        f"trails buy-and-hold IEF by {sig['holdout_gap']:.2f} points.",
        table(["Check", "Result"],
              [["Lag 0 (the leak), holdout net", f"{sig['lag_0_leak']['holdout_net']:.2f}%"],
               ["Placebo, median holdout net of 1,000 shuffled signals", f"{sig['placebo']['median']:.2f}%"],
               ["Placebo, share of shuffles at least as good as the real signal",
                f"{sig['placebo']['share_at_least_actual']:.1f}%"],
               ["DGS10 values revised between the 2026-09-30 vintage and today",
                f"{sig['revision_check']['revised']} of {sig['revision_check']['shared_dates']}"],
               *[[f"Cost {c['cost']:.2f}% a switch, holdout net",
                  f"{c['holdout_net']:.2f}% (failure rule "
                  f"{'triggered' if c['failure_rule_triggered'] else 'not triggered'})"]
                 for c in sig["cost_sensitivity"]]]),
    ]
    return "\n\n".join(parts) + "\n"


def lab_outputs():
    for script in LAB_SCRIPTS:
        done = subprocess.run([sys.executable, script], capture_output=True, text=True, check=True)
        with open(os.path.join(OUT, script.replace(".py", ".txt")), "w") as f:
            f.write(f"$ python3 {script}\n{done.stdout}")


def main():
    os.makedirs(OUT, exist_ok=True)
    n = numbers()
    with open(os.path.join(OUT, "decision-numbers.json"), "w") as f:
        json.dump(n, f, indent=2)
        f.write("\n")
    with open(os.path.join(OUT, "decision-report.md"), "w", encoding="utf-8") as f:
        f.write(report(n))
    lab_outputs()
    c = n["portfolios"]["Constrained portfolio"]
    print(f"As of {n['as_of']}: constrained portfolio {wtext(c['weights'])}, return estimate "
          f"{c['return']:.2f}%, volatility {c['volatility']:.2f}%, verdict {c['verdict']}.")
    print(f"Process status: {n['process_status']}. Signal failure rule: "
          f"{'triggered' if n['signal']['failure_rule_triggered'] else 'not triggered'}.")
    print(f"Wrote {OUT}/decision-report.md, {OUT}/decision-numbers.json and the lab outputs.")


if __name__ == "__main__":
    main()
