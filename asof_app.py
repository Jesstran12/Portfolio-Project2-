"""Lab 17 - as-of rates: FRED's values today against ALFRED's values as known on a chosen date.

Data: FRED and ALFRED public CSV downloads, no API key, one request per series.
Run: python3 -m streamlit run asof_app.py
"""

import csv
import io
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------- editable inputs
SERIES = {
    "BAA": "Moody's Baa corporate bond yield",
    "FEDFUNDS": "Federal funds rate",
    "DGS10": "10-year Treasury yield",
    "MORTGAGE30US": "30-year mortgage rate",
    "PAYEMS": "Payroll jobs",
}
UNITS = {"PAYEMS": "thousands"}  # unit of a built-in series; any other built-in is a percent
START = date(2020, 1, 1)
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={id}"
ALFRED_CSV = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={id}&vintage_date={vintage}"
FRED_PAGE = "https://fred.stlouisfed.org/series/{id}"
# ---------------------------------------------------------------- end of inputs


def parse(text, series_id):
    """CSV text -> {date: value or None}; "." or blank is a missing day. Raises ValueError if not a series."""
    rows = list(csv.reader(io.StringIO(text)))
    if not rows or len(rows[0]) < 2 or rows[0][0] != "observation_date" or len(rows) < 2:
        raise ValueError(f"no data for '{series_id}' (unknown series ID?)")
    return {date.fromisoformat(r[0]): (None if r[1].strip() in (".", "") else float(r[1])) for r in rows[1:] if r}


def download(url, series_id):
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return parse(resp.read().decode("utf-8-sig"), series_id)
    except urllib.error.HTTPError as err:
        raise ValueError(f"no data for '{series_id}' (HTTP {err.code}, unknown series ID?)") from None


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def fred_today(series_id):
    """Today's values from FRED."""
    return download(FRED_CSV.format(id=urllib.parse.quote(series_id)), series_id)


@st.cache_data(show_spinner=False)
def alfred_as_of(series_id, vintage):
    """Values as known on the vintage date (ISO text), from ALFRED. A past vintage never changes."""
    return download(ALFRED_CSV.format(id=urllib.parse.quote(series_id), vintage=vintage), series_id)


def unit_of(series_id):
    """'%', another unit for a built-in series, or '' for a series the user added (unit unknown)."""
    return UNITS.get(series_id, "%") if series_id in SERIES else ""


def show(series_id, value):
    """A value with its unit: 5.05%, 159,536 thousands, or 27,610.13 for an added series."""
    unit = unit_of(series_id)
    if unit == "%":
        return f"{value:,.2f}%"
    return f"{value:,.0f} {unit}" if unit else f"{value:,.2f}"


def last_measured(values):
    """(date, value) of the last non-missing day, or (None, None)."""
    days = [d for d, v in values.items() if v is not None]
    return (max(days), values[max(days)]) if days else (None, None)


def compare(series_id, as_of):
    """One table row: then vs today, new values since, revisions on shared dates."""
    now = fred_today(series_id)
    then = alfred_as_of(series_id, as_of.isoformat())
    then_d, then_v = last_measured(then)
    now_d, now_v = last_measured(now)
    if then_d is None:
        raise ValueError(f"'{series_id}' had no values yet on {as_of}")
    new = sum(1 for d, v in now.items() if v is not None and d > then_d)
    revised = sum(1 for d, v in then.items()
                  if v is not None and now.get(d) is not None and abs(now[d] - v) > 1e-9)
    row = {"Series": FRED_PAGE.format(id=series_id), "Name": SERIES.get(series_id, ""),
           "Last date (then)": then_d, "Value (then)": then_v,
           "Last date (today)": now_d, "Value (today)": now_v,
           "New values since": new, "Revised values": revised}
    return now, then, then_d, row


def chart(series_id, now, then, start, then_d):
    """Today (solid) vs known then (dashed); after the last value known then is shaded; hover tooltip."""
    then_label = "Known then"
    wide = pd.DataFrame({"Today": pd.Series(now, dtype=float), then_label: pd.Series(then, dtype=float)})
    wide = wide[wide.index >= start].dropna(how="all")
    wide.index = pd.to_datetime(wide.index)
    wide["Revision"] = wide["Today"] - wide[then_label]
    wide = wide.rename_axis("Date").reset_index()
    long = wide.melt("Date", ["Today", then_label], var_name="Line", value_name="Value").dropna()

    unit = unit_of(series_id)
    x = alt.X("Date:T", title=None,
              axis=alt.Axis(grid=False, format="%b %Y", labelAngle=0, labelOverlap=True, labelPadding=6))
    y = alt.Y("Value:Q", title=unit or None, scale=alt.Scale(zero=False), axis=alt.Axis(grid=False))
    lines = alt.Chart(long).mark_line(strokeWidth=1.5).encode(
        x, y,
        color=alt.Color("Line:N", title=None, sort=["Today", then_label],
                        scale=alt.Scale(range=["#1f6fb4", "#e07b39"]), legend=alt.Legend(orient="top-left")),
        strokeDash=alt.StrokeDash("Line:N", sort=["Today", then_label],
                                  scale=alt.Scale(range=[[1, 0], [5, 3]]), legend=None),
    )

    marks = pd.DataFrame({"start": [pd.Timestamp(then_d)], "end": [wide["Date"].max()]})
    shade = alt.Chart(marks).mark_rect(opacity=0.08, color="gray").encode(x="start:T", x2="end:T")
    rule = alt.Chart(marks).mark_rule(strokeDash=[2, 2], color="gray").encode(x="start:T")

    hover = alt.selection_point(fields=["Date"], nearest=True, on="pointerover", empty=False)
    fmt = ".2f"
    tips = [alt.Tooltip("Date:T", format="%Y-%m-%d"), alt.Tooltip("Today:Q", format=fmt),
            alt.Tooltip(f"{then_label}:Q", format=fmt), alt.Tooltip("Revision:Q", format="+.2f")]
    hover_rule = alt.Chart(wide).mark_rule(color="gray", opacity=0.5).encode(
        x="Date:T", opacity=alt.condition(hover, alt.value(0.5), alt.value(0)), tooltip=tips,
    ).add_params(hover)

    return (shade + lines + rule + hover_rule).properties(height=280, padding={"bottom": 20}).configure_view(strokeWidth=0)


