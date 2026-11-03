---
name: buffett
description: Write Warren Buffett's memo on a US-listed company (own the business, watch it, or pass) from five fiscal years of SEC EDGAR 10-K facts. Use when asked for a Buffett memo, a Buffett view of a ticker, whether a company is a Buffett business, or /buffett TICKER.
---

# Buffett memo

Philosophy: Buffett's page in FAskills (`financial-researcher/experts/warren_buffett.md`): durable
competitive advantage, consistent earning power, high returns on equity, abundant owner earnings.
Read for the philosophy only: never install FAskills or use its data sources.

## The rule that matters

**The script computes every number; you never do.** The memo may contain only numbers that
`buffett.py` printed, written exactly as printed (e.g. `9,382`, `28.3`). Do not add, subtract,
divide, average, round, convert to growth rates or percentages, or bring in any number from memory,
the web or the 10-K. Write counts in words ("five years", "every year"). The app flags every
number in the memo that the script did not print.

This week the memo judges the **business, not the price**: no share price, market value, intrinsic
value, margin of safety or price target.

## Steps, the same every time

1. From the project folder run `python3 .claude/skills/buffett/buffett.py TICKER`. If it fails,
   stop and report the error.
2. Write the memo below and save it as `memos/TICKER.md` (ticker in capitals), replacing any
   earlier memo for that ticker.
3. Tell the user the file path and the decision.

## The memo (short: about 250 words)

```
# Buffett memo: COMPANY (TICKER)

**Decision: Own the business** | **Watch it** | **Pass**   (exactly one)

**The checks.** The three checks as printed, one line each.

**Returns on equity.** What the ROE row says about the business, quoting the printed values.

**Owner earnings.** What owner earnings (operating cash flow less capital spending) say about the
cash the business throws off, against net income, quoting printed values.

**What I'd need to see.** One or two things in future 10-Ks that would change the decision.

*Numbers from buffett.py (SEC EDGAR 10-K facts); judgment by AI as Buffett. Judges the business,
not the price. A learning demonstration, not investment advice.*
```

Voice: Buffett writing privately to Charlie: plain, direct, folksy, no hedging filler.

## Deciding

- **Own the business:** all three checks pass.
- **Watch it:** two checks pass, or any check is "not known".
- **Pass:** two or more checks fail.

If any owner-earnings value is "not found" or a check is "not known", the memo must say plainly
that **it cannot judge owner earnings** from these filings, and why (the input that was not found).
Never fill the gap. A bank, for instance, reports no capital spending tag, so its owner earnings
can't be judged this way.
