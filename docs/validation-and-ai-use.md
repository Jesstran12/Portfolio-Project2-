# Validation and AI use

> **AI announcement.** I used Claude Code (Anthropic, model Claude Fable 5.2) to help me build
> this project. Claude wrote most of the code and the tests, drafted the documents, and proposed
> the mandate numbers. I chose the funds, downloaded the prices, wrote the changed-input
> prediction with AI closed, checked the AI's output, and made the decision. The analysis and
> the decision are mine.
>
> **Education, not investment advice.** This is a FIN 43900 course project on a hypothetical
> client, and nothing in it is a recommendation to buy or sell.

Written for a reader who wants to challenge the decision. Every result below can be reproduced
with `python3 -m pytest -q` and `python3 make_output.py`; the numbers are in
[output/decision-report.md](../output/decision-report.md). Decision under test: **pilot the
constrained portfolio (BIL 65 / IEF 0 / LQD 0 / VTI 20 / VXUS 15), reject the DGS10 signal**, as
of 2026-09-30.

## 1. The claims most likely to reverse the decision

Ranked by how easily each could reverse it.

| # | Claim | Test aimed at it | Result | Action it drives |
|---|---|---|---|---|
| 1 | The constrained weights are stable enough to act on | Stress run: 22 reruns with one input changed (`test_stress_run_known_answers`) | **Fails.** BIL moves 20 points on the last-36-month window; VTI ranges from 5% to 40% | Pilot, not adopt. The memo gives a range. Adoption gate GATE-1 |
| 2 | The portfolio would have met the mandate on data it had not seen | Out-of-sample: estimate on 36 months, hold 22 (`test_out_of_sample_uses_no_later_data`) | **Passes on risk and objective** (8.19% a year, 5.15% volatility), but trails the benchmark's 10.30% return | Supports a pilot. The memo claims lower risk, not higher return |
| 3 | The loss rules mean what the client means | Constraint stress: loss limit at 5% and 15% | **At 5% no mix passes** | Committee ask 2; adoption gate GATE-2 |
| 4 | The signal adds value after costs | Frozen rule, holdout run once, placebo, lag-0 leak (`test_frozen_dgs10_rule_known_answer` and two more) | **Fails.** Holdout net 2.12% against 3.02% for holding IEF; 69.4% of shuffled signals do as well | Signal rejected |
| 5 | The signal used only data known at the time | ALFRED vintage comparison; month-end value check (`test_dgs10_is_point_in_time`) | **Passes.** 0 of 1,268 values revised; the rule uses the 2026-09-29 value at the September close | The holdout result can be trusted as a fair test |
| 6 | The search returns the true lowest-risk passing mix | Brute force over all 10,626 mixes (`test_constrained_portfolio_passes_and_is_the_lowest_risk_passing_mix`) | **Passes** | The decision number is what the method says it is |
| 7 | The engine computes volatility correctly | Hand calculation of 10.46% (`test_benchmark_volatility_matches_the_hand_calculation`) | **Passes** | Same |
| 8 | Excluding the partial October row does not drive the result | Stress run with the row included | Equity stays 35%; 10 points move from VXUS to VTI | Reported in the mandate file; inside the range |

## 2. Sources and the as-of boundary

Prices: Yahoo Finance monthly Adj Close, downloaded 2026-10-22, used through **2026-09-30**.
Signal: FRED DGS10, downloaded 2026-11-23, used with its one-day publication lag. Nothing dated
after 2026-09-30 enters any decision number. Full cards, with definitions, transformations,
exclusions, revisions and licensing: [data-cards.md](data-cards.md). File hashes are printed in
the decision report, and `tests/test_output.py` fails if the committed output no longer matches
what the code produces.

## 3. Known-answer and baseline checks

Run on 2026-11-23: `python3 -m pytest -q` → **37 passed**.

