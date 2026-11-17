# Rule card: Lab 18 training signal

Frozen before the backtest runs. `backtest.py` holds these values as its inputs; `app.py` shows
the result for these values as locked numbers. Built with AI help; a learning demonstration, not
investment advice.

| Rule card | Value |
|---|---|
| Signal | month-end card-spend change, published by month-end |
| Rule | signal above 0 → hold the equity fund next month; otherwise Treasury bills |
| Lag | one month: this month's signal decides next month's position |
| Cost | 0.10% in any month the position switches; start in bills |
| Bills return | 0.3% a month |
| Development | 2025-01 to 2025-12 |
| Holdout | 2026-01 to 2026-06, run once, never tuned |
| Benchmark | buy-and-hold equity fund |
| Failure rule | stop if the holdout net return trails buy-and-hold |

## Known answer (`python3 backtest.py`)

| Period | Rule gross | Rule net | Buy-and-hold | Switches |
|---|---:|---:|---:|---:|
| Development | 6.55 | 6.13 | 5.33 | 4 |
| Holdout | −5.52 | −6.09 | −2.09 | 6 |

Failure rule: triggered, the holdout net trails buy-and-hold by 4.00 points. Lag 0 (the leak):
development net 17.72.

Decision: _your line here: continue unchanged, stop, or register a new hypothesis_