def combined_chart(series, start):
    """Today's values of several percent series on one chart; hover shows every series on that date."""
    wide = pd.DataFrame({sid: pd.Series(v, dtype=float) for sid, v in series.items()})
    wide = wide[wide.index >= start].dropna(how="all")
    wide.index = pd.to_datetime(wide.index)
    wide = wide.rename_axis("Date").reset_index()
    long = wide.melt("Date", list(series), var_name="Series", value_name="Value").dropna()

    x = alt.X("Date:T", title=None,
              axis=alt.Axis(grid=False, format="%b %Y", labelAngle=0, labelOverlap=True, labelPadding=6))
    lines = alt.Chart(long).mark_line(strokeWidth=1.5).encode(
        x, alt.Y("Value:Q", title="%", scale=alt.Scale(zero=False), axis=alt.Axis(grid=False)),
        color=alt.Color("Series:N", title=None, sort=list(series), legend=alt.Legend(orient="top-left")),
    )
    hover = alt.selection_point(fields=["Date"], nearest=True, on="pointerover", empty=False)
    tips = [alt.Tooltip("Date:T", format="%Y-%m-%d")] + [alt.Tooltip(f"{sid}:Q", format=".2f") for sid in series]
    hover_rule = alt.Chart(wide).mark_rule(color="gray").encode(
        x="Date:T", opacity=alt.condition(hover, alt.value(0.5), alt.value(0)), tooltip=tips,
    ).add_params(hover)
    return (lines + hover_rule).properties(height=360, padding={"bottom": 20}).configure_view(strokeWidth=0)


st.set_page_config(page_title="As-of rates", layout="wide")
st.title("Interest rates: today vs as known then")
st.caption(f"Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, downloaded {date.today():%B %-d, %Y}; "
           "built with AI help, a learning demonstration, not investment advice.")

with st.sidebar:
    extra = st.text_input("Add a FRED series ID", placeholder="e.g. UNRATE").strip().upper()
    options = list(SERIES) + ([extra] if extra and extra not in SERIES else [])
    chosen = st.multiselect("Series", options, default=list(SERIES) + ([extra] if extra and extra not in SERIES else []),
                            format_func=lambda s: f"{s}: {SERIES[s]}" if s in SERIES else s)
    start = st.date_input("Start date", START, max_value=date.today())
    as_of = st.date_input("As known on", date.today(), max_value=date.today())

st.markdown(f"Solid line: today's data. Dashed line: the data **as known on {as_of}**. "
            "Shaded: dates whose values were not yet published then.")

results, errors = {}, {}
for sid in chosen:
    try:
        with st.spinner(f"Downloading {sid}..."):
            results[sid] = compare(sid, as_of)
    except (ValueError, urllib.error.URLError, OSError) as err:
        errors[sid] = err

rates = [sid for sid in results if unit_of(sid) == "%"]
if rates:
    st.subheader("All series, today")
    st.altair_chart(combined_chart({sid: results[sid][0] for sid in rates}, start), use_container_width=True)
    others = [sid for sid in results if unit_of(sid) != "%"]
    if others:
        st.caption(f"Not shown here, not in percent or unit unknown: {', '.join(others)}. See its own chart below.")

rows = []
for sid in chosen:
    st.subheader(f"{sid}: {SERIES.get(sid, '')}".rstrip(": "))
    if sid in errors:
        st.error(f"{sid}: {errors[sid]}")
        continue
    now, then, then_d, row = results[sid]
    st.metric(f"Latest ({row['Last date (today)']})", show(sid, row['Value (today)']),
              f"{row['Value (today)'] - row['Value (then)']:+,.2f} since the last value known then",
              delta_color="off")
    st.altair_chart(chart(sid, now, then, start, then_d), use_container_width=True)
    st.caption(f"Last value known then: **{then_d}** ({show(sid, row['Value (then)'])})")
    rows.append(row)

if rows:
    st.subheader(f"Then ({as_of}) vs today")
    st.dataframe(
        pd.DataFrame(rows), hide_index=True,
        column_config={"Series": st.column_config.LinkColumn("Series", display_text=r"series/(.*)$")},
    )