| Known answer | Expected | Got |
|---|---|---|
| Meridian 40/60 benchmark volatility, by hand: √(0.4²×0.06² + 0.6²×0.16² + 2×0.4×0.6×0.25×0.06×0.16) | 10.46% | 10.46% |
| Lab 14 equal weight, return and volatility | 5.20%, 5.21% | match |
| Lab 14 inverse volatility, return and volatility | 3.77%, 1.05% | match |
| Lab 15 lowest-risk mix, and with the equity estimate cut to 7.0 | 0/20/25/55 (6.51%, 9.44%); 0/10/10/80 (6.53%, 12.94%) | match |
| Lab 13 candidates A to E, rules failed | 0, 3, 1, 0, 1 | match |
| Week 12 training backtest at its frozen cost of 0.10% | development net 6.13%, holdout net −6.09% | match |
| Worst 12-month return on a made-up series | (0.99¹² − 1) × 100 | match |
| Signal rule on four made-up months, by hand | 3 switches; net as computed by hand | match |
| Bridge columns add up to the difference between the two portfolios | exact | match |

Baselines on the client's universe (complete months, 58 returns): benchmark 60/40 6.57% return
estimate and 11.83% volatility; equal weight 4.82% and 8.91%; inverse volatility 3.65% and 1.62%.

## 4. Mandate check

| Portfolio | Verdict | Rules failed, with the measured value |
|---|---|---|
| Benchmark 60/40 | FAIL: M6, M7 | 95% loss estimate 12.88% (limit 10%); worst 12 months −17.37% (limit −10%) |
| Equal weight | FAIL: M5, M7 | return estimate 4.82% (objective 6.5%); worst 12 months −13.36% |
| Inverse volatility | FAIL: M5 | return estimate 3.65% |
| Constrained portfolio | PASS | none: reserve 65%, equity 35%, return 6.54%, 95% loss estimate 2.16%, worst 12 months −5.33% |

Each rule has a test that fails it alone and checks the verdict names it
(`test_verdict_names_each_failed_rule`), and a test that a value exactly on a limit passes. A
test also checks that the limits in `docs/mandate.md` and in `client_mandate.py` are the same.

## 5. Point-in-time and leakage

- **Publication lag.** DGS10 for day *t* is published on *t*+1. At each month's last close the
  rule uses the second-to-last trading day's value. The ALFRED vintage "as known on 2026-09-30"
  ends on 2026-09-29, the same value the rule uses.
- **Revisions.** 0 of the 1,268 dates shared by the vintage and today's download differ.
- **Check against the source.** 2026-10-01 = 5.24, 2026-10-15 = 5.10, 2026-10-28 = 5.05 in the
  FRED CSV, matching the Lab 17 readings.
- **The leak, shown as a leak.** With lag 0 the rule uses the month's own yield change: holdout
  net 16.38% against 2.12% for the honest rule. The app labels it a leak.
- **Rule frozen first.** `rule-card-dgs10.md` and `signal_rule.py` were committed in `42b8b8a`
  (2026-11-23 09:25 −0600) after being run only on made-up data. The first run on real data came
  after that commit, and the result was recorded in `b87e553`.
- **The older training rule.** `rule-card.md` was committed after `backtest.py` was written, so
  its commit time does not prove that rule came first. It is not part of this decision.
- **Prices.** A month-end close is known at the close. The October 2026 row is a partial month
  and is excluded from the base case.

## 6. Holdout and placebo

| Period | Months | Rule gross | Rule net | Hold IEF | Hold BIL | Switches |
|---|---:|---:|---:|---:|---:|---:|
| Development, 2021-12 to 2024-12 | 37 | −3.33% | −5.16% | −13.08% | 11.95% | 19 |
| Holdout, 2025-01 to 2026-09 | 21 | 3.25% | 2.12% | 3.02% | 6.92% | 11 |

The holdout was run once. Failure rule: triggered, by 0.91 points. Placebo: 1,000 shuffles of
the signal (seed 43900) give a median holdout net of 4.10%, and 69.4% of them do at least as
well as the real signal. At a cost of 0.00% the rule would be ahead (3.25% against 3.02%); at
0.25% it is further behind (0.44%). So the verdict rests on the cost assumption, which is why
cost is the input chosen for the Locked Changed-Input Record. Lag 2 gave a better holdout number
in the app's sensitivity panel; it was not adopted, because picking a lag after seeing the
holdout is tuning.

