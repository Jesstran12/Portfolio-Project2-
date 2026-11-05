"""Michael Burry's numbers: the same SEC EDGAR 10-K facts as buffett.py, his two checks.

Cash backing = operating cash flow vs net income, every year.
Leverage = Liabilities / StockholdersEquity, latest fiscal year.
A missing input prints "not found"; a check that needs it is "not known", never estimated.
Run: python3 .claude/skills/burry/burry.py COST   (add --json for machine-readable output)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "buffett"))
import buffett as b  # noqa: E402

# ---------------------------------------------------------------- editable inputs
MAX_LEVERAGE = 2.0  # liabilities no more than this many times equity, latest year
# ---------------------------------------------------------------- end of inputs

NOT_FOUND, NOT_KNOWN = b.NOT_FOUND, b.NOT_KNOWN


def is_num(v):
    return isinstance(v, (int, float))


def metrics(rows):
    """Per-year liabilities / equity (not known if equity is zero or negative)."""
    lev = {}
    for end, row in rows.items():
        li, eq = row["Liabilities"][0], row["Equity"][0]
        if not (is_num(li) and is_num(eq)):
            lev[end] = NOT_FOUND
        elif eq <= 0:
            lev[end] = NOT_KNOWN
        else:
            lev[end] = li / eq
    return {"leverage": lev}


def checks(rows, m):
    """His two checks: 'pass', 'fail', or 'not known' when an input is missing."""
    pairs = [(r["Operating cash flow"][0], r["Net income"][0]) for r in rows.values()]
    cash_known = bool(pairs) and all(is_num(o) and is_num(n) for o, n in pairs)
    latest = list(m["leverage"].values())[-1] if m["leverage"] else NOT_FOUND
    return {
        "Operating cash flow at least net income every year":
            ("pass" if all(o >= n for o, n in pairs) else "fail") if cash_known else NOT_KNOWN,
        f"Liabilities no more than {MAX_LEVERAGE:g} times equity, latest year":
            ("pass" if latest <= MAX_LEVERAGE else "fail") if is_num(latest) else NOT_KNOWN,
    }


def analyze(ticker, base=None):
    base = base or b.analyze(ticker)
    m = metrics(base["rows"])
    return {**base, "investor": "Burry", "metrics": m, "checks": checks(base["rows"], m)}


def report(r):
    out = [f"{r['company']} ({r['ticker']}), CIK {r['cik']}",
           f"Source: {r['source']} (10-K filings only), $ millions", "",
           f"  {'FY end':<14}{'Op. cash flow':>14}{'Net income':>12}{'Liabilities':>13}{'Equity':>10}{'Liab / equity':>15}"]
    for end, row in r["rows"].items():
        lev = r["metrics"]["leverage"][end]
        out.append(f"  {end:<14}{b.show('x', row['Operating cash flow'][0]):>14}{b.show('x', row['Net income'][0]):>12}"
                   f"{b.show('x', row['Liabilities'][0]):>13}{b.show('x', row['Equity'][0]):>10}"
                   f"{(f'{lev:.2f}' if is_num(lev) else lev):>15}")
    out += ["", "Burry's checks"]
    out += [f"  {c:<52} {res}" for c, res in r["checks"].items()]
    return "\n".join(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit("Usage: python3 burry.py TICKER [--json]")
    try:
        r = analyze(args[0])
    except ValueError as err:
        raise SystemExit(f"Refusing to run: {err}")
    print(json.dumps(r, indent=2) if "--json" in sys.argv else report(r))


if __name__ == "__main__":
    main()
