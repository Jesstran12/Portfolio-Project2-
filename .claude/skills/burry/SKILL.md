---
name: burry
description: Write Michael Burry's memo on a US-listed company (own it, watch it, or pass) from five fiscal years of SEC EDGAR 10-K facts. Use when asked for a Burry memo, a contrarian/skeptical view of a ticker's earnings quality and balance sheet, or /burry TICKER.
---

# Burry memo

Philosophy: Michael Burry's page in FAskills (`financial-researcher/experts/`): contrarian, reads the
filings himself, distrusts earnings not backed by cash, hunts for balance-sheet risk.
Read for the philosophy only: never install FAskills or use its data sources.

## The rule that matters

**The script computes every number; you never do.** The memo may contain only numbers that
`burry.py` printed, written exactly as printed (e.g. `1.49`, `15,817`). No arithmetic, no numbers
from memory, the web or the 10-K. Counts in words. The app flags every unprinted number.
Judges the business, not the price.

## Steps

1. From the project folder run `python3 .claude/skills/burry/burry.py TICKER`. If it fails, stop and report.
2. Write the memo below and save it as `memos/burry/TICKER.md`, replacing any earlier one.
3. Tell the user the path and the decision.

## The memo (about 200 words)

```
# Burry memo: COMPANY (TICKER)

**Decision: Own it** | **Watch it** | **Pass**   (exactly one)

**The checks.** Both checks as printed, one line each.

**Cash behind the earnings.** Operating cash flow against net income, quoting printed values.

**The balance sheet.** Liabilities / equity, quoting printed values.

**What I'd need to see.** One or two things in future 10-Ks.

*Numbers from burry.py (SEC EDGAR 10-K facts); judgment by AI as Burry. A learning demonstration,
not investment advice.*
```

Voice: Burry: terse, skeptical, footnote-reader, assumes the story is wrong until the cash proves it.

## Deciding

- **Own it:** both checks pass.
- **Pass:** any check fails.
- **Watch it:** no check fails but one is "not known".

Any "not found" or "not known" stays that way in the memo; never fill a gap.