Out-of-sample test of the portfolio itself: estimated on 2021-12 to 2024-11, the search chose
60 / 0 / 0 / 40 / 0; held over 2024-12 to 2026-09 it returned 8.19% a year at 5.15% volatility
with a largest drawdown of −2.78%. Benchmark: 10.30%, 8.18%, −4.46%. Equal weight: 8.22%, 5.91%,
−3.40%. Inverse volatility: 4.44%, 1.01%, −0.35%.

## 7. Stress run

Twenty-two reruns of the search, each with one thing changed; the full table is in the decision
report.

| Group | What moved | Result |
|---|---|---|
| Estimates | Each fund's return ±1 point | Largest move 15 points (BIL −1 point: 60 / 0 / 0 / 35 / 5). IEF and LQD estimates never matter |
| Window | Last 36 months; first 36; partial October included | 85 / 0 / 0 / 5 / 10; 60 / 0 / 0 / 40 / 0; 65 / 0 / 0 / 30 / 5 |
| Costs | Yearly cost drag of 0.10% and 0.25% | Equity stays 35%; the split between VTI and VXUS moves |
| Constraints | Objective 6.0% and 7.0%; reserve 10%; equity cap 50%; loss limit 5% and 15% | Equity 30% to 40%; at a 5% loss limit no mix passes |

Range across the feasible runs: BIL 60% to 85%, VTI 5% to 40%, VXUS 0% to 25%, total equity 15%
to 40%. Named scenarios on the target weights: 2022 replay −5.33%; a hypothetical 30% equity
fall −10.50% (past the limit); stock-bond correlation at +0.80 leaves the 95% loss estimate at
2.16%, because the portfolio holds no bonds.

**Finer grid (cross-check on the search).** In 2.5-point steps the search gives 67.5 / 0 / 0 /
30 / 2.5 at 5.18% volatility, against 5.29% on the 5-point grid. The grid costs about a tenth of
a point of risk, but the split between VTI and VXUS moves 12.5 points. The two equity funds are
close substitutes (correlation 0.80), so the memo gives a range for total equity and does not
defend the split.

**Estimation error (bootstrap).** The 58 months were resampled with replacement 300 times
(seed 43900) and the search rerun on each. A passing mix was found in 227 of them; in 24.3% no
mix passed. Across the feasible resamples, from the 5th to the 95th percentile: BIL 50% to 85%
(median 75%), total equity 15% to 50% (median 25%). This is wider than the stress-run range and
is the strongest single reason the decision is a pilot.

**Stop conditions, evaluated on 2026-09-30.** STOP-1 (no mix passes): not fired. STOP-2
(trailing 12-month return below −10%): not fired, +8.30%. GATE-1 (no weight moves more than 10
points): fired, 20 points. GATE-2 (every stress run feasible): fired. Signal failure rule: fired.
Status: pilot.

## 8. Limitations, and what each one does to the decision

| Limitation | Effect on the decision |
|---|---|
| 58 months of history that include one rate shock; bond estimates are negative | Pilot, not adopt; adoption gate GATE-1 |
| Estimates are past averages; BIL's depends on recent short rates | Trigger: BIL estimate below 2.73% forces a re-run |
| The 95% loss estimate assumes normal returns | M7 history replay is required as well; trigger on the 2022 replay |
| A 30% equity fall costs 10.50% at target weights | Equity capped at 40% in the range; stop condition STOP-2 |
| The loss limit's meaning is the client's to settle | Committee ask 2; GATE-2 stays fired until it is answered |
| Prices copied by hand; Adj Close is restated over time | File hash in the output; the data card says a fresh download will differ in level |
| 5-point grid | Weights are reported as multiples of 5 and the range is wider than one step |
| One signal tested once | The signal is rejected, not the idea; a new rule needs a new rule card and new data |
| The mandate numbers were proposed by AI | Reviewed and approved by the student on 2026-11-23; the stress run shows what moving each limit does |

### Model risk, under the three headings from the Week 12 reading

