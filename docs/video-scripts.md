# Video scripts and timestamp indexes

Drafted by the AI assistant for the student to rehearse and change. Say the lines in your own
words. The times are targets with 10 to 15 seconds of slack, because graders stop watching at
the limit. Each video answers one question and does not repeat the others. Every number is from
[output/decision-numbers.json](../output/decision-numbers.json).

Recording rules: YouTube links, Unlisted or Public (never Private), captions on, small webcam
view in a corner, clear audio, 720p or better.

## Where each requirement is shown

| Requirement | Video 1 | Video 2 | Video 3 |
|---|---|---|---|
| 1 The app runs | 0:50, 1:30 | 4:25 | 0:00 (live, opening) |
| 2 The mandate | 0:25 | 1:15 | 0:20, 0:50 |
| 3 Two baselines and the portfolio, each with a verdict | | 1:15 | 0:50, 1:25 |
| 4 Point-in-time signal and data card | 1:30 | 2:40 | 3:30 |
| 5 Stress run and stop condition | 0:50 | 3:45 | 1:55, 3:00, 3:55 |
| 6 Locked Changed-Input Record | | 3:55 | |
| 7 Recommendation, range, triggers | 2:35 | | 0:50, 1:55, 3:55 |
| 8 The two statements | 0:00 | 0:00 | 0:00 |

## Where the work beyond the base requirements is shown

| Addition | Where |
|---|---|
| A machine cold run on every push (GitHub Actions) and the README badge | Video 2, 3:10 |
| 37 automated tests: hand calculations, a brute-force check of the search, each rule failed alone | Video 2, 3:10 |
| One source of truth: a test fails if the memo or README quotes a number not in the output file | Video 2, 3:10 |
| DGS10 rule card and its failed holdout (`rule-card-dgs10.md`) | Video 1, 1:30 |
| Placebo run and the lag-0 leak shown as a leak | Video 3, 3:30 |
| Out-of-sample test of the portfolio itself | Video 3, 2:25 |
| Bootstrap of the estimates (300 resamples) | Video 2, 4:25; Video 3, 3:00 |
| Three named scenarios, including the 2022 replay | Video 3, 3:55 |
| Monitoring triggers evaluated live in the app | Video 3, 3:55 |
| An AI error caught and corrected (the bridge total) | Video 1, 2:00 |
| File hashes and a data card for every input, ALFRED revision check | Video 2, 0:45 and 2:40 |

## Set up before any recording

Run these once in a terminal with a large font, then leave the app running.

```
cd ~/Portfolio-Project2-
source .venv/bin/activate
git status                       # should say "nothing to commit, working tree clean"
python3 -m streamlit run app.py  # leave running; the app opens at http://localhost:8501
```

Open a second terminal tab for the commands in the videos:

```
cd ~/Portfolio-Project2-
source .venv/bin/activate
clear
```

Then prepare the app so nothing is slow on camera:

1. In the sidebar, change **M6 and M7 loss limit (%)** from 10 to 5, wait for the page, and
   change it back to 10. The result is cached, so the change is instant when you record.
2. On tab **3 Stress run**, tick **Run the estimation-error test (300 resamples, about 10
   seconds)** and wait for it. It stays cached too. Untick it again if you want to tick it live.
3. Set the browser zoom so a whole table fits on screen (about 110%).

