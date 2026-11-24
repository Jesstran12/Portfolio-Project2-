"""Project 2 - the Riverbend Reserve app: mandate verdicts, the stress run and the signal.

This file only lays out the page. Every number comes from process.py, client_mandate.py,
portfolio.py, signal_rule.py or backtest.py; there is no copy of the math here.
Run: python3 -m streamlit run app.py
"""
import csv
import io

import streamlit as st

import backtest as bt
import client_mandate as cm
import process as pr
import signal_rule as sr

st.set_page_config(page_title="Riverbend Reserve: mandate-checked portfolio", layout="wide")
st.title("Riverbend Reserve: a mandate-checked portfolio process")
st.caption("**AI announcement.** Built with Claude Code (Anthropic); the analysis, the checks and the "
           "decision are the student's. **Education, not investment advice.** A FIN 43900 course "
           "project on a hypothetical client.")

WORD = {True: "PASS", False: "FAIL"}


def words(ok):
    """Verdicts as words with a symbol, never colour alone."""
    return ("✔ PASS" if ok else "✘ FAIL")


def weights_text(weights):
    return " / ".join(f"{w:.0f}" for w in weights)


# ---------------------------------------------------------------- sidebar: data and what-if
with st.sidebar:
    st.header("Data")
    upload = st.file_uploader("Replace prices.csv (date, BIL, IEF, LQD, VTI, VXUS; monthly, oldest first)",
                              type="csv")
    partial_last = False
    if upload is not None:
        partial_last = st.checkbox("The last row is a partial month: leave it out", value=False)

    st.header("What-if: mandate limits")
    st.caption("The mandate's own numbers are the defaults. Move one and every verdict is re-tested.")
    R = cm.RULES
    rules = {
        "objective": st.number_input("M5 return objective (%)", 0.0, 20.0, R["objective"], 0.5),
        "reserve_min": st.number_input("M3 reserve minimum (%)", 0.0, 100.0, R["reserve_min"], 1.0),
        "equity_max": st.number_input("M4 equity cap (%)", 0.0, 100.0, R["equity_max"], 5.0),
        "loss_limit": st.number_input("M6 and M7 loss limit (%)", 1.0, 50.0, R["loss_limit"], 1.0),
    }
    what_if = rules != R

    st.header("What-if: signal")
    st.caption("Sensitivity only. The locked result never changes.")
    lag = st.select_slider("Signal lag (months)", options=[0, 1, 2], value=sr.FROZEN["lag"])
    cost = st.slider("Trading cost (% a switch)", 0.0, 1.0, sr.FROZEN["cost"], 0.05)


# ---------------------------------------------------------------- load and compute
@st.cache_data(show_spinner="Running the search and the stress run...")
def compute(rows_key, rules_key, last_complete, signal_failed):
    return pr.build([list(r) for r in rows_key], signal_failed=signal_failed, rules=dict(rules_key),
                    last_complete=last_complete)


@st.cache_data(show_spinner="Resampling the monthly returns...")
def bootstrap_cached(monthly_key, tickers_key, rules_key):
    months = [list(r) for r in monthly_key]
    return pr.bootstrap(pr.estimate_from_monthly(list(tickers_key), months), dict(rules_key))


try:
    signal, sig_returns, known = sr.load()
    locked = sr.run(signal, sig_returns, **sr.FROZEN)
except (OSError, ValueError, KeyError) as err:
    signal, locked = None, None
    signal_error = str(err)

try:
    if upload is None:
        source = f"prices.csv (committed; downloaded {pr.PRICES_DOWNLOADED})"
        raw = pr.read_rows()
        last_complete = pr.LAST_COMPLETE_MONTH
    else:
        source = f"{upload.name} (uploaded)"
        raw = [r for r in csv.reader(io.StringIO(upload.getvalue().decode("utf-8-sig"))) if r]
        checked = pr.validate_rows(raw)
        last_complete = checked[-2 if partial_last else -1][0][:7]
    b = compute(tuple(tuple(r) for r in raw), tuple(sorted(rules.items())), last_complete,
                None if locked is None else locked["failure"])
except (ValueError, UnicodeDecodeError, IndexError, ZeroDivisionError) as err:
    st.error(f"Could not use this price file: {err}. Expected a header row "
             "'date,BIL,IEF,LQD,VTI,VXUS' and one row of prices per month, oldest first.")
    st.stop()

est, tickers, chosen = b["estimates"], b["estimates"]["tickers"], b["chosen"]