- **Conceptual soundness.** The method fits its purpose, which is to find a low-risk mix that
  respects a written mandate, and it is simple enough to explain line by line. Its weak point is
  the input: five-year average returns stand in for expected returns, and the search treats them
  as exact. The process does not forecast and should not be read as if it did.
- **Outcome analysis.** Known answers match (section 3). Out of sample the portfolio met the
  objective with less risk than the baselines but less return than the benchmark (section 6).
  The signal failed its holdout and a placebo. The bootstrap finds no passing mix in 24.3% of
  resamples. On this evidence the process may be piloted and may not be adopted.
- **Ongoing monitoring.** Six triggers and four stop or gate conditions are evaluated in the app
  and in the decision report, each with its current value. They are reviewed every quarter. The
  owner is the analyst; the committee decides on any stop.

## 9. Named AI uses

Tool: **Claude Code** (Anthropic), model **Claude Fable 5.2** (`claude-fable-5-2`). Interaction
date for the Project 2 build: **2026-11-23**. The earlier lab files were also built with AI
help, as each one states; _the student adds the tool and dates for those_. The commit
history from `4db960e` onward is the trace of the build session.

| # | Task given to the AI | Disposition | Independent check | Resulting decision |
|---|---|---|---|---|
| 1 | Write the mandate rules and the constrained search | Accept | Brute force over all 10,626 mixes finds no passing mix with lower volatility; each rule failed alone in a test; the volatility formula checked by hand (10.46%) | The constrained portfolio is the decision number |
| 2 | Propose the client's mandate numbers | Accept (approved by the student, 2026-11-23, without change) | Each number has a stated reason in `docs/mandate.md`; the stress run moves each limit | The proposed numbers are the mandate |
| 3 | Build and test the DGS10 signal | Accept the result, **reject the signal** | Rule card committed before the run; three values against the FRED CSV; ALFRED vintage shows 0 revisions; placebo | Signal rejected |
| 4 | Report the bridge from benchmark to portfolio | **Corrected** | The report's total (−6.55) disagreed with the app's (−6.54) and with 5.29 − 11.83. The AI had added rounded rows. Fixed to round the exact sum | Report and app now agree; a test checks the bridge adds up |
| 5 | Handle the partial October row | Modify | The Lab 15 answer (65 / 0 / 0 / 30 / 5) included it. Both versions are computed and shown | Base case excludes it; as-of date is 2026-09-30 |
| 6 | Sensitivity of the signal to its lag | **Reject** the better-looking lag 2 | Choosing a parameter after seeing the holdout is tuning | The frozen lag of 1 stands and the rule fails |
| 7 | Draft the README, memo, this record and the video scripts | The student wrote the two statements in their own words on 2026-11-23 (AI tidied spelling only); other edits pending | `tests/test_consistency.py` compares every quoted number with `output/decision-numbers.json` | Documents agree with the output |

**One AI output I checked independently** _(the student redoes this by hand for Video 1)_:
the worst twelve months of the target portfolio. By calculator, from the 2022 fund returns in
the decision report: 0.65 × 1.4 + 0.20 × (−19.5) + 0.15 × (−16.1) = −5.4%. The app says −5.33%.
The small gap is monthly rebalancing against a single yearly sum. The check passes.

## 10. Locked Changed-Input Record

> **Note from the build session (not part of the record).** The prediction below was drafted in
> commit `33319b3`, before the decision signal moved from the training rule in `backtest.py` to
> the DGS10 rule in `signal_rule.py`. `backtest.py` is unchanged, so the prediction can still be
> run as written. The student kept the prediction as drafted and ran `backtest.py`, so this
> record tests the training rule and not the DGS10 rule the decision rests on. No AI session
> has run either file at 0.50%, and the committed output stops at 0.25%. The student ran the
> changed input and wrote the last two rows; the output row is the script's printed output.

