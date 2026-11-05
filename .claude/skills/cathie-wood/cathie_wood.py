"""Cathie Wood's checks on the same SEC EDGAR 10-K facts as the Buffett skill.

The facts come from buffett.py (one download, one set of numbers for the whole panel); this file
only adds Cathie Wood's two checks. Anything missing gives "not known", never an estimate.
Run: python3 .claude/skills/cathie-wood/cathie_wood.py COST
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "buffett"))
import buffett as b  # noqa: E402

# ---------------------------------------------------------------- editable inputs
MIN_GROWTH = 15.0  # percent a year, revenue, first year to last (compound)
MIN_RD = 5.0       # percent of revenue, latest year
# ---------------------------------------------------------------- end of inputs


def is_num(v):
    return isinstance(v, (int, float))


def growth(rows):
    """Revenue growth a year in percent = (last / first) ** (1 / (years - 1)) - 1, or NOT_KNOWN."""
    rev = [r["Revenue"][0] for r in rows.values()]
    if len(rev) < 2 or not all(is_num(v) for v in rev) or rev[0] <= 0:
        return b.NOT_KNOWN
    return ((rev[-1] / rev[0]) ** (1 / (len(rev) - 1)) - 1) * 100


def rd_share(row):
    """R&D as a percent of revenue for one year, or 'not found' if either input is missing."""
    rd, rev = row["R&D"][0], row["Revenue"][0]
    if not is_num(rd) or not is_num(rev) or rev <= 0:
        return b.NOT_FOUND
    return rd / rev * 100


def checks(rows):
    """Cathie Wood's two checks: 'pass', 'fail', or 'not known' when an input is missing."""
    g = growth(rows)
    latest = rd_share(list(rows.values())[-1]) if rows else b.NOT_FOUND
    return {
        f"Revenue grew {MIN_GROWTH:g}% or more a year, first year to last":
            ("pass" if g >= MIN_GROWTH else "fail") if is_num(g) else b.NOT_KNOWN,
        f"R&D {MIN_RD:g}% or more of revenue, latest year":
            ("pass" if latest >= MIN_RD else "fail") if is_num(latest) else b.NOT_KNOWN,
    }


def analyze(ticker, result=None):
    result = result or b.analyze(ticker)
    rows = result["rows"]
    return {**result, "growth": growth(rows),
            "rd_share": {end: rd_share(row) for end, row in rows.items()},
            "checks": checks(rows)}


def pct(v):
    return f"{v:.2f}" if is_num(v) else v


def report(res):
    """The printed report: every number Cathie Wood's memo may use appears here."""
    ends = list(res["rows"])
    out = [f"{res['company']} ({res['ticker']}), CIK {res['cik']}",
           f"Source: {res['source']} (10-K filings only), $ millions", ""]
    for end, row in res["rows"].items():
        out.append(f"Fiscal year ending {end}")
        for line in ("Revenue", "R&D"):
            out.append(f"  {line:<20} {b.show(line, row[line][0]):>12}   {row[line][1] or b.NOT_FOUND}")
        out.append(f"  {'R&D / revenue (%)':<20} {pct(res['rd_share'][end]):>12}")
        out.append("")
    span = f"{ends[0]} to {ends[-1]}" if ends else "no years"
    out.append(f"Revenue growth a year (%), {span}: {pct(res['growth'])}")
    out.append("")
    out.append("Cathie Wood's checks")
    for check, r in res["checks"].items():
        out.append(f"  {check:<58} {r}")
    return "\n".join(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit("Usage: python3 cathie_wood.py TICKER")
    try:
        print(report(analyze(args[0])))
    except ValueError as err:
        raise SystemExit(f"Refusing to run: {err}")


if __name__ == "__main__":
    main()
