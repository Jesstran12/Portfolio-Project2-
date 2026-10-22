"""Lab 13 - Meridian Foundation Reserve: mandate checker.

Standard library only. Edit the inputs at the top; everything below is computed from them.
Run: python mandate.py
"""

# ---------------------------------------------------------------- editable inputs
# holding: (issuer, business days to redeem, reserve-eligible)
HOLDINGS = {
    "Cash":                       ("none",             0,  True),
    "Treasury bills":             ("U.S. Treasury",    1,  True),
    "Treasury 10-year note":      ("U.S. Treasury",    1,  True),
    "Global equity index fund":   ("diversified fund", 2,  False),
    "Investment-grade bond fund": ("diversified fund", 3,  False),
    "Private real estate fund":   ("diversified fund", 90, False),
    "Acme Corp bonds":            ("Acme Corp",        4,  False),
    "Acme Corp stock":            ("Acme Corp",        1,  False),
}

# candidate portfolios, percent weights
CANDIDATES = {
    "A": {"Cash": 2, "Treasury bills": 2, "Treasury 10-year note": 10,
          "Global equity index fund": 60, "Investment-grade bond fund": 26,
          "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 0},
    "B": {"Cash": 1, "Treasury bills": 0, "Treasury 10-year note": 0,
          "Global equity index fund": 55, "Investment-grade bond fund": 20,
          "Private real estate fund": 15, "Acme Corp bonds": 5, "Acme Corp stock": 4},
    "C": {"Cash": 1, "Treasury bills": 1, "Treasury 10-year note": 0,
          "Global equity index fund": 70, "Investment-grade bond fund": 20,
          "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 8},
    # D: AI-proposed attack portfolio (section E) - passes every checkable rule
    "D": {"Cash": 3, "Treasury bills": 0, "Treasury 10-year note": 0,
          "Global equity index fund": 89, "Investment-grade bond fund": 0,
          "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 8},
    # E: the client's own 40/60 benchmark (Lab 14)
    "E": {"Cash": 0, "Treasury bills": 0, "Treasury 10-year note": 0,
          "Global equity index fund": 60, "Investment-grade bond fund": 40,
          "Private real estate fund": 0, "Acme Corp bonds": 0, "Acme Corp stock": 0},
}

RESERVE_SIZE = 100.0          # USD millions
QUARTERLY_DISTRIBUTION = 0.75  # USD millions
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW_DAYS = 5      # business days
MIN_LIQUID_SHARE = 90.0        # percent
ISSUER_LIMIT = 8.0             # percent
EXEMPT_ISSUERS = {"none", "U.S. Treasury", "diversified fund"}
# ---------------------------------------------------------------- end of inputs


def reserve_minimum():
    return QUARTERS_TO_COVER * QUARTERLY_DISTRIBUTION / RESERVE_SIZE * 100


def largest_company(weights):
    by_issuer = {}
    for holding, w in weights.items():
        issuer = HOLDINGS[holding][0]
        if issuer not in EXEMPT_ISSUERS:
            by_issuer[issuer] = by_issuer.get(issuer, 0) + w
    return max(by_issuer.values(), default=0.0)


def check(weights, reserve_min):
    """Return a list of (rule, measured value, passed)."""
    total = sum(weights.values())
    lowest = min(weights.values())
    reserve = sum(w for h, w in weights.items() if HOLDINGS[h][2])
    liquid = sum(w for h, w in weights.items() if HOLDINGS[h][1] <= LIQUIDITY_WINDOW_DAYS)
    company = largest_company(weights)
    return [
        ("Weights sum to 100", total, abs(total - 100) < 1e-9),
        ("Long-only (lowest weight)", lowest, lowest >= 0),
        (f"Reserve-eligible >= {reserve_min:.1f}%", reserve, reserve >= reserve_min),
        (f"Redeemable in {LIQUIDITY_WINDOW_DAYS} days >= {MIN_LIQUID_SHARE:.0f}%",
         liquid, liquid >= MIN_LIQUID_SHARE),
        (f"Largest single company <= {ISSUER_LIMIT:.0f}%", company, company <= ISSUER_LIMIT),
    ]


def main():
    reserve_min = reserve_minimum()
    print(f"Reserve minimum: {QUARTERS_TO_COVER} x {QUARTERLY_DISTRIBUTION} / "
          f"{RESERVE_SIZE:g} = {reserve_min:.1f}% of the portfolio\n")
    for name, weights in CANDIDATES.items():
        missing = set(HOLDINGS) - set(weights)
        unknown = set(weights) - set(HOLDINGS)
        if missing or unknown:
            raise ValueError(f"Candidate {name}: missing {missing or '-'}, unknown {unknown or '-'}")
        print(f"Candidate {name}")
        results = check(weights, reserve_min)
        for rule, value, ok in results:
            print(f"  {rule:<34} {value:6.1f}  {'pass' if ok else 'FAIL'}")
        print(f"  {'Calendar-year loss <= 10%':<34} {'':6}  requires CIO clarification")
        fails = sum(not ok for _, _, ok in results)
        print("  Verdict: " + ("passes every checkable rule" if fails == 0
                               else f"fails {fails} rule(s)") + "\n")


if __name__ == "__main__":
    main()
