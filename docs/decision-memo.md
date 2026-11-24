# Decision memo: Riverbend Scholarship Reserve

**To:** the Investment Committee · **From:** the portfolio analyst · **Date:** 2026-11-23 ·
**Data as of:** 2026-09-30

> **AI announcement.** I used Claude Code (Anthropic, model Claude Fable 5.2) to help me build
> this project. Claude wrote most of the code and the tests, drafted the documents, and proposed
> the mandate numbers. I chose the funds, downloaded the prices, wrote the changed-input
> prediction with AI closed, checked the AI's output, and made the decision. The analysis and
> the decision are mine.
>
> **Education, not investment advice.** This is a FIN 43900 course project on a hypothetical
> client, and nothing in it is a recommendation to buy or sell.

## Decision

**Pilot the constrained portfolio for twelve months. Do not adopt it as standing policy yet.
Reject the DGS10 timing signal.**

- **Target:** BIL 65 / IEF 0 / LQD 0 / VTI 20 / VXUS 15. Return estimate 6.54% a year,
  volatility 5.29%. It passes all seven mandate rules.
- **Allocation range:** equity (VTI + VXUS) **15% to 40%**; Treasury bills (BIL) **60% to 85%**.
  The range is the spread of answers across 22 stress runs, not a number I chose.
- **Condition:** the pilot runs with a quarterly review of the estimates, verdicts and triggers.
- **Reversal:** stop if either stop condition fires; adopt once both adoption gates clear (below).

The client is a $5 million reserve paying out 4% a year, with a horizon of five years or longer
and a yearly rebalance. The mandate is long-only, with a 6.5% return objective, at least 4% in
Treasuries, at most 70% in equity, and a 10% limit on twelve-month losses
([mandate.md](mandate.md)). Project 2 has no Edition A or B; the commit history shows how the
work changed.

## What the analysis changes

| Question | Without this analysis | With it |
|---|---|---|
| Is the 60/40 benchmark safe to hold? | Yes, it is the default | No. It fails the client's own loss limit twice: 95% loss estimate 12.88%, and −17.37% in the worst twelve months |
| What should we hold? | One optimizer answer | A range. The answer moves 20 points when the window changes, so a single point would be false precision |
| Should we time bonds with the 10-year yield? | The rule looked reasonable | No. It trailed buy-and-hold on data it had never seen |

## Evidence

**The portfolio.** Estimates use 58 monthly returns, December 2021 to September 2026.

| Portfolio | BIL / IEF / LQD / VTI / VXUS | Return est. | Volatility | 95% loss est. | Worst 12 months | Verdict |
|---|---|---:|---:|---:|---:|---|
| Benchmark 60/40 | 0 / 20 / 20 / 40 / 20 | 6.57% | 11.83% | 12.88% | −17.37% | FAIL: M6, M7 |
| Equal weight | 20 / 20 / 20 / 20 / 20 | 4.82% | 8.91% | 9.84% | −13.36% | FAIL: M5, M7 |
| Inverse volatility | 86 / 5 / 4 / 3 / 3 | 3.65% | 1.62% | −0.98% | −1.29% | FAIL: M5 |
| **Constrained** | **65 / 0 / 0 / 20 / 15** | **6.54%** | **5.29%** | **2.16%** | **−5.33%** | **PASS** |

The constrained portfolio earns almost the benchmark's return estimate with less than half its
volatility, because in this sample bond funds lost money and Treasury bills did not. Moving
from the benchmark means trading 65% of the portfolio once, at a cost of about 0.13%.

**Out of sample.** Estimated on the first 36 months and then held for the last 22 without
change, the process's portfolio returned 8.19% a year at 5.15% volatility. The benchmark
returned more (10.30%) at 8.18% volatility; equal weight returned 8.22% at 5.91%. The process
delivered what it promises, lower risk while meeting 6.5%, but it did not beat the baselines on
return.

**The signal.** The rule (hold IEF next month if the 10-year yield fell this month, otherwise
BIL) was frozen and committed before it was run. In the 21-month holdout it earned 3.25% before
costs and 2.12% after, against 3.02% for simply holding IEF. Its failure rule is triggered by
0.91 points. Shuffled signals did at least as well 69.4% of the time. It is rejected.

## Assumptions and sensitivities

- **Return estimates are five-year averages.** A one-point cut to BIL's estimate moves 15 points
  into US equity; the last 36 months alone give 85% bills.
- **Estimation error.** Resampling the 58 months 300 times puts equity between 15% and 50%, and
  in 24.3% of resamples no portfolio passes. This is the main reason for a pilot.
- **The loss limit means 10%.** At 5% no portfolio in this universe reaches 6.5%.
- **The partial October row is excluded.** Including it keeps equity at 35% but moves 10 points
  from VXUS to VTI.
- **Costs.** 0.10% of value traded. A yearly cost drag of 0.25% keeps equity at 35%.

## Risks, failure conditions and triggers

| Risk or limitation | What I monitor | Now | Action if it fires |
|---|---|---|---|
| Loss beyond the client's tolerance | Trailing 12-month return below −10% (STOP-2) | +8.30% | **Stop**: move to bills and return to the committee |
| The mandate cannot be met | No mix passes all seven rules at a quarterly review (STOP-1) | A mix passes | **Stop** |
| Unstable answer; short, unusual history | Any weight moving more than 10 points in the stress run (GATE-1) | 20 points | Stay in pilot; **adopt** only when this clears |
| The loss limit is unsettled | A stress run with no passing mix (GATE-2) | Fails at a 5% limit | Client answers the question below |
| Bill yields fall | BIL return estimate below 2.73% | 3.73% | Re-run; expect equity near the top of the range |
| Equity shock: a 30% fall costs 10.50% at target weights | Equity above 40% or below 15% | 35% | Rebalance into the range |
| Normal-distribution loss estimate understates bad years | 2022 replay on current weights | −5.33% | Review if below −8% |
| Trading costs | Yearly rebalance turnover above 25% | 4.1% at most | Review the rebalancing rule |
| The signal | Holdout net trails buy-and-hold | Trails by 0.91 | Stays rejected; a new rule needs new data |

## Action requested

1. Approve a twelve-month pilot at the target weights, inside the range above.
2. Answer: is the 10% loss limit a line never to be crossed, or a one-year-in-twenty loss? If
   it should be 5%, the 6.5% objective has to give way.
3. Note that the 60/40 benchmark fails the loss limit, and decide whether it stays the yardstick.
4. Confirm that the DGS10 signal is not used.

Every number here comes from [output/decision-numbers.json](../output/decision-numbers.json) and
is shown in [output/decision-report.md](../output/decision-report.md). Tests, limitations and the
record of AI use are in [validation-and-ai-use.md](validation-and-ai-use.md).
