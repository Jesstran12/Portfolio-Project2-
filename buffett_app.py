"""Lab 18 - Buffett's checks from SEC EDGAR, and a memo checked against the numbers the script printed.

Every number is computed by the skill's script, .claude/skills/buffett/buffett.py; this file only
handles the page. The memo is written by the skill and saved in memos/TICKER.md.
Run: python3 -m streamlit run buffett_app.py
"""

import re
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / ".claude" / "skills" / "buffett"))
import buffett as b  # noqa: E402

MEMOS = HERE / "memos"
NUMBER = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")  # 9,382 · 28.3 · 2026 (sign ignored)


def numbers(text):
    """Every number in the text as a float, commas dropped."""
    return {float(m.group().replace(",", "")) for m in NUMBER.finditer(text)}


def flag(memo, printed):
    """(memo with unprinted numbers highlighted, list of unprinted numbers as written)."""
    allowed = numbers(printed)
    flagged = []

    def mark(m):
        if float(m.group().replace(",", "")) in allowed:
            return m.group()
        flagged.append(m.group())
        return f":red-background[**{m.group()}**]"

    return NUMBER.sub(mark, memo), flagged


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def load(ticker):
    return b.analyze(ticker)


st.set_page_config(page_title="Buffett memo", layout="wide")
st.title("Buffett's checks and memo")
st.caption("Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.")

ticker = st.text_input("Ticker", "COST").strip().upper()
if not ticker:
    st.stop()
try:
    with st.spinner(f"Downloading {ticker} from SEC EDGAR..."):
        result = load(ticker)
except (ValueError, OSError) as err:
    st.error(f"Could not load {ticker}: {err}")
    st.stop()

rows = result["rows"]
st.subheader(f"{result['company']} ({ticker}), CIK {result['cik']}")
st.caption(f"Source: {result['source']}, 10-K filings only, $ millions")

# ---------------------------------------------------------------- chart
lines = ["Owner earnings", "Net income"]
long = pd.DataFrame([{"Fiscal year ending": end, "Line": line, "$ millions": row[line][0] / 1e6}
                     for end, row in rows.items() for line in lines
                     if isinstance(row[line][0], (int, float))])
if long.empty:
    st.warning("Neither owner earnings nor net income was found, so there is nothing to chart.")
else:
    chart = alt.Chart(long).mark_line(point=True, strokeWidth=2).encode(
        x=alt.X("Fiscal year ending:N", title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("$ millions:Q", axis=alt.Axis(grid=False, format=",.0f")),
        color=alt.Color("Line:N", title=None, sort=lines, scale=alt.Scale(range=["#1f6fb4", "#e07b39"]),
                        legend=alt.Legend(orient="top-left")),
        tooltip=["Fiscal year ending", "Line", alt.Tooltip("$ millions:Q", format=",.0f")],
    ).properties(height=320).configure_view(strokeWidth=0)
    st.altair_chart(chart, use_container_width=True)
    missing = [line for line in lines if any(not isinstance(r[line][0], (int, float)) for r in rows.values())]
    if missing:
        st.caption(f"Years with {' or '.join(m.lower() for m in missing)} not found are left off the chart.")

# ---------------------------------------------------------------- table and checks
left, right = st.columns([3, 1])
with left:
    st.markdown("**Five fiscal years, as printed by the script**")
    table = pd.DataFrame({end: {line: b.show(line, v) for line, (v, _) in row.items()} for end, row in rows.items()})
    tags = [", ".join(dict.fromkeys(r[line][1] for r in rows.values() if r[line][1])) or b.NOT_FOUND
            for line in table.index]  # a line's tag can change between years; list each once
    table["XBRL tag"] = tags
    st.dataframe(table, width="stretch")
with right:
    st.markdown("**Buffett's checks**")
    for check, res in result["checks"].items():
        icon = {"pass": ":green[pass]", "fail": ":red[fail]"}.get(res, ":orange[not known]")
        st.markdown(f"{check}: **{icon}**")

# ---------------------------------------------------------------- memo
st.subheader("Buffett's memo")
path = MEMOS / f"{ticker}.md"
if not path.exists():
    st.info(f"No memo yet. Ask your AI: `/buffett {ticker}` (it saves {path.relative_to(HERE)}).")
    st.stop()

memo = st.text_area(f"{path.relative_to(HERE)} (edit to test the flags)", path.read_text(), height=260)
if st.button("Save edits to the file"):
    path.write_text(memo)
    st.success(f"Saved {path.relative_to(HERE)}")

marked, flagged = flag(memo, b.report(result))
if flagged:
    st.error(f"{len(flagged)} number(s) in the memo were not printed by the script: {', '.join(flagged)}")
else:
    st.success("Every number in the memo was printed by the script.")
st.markdown(marked)
