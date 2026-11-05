"""Lab 19 - Legend panel: Buffett, Cathie Wood and Burry on the same SEC EDGAR 10-K facts.

Every number comes from the three skills' scripts; this file only lays out the page.
Memos: memos/TICKER.md (Buffett), memos/cathie_wood/TICKER.md, memos/burry/TICKER.md.
Run: python3 -m streamlit run panel_app.py
"""

import re
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

HERE = Path(__file__).parent
SKILLS = HERE / ".claude" / "skills"
for name in ("buffett", "cathie_wood", "burry"):
    sys.path.insert(0, str(SKILLS / name))
import buffett as b  # noqa: E402
import burry as bu  # noqa: E402
import cathie_wood as cw  # noqa: E402

MEMOS = HERE / "memos"
NUMBER = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")


def numbers(text):
    return {float(m.group().replace(",", "")) for m in NUMBER.finditer(text)}


def flag(memo, printed):
    """(memo with unprinted numbers highlighted, unprinted numbers as written)."""
    allowed, flagged = numbers(printed), []

    def mark(m):
        if float(m.group().replace(",", "")) in allowed:
            return m.group()
        flagged.append(m.group())
        return f":red-background[**{m.group()}**]"

    return NUMBER.sub(mark, memo), flagged


def verdict(checks):
    """Panel verdict from the checks alone: any fail -> Pass; all pass -> Own; else Watch."""
    vals = list(checks.values())
    if "fail" in vals:
        return "Pass"
    return "Own" if all(v == "pass" for v in vals) else "Watch"


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def load(ticker):
    base = b.analyze(ticker)  # one download, shared by all three
    return {
        "Buffett": (base, b.report(base), MEMOS / f"{ticker}.md"),
        "Cathie Wood": (r := cw.analyze(ticker, base), cw.report(r), MEMOS / "cathie_wood" / f"{ticker}.md"),
        "Burry": (r2 := bu.analyze(ticker, base), bu.report(r2), MEMOS / "burry" / f"{ticker}.md"),
    }


st.set_page_config(page_title="Legend panel", layout="wide")
st.title("Legend panel: Buffett, Cathie Wood, Burry")
st.caption("Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.")

ticker = st.text_input("Ticker", "COST").strip().upper()
if not ticker:
    st.stop()
try:
    with st.spinner(f"Downloading {ticker} from SEC EDGAR..."):
        panel = load(ticker)
except (ValueError, OSError) as err:
    st.error(f"Could not load {ticker}: {err}")
    st.stop()

base = panel["Buffett"][0]
st.subheader(f"{base['company']} ({ticker}), CIK {base['cik']}")

# ---------------------------------------------------------------- panel table
ICON = {"pass": "✅ pass", "fail": "❌ fail"}
rows = []
for investor, (res, _, _) in panel.items():
    for check, val in res["checks"].items():
        extra = ""
        if investor == "Cathie Wood" and check.startswith("Revenue") and val != b.NOT_KNOWN:
            extra = f" ({cw.pct(res['metrics']['growth'])}%)"
        if investor == "Burry" and check.startswith("Liabilities") and val != b.NOT_KNOWN:
            extra = f" ({list(res['metrics']['leverage'].values())[-1]:.2f})"
        rows.append({"Investor": investor, "Check": check, ticker: ICON.get(val, "❔ not known") + extra})
st.markdown("**Investor × check**")
st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

cols = st.columns(3)
for col, (investor, (res, _, _)) in zip(cols, panel.items()):
    vals = list(res["checks"].values())
    col.metric(investor, verdict(res["checks"]),
               f"{vals.count('pass')} of {len(vals)} pass", delta_color="off")

with st.expander("Each script's printed output"):
    for investor, (_, printed, _) in panel.items():
        st.markdown(f"**{investor}**")
        st.code(printed, language=None)

# ---------------------------------------------------------------- memos side by side
st.subheader("The three memos")
all_flagged = {}
cols = st.columns(3)
for col, (investor, (_, printed, path)) in zip(cols, panel.items()):
    with col:
        st.markdown(f"**{investor}** · `{path.relative_to(HERE)}`")
        if not path.exists():
            slug = {"Buffett": "buffett", "Cathie Wood": "cathie_wood", "Burry": "burry"}[investor]
            st.info(f"No memo yet. Ask your AI: `/{slug} {ticker}`")
            all_flagged[investor] = None
            continue
        marked, flagged = flag(path.read_text(), printed)
        all_flagged[investor] = flagged
        if flagged:
            st.error(f"Unprinted: {', '.join(flagged)}")
        else:
            st.success("Every number printed by the script.")
        st.markdown(marked)

missing = [i for i, f in all_flagged.items() if f is None]
bad = {i: f for i, f in all_flagged.items() if f}
st.subheader("Unprinted-number flag, all memos")
if bad:
    st.error("; ".join(f"{i}: {', '.join(f)}" for i, f in bad.items()))
elif missing:
    st.warning(f"Missing memo(s): {', '.join(missing)}. The others print only script numbers.")
else:
    st.success("All three memos use only numbers their scripts printed.")