st.info(f"**As of {pr.AS_OF if upload is None else b['last_month']}** · {source} · estimates from "
        f"{b['window']}" + (f" · excluded as partial: {', '.join(b['dropped_rows'])}"
                            if b["dropped_rows"] else ""))
if what_if:
    st.warning("What-if mode: at least one limit in the sidebar differs from the written mandate. "
               "The verdicts below use your limits, not the mandate's.")

tab_decision, tab_mandate, tab_stress, tab_signal, tab_data = st.tabs(
    ["1 Decision", "2 Mandate and portfolios", "3 Stress run", "4 Signal", "5 Data and method"])

# ---------------------------------------------------------------- 1 decision
with tab_decision:
    stops = {s["id"]: s for s in b["stops"]}
    stop_fired = stops["STOP-1"]["fired"] or stops["STOP-2"]["fired"]
    gate_fired = stops["GATE-1"]["fired"] or stops["GATE-2"]["fired"]
    if stop_fired:
        st.error("**Process status: STOP.** A stop condition has fired; see the table below.")
    elif gate_fired:
        st.warning("**Process status: PILOT, not adopt.** The portfolio passes the mandate, but an "
                   "adoption gate has not been met; see the table below.")
    else:
        st.success("**Process status: adoption gates met.** No stop condition has fired.")
    if locked is not None:
        st.write("**Signal status:** " + (
            "REJECT. The frozen DGS10 rule's holdout net return trails buy-and-hold IEF."
            if locked["failure"] else "the frozen DGS10 rule's failure rule is not triggered."))

    st.subheader("Three portfolios and the benchmark, each with its mandate verdict")
    st.dataframe([{
        "Portfolio": name,
        "BIL / IEF / LQD / VTI / VXUS (%)": weights_text(j["weights"]),
        "Return estimate (%)": round(j["measures"]["return"], 2),
        "Volatility (%)": round(j["measures"]["volatility"], 2),
        "95% loss estimate (%)": round(j["measures"]["loss_95"], 2),
        "Worst 12 months (%)": round(j["measures"]["worst_12m"], 2),
        "Mandate verdict": ("✔ " if j["verdict"] == "PASS" else "✘ ") + j["verdict"],
    } for name, j in b["judged"].items()], hide_index=True)
    for name, j in b["judged"].items():
        if j["verdict"] != "PASS":
            st.caption(f"{name} fails: " + "; ".join(cm.failed_rules(j["checks"])))
    if chosen is None:
        st.error("No mix on the 5-point grid passes every rule with these limits. "
                 "Loosen a limit in the sidebar, or treat this as a stop.")
    st.caption("Percent a year. Return = mean monthly return × 12, a historical estimate and not a "
               "forecast. Volatility = standard deviation of monthly returns × √12. 95% loss estimate "
               "= 1.645 × volatility − return. Weights are long-only and searched in 5-point steps.")

    if b["ranges"]:
        st.subheader("Allocation range: where the answer lands across the stress run")
        st.dataframe([{"Fund": k, "Base case (%)": (
            sum(w for w, t in zip(b["stress"][0]["weights"], tickers) if cm.UNIVERSE[t][3])
            if k.startswith("Equity") else b["stress"][0]["weights"][tickers.index(k)]),
            "Lowest (%)": lo, "Highest (%)": hi} for k, (lo, hi) in b["ranges"].items()],
            hide_index=True)

    triggers = pr.monitoring(b)
    if triggers:
        st.subheader("Monitoring triggers, evaluated now")
        st.dataframe([{"Trigger": t["trigger"], "Fires when": t["fires when"], "Now": t["now"],
                       "Status": "✘ FIRED" if t["fired"] else "✔ not fired"} for t in triggers],
                     hide_index=True)

    st.subheader("Stop conditions and adoption gates, evaluated now")
    st.dataframe([{"ID": s["id"], "Type": s["kind"], "Condition": s["condition"],
                   "Current value": s["value"],
                   "Status": "✘ FIRED" if s["fired"] else "✔ not fired"} for s in b["stops"]],
                 hide_index=True)

