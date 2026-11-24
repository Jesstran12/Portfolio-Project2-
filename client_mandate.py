"""Project 2 - the client mandate as code: every rule, and a pass/fail verdict for any weights.

The written mandate is docs/mandate.md; the numbers there and here must agree (tests check it).
Standard library only. Edit the inputs at the top; everything below is computed from them.
Run: python3 client_mandate.py
"""

import math

import portfolio as p

# ---------------------------------------------------------------- editable inputs (the mandate)
CLIENT = "Riverbend Scholarship Reserve (hypothetical client)"

# ticker: (fund, role, reserve-eligible, equity)
UNIVERSE = {
    "BIL":  ("SPDR Bloomberg 1-3 Month T-Bill ETF",                "cash and reserve",     True,  False),
    "IEF":  ("iShares 7-10 Year Treasury Bond ETF",                "government bonds",     True,  False),
    "LQD":  ("iShares iBoxx $ Investment Grade Corporate Bond ETF", "corporate bonds",      False, False),
    "VTI":  ("Vanguard Total Stock Market ETF",                    "US equity",            False, True),
    "VXUS": ("Vanguard Total International Stock ETF",             "international equity", False, True),
}

# benchmark, percent weights: 60% equity (two thirds US), 40% bonds (half Treasury, half corporate)
BENCHMARK = {"BIL": 0, "IEF": 20, "LQD": 20, "VTI": 40, "VXUS": 20}

SPENDING_RATE = 4.0          # percent of the reserve paid out as scholarships each year
INFLATION_ASSUMPTION = 2.5   # percent a year, the client's planning assumption (not an estimate)

RULES = {
    "objective": SPENDING_RATE + INFLATION_ASSUMPTION,  # percent a year: spending plus inflation
    "reserve_min": SPENDING_RATE,   # percent in BIL + IEF: twelve months of payouts
    "equity_max": 70.0,             # percent in VTI + VXUS: the benchmark's 60 plus 10
    "loss_limit": 10.0,             # percent: the most the client accepts losing over twelve months
}
Z_95 = 1.645                 # one-sided 95% point of the normal distribution
# ---------------------------------------------------------------- end of inputs

TICKERS = list(UNIVERSE)


def benchmark_weights(tickers=TICKERS):
    return [BENCHMARK.get(t, 0) / 100 for t in tickers]


def portfolio_returns(weights, monthly):
    """Monthly portfolio returns (decimal) for fixed weights, rebalanced every month."""
    return [sum(w * r for w, r in zip(weights, row)) for row in monthly]


def worst_12_month_return(weights, monthly):
    """Lowest compounded return (percent) over any 12 consecutive months in the sample."""
    series = portfolio_returns(weights, monthly)
    if len(series) < 12:
        raise ValueError("Need at least 12 monthly returns to measure a 12-month loss")
    worst = None
    for start in range(len(series) - 11):
        growth = 1.0
        for r in series[start:start + 12]:
            growth *= 1 + r
        if worst is None or growth < worst:
            worst = growth
    return (worst - 1) * 100


def loss_estimate_95(ret, vol):
    """One-year loss (percent, positive = loss) exceeded about 1 year in 20: 1.645 x vol - return."""
    return Z_95 * vol - ret


def measure(weights, tickers, returns, cov, monthly):
    """Every number the rules need, in percent. weights are decimals in ticker order."""
    ret = p.expected_return(weights, returns)
    vol = p.volatility(weights, cov)
    return {
        "total": sum(weights) * 100,
        "lowest": min(weights) * 100,
        "reserve": sum(w for w, t in zip(weights, tickers) if UNIVERSE[t][2]) * 100,
        "equity": sum(w for w, t in zip(weights, tickers) if UNIVERSE[t][3]) * 100,
        "return": ret,
        "volatility": vol,
        "loss_95": loss_estimate_95(ret, vol),
        "worst_12m": worst_12_month_return(weights, monthly),
    }


def check(m, rules=RULES):
    """List of (rule id, rule text, measured value, passed) for the measures m."""
    eps = 1e-9
    return [
        ("M1", "Weights sum to 100%", m["total"], abs(m["total"] - 100) < 1e-6),
        ("M2", "Long-only: lowest weight >= 0%", m["lowest"], m["lowest"] >= -eps),
        ("M3", f"Reserve (BIL + IEF) >= {rules['reserve_min']:.1f}%", m["reserve"],
         m["reserve"] >= rules["reserve_min"] - eps),
        ("M4", f"Equity (VTI + VXUS) <= {rules['equity_max']:.0f}%", m["equity"],
         m["equity"] <= rules["equity_max"] + eps),
        ("M5", f"Return estimate >= {rules['objective']:.1f}% objective", m["return"],
         m["return"] >= rules["objective"] - eps),
        ("M6", f"One-year 95% loss estimate <= {rules['loss_limit']:.0f}%", m["loss_95"],
         m["loss_95"] <= rules["loss_limit"] + eps),
        ("M7", f"Worst 12-month return in the sample >= -{rules['loss_limit']:.0f}%", m["worst_12m"],
         m["worst_12m"] >= -rules["loss_limit"] - eps),
    ]


def verdict(checks):
    """'PASS' or 'FAIL: M5, M7' naming every failed rule."""
    failed = [rule_id for rule_id, _, _, ok in checks if not ok]
    return "PASS" if not failed else "FAIL: " + ", ".join(failed)


def failed_rules(checks):
    """Plain-language list of the failed rules with the measured value."""
    return [f"{rule_id} {text} (measured {value:.2f}%)" for rule_id, text, value, ok in checks if not ok]


def main():
    print(CLIENT)
    print(f"Objective {RULES['objective']:.1f}% = spending {SPENDING_RATE:.1f}% + inflation "
          f"assumption {INFLATION_ASSUMPTION:.1f}%")
    print("Benchmark: " + " / ".join(f"{t} {BENCHMARK[t]}" for t in TICKERS))
    example = {"total": 100, "lowest": 0, "reserve": 0, "equity": 100, "return": 0,
               "loss_95": 0, "worst_12m": 0}
    for rule_id, text, _, _ in check(example):
        print(f"  {rule_id}  {text}")
    assert math.isclose(sum(BENCHMARK.values()), 100)


if __name__ == "__main__":
    main()
