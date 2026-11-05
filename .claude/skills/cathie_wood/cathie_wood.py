"""Cathie Wood's numbers: the same SEC EDGAR 10-K facts as buffett.py, her two checks.

Revenue growth a year = (last revenue / first revenue)^(1/4) - 1, first fiscal year to last.
R&D share = ResearchAndDevelopmentExpense / revenue, latest fiscal year.
A missing input prints "not found"; a check that needs it is "not known", never estimated.
Run: python3 .claude/skills/cathie_wood/cathie_wood.py COST   (add --json for machine-readable output)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "buffett"))
import buffett as b  # noqa: E402  (one fetch, one set of facts, shared by every investor)

# ---------------------------------------------------------------- editable inputs
MIN_GROWTH = 15.0  # percent a year, first year to last (her page: high-growth disruptors)
MIN_RD = 5.0       # percent of revenue, latest year
# ---------------------------------------------------------------- end of inputs

NOT_FOUND, NOT_KNOWN = b.NOT_FOUND, b.NOT_KNOWN


def is_num(v):
    return isinstance(v, (int, float))


def metrics(rows):
    """Per-year R&D / revenue (%), and revenue growth a year (%), first year to last."""
    ends = list(rows)
    rd_share = {}
    for end, row in rows.items():
        rd, rev = row["R&D"][0], row["Revenue"][0]
        rd_share[end] = rd / rev * 100 if is_num(rd) and is_num(rev) and rev > 0 else NOT_FOUND
    growth = NOT_FOUND
    if len(ends) > 1:
        first, last = rows[ends[0]]["Revenue"][0], rows[ends[-1]]["Revenue"][0]
        if is_num(first) and is_num(last) and first > 0 and last > 0:
            growth = ((last / first) ** (1 / (len(ends) - 1)) - 1) * 100  # five years -> four steps
    return {"rd_share": rd_share, "growth": growth}


def checks(m):
    """Her two checks: 'pass', 'fail', or 'not known' when an input is missing."""
    latest = list(m["rd_share"].values())[-1] if m["rd_share"] else NOT_FOUND
    g = m["growth"]
    return {
        f"Revenue grew {MIN_GROWTH:g}% or more a year, first year to last":
            ("pass" if g >= MIN_GROWTH else "fail") if is_num(g) else NOT_KNOWN,
        f"R&D {MIN_RD:g}% or more of revenue, latest year":
            ("pass" if latest >= MIN_RD else "fail") if is_num(latest) else NOT_KNOWN,
    }


def analyze(ticker, base=None):
    base = base or b.analyze(ticker)
    m = metrics(base["rows"])
    return {**base, "investor": "Cathie Wood", "metrics": m, "checks": checks(m)}


def pct(v):
    return f"{v:.2f}" if is_num(v) else v


def report(r):
    out = [f"{r['company']} ({r['ticker']}), CIK {r['cik']}",
           f"Source: {r['source']} (10-K filings only), $ millions", "",
           f"  {'FY end':<14}{'Revenue':>12}{'R&D':>12}{'R&D / revenue (%)':>20}"]
    for end, row in r["rows"].items():
        out.append(f"  {end:<14}{b.show('Revenue', row['Revenue'][0]):>12}"
                   f"{b.show('R&D', row['R&D'][0]):>12}{pct(r['metrics']['rd_share'][end]):>20}")
    out += ["", f"  Revenue growth a year, first year to last (%): {pct(r['metrics']['growth'])}", "",
            "Cathie Wood's checks"]
    out += [f"  {c:<56} {res}" for c, res in r["checks"].items()]
    return "\n".join(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit("Usage: python3 cathie_wood.py TICKER [--json]")
    try:
        r = analyze(args[0])
    except ValueError as err:
        raise SystemExit(f"Refusing to run: {err}")
    print(json.dumps(r, indent=2) if "--json" in sys.argv else report(r))


if __name__ == "__main__":
    main()
