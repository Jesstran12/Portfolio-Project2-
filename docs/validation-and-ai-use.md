# Validation and AI use

> **AI announcement.** _(your own words)_
>
> **Education, not investment advice.** _(your own words)_

## Known-answer and baseline checks

## Mandate check

## Point-in-time and leakage

Note: the rule card (`rule-card.md`) was committed after `backtest.py` was written, so its commit
time does not prove the rule came first. _(Keep, edit or replace with your Lab 18 commit link.)_

## Holdout and placebo

## Stress run

## Locked Changed-Input Record

| Field | Entry |
|---|---|
| Input changed | Trading cost per switch (`COST` in `backtest.py`) |
| Old value (units) | 0.10% per switch |
| New value (units) | 0.50% per switch |
| Expected direction of the output | Cost changes only the gap between gross and net. Gross returns and switch counts stay the same, because the position depends only on the signal. Net falls in both periods, more in the holdout, because it has 6 switches against 4. Holdout net goes further below −6.09%. Buy-and-hold has no switches, so it stays at −2.09%. |
| Expected decision effect | As the rule is already triggered in our baseline model, it will be triggered regardless. Decision: no change; a higher cost strengthens the case to stop. |
| Prediction commit (link and time) | |
| Actual output, before → after | |
| Decision changes? | |
| Why it matched, or not; or why nothing changed | |

## Cold run (partner)

| Field | Entry |
|---|---|
| Command | |
| First failure | |
| Elapsed time | |
| Where the result is | |
| Fix pushed (commit), or "clean, no fix needed" | |

## One AI output I checked independently
