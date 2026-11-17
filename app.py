"""Lab 15 - lowest-risk mix that meets the mandate, Meridian or my own funds.

Every calculation is imported from portfolio.py and backtest.py; this file only handles the page.
Run: python3 -m streamlit run app.py
"""
import csv
import io

import streamlit as st

import backtest as bt
import portfolio as p

RESERVE_TICKERS = {"BIL", "IEF"}  # cash and Treasuries count toward the reserve minimum (mandate S3)

st.set_page_config(page_title="Lowest-risk mix", layout="wide")
st.title("Lowest-risk mix that meets the mandate")
st.caption("Built with AI help · a learning demonstration, not investment advice.")

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    objective = st.number_input("Objective return (%)", value=p.OBJECTIVE_RETURN, step=0.1)
    reserve_min = st.number_input("Reserve minimum (%)", value=3.0, min_value=0.0,
                                  max_value=100.0, step=0.5)
    upload = st.file_uploader("prices.csv (date, then one column per ticker, oldest first)",
                              type="csv")
    last_36 = st.toggle("Last 36 months only", value=False, disabled=upload is None)
    st.markdown("**Signal backtest (sensitivity only)**")
    lag = st.select_slider("Signal lag (months)", options=[0, 1], value=bt.FROZEN["lag"],
                           help="The data starts one month before development, so 1 is the longest lag.")
    cost = st.slider("Trading cost (% a switch)", min_value=0.0, max_value=1.0,
                     value=bt.FROZEN["cost"], step=0.05)

# ---------------------------------------------------------------- inputs as loaded
if upload is None:
    source = "Meridian"
    names = list(p.SLEEVES)
    loaded_returns = [p.SLEEVES[n][0] for n in names]
    loaded_vols = [p.SLEEVES[n][1] for n in names]
    loaded_corr = p.CORRELATION
    loaded_eligible = [p.SLEEVES[n][2] for n in names]
    vols, corr = loaded_vols, loaded_corr
else:
    source = upload.name
    rows = list(csv.reader(io.StringIO(upload.getvalue().decode("utf-8-sig"))))
    try:
        names, loaded_returns, loaded_vols, loaded_corr = p.estimates_from_prices(rows)
        _, _, vols, corr = p.estimates_from_prices(rows, 36 if last_36 else None)
    except (ValueError, IndexError, ZeroDivisionError) as err:
        st.error(f"Could not read {upload.name}: {err}. Expected monthly prices: a header row "
                 "'date,TICKER1,TICKER2,...', then one row per month, oldest first, prices only.")
        st.stop()
    loaded_eligible = [n.upper() in RESERVE_TICKERS for n in names]  # ticked by default; untick to test

try:
    p.validate_correlation(corr, len(names))
except ValueError as err:
    st.error(f"Refusing to run: {err}")
    st.stop()

# ---------------------------------------------------------------- editable inputs
st.subheader(f"Inputs: {source}" + (" (last 36 months)" if upload is not None and last_36 else ""))
returns, eligible = [], []
cols = st.columns(len(names))
for i, (col, name) in enumerate(zip(cols, names)):
    with col:
        st.markdown(f"**{name}**")
        returns.append(st.number_input("Expected return (%)", value=round(loaded_returns[i], 2),
                                       step=0.1, format="%.2f", key=f"{source}-ret-{name}"))
        st.caption(f"Volatility {vols[i]:.2f}%")
        eligible.append(st.checkbox("Reserve-eligible", value=loaded_eligible[i],
                                    key=f"{source}-res-{name}"))

# ---------------------------------------------------------------- answers
now = p.lowest_risk_mix(returns, vols, corr, eligible, objective, reserve_min)
as_loaded = p.lowest_risk_mix(loaded_returns, loaded_vols, loaded_corr, eligible,
                              objective, reserve_min)


def show(title, result):
    st.subheader(title)
    if result is None:
        st.warning("No mix meets the objective.")
        return
    weights, ret, vol = result
    st.table({"Asset": names, "Weight (%)": [f"{w * 100:.2f}" for w in weights]})
    st.write(f"Expected return **{ret:.2f}%** · Volatility **{vol:.2f}%** · "
             f"Reserve-eligible **{p.reserve_eligible_weight(weights, eligible):.2f}%**")


left, right = st.columns(2)
with left:
    show("Lowest-risk mix: your inputs", now)
with right:
    show("Lowest-risk mix: inputs as loaded" + ("" if upload is None else " (all months)"),
         as_loaded)

if now and as_loaded:
    changes = [abs(a - b) * 100 for a, b in zip(now[0], as_loaded[0])]
    i = max(range(len(changes)), key=changes.__getitem__)
    st.metric("Largest weight change", f"{changes[i]:.2f} points", help=names[i])
    st.caption(f"Largest change is in {names[i]}. Both answers use the same objective, "
               "reserve minimum and reserve ticks; only the estimates differ. "
               "Mixes are searched in 5-point steps.")


# ---------------------------------------------------------------- signal backtest (backtest.py)
st.header("Signal backtest: the frozen rule and its holdout")
st.caption("Rule card: rule-card.md. The locked result uses the frozen lag and cost; "
           "the sidebar controls run a sensitivity scenario and never change the locked evidence.")


def backtest_table(res):
    return {"Period": ["Development", "Holdout"],
            **{col: [f"{res[k][key]:.2f}" if key != "switches" else str(res[k][key])
                     for k in ("Development", "Holdout")]
               for col, key in (("Rule gross (%)", "gross"), ("Rule net (%)", "net"),
                                ("Buy-and-hold (%)", "buy_and_hold"), ("Switches", "switches"))}}


locked = bt.run(**bt.FROZEN)
left, right = st.columns(2)
with left:
    st.subheader(f"Locked: lag {bt.FROZEN['lag']}, cost {bt.FROZEN['cost']:.2f}%")
    a, b_ = st.columns(2)
    a.metric("Holdout gross", f"{locked['Holdout']['gross']:.2f}%")
    b_.metric("Holdout net", f"{locked['Holdout']['net']:.2f}%")
    st.table(backtest_table(locked))
    gap = locked["Holdout"]["buy_and_hold"] - locked["Holdout"]["net"]
    if locked["failure"]:
        st.error(f"Failure rule triggered: holdout net trails buy-and-hold by {gap:.2f} points.")
    else:
        st.success("Failure rule not triggered.")
with right:
    st.subheader(f"Sensitivity: lag {lag}, cost {cost:.2f}%")
    try:
        scen = bt.run(lag=lag, cost=cost)
    except ValueError as err:
        st.error(f"Cannot run: {err}")
    else:
        a, b_ = st.columns(2)
        a.metric("Holdout gross", f"{scen['Holdout']['gross']:.2f}%",
                 f"{scen['Holdout']['gross'] - locked['Holdout']['gross']:+.2f} vs locked", delta_color="off")
        b_.metric("Holdout net", f"{scen['Holdout']['net']:.2f}%",
                  f"{scen['Holdout']['net'] - locked['Holdout']['net']:+.2f} vs locked", delta_color="off")
        st.table(backtest_table(scen))
        st.write("Failure rule: **" + ("triggered" if scen["failure"] else "not triggered") + "**")
        if lag == 0:
            st.warning("Lag 0 trades on a signal it could not have had yet: this is the leak, not evidence.")