# ---------------------------------------------------------------- 2 mandate and portfolios
with tab_mandate:
    st.markdown(f"**Client:** {cm.CLIENT}. The written mandate is `docs/mandate.md`.")
    st.subheader("Estimates the verdicts rest on")
    st.dataframe([{"Fund": t, "Role": cm.UNIVERSE[t][1],
                   "Return estimate (% a year)": round(est["returns"][i], 2),
                   "Volatility (% a year)": round(est["vols"][i], 2),
                   **{f"Corr. {u}": round(est["corr"][i][k], 2) for k, u in enumerate(tickers)}}
                  for i, t in enumerate(tickers)], hide_index=True)

    st.subheader("Rule by rule")
    pick = st.selectbox("Portfolio", list(b["judged"]), index=len(b["judged"]) - 1)
    j = b["judged"][pick]
    st.write(f"Weights {weights_text(j['weights'])} · verdict **{j['verdict']}**")
    st.dataframe([{"Rule": rid, "Test": text, "Measured (%)": round(value, 2), "Result": words(ok)}
                  for rid, text, value, ok in j["checks"]], hide_index=True)

    st.subheader("Check your own weights")
    cols = st.columns(len(tickers))
    default = j["weights"]
    mine = [cols[i].number_input(f"{t} (%)", -100.0, 200.0, float(default[i]), 5.0, key=f"w-{pick}-{t}")
            for i, t in enumerate(tickers)]
    own = pr.judge([w / 100 for w in mine], est, rules)
    st.write(f"Return estimate **{own['measures']['return']:.2f}%** · volatility "
             f"**{own['measures']['volatility']:.2f}%** · verdict **{own['verdict']}**")
    for line in cm.failed_rules(own["checks"]):
        st.write("✘ " + line)

    if chosen is not None:
        st.subheader("Bridge: from the benchmark to the constrained portfolio")
        st.dataframe([{"Fund": r["fund"], "Benchmark (%)": round(r["from"]), "Portfolio (%)": round(r["to"]),
                       "Change (points)": round(r["change"]),
                       "Adds to return (points)": round(r["return_added"], 2),
                       "Adds to volatility (points)": round(r["risk_added"], 2)} for r in b["bridge"]]
                     + [{"Fund": "Total", "Benchmark (%)": 100, "Portfolio (%)": 100, "Change (points)": 0,
                         "Adds to return (points)": round(sum(r["return_added"] for r in b["bridge"]), 2),
                         "Adds to volatility (points)": round(sum(r["risk_added"] for r in b["bridge"]), 2)}],
                     hide_index=True)
        st.caption("Return added = weight change × the fund's return estimate. Volatility added = the "
                   "change in the fund's share of portfolio volatility. Each column adds up to the "
                   "difference between the two portfolios.")
        t = b["turnover"]
        a, c, d = st.columns(3)
        a.metric("One-way turnover from the benchmark", f"{t['from_benchmark']:.0f}%")
        c.metric(f"Cost of that move at {t['cost_rate']:.2f}% of value traded", f"{t['cost_from_benchmark']:.2f}%")
        d.metric("Largest yearly rebalance (one-way)", f"{max(t['rebalance']):.1f}%",
                 help=f"Budget {t['budget']:.0f}% a year. Each year in the sample: "
                      + ", ".join(f"{x:.1f}%" for x in t["rebalance"]))

