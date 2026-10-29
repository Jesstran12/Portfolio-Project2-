# Lab 17: As-Of Data from FRED and ALFRED

**The question.** Was each number knowable on the day I would have traded on it, and may Project 2
use it?

Files: [`asof_app.py`](asof_app.py) (FRED today vs ALFRED as known on a date), building on Lab 16's
[`asof.py`](asof.py) (the provenance gate on a toy table). Run: `python3 asof.py` and
`python3 -m streamlit run asof_app.py`.

## Probe: PAYEMS, as known on 2025-01-15

| | As known on 2025-01-15 | Today (2026-10-29) |
| --- | ---: | ---: |
| Last month measured | Dec 2024 | Sep 2026 |
| Dec 2024 payrolls (thousands) | **159,536** | **158,316** (1,220 lower) |
| New values since | | 21 |
| Revised values on the same dates | | **381** |

This matches the expected result: 159,536 as known then, today's figure lower, and a revised count
well above zero. That shows the app read two different downloads, not today's data twice. The 381
revisions reach far back because the BLS benchmark revision restates years of history every
February. A backtest that used today's PAYEMS for a January 2025 decision would be trading on
numbers that did not exist then.

## E: my series, DGS10

| As known on | Last date measured | Value | New values since | Revised |
| --- | --- | ---: | ---: | ---: |
| 2026-09-30 (last day of last month) | 2026-09-29 | 5.26 | 20 | 0 |
| 2026-10-29 (today) | 2026-10-28 | 5.05 | 0 | 0 |

When I move the date from 2026-09-30 to today, the 20 daily values from 2026-09-30 to 2026-10-28
appear. They are missing on the earlier date because they had not been published yet. On both dates
the revised count is **0**. DGS10 is a daily market rate, so it shows almost no lag (one business
day: the 2026-09-30 vintage already ends at 2026-09-29) and no revisions. For a market rate like
this, today's data is the as-of data, apart from that one-day lag. PAYEMS is the opposite case.

## Data card: DGS10

| Field | |
| --- | --- |
| Source | Board of Governors of the Federal Reserve System, H.15 Selected Interest Rates, via FRED (Federal Reserve Bank of St. Louis): <https://fred.stlouisfed.org/series/DGS10>; vintages from ALFRED: <https://alfred.stlouisfed.org/series?seid=DGS10> |
| What it measures | Market yield on US Treasury securities at 10-year constant maturity, quoted on an investment basis |
| Units | Percent per year, daily, not seasonally adjusted; blank or "." on days with no market (weekends, holidays) |
| How late it is published | About one business day: the value for day *t* appears on FRED by day *t*+1 |
| Revised? | No. 0 revised values against both the 2026-09-30 and today vintages |
| Download date | 2026-10-29 |

**Three values read against the FRED page.** Check each on <https://fred.stlouisfed.org/series/DGS10>
(hover the chart or use Download → CSV):

| Date | App (today's data) | FRED page | Match? |
| --- | ---: | ---: | --- |
| 2026-10-01 | 5.24 | | |
| 2026-10-15 | 5.10 | | |
| 2026-10-28 | 5.05 | | |

## May Project 2 use it?

DGS10 can be used for decisions on or after the day after each date, because nothing is revised and
the only gap is the one-day publication lag. PAYEMS, or any macro series that gets revised, has to
come from ALFRED as known on the decision date, never from today's FRED download.

Built with AI help; a learning demonstration, not investment advice.
