# Data cards

One card for every material input to the decision. The files are dated snapshots committed to
this repository, so the app and every script run offline and give the same numbers each time.
SHA-256 hashes of the files are printed in [`output/decision-report.md`](../output/decision-report.md).

Education, not investment advice. No personal data, no credentials and no API keys are used
anywhere in this project.

## 1. Fund prices: `prices.csv`

| Field | Entry |
|---|---|
| Source and link | Yahoo Finance, Historical Data → Monthly, Adj Close: <https://finance.yahoo.com/quote/BIL/history/> (and the same page for IEF, LQD, VTI, VXUS) |
| What it measures | Month-end adjusted closing price of one share of each fund. Adj Close adds back distributions and splits, so the ratio of two values is a total return |
| Units | US dollars per share, adjusted. One row per month, labelled with the first day of the month and holding that month's last close |
| Coverage | 60 rows, November 2021 to October 2026; five funds |
| Download date | 2026-10-22 |
| As-of boundary | **2026-09-30.** The September 2026 row is the last complete month |
| Publication lag | None that matters: a closing price is known at the close |
| Revisions | Yes, in one way. Yahoo restates every past Adj Close each time a fund pays a distribution, so a later download shows different price levels. Returns are unaffected except for rounding. The file is a snapshot as of the download date |
| Transformations | Monthly return = price ÷ previous price − 1. Return estimate = mean × 12. Volatility = sample standard deviation × √12. Correlation = Pearson, on monthly returns. All in `portfolio.py` (`estimates_from_prices`) |
| Exclusions | The row dated 2026-10-01 holds prices from October 21, a partial month. It is kept in the file and excluded from the base case by `process.py` (`LAST_COMPLETE_MONTH = "2026-09"`). The stress run shows the answer with it included. Nothing else is removed or cleaned |
| Licensing | Yahoo's terms of service allow personal, non-commercial use: <https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html>. This is a course project; the file holds only the 60 monthly values needed to reproduce the result |
| Privacy | Public market data. No personal data |

| Ticker | Fund | Issuer | First value (Nov 2021) | Last complete value (Sep 2026) |
|---|---|---|---:|---:|
| BIL | SPDR Bloomberg 1-3 Month T-Bill ETF | State Street | 76.3466 | 91.3770 |
| IEF | iShares 7-10 Year Treasury Bond ETF | BlackRock | 99.3899 | 89.0030 |
| LQD | iShares iBoxx $ Investment Grade Corporate Bond ETF | BlackRock | 108.8936 | 101.7410 |
| VTI | Vanguard Total Stock Market ETF | Vanguard | 217.7796 | 374.2400 |
| VXUS | Vanguard Total International Stock ETF | Vanguard | 53.4722 | 84.9600 |

Known weakness: the values were copied from Yahoo by hand in October and cannot be re-downloaded
to the same price levels, because of the restatement described above. A fresh download should
reproduce the monthly returns to rounding.

## 2. The signal: `data/dgs10.csv`

| Field | Entry |
|---|---|
| Source and link | Board of Governors of the Federal Reserve System, H.15 Selected Interest Rates, through FRED (Federal Reserve Bank of St. Louis): <https://fred.stlouisfed.org/series/DGS10>. Downloaded as CSV from `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10&cosd=2021-09-01` |
| What it measures | Market yield on US Treasury securities at 10-year constant maturity, quoted on an investment basis |
| Units | Percent a year, daily, not seasonally adjusted. Blank on days with no market |
| Coverage | 2021-09-01 to 2026-11-19: 1,362 dated rows, 1,303 with a value, 59 blank (holidays) |
| Download date | 2026-11-23 |
| Publication lag | One business day: the value for day *t* appears on FRED on day *t*+1 |
| How the rule respects the lag | At each month's last close the rule uses the value for the second-to-last trading day (`known_at_month_end` in `signal_rule.py`). The value for the last day is never used, because it is not out yet |
| Revisions | None found. `data/dgs10_vintage_2026-09-30.csv` is the ALFRED vintage "as known on 2026-09-30" (<https://alfred.stlouisfed.org/series?seid=DGS10>). All 1,268 dates it shares with today's file carry the same value: 0 revised. Its last date is 2026-09-29, which confirms the one-day lag |
| Transformations | Signal for month *m* = known month-end yield of *m* − known month-end yield of *m* − 1, in percentage points. Blank days are skipped |
| Exclusions | Values after 2026-09-30 are in the file but no decision uses them: the last position decided is September 2026, from the August signal |
| Check against the source | Three values read from the FRED CSV on 2026-11-23 and compared with the Lab 17 app readings: 2026-10-01 = 5.24, 2026-10-15 = 5.10, 2026-10-28 = 5.05. All three match. A test repeats the check on the committed file |
| Licensing | FRED terms of use: <https://fred.stlouisfed.org/legal/>. DGS10 is a Board of Governors series, public domain, citation requested |
| Privacy | Public data. No API key is used (the CSV link needs none) |

## 3. The inflation assumption behind the objective

| Field | Entry |
|---|---|
| Value | 2.5% a year |
| What it is | The client's planning assumption. The 6.5% objective is the 4.0% payout plus this number |
| Source | An assumption, not a data series and not an estimate from this project. For reference, the Federal Reserve's longer-run inflation goal is 2%: <https://www.federalreserve.gov/monetarypolicy/review-of-monetary-policy-strategy-tools-and-communications-statement-on-longer-run-goals-monetary-policy-strategy.htm> |
| As-of date | Set with the mandate, 2026-11-23 |
| Sensitivity | The stress run moves the objective to 6.0% and 7.0%, the same as moving this assumption to 2.0% and 3.0% |
| Revisions | Reviewed with the mandate once a year |

## 4. The course training signal: `backtest.py`

Not an input to the decision. The Week 12 lab's card-spend series is typed into `backtest.py`
by the course; it has no public source, so no process could be adopted on it. It stays in the
repository as a lab file and as a known-answer test.
