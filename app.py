"""Lab 15 - lowest-risk mix that meets the mandate, Meridian or my own funds.

Every calculation is imported from portfolio.py; this file only handles the page.
Run: python3 -m streamlit run app.py
"""
import csv
import io

import streamlit as st

import portfolio as p

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
    loaded_eligible = [False] * len(names)

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
