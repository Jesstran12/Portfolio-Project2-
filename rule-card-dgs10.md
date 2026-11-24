# Rule card: the DGS10 yield-trend rule

**Frozen before the backtest ran.** This file and `signal_rule.py` were committed before the rule
was run on real data; the commit that adds the results comes after it in the history. The values
below are the inputs at the top of [`signal_rule.py`](signal_rule.py). The app shows the result
for these values as locked numbers. Built with AI help; education, not investment advice.

| Rule card | Value |
|---|---|
| Signal | Change in the 10-year Treasury constant-maturity yield (FRED `DGS10`) over the month, in percentage points |
| Point in time | DGS10 for day *t* is published on day *t*+1. The month-end value is the one for the second-to-last trading day of the month, the newest value already published at the last close |
| Rule | Yield fell over the month (signal below 0) → hold IEF next month; otherwise hold BIL |
| Why this direction | Decided before the run: yields move in trends more often than they reverse within a month, and IEF's price falls when the 10-year yield rises |
| Lag | One month: this month's signal decides next month's position |
| Cost | 0.10% in any month the position switches; the run starts in BIL |
| Returns | Monthly Adj Close returns of IEF and BIL from `prices.csv`, complete months only |
| Development | 2021-12 to 2024-12 (37 months) |
| Holdout | 2025-01 to 2026-09 (21 months), run once, never tuned |
| Benchmark | Buy-and-hold IEF |
| Failure rule | Stop if the holdout net return trails buy-and-hold IEF |
| Placebo | The signal shuffled across months 1,000 times (seed 43900); the rule is evidence only if it beats most of them |

What the rule would be used for: choosing between BIL and IEF inside the reserve sleeve. It does
not set the equity weight.

## Result (`python3 signal_rule.py`)

First run on real data on 2026-11-23, after the commit that froze this card. Compounded returns
over each period, in percent.

| Period | Months | Rule gross | Rule net | Hold IEF | Hold BIL | Switches |
|---|---:|---:|---:|---:|---:|---:|
| Development | 37 | −3.33 | −5.16 | −13.08 | 11.95 | 19 |
| Holdout | 21 | 3.25 | 2.12 | 3.02 | 6.92 | 11 |

**Failure rule: triggered.** The holdout net return (2.12%) trails buy-and-hold IEF (3.02%) by
0.91 points. Before costs the rule is ahead (3.25%); 11 switches at 0.10% take it behind.

Failure tests:

- **Lag 0 (the leak).** Using the month's own yield change gives a holdout net of 16.38% and a
  development net of 45.86%. Nobody could trade on that; it shows how large a timing error looks.
- **Placebo.** With the signal shuffled across months 1,000 times, the median holdout net is
  4.10%, and 69.4% of the shuffles do at least as well as the real signal.
- **Simply holding BIL** earned 6.92% in the holdout, more than the rule and more than IEF.

**Decision: stop.** The rule is rejected and is not used to set any weight. It is not re-tuned:
the holdout has now been seen, so any change to the rule would need new data to test it.
