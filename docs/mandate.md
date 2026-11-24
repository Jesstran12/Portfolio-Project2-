# Mandate: Riverbend Scholarship Reserve

> **Status: approved by the student on 2026-11-23.** The numbers were proposed by the AI
> assistant, each with its reason, and the student reviewed and approved them without change.
> The same numbers are the constants at the top of
> [`client_mandate.py`](../client_mandate.py); a test fails if the two disagree.
>
> Riverbend is a hypothetical client written for FIN 43900 Project 2. Education, not investment
> advice.

## Decision frame

| | |
|---|---|
| Intended user | The reserve's three-person investment committee, who are not finance specialists |
| Client | A $5 million scholarship reserve that pays out 4% of its value each year |
| Action requested | Adopt, pilot or reject a rule-based way of setting the reserve's fund weights |
| Horizon | Five years or longer; the reserve is meant to be permanent |
| Review and rebalancing | Estimates and verdicts reviewed every quarter; weights rebalanced once a year, or sooner if a monitoring trigger fires |
| Tax and legal | Tax-exempt; no borrowing, no short positions, no derivatives |

## Objective

Earn **6.5% a year** over rolling five-year periods: the 4.0% payout plus a 2.5% inflation
assumption, so the reserve keeps its purchasing power. The objective is tested on the return
*estimate* (rule M5). It is an average of past returns, not a forecast.

## Universe

Five low-cost exchange-traded funds, each priced daily and sold within two business days.

| Ticker | Fund | Role | Counts as reserve | Counts as equity |
|---|---|---|---|---|
| BIL | SPDR Bloomberg 1-3 Month T-Bill ETF | cash and reserve | yes | no |
| IEF | iShares 7-10 Year Treasury Bond ETF | government bonds | yes | no |
| LQD | iShares iBoxx $ Investment Grade Corporate Bond ETF | corporate bonds | no | no |
| VTI | Vanguard Total Stock Market ETF | US equity | no | yes |
| VXUS | Vanguard Total International Stock ETF | international equity | no | yes |

## Benchmark

**60/40: BIL 0 / IEF 20 / LQD 20 / VTI 40 / VXUS 20.** Equity is 60% (two thirds US, one third
international) and bonds are 40% (half Treasury, half corporate). It is the yardstick for return
and risk, and it is what the committee would hold if it did nothing. It is not a limit on the
weights; rule M4 is.

## Risk measure and limits

The risk measure the search minimises is **volatility**: the standard deviation of monthly
returns × √12, in percent a year.

The client's loss tolerance is **10% over any twelve months**. Lab 13 found that a loss limit
with no measure cannot be tested, so this mandate measures it two ways and requires both:

- **M6, a 1-in-20 estimate.** 1.645 × volatility − return estimate must be 10% or less. This is
  the loss a normal distribution puts at the 5% tail for one year.
- **M7, a history replay.** The weights, held through every 12-month window in the sample, must
  never have returned less than −10%. The sample includes 2022.

## The rules

| Rule | Type | Test | Reason for the number |
|---|---|---|---|
| M1 | Hard constraint | Weights sum to 100% | Fully invested |
| M2 | Hard constraint | Lowest weight ≥ 0% | Long-only |
| M3 | Hard constraint | BIL + IEF ≥ 4.0% | Twelve months of payouts held in Treasuries |
| M4 | Hard constraint | VTI + VXUS ≤ 70% | The benchmark's 60% plus 10 points; this stops the "97% equity passes every rule" portfolio from Lab 13 |
| M5 | Objective | Return estimate ≥ 6.5% | 4.0% payout + 2.5% inflation assumption |
| M6 | Risk limit | One-year 95% loss estimate ≤ 10% | The client's stated tolerance, read as 1-in-20 |
| M7 | Risk limit | Worst 12-month return in the sample ≥ −10% | The same tolerance, read as "it has not happened in this history" |

A portfolio's verdict is **PASS** only if all seven pass. Otherwise it is **FAIL** followed by
the rules it failed, for example `FAIL: M6, M7`.

Not tested on a single set of weights: turnover. The budget is 25% a year (one-way). The app
reports the turnover of moving from the benchmark and of each yearly rebalance against it.

## Conventions

- Returns are arithmetic means of monthly returns × 12; volatility is the sample standard
  deviation × √12; both in percent a year.
- Prices are month-end Adj Close, which includes distributions.
- The base case uses complete months only: December 2021 to September 2026, 58 monthly returns,
  as of **2026-09-30**.
- Weights are searched in 5-point steps, so every answer is a multiple of 5.

## The partial October 2026 row

`prices.csv` ends with a row dated 2026-10-01 whose prices are from October 21, part-way through
the month. **The base case excludes it.** A month-to-date return is not a monthly return, and
the as-of date would otherwise be a day nobody chose. The row stays in the file and the stress
run shows the answer with it included:

| | BIL / IEF / LQD / VTI / VXUS | Equity |
|---|---|---:|
| Complete months only (base case, 58 returns) | 65 / 0 / 0 / 20 / 15 | 35 |
| Partial October included (59 returns) | 65 / 0 / 0 / 30 / 5 | 35 |

Total equity is the same; 10 points move between the two equity funds. The second row is the
Lab 15 answer.

## The one question for the client

> "Is the 10% twelve-month loss limit a line that must never be crossed, or a loss you accept
> about one year in twenty? And if we tighten it to 5%, which gives way: the limit or the 6.5%
> objective?"

Why it matters: at a 5% limit no mix in this universe reaches 6.5% (stress run, constraints
group). At 10% the 60/40 benchmark itself fails both loss rules.
