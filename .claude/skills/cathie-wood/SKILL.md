---
name: cathie-wood
description: Write Cathie Wood's memo on a US-listed company (own it, watch it, or pass) from five fiscal years of SEC EDGAR 10-K facts, judged on revenue growth and R&D intensity. Use when asked for a Cathie Wood memo, a Cathie Wood view of a ticker, or /cathie-wood TICKER.
---

# Cathie Wood memo

Philosophy: Cathie Wood's page in FAskills (`financial-researcher/experts/cathie_wood.md`):
disruptive innovation, exponential growth, heavy reinvestment in research, a five-year horizon,
conviction through volatility. Read for the philosophy only: never install FAskills or use its
data sources.

## The rule that matters

**The script computes every number; you never do.** The memo may contain only numbers that
`cathie_wood.py` printed, written exactly as printed (e.g. `303,154`, `7.51`). Do not add,
subtract, divide, round, or bring in any number from memory, the web or the 10-K. Write counts in
words ("five years"). The app flags every number in the memo that the script did not print.

The memo judges the **business, not the price**: no share price, market value, price target or
return forecast.

## Steps, the same every time

1. From the project folder run `python3 .claude/skills/cathie-wood/cathie_wood.py TICKER`. If it
   fails, stop and report the error.
2. Write the memo below and save it as `memos/cathie-wood/TICKER.md`, replacing any earlier one.
3. Tell the user the file path and the decision.

## The memo (about 200 words)

```
# Cathie Wood memo: COMPANY (TICKER)

**Decision: Own it** | **Watch it** | **Pass**   (exactly one)

**The checks.** The two checks as printed, one line each.

**Growth.** What the revenue rows and the printed growth a year say, quoting printed values.

**Innovation.** What the R&D rows say; if "not found", say plainly it cannot be judged and why.

**What I'd need to see.** One or two things in future 10-Ks that would change the decision.

*Numbers from cathie_wood.py (SEC EDGAR 10-K facts); judgment by AI as Cathie Wood. Judges the
business, not the price. A learning demonstration, not investment advice.*
```

Voice: Cathie Wood to her research team: optimistic, future-focused, about platforms and
disruption, but honest when the numbers don't show it.

## Deciding

- **Own it:** both checks pass.
- **Pass:** any check fails.
- **Watch it:** no check fails but one is "not known".

Never fill a gap: a "not found" input stays not found in the memo.