# ---------------------------------------------------------------- 3 stress run
with tab_stress:
    st.subheader("The search repeated with one thing changed")
    st.dataframe([{"Group": r["group"], "Change": r["label"],
                   "BIL / IEF / LQD / VTI / VXUS (%)": "no mix passes" if r["weights"] is None
                   else weights_text(r["weights"]),
                   "Largest move from base (points)": None if r["weights"] is None or b["stress"][0]["weights"] is None
                   else max(abs(x - y) for x, y in zip(r["weights"], b["stress"][0]["weights"]))}
                  for r in b["stress"]], hide_index=True, height=36 * (len(b["stress"]) + 1) + 2)
    st.caption("Estimates: each fund's return ±1 point. Window: which months the estimates use. "
               "Costs: a yearly cost taken off every return before the objective is tested. "
               "Constraints: one mandate limit moved.")

    st.subheader("Named scenarios on fixed weights")
    for s in b["scenarios"]:
        st.markdown(f"**{s['name']}** ({s['unit']}). {s['detail']}.")
        st.dataframe([{"Portfolio": n, s["unit"]: round(v, 2),
                       f"Against the {rules['loss_limit']:.0f}% loss limit": words(
                           (v <= rules["loss_limit"]) if "loss" in s["unit"] else (v >= -rules["loss_limit"]))}
                      for n, v in s["results"].items()], hide_index=True)

    st.subheader("Out-of-sample test of the portfolio")
    o = b["out_of_sample"]
    if o is None:
        st.write("The file is too short for this test (it needs 36 months to estimate and 12 to hold).")
    else:
        st.write(f"Estimated on {o['estimation']}, then held unchanged over {o['holding']}.")
        if not o["feasible"]:
            st.warning("No mix passed the mandate on the early window, so only the baselines are shown.")
        st.dataframe([{"Portfolio": n, "Weights (%)": weights_text(v["weights"]),
                       "Realized return (% a year)": round(v["annual_return"], 2),
                       "Realized volatility (% a year)": round(v["volatility"], 2),
                       "Largest drawdown (%)": round(v["max_drawdown"], 2)}
                      for n, v in o["results"].items()], hide_index=True)

    st.subheader("Cross-checks on the search")
    g = pr.grid_check(est, rules)
    if g is not None:
        st.write(f"**Finer grid.** In {g['fine_step']}-point steps the search gives "
                 f"{' / '.join(f'{w:g}' for w in g['fine_weights'])} at {g['fine_volatility']:.2f}% volatility, "
                 f"against {g['coarse_volatility']:.2f}% on the 5-point grid. Largest weight difference: "
                 f"{g['largest_weight_gap']:g} points.")
    if st.checkbox(f"Run the estimation-error test ({pr.BOOTSTRAP_RUNS} resamples, about 10 seconds)"):
        boot = bootstrap_cached(tuple(tuple(r) for r in est["monthly"]), tuple(tickers),
                                tuple(sorted(rules.items())))
        st.write(f"The months were resampled with replacement {boot['runs']} times (seed {boot['seed']}) "
                 f"and the search rerun on each. A passing mix was found in **{boot['feasible']}** of them.")
        st.dataframe([{"Fund": k, "5th percentile (%)": v["p05"], "Median (%)": v["median"],
                       "95th percentile (%)": v["p95"]} for k, v in boot["weights"].items()],
                     hide_index=True)

    st.subheader("The condition that stops the process")
    st.markdown(
        f"- **Stop** if no mix passes every mandate rule on the current estimates (STOP-1), or if the "
        f"held portfolio's trailing 12-month return falls below −{rules['loss_limit']:.0f}% (STOP-2).\n"
        f"- **Do not adopt** (pilot only) while any weight moves more than {pr.STABILITY_LIMIT:.0f} points "
        f"in the stress run (GATE-1) or any stress run finds no passing mix (GATE-2).")
    for s in b["stops"]:
        st.write(f"{'✘ FIRED' if s['fired'] else '✔ not fired'} · **{s['id']}** {s['condition']}: {s['value']}")

