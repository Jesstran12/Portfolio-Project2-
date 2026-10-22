# Lab 13: Portfolio Mandate Defense (Meridian Foundation Reserve)

**D: the question.** Which of these portfolios does the Meridian Foundation's mandate permit, and
what must the CIO answer before anyone optimizes?

**Short answer.** Of the three candidates, only **A** passes every rule that can be checked. B fails
three rules and C fails one. None of them can be called *suitable* until the CIO says how the 10%
calendar-year loss limit (S9) is measured, because that is the one statement that decides how
much equity the reserve can hold.

Files: [`mandate.py`](mandate.py) (the checker). Run it with `python mandate.py`.

## R: sorting S1–S10

| #   | Type | Reason |
| --- | ---- | ------ |
| S1  | Hard constraint | The time horizon and rebalancing schedule are fixed inputs: a 7-year horizon, rebalanced once a year. |
| S2  | Objective | CPI + 4% net, over rolling 5-year periods, is the return target. It is measured afterwards and cannot be checked as a limit on today's weights. |
| S3  | Hard constraint | $0.75M × 4 quarters = $3M = 3.0% of the reserve, held in cash or Treasuries. Checkable. |
| S4  | Objective | The 60/40 benchmark is the yardstick that performance and risk are judged against. It does not limit the weights. |
| S5  | Hard constraint | Long-only means no weight can be below zero. Checkable. |
| S6  | Hard constraint | No single company above 8%, with one company's securities counted together. Checkable. |
| S7  | Hard constraint | Turnover of at most 25% a year is checkable, but only between two portfolios. A single snapshot can't test it, so it is out of scope today. |
| S8  | Hard constraint | At least 90% must be redeemable within 5 business days. Checkable from the redemption days. |
| S9  | Unverifiable promise | "Cannot have a calendar-year loss greater than 10%" names no measure (VaR? worst historical year? stress test?) and no breach rule. No portfolio with equities can promise it, so it is reported, never tested. |
| S10 | Missing | There is no preference and no objective for the pilot to optimize. Before optimizing, someone has to say what is being maximized or minimized. |

## I: the checker

`mandate.py` uses only the standard library. Every input (holdings, candidates, reserve size,
distribution, quarters, window, liquid share, issuer limit) is an editable constant at the top,
and every value is computed from them. Treasuries, cash and diversified funds are exempt from the
issuer limit, and Acme's bonds and stock are added together.

## V: proof on the known answer

```
Reserve minimum: 4 x 0.75 / 100 = 3.0% of the portfolio

Candidate A                             B                  C
  Weights sum to 100        100.0 pass   100.0 pass         100.0 pass
  Long-only (lowest)          0.0 pass     0.0 pass           0.0 pass
  Reserve-eligible >= 3.0%   14.0 pass     1.0 FAIL           2.0 FAIL
  Redeemable 5d >= 90%      100.0 pass    85.0 FAIL         100.0 pass
  Largest company <= 8%       0.0 pass     9.0 FAIL (5+4)     8.0 pass
  Calendar-year loss        requires CIO clarification (all)
  Verdict                   passes every  fails 3 rule(s)   fails 1 rule(s)
                            checkable rule
```

Every value matches the lab's table. B's 9.0% is Acme bonds (5) plus Acme stock (4): neither
holding breaks the limit alone, but together they do.

**Probe.** In A, I set Cash to −2 and the global equity fund to 64, then reran. Lowest weight was
−2.0 → **FAIL** long-only. The reserve still passed at 10.0, nothing else failed, and the verdict
was "fails 1 rule(s)". I then set both weights back.

## E: attacking my own checker

**Candidate D** (from the AI): Cash 3, global equity fund 89, Acme Corp stock 8, everything else 0.

```
Candidate D
  Weights sum to 100                  100.0  pass
  Long-only (lowest weight)             0.0  pass
  Reserve-eligible >= 3.0%              3.0  pass
  Redeemable in 5 days >= 90%         100.0  pass
  Largest single company <= 8%          8.0  pass
  Calendar-year loss <= 10%                  requires CIO clarification
  Verdict: passes every checkable rule
```

**Judgment.** The objection holds. D puts 97% in equities against a 60/40 benchmark (S4), and in a
bad equity year such as 2008 or 2022 it would lose several times the 10% the CIO named. **S9
decides it**: D shows that the only rule protecting the client from this outcome is the one the
checker can't test. D also sits *exactly* on the reserve minimum and the issuer limit, so a small
market move would breach both. That is a monitoring problem the snapshot rules can't see.

**Partner swap (playing both roles).** If a colleague's D were an all-bond or all-cash portfolio
that passes every rule, I would cite **S2**: CPI + 4% net is very unlikely with near-zero equity,
so it passes the rules and fails the objective.

## Your question for the CIO

> **"When you say the reserve cannot lose more than 10% in a calendar year, do you mean it must
> never happen, even in a 2008-type year, or that it should be unlikely, say a 1-in-20-year
> event (95% one-year VaR ≤ 10%)? And what must we do if it is breached?"**

**The answer that changes the portfolio.** If it means *never*, even in a historical worst year,
equities must sit well below the 60% benchmark (a 60/40 portfolio lost roughly 15–20% in both
2008 and 2022). That probably makes CPI + 4% (S2) unreachable, so the CIO must choose which
statement gives way. If it means *1-in-20*, a portfolio near the 60/40 benchmark, like A, is
defensible, and S9 becomes a measurable risk limit that the optimizer can use as a constraint.

## Investment policy statement: learn on my own

1. **What it is.** An IPS is the written agreement between a client and the manager. It sets out
   what the money is for, the return and risk objectives, and the constraints the portfolio must
   respect. It is the standard every later decision is checked against.
2. **How it works.** In the CFA Institute framework, **objectives** (return and risk) say what the
   portfolio is trying to achieve. **Constraints** (liquidity, time horizon, legal/regulatory, tax,
   unique circumstances) limit how it may get there. Risk is split into *ability* and
   *willingness* to bear it, and each objective should be measurable.
3. **Mapping S1–S10.**

| IPS element | Statements |
| ----------- | ---------- |
| Return objective | S2 (CPI + 4% net, rolling 5 years); S4 as the benchmark |
| Risk objective | S9 (calendar-year loss: willingness stated, measure missing); S4 (benchmark risk) |
| Liquidity constraint | S3 (12-month payout reserve), S8 (90% in 5 days) |
| Time horizon | S1 (7 years, annual rebalancing) |
| Legal / regulatory / policy limits | S5 (long-only), S6 (8% issuer), S7 (25% turnover) |
| Tax | S10 (no tax preference stated) |
| Unique circumstances / preferences | S10 (no sector, ESG or home-bias preference; no optimization target) |

## Reflect

1. **Why a portfolio can pass every checkable rule and still be wrong for this client.** The
   checker tests only constraints I can measure on today's weights. The client's real goals are
   the return objective (S2) and the loss tolerance (S9), and neither can be checked on a snapshot.
   Candidate D proves it: it passes every rule while taking on far more risk than the client
   described. Passing means the portfolio is *permitted*. Being *suitable* also requires meeting
   the objectives.
2. **The type I was least sure of.** S4, the benchmark. It reads like a target allocation, which
   would make it a hard constraint, but the CIO never gave a tracking-error or deviation limit. I
   typed it as an objective (the yardstick) and not a rule. If the CIO added "stay within ±10% of
   the 60/40 weights", it would become a hard constraint, and that one rule would stop D.