| Field | Entry |
|---|---|
| Input changed | Trading cost per switch (`COST` in `backtest.py`) |
| Old value (units) | 0.10% per switch |
| New value (units) | 0.50% per switch |
| Expected direction of the output | Cost changes only the gap between gross and net. Gross returns and switch counts stay the same, because the position depends only on the signal. Net falls in both periods, more in the holdout, because it has 6 switches against 4. Holdout net goes further below −6.09%. Buy-and-hold has no switches, so it stays at −2.09%. |
| Expected decision effect | As the rule is already triggered in our baseline model, it will be triggered regardless. Decision: no change; a higher cost strengthens the case to stop. |
| Prediction commit (link and time) | <https://github.com/Jesstran12/Portfolio-Project2-/commit/33319b3>, 2026-11-23 09:03 −0600 |
| Actual output, before → after | Run by the student with `python3 backtest.py`, changing only `COST`. **Before (0.10%):** development gross 6.55, net 6.13, buy-and-hold 5.33, 4 switches; holdout gross −5.52, net −6.09, buy-and-hold −2.09, 6 switches; failure rule TRIGGERED (4.00 points). **After (0.50%):** development gross 6.55, net 4.46, buy-and-hold 5.33, 4 switches; holdout gross −5.52, net −8.35, buy-and-hold −2.09, 6 switches; failure rule TRIGGERED (6.26 points). Development net 6.13 → 4.46; holdout net −6.09 → −8.35. `COST` was set back to 0.10 after the run. |
| Decision changes? | No. The failure rule was triggered before and is still triggered after. The holdout shortfall against buy-and-hold widened from 4.00 to 6.26 points, so the case to stop is stronger. |
| Why it matched, or not; or why nothing changed | Every part of the prediction matched. Gross returns (6.55 and −5.52) and switch counts (4 and 6) did not move, because cost is taken off after the position is chosen. Net fell in both periods, by 1.67 points in development and 2.26 in the holdout; the holdout fell more because it has 6 switches against 4. Buy-and-hold stayed at −2.09 because it never switches. The rule stayed triggered. One thing the prediction did not mention: at 0.50% the development net (4.46) also falls below buy-and-hold (5.33), so the rule now loses in the period it was built on as well. |

## 11. Cold run

### AI cold run, 2026-11-23

Run by the AI assistant, not by a person. Commit `20df385` was cloned into an empty folder and
only the README's commands were used.

| Field | Entry |
|---|---|
| Command | `python3 -m venv .venv`, `source .venv/bin/activate`, `pip install -r requirements.txt`, `python3 make_output.py`, then `python3 -m pytest -q` and `python3 -m streamlit run app.py` |
| First failure | None |
| Elapsed time | 33 seconds from clone to the app answering, on a machine with a warm pip cache |
| Where the result is | Printed by `make_output.py` ("constrained portfolio 65 / 0 / 0 / 20 / 15, return estimate 6.54%, volatility 5.29%, verdict PASS"), and in `output/decision-report.md`. `git status` was clean afterwards, so the regenerated output is identical to the committed output. 34 tests passed. The app's health check returned 200 |
| Fix pushed (commit), or "clean, no fix needed" | Clean, no fix needed |

What this run does not show: it was on the author's own machine (macOS, Python 3.14.3), and the
clone was taken from the local repository, not from GitHub. It is weaker evidence than a
stranger's run.

### Machine cold run (GitHub Actions), 2026-11-23

A second cold run that nobody coached: on every push, `.github/workflows/ci.yml` starts a clean
Ubuntu machine with Python 3.14, installs `requirements.txt`, runs the tests, runs
`python make_output.py` and fails if `output/` differs from what is committed.

| Field | Entry |
|---|---|
| Command | The workflow's four steps, on commit `ede12fe` |
| First failure | None |
| Elapsed time | 1 minute 10 seconds |
| Where the result is | <https://github.com/Jesstran12/Portfolio-Project2-/actions/runs/45212099828>; the badge at the top of the README shows the latest run |
| Fix pushed (commit), or "clean, no fix needed" | Clean, no fix needed |

This run was on a different operating system from the author's machine and cloned from GitHub,
which covers the two gaps in the AI cold run above.

### Partner cold run

_The student fills this in if a partner runs it._

| Field | Entry |
|---|---|
| Command | |
| First failure | |
| Elapsed time | |
| Where the result is | |
| Fix pushed (commit), or "clean, no fix needed" | |