# ---------------------------------------------------------------- 4 signal
with tab_signal:
    if locked is None:
        st.error(f"The signal files could not be read ({signal_error}). The rest of the app is unaffected.")
    else:
        st.markdown(
            f"**Frozen rule** (`rule-card-dgs10.md`): if the 10-year Treasury yield (FRED DGS10) fell over "
            f"the month, hold {sr.RISK_FUND} next month; otherwise hold {sr.SAFE_FUND}. The month-end value "
            f"is the one already published at the last close (one-day lag). Development "
            f"{sr.DEVELOPMENT[0]} to {sr.DEVELOPMENT[1]}; holdout {sr.HOLDOUT[0]} to {sr.HOLDOUT[1]}, run once.")

        def signal_table(res):
            return [{"Period": k, "Months": res[k]["months"], "Rule gross (%)": round(res[k]["gross"], 2),
                     "Rule net (%)": round(res[k]["net"], 2),
                     f"Hold {sr.RISK_FUND} (%)": round(res[k]["buy_and_hold"], 2),
                     f"Hold {sr.SAFE_FUND} (%)": round(res[k]["safe_only"], 2),
                     "Switches": res[k]["switches"]} for k in ("Development", "Holdout")]

        left, right = st.columns(2)
        with left:
            st.subheader(f"Locked: lag {sr.FROZEN['lag']}, cost {sr.FROZEN['cost']:.2f}%")
            st.dataframe(signal_table(locked), hide_index=True)
            h = locked["Holdout"]
            gap = h["buy_and_hold"] - h["net"]
            if locked["failure"]:
                st.error(f"✘ Failure rule TRIGGERED: holdout net trails buy-and-hold {sr.RISK_FUND} "
                         f"by {gap:.2f} points.")
            else:
                st.success(f"✔ Failure rule not triggered: holdout net leads by {-gap:.2f} points.")
            st.caption(f"Gross to net in the holdout: {h['gross']:.2f}% − {h['switches']} switches × "
                       f"{sr.FROZEN['cost']:.2f}% ≈ {h['net']:.2f}% (compounded monthly).")
        with right:
            st.subheader(f"Sensitivity: lag {lag}, cost {cost:.2f}%")
            try:
                scen = sr.run(signal, sig_returns, lag=lag, cost=cost)
            except ValueError as err:
                st.error(f"Cannot run: {err}")
            else:
                st.dataframe(signal_table(scen), hide_index=True)
                st.write("Failure rule: **" + ("triggered" if scen["failure"] else "not triggered") + "**")
                if lag == 0:
                    st.warning("Lag 0 uses the month's own yield change to choose that month's position. "
                               "Nobody could have known it in time: this is a leak, not evidence.")
                if lag == 2:
                    st.caption("Lag 2 was not the frozen rule. Choosing it after seeing this table "
                               "would be tuning on the holdout.")

        st.subheader("Placebo: the same rule on a shuffled signal")
        pl = sr.placebo(signal, sig_returns)
        st.write(f"{pl['runs']:,} shuffles (seed {pl['seed']}). Real rule, holdout net: **{pl['actual']:.2f}%**. "
                 f"Shuffled signals: median {pl['median']:.2f}%, middle 90% from {pl['p05']:.2f}% to "
                 f"{pl['p95']:.2f}%. **{pl['share_at_least_actual']:.1f}%** of the shuffles did at least "
                 "as well as the real signal.")

        with st.expander("Month-by-month log of the locked run (holdout)"):
            st.dataframe([{"Month": x["month"], "Signal from": x["signal_month"],
                           "Yield change (points)": round(x["signal"], 2), "Held": x["position"],
                           "Switched": "yes" if x["switched"] else "no",
                           "Return before cost (%)": round(x["return"], 2)} for x in h["log"]],
                         hide_index=True)

    with st.expander("Training rule from the Week 12 lab (course-authored data; not part of the decision)"):
        t = bt.run(**bt.FROZEN)
        st.dataframe([{"Period": k, "Rule gross (%)": round(t[k]["gross"], 2),
                       "Rule net (%)": round(t[k]["net"], 2),
                       "Buy-and-hold (%)": round(t[k]["buy_and_hold"], 2), "Switches": t[k]["switches"]}
                      for k in ("Development", "Holdout")], hide_index=True)
        st.caption(f"`backtest.py` at its frozen lag {bt.FROZEN['lag']} and cost {bt.FROZEN['cost']:.2f}%. "
                   "Failure rule " + ("triggered." if t["failure"] else "not triggered."))

# ---------------------------------------------------------------- 5 data and method
with tab_data:
    st.subheader("Inputs")
    st.dataframe([
        {"Input": "Fund prices", "File": pr.PRICES_FILE, "Source": "Yahoo Finance, monthly Adj Close",
         "Downloaded": pr.PRICES_DOWNLOADED, "As-of boundary": pr.AS_OF,
         "SHA-256 (first 16)": pr.sha256(pr.PRICES_FILE)[:16]},
        {"Input": "10-year Treasury yield", "File": sr.DGS10_FILE, "Source": "FRED series DGS10",
         "Downloaded": sr.DGS10_DOWNLOADED, "As-of boundary": "one-day publication lag",
         "SHA-256 (first 16)": pr.sha256(sr.DGS10_FILE)[:16]},
    ], hide_index=True)
    st.markdown(
        "Full data cards, with definitions, transformations, exclusions, revisions and licensing: "
        "`docs/data-cards.md`. The same numbers without running anything: `output/decision-report.md`.")
    st.subheader("Conventions")
    st.markdown(
        "- Monthly return = this month's Adj Close ÷ last month's − 1. Adj Close includes distributions.\n"
        "- Return estimate = arithmetic mean of monthly returns × 12. Volatility = sample standard "
        "deviation × √12. Both in percent a year. They are estimates from history, not forecasts.\n"
        "- Weights are long-only, in 5-point steps (10,626 mixes of five funds), rebalanced to target.\n"
        "- The constrained portfolio is the lowest-volatility mix that passes all seven mandate rules.\n"
        f"- Rows after {last_complete} are treated as partial months and left out of the base case.")
    st.subheader("Mandate limits in use")
    st.dataframe([{"Limit": k, "Mandate": cm.RULES[k], "In use": v,
                   "Changed": "yes" if cm.RULES[k] != v else "no"} for k, v in rules.items()],
                 hide_index=True)
