"""Buffett's numbers from SEC EDGAR: the last five fiscal years of 10-K facts, ROE, owner earnings, checks.

Standard library only, no API key. Edit the inputs at the top; everything below is computed from them.
A value not found prints "not found", never an estimate.
Run: python3 .claude/skills/buffett/buffett.py COST        (add --json for machine-readable output)
"""

import json
import sys
import urllib.request
from datetime import date

# ---------------------------------------------------------------- editable inputs
USER_AGENT = "Jess Tran tran334@purdue.edu"  # SEC asks every caller to name themselves
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
YEARS = 5
FORM = "10-K"
ONE_YEAR_DAYS = (350, 380)  # a flow counts as one year if its period is this long (52/53-week years)

# line: (kind, us-gaap tags in order of preference)
LINES = {
    "Revenue":             ("flow",    ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"]),
    "Net income":          ("flow",    ["NetIncomeLoss"]),
    "Operating cash flow": ("flow",    ["NetCashProvidedByUsedInOperatingActivities"]),
    "Capital spending":    ("flow",    ["PaymentsToAcquirePropertyPlantAndEquipment",
                                        "PaymentsToAcquireProductiveAssets"]),
    "Equity":              ("instant", ["StockholdersEquity"]),
    # Lab 19: shared with the Cathie Wood and Burry skills
    "Liabilities":         ("instant", ["Liabilities"]),
    "R&D":                 ("flow",    ["ResearchAndDevelopmentExpense"]),
}
MIN_ROE = 15.0  # percent, every year
# ---------------------------------------------------------------- end of inputs

NOT_FOUND, NOT_KNOWN = "not found", "not known"


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def cik_for(ticker):
    """(CIK, company name) from SEC's ticker list."""
    for row in get_json(TICKERS_URL).values():
        if row["ticker"].upper() == ticker.upper():
            return row["cik_str"], row["title"]
    raise ValueError(f"ticker '{ticker}' is not in SEC's ticker list")


def one_year(fact):
    if "start" not in fact:
        return False
    length = (date.fromisoformat(fact["end"]) - date.fromisoformat(fact["start"])).days
    return ONE_YEAR_DAYS[0] <= length <= ONE_YEAR_DAYS[1]


def by_period_end(gaap, tag, kind):
    """{period end: fact} for one tag: 10-K only, flows one year long, the latest filing wins."""
    out = {}
    for fact in gaap.get(tag, {}).get("units", {}).get("USD", []):
        if fact.get("form") != FORM:
            continue
        if (kind == "flow") != one_year(fact):  # flows need a one-year period; instants have no start
            continue
        end = fact["end"]
        if end not in out or fact["filed"] > out[end]["filed"]:
            out[end] = fact
    return out


def fiscal_year_ends(gaap):
    """The last YEARS fiscal-year-end dates: the ends of one-year flows reported in 10-Ks."""
    ends = set()
    for kind, tags in LINES.values():
        if kind == "flow":
            for tag in tags:
                ends |= set(by_period_end(gaap, tag, kind))
    return sorted(ends)[-YEARS:]


def year_row(gaap, end):
    """One fiscal year: {line: (value in USD, tag)}, or (NOT_FOUND, None) if no tag has that year."""
    row = {}
    for line, (kind, tags) in LINES.items():
        row[line] = (NOT_FOUND, None)
        for tag in tags:  # first tag in the list that has this year wins
            fact = by_period_end(gaap, tag, kind).get(end)
            if fact is not None:
                row[line] = (fact["val"], tag)
                break
    ni, eq = row["Net income"][0], row["Equity"][0]
    if ni == NOT_FOUND or eq == NOT_FOUND:
        row["ROE (%)"] = (NOT_FOUND, "NetIncomeLoss / StockholdersEquity")
    elif eq <= 0:
        row["ROE (%)"] = (NOT_KNOWN, "NetIncomeLoss / StockholdersEquity")
    else:
        row["ROE (%)"] = (ni / eq * 100, "NetIncomeLoss / StockholdersEquity")
    ocf, capex = row["Operating cash flow"], row["Capital spending"]
    row["Owner earnings"] = (NOT_FOUND if NOT_FOUND in (ocf[0], capex[0]) else ocf[0] - capex[0],
                             f"{ocf[1] or LINES['Operating cash flow'][1][0]} - "
                             f"{capex[1] or LINES['Capital spending'][1][0]}")
    return row


def checks(rows):
    """Buffett's three checks: 'pass', 'fail', or 'not known' when any input is missing."""
    roe = [r["ROE (%)"][0] for r in rows.values()]
    oe = [r["Owner earnings"][0] for r in rows.values()]

    def known(vals):
        return bool(vals) and all(isinstance(v, (int, float)) for v in vals)

    def result(ok):
        return "pass" if ok else "fail"

    return {
        f"ROE of {MIN_ROE:g}% or more every year": result(all(v >= MIN_ROE for v in roe)) if known(roe) else NOT_KNOWN,
        "Owner earnings positive every year": result(all(v > 0 for v in oe)) if known(oe) else NOT_KNOWN,
        "Owner earnings grew, first year to last": result(oe[-1] > oe[0]) if known(oe) and len(oe) > 1 else NOT_KNOWN,
    }


def analyze(ticker):
    """Everything the skill and the app need for one ticker."""
    cik, name = cik_for(ticker)
    gaap = get_json(FACTS_URL.format(cik=cik)).get("facts", {}).get("us-gaap", {})
    rows = {end: year_row(gaap, end) for end in fiscal_year_ends(gaap)}
    return {"ticker": ticker.upper(), "company": name, "cik": cik,
            "source": FACTS_URL.format(cik=cik), "rows": rows, "checks": checks(rows)}


def show(line, value):
    """As printed: $ millions with commas, ROE to one decimal, or 'not found' / 'not known'."""
    if not isinstance(value, (int, float)):
        return value
    return f"{value:.1f}" if line == "ROE (%)" else f"{value / 1e6:,.0f}"


def report(result):
    """The printed report: every number the memo may use appears here."""
    out = [f"{result['company']} ({result['ticker']}), CIK {result['cik']}",
           f"Source: {result['source']} (10-K filings only), $ millions",
           ""]
    for end, row in result["rows"].items():
        out.append(f"Fiscal year ending {end}")
        for line, (value, tag) in row.items():
            out.append(f"  {line:<20} {show(line, value):>12}   {tag or NOT_FOUND}")
        out.append("")
    out.append("Buffett's checks")
    for check, res in result["checks"].items():
        out.append(f"  {check:<42} {res}")
    return "\n".join(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit("Usage: python3 buffett.py TICKER [--json]")
    try:
        result = analyze(args[0])
    except ValueError as err:
        raise SystemExit(f"Refusing to run: {err}")
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print(report(result))


if __name__ == "__main__":
    main()