Browser tabs to have open: the app, the repository on GitHub (README), the Actions page
(<https://github.com/Jesstran12/Portfolio-Project2-/actions>), and the prediction commit
(<https://github.com/Jesstran12/Portfolio-Project2-/commit/97aa33f>).

Editor files to have open for Video 2, in this order: `process.py`, `client_mandate.py`,
`signal_rule.py`. In VS Code, `code -g process.py:135` jumps to a line.

---

## Video 1: how the system and my thinking changed (limit 3:00, target 2:50)

**The one question:** what changed since my first mandate, and which AI output did I check?

Open beforehand: GitHub README, `lab-13-portfolio-mandate.md`, `lab-15-lowest-risk-mix.md`,
`docs/mandate.md`, `docs/validation-and-ai-use.md`, the app, a terminal, a calculator.

| Time | Show | Do or run | Say |
|---|---|---|---|
| 0:00 | README on GitHub, the AI announcement block at the top | Nothing; hold on the block | "I'm Jess. AI announcement: I used Claude Code, model Claude Fable 5.2, to help build this project. It wrote most of the code and tests and drafted the documents. I chose the funds, downloaded the prices, wrote my changed-input prediction with AI closed, checked its output, and the analysis and the decision are mine. This is education, not investment advice." |
| 0:25 | `lab-13-portfolio-mandate.md`, line 60 (Candidate D) and line 73 (the judgment) | Scroll from line 60 to 73, then switch to `docs/mandate.md`, "Risk measure and limits" | "I started in Lab 13 with a rule checker. A portfolio with 97% in equity passed every rule, because the client's 10% loss limit had no measure behind it. So in my own mandate the loss limit is measured two ways, as a one-year-in-twenty estimate and as a replay of history, and equity is capped at 70%." |
| 0:50 | `lab-15-lowest-risk-mix.md`, lines 55 to 56; then the app, tab **3 Stress run**, the first table | Point at "25 points", then click tab 3 and scroll down the 22 rows | "In Lab 15 the optimizer gave me one answer. Then moving one estimate by one point moved a quarter of the money. So I stopped trusting a single answer. The app now reruns the search 22 times with one input changed, and the spread of those answers is my allocation range: equity 15 to 40%." |
| 1:15 | `docs/mandate.md`, section "The partial October 2026 row" (line 87), the two-row table | Scroll to it | "I also corrected my own earlier result. My Lab 15 file ended with a half-finished October. I now exclude it, so the as-of date is September 30, and I show the answer both ways." |
| 1:30 | `rule-card-dgs10.md`, then the app, tab **4 Signal**, the red "Failure rule TRIGGERED" box | Show the rule card table for a few seconds; then click tab 4 | "The signal changed too. I had a data card for the 10-year Treasury yield, but I had tested a course training series. I rebuilt the rule on the real yield and wrote down its rule card: the rule, the lag, the cost and the failure rule. It failed its holdout: 2.12% after costs, against 3.02% for just holding the bond fund. So I reject it." |
| 2:00 | `docs/validation-and-ai-use.md`, section 9, row 4 and the paragraph under the table; a calculator beside it | Type on the calculator: `0.65 × 1.4 + 0.20 × −19.5 + 0.15 × −16.1` and show −5.405 | "The AI output I checked: the app says my portfolio's worst twelve months is minus 5.33%. By hand, with the 2022 fund returns: 65% times 1.4, plus 20% times minus 19.5, plus 15% times minus 16.1, gives minus 5.4. The small gap is monthly rebalancing, so I accepted it. I also caught an error: the AI added up rounded rows in the bridge table and was off by a hundredth. That was fixed, and a test now checks that the bridge adds up." |
| 2:35 | README, "The decision" table | Scroll to it and stop | "So my thinking moved from 'find the best portfolio' to 'find out how far I can trust the answer'. That is why my decision is pilot, not adopt." |

**Timestamp index for the manifest**

| Required element | Time |
|---|---|
| The two statements | 0:00 |
| How the system changed (mandate, range, as-of date, signal) | 0:25 to 2:00 |
| One AI output checked, with the check and the disposition | 2:00 |
| How my thinking changed | 2:35 |

---

## Video 2: code walkthrough (limit 5:00, target 4:45)

**The one question:** how does my code turn the data into the result, and which test passed or
failed? Stay in the code and the terminal; reading the README or showing only the app does not
count.

Open beforehand: README (Mermaid diagram), the three source files, the terminal (cleared), the
Actions page, `docs/validation-and-ai-use.md`, the app on tab 3 with the estimation-error test
already ticked.

| Time | Show | Do or run | Say |
|---|---|---|---|
| 0:00 | README, top | Hold on the AI announcement | "I'm Jess. I built this with Claude Code, which wrote most of the code. I checked it, and the analysis and the decision are mine. This is education, not investment advice." |
| 0:12 | README, the Mermaid diagram under "How it works" | Trace the arrows with the cursor, top to bottom | "The architecture. Two data files go in: monthly prices for five funds, and the daily 10-year Treasury yield from FRED. `portfolio.py` is the math engine. `client_mandate.py` is the mandate written as code. `process.py` is the pipeline: validate, estimate, search, stress. `signal_rule.py` is the signal. `app.py` only lays out the page and holds no math, and `make_output.py` writes the visible output." |
| 0:45 | `process.py` lines 50, 83, 89 and 98: `validate_rows`, `complete_rows`, `monthly_returns`, `estimate` | Scroll through the four functions; pause on `LAST_COMPLETE_MONTH` at line 26 | "The data flow. Prices are validated, so a bad file gives a plain message and not a traceback. The partial October row is dropped. Each monthly return is this month's price over last month's, minus one. The return estimate is the mean times 12, and volatility is the standard deviation times the square root of 12. The output prints a hash of each data file." |
| 1:15 | `client_mandate.py` lines 30 to 35 (`RULES`), 66 (`loss_estimate_95`), 51 (`worst_12_month_return`), 87 (`check`), 106 (`verdict`) | Scroll in that order | "The financial logic. The mandate is seven rules. The objective is the 4% payout plus 2.5% inflation. M6 is a one-year-in-twenty loss: 1.645 times volatility, minus the return. M7 replays the weights through every twelve-month window in the sample. `check` returns each rule with its measured value, and `verdict` names every rule that failed. The benchmark and both baselines go through the same function." |
| 1:50 | `process.py` line 135, `constrained_portfolio` | Go through it line by line with the cursor: the loop, the four `continue` tests, the sort, the final loop | "This function produces my decision number. It walks all 10,626 long-only mixes in 5-point steps. It drops a mix if the return misses the objective, if the reserve is too small, if equity is over the cap, or if the loss estimate is over the limit. It sorts the survivors by volatility. Then, lowest risk first, it returns the first one that also passes the history rule, which is the slow test, so it runs last. The answer is 65, 0, 0, 20, 15. If nothing passes it returns None, and the app reports a stop." |
| 2:40 | `signal_rule.py` line 41 (`known_at_month_end`) and line 89 (`run`) | Point at `obs[-2]` on line 51, then at `signal[source] < 0` and `r - cost if switched` in `run` | "The signal. A day's yield is published the next day, so at each month-end I take the second-to-last value. That is what makes it point-in-time. If the yield fell, hold the bond fund IEF next month, otherwise bills, and charge 0.10% for each switch. I compared the file with the ALFRED vintage, and no value was revised." |
| 3:10 | Terminal; then the Actions page while the tests run | Run: `python3 make_output.py && python3 -m pytest -q` (about 25 seconds; keep talking). Expected: the three printed lines ending "Wrote output/decision-report.md…", then `37 passed`. Switch to the Actions page and point at the green runs | "To reproduce: install the requirements and run one command. It prints the decision and rewrites the output folder. Then 37 tests. They include a volatility calculation done by hand, a brute-force check that no passing mix has lower risk, and a test that fails if my memo quotes a number that is not in the output file. GitHub reruns all of this on a clean machine on every push." |
| 3:45 | `docs/validation-and-ai-use.md`, section 1, row 1 of the claims table | Scroll to it | "My highest-risk claim is that the weights are stable enough to act on. The test aimed at it is the stress run, and the claim fails: on the last 36 months, bills move 20 points. That failed test is why I say pilot." |
| 3:55 | Same file, section 10 (the Locked record); then the terminal | Run: `git log -1 --format='%h %ad %s' 97aa33f` (shows 2026-11-17, six days before the result commit `e965644`). Run: `python3 backtest.py` (holdout net −6.09, TRIGGERED, 4.00 points). Run: `python3 -c "import backtest as b; r=b.run(cost=0.50); print(round(r['Development']['net'],2), round(r['Holdout']['net'],2), r['failure'])"` (expected `4.46 -8.35 True`) | "My changed-input test. With AI closed, I predicted what raising the trading cost from 0.10% to 0.50% would do, and committed it before any run. I predicted that gross returns and switches stay the same, net falls, and the decision does not change. Before: holdout net minus 6.09. After: minus 8.35, still triggered. The prediction matched. What I missed is that the rule now loses in development too. One caveat: this record is on the course training rule. For the yield rule, the report shows costs of 0, 0.10 and 0.25, and it fails once any cost is charged." |
| 4:25 | The app, tab **3 Stress run**, "Cross-checks on the search", the estimation-error result | Scroll to it (already ticked) | "One failure mode: estimation error. I resampled the monthly returns 300 times. In 24.3% of the resamples no portfolio passes the mandate at all, and equity ranges from 15 to 50%. When that happens the search returns nothing and the app says stop. It does not force an answer." |
| 4:40 | README, "Known limitations" | Scroll to it | "The other limitations are listed in the README. Thank you." |

Notes for this video:

- The `python3 -c` line runs the changed value without editing `backtest.py`, so `COST` stays
  at 0.10 and the tests keep passing. If you would rather edit the file on camera, change line
  19 to `COST = 0.50`, run `python3 backtest.py`, and change it back before you stop recording.
- You must be able to explain `constrained_portfolio` unaided. Rehearse that block most.

**Timestamp index for the manifest**

| Required element | Time |
|---|---|
| The two statements | 0:00 |
| Architecture | 0:12 |
| Data flow | 0:45 |
| Key functions and financial logic | 1:15 to 3:10 |
| How to reproduce | 3:10 |
| Validation test on the highest-risk claim | 3:45 |
| Locked Changed-Input test | 3:55 |
| One failure mode | 4:25 |

---

## Video 3: committee presentation (limit 5:00, target 4:45)

**The one question:** what should the committee do, under what conditions, and what reverses it?
Open with the app running live. Lead with the decision. Do not explain how the code works; that
is Video 2.

Open beforehand: the app on tab **1 Decision** with the sidebar visible and the loss limit at
10, and `docs/decision-memo.md` on GitHub in a second browser tab. No terminal is needed; the
app is already running from the setup section.

| Time | Show | Do or run | Say |
|---|---|---|---|
| 0:00 | **The app, live**, tab **1 Decision**; the blue "As of 2026-09-30" bar and the yellow "PILOT, not adopt" box | Nothing yet | "Good afternoon. I'm Jess, the analyst for the Riverbend Scholarship Reserve. Two statements first. I built this tool with Claude Code, and the analysis and the decision are mine. And this is education, not investment advice." |
| 0:20 | Sidebar, **M6 and M7 loss limit (%)** | Change 10 to 5: the status turns red, "Process status: STOP", and a what-if warning appears. Change it back to 10 | "This is the tool, running now. Every portfolio carries a verdict against your mandate. Watch what happens if I tighten your loss limit from 10% to 5%: no portfolio passes, and the process stops. I will come back to that." |
| 0:50 | Tab 1, the table "Three portfolios and the benchmark, each with its mandate verdict", last row | Point at the Constrained row | "My recommendation: pilot the constrained portfolio for twelve months. Do not adopt it as policy yet. And reject the yield timing signal. The target is 65% Treasury bills, 20% US equity, 15% international equity. As of September 30, its return estimate is 6.54% against your 6.5% objective, with volatility of 5.29%. It passes all seven of your rules." |
| 1:25 | Same table, the benchmark, equal weight and inverse volatility rows | Point at "FAIL: M6, M7" on the benchmark | "Why move at all? Your 60/40 benchmark fails your own loss limit. Its one-in-twenty loss estimate is 12.88%, and in 2022 it would have lost 17.37%. Equal weight and inverse volatility both miss the return objective. The constrained portfolio's worst twelve months was a loss of 5.33%." |
| 1:55 | Tab 1, "Allocation range: where the answer lands across the stress run" | Scroll down to it | "I am giving you a range, not a point: equity between 15 and 40%, bills between 60 and 85%. That range is where the answer landed across 22 stress tests. I did not choose it." |
| 2:25 | Tab **3 Stress run**, "Out-of-sample test of the portfolio" | Click tab 3 and scroll to it | "The evidence I trust most. I built the portfolio using only the first three years, then held it for the 22 months it had never seen. It returned 8.19% a year at 5.15% volatility. The benchmark returned more, 10.30%, with more risk. So this process lowers risk while meeting the objective. I do not claim it beats the benchmark." |
| 3:00 | Tab 3, the first table (the last-36-months row and "BIL return -1 point"), then the estimation-error result | Scroll up to the stress table, then down to the bootstrap | "Why only a pilot? If I estimate from the last three years alone, bills go to 85%, a 20-point move. The estimates assume bills keep paying about 3.7%; if that falls by one point, 15 points move into US equity. And when I resample the history 300 times, about a quarter of the time no portfolio passes at all." |
| 3:30 | Tab **4 Signal**: the "Locked" table, the red failure box, the placebo line | Click tab 4. Optional: set **Signal lag** to 0 in the sidebar to show the leak warning, then back to 1 | "The signal. The rule was fixed and committed before I tested it. On unseen data it made 2.12% after costs; holding the bond fund made 3.02%. Random signals did at least as well 69% of the time. I recommend we do not use it." |
| 3:55 | Tab 1, "Monitoring triggers, evaluated now" and "Stop conditions and adoption gates, evaluated now"; then tab 3, "Named scenarios on fixed weights" | Click tab 1 and scroll to the two tables; then tab 3, scenarios | "What I will monitor, with today's values on screen. I stop and come back to you if the portfolio loses more than 10% over twelve months, or if no portfolio passes your mandate at a quarterly review. Today it is up 8.30%. I move to adopt when no weight shifts more than 10 points in the stress tests; today that is 20. One risk to name plainly: a 30% fall in equities would cost this portfolio 10.5%, just past your limit." |
| 4:25 | `docs/decision-memo.md` on GitHub, "Action requested" | Switch browser tab | "My ask. One, approve the twelve-month pilot inside that range. Two, tell me whether 10% is a line never to cross or a one-year-in-twenty loss, because at 5% your 6.5% objective cannot be met. Three, decide whether 60/40 stays your yardstick. Thank you. I am glad to take questions." |

**Timestamp index for the manifest**

| Required element | Time |
|---|---|
| App running live (opening) | 0:00 to 0:50 |
| The two statements | 0:00 |
| The decision | 0:50 |
| Evidence and as-of date | 0:50 to 3:00 |
| Allocation range | 1:55 |
| Assumptions and sensitivities | 3:00 |
| Risks, conditions and triggers | 3:30 to 4:25 |
| Committee ask | 4:25 |

A sceptical question to rehearse: "Your portfolio holds no bonds at all. Isn't that just 2022
talking?" An honest answer: yes, in part. The estimates cannot tell a one-off shock from a
permanent change, which is why this is a pilot with a range and not a policy.

---

## After recording

1. Upload each video to YouTube as Unlisted, turn captions on, and open each link in a private
   window to confirm it plays while logged out.
2. Change the times in the three timestamp indexes above to match the real recordings.
3. Paste the auto-captions into a session to be corrected into `docs/transcript-video-1.txt`,
   `-2.txt` and `-3.txt` (tickers, finance terms, numbers).
4. Add the three URLs, titles and durations to [manifest.md](manifest.md), commit and push.
