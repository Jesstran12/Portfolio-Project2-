# SPEC: Project 2 — Investment Management Application

Working spec for the implementation session. Compiled 2026-11-23 from this repository and the
course repository at `/Users/jesstran/FIN43900-Fall2026` (commit `bb73c5f`). Not a submission
file.

## Resume here

**Every session: read this section first, work the next unticked step, and update this section
before ending.** Step numbers refer to section 6.

**Last updated:** 2026-11-23, by the implementation session.
**Next step:** the student's step 12c, record and upload the three videos (12a and 12b done; 12c to 12e open). Tier 3 not started.

| Step | Owner | Done | Note |
|---|---|---|---|
| 1 Due date confirmed; section 4 decisions settled | Student + AI | [x] | Decisions settled on the recommended options (student instruction, 2026-11-23). Student confirmed the due date: 2026-11-23, 11:59 PM Eastern (10:59 PM Central). |
| 2 Environment; app starts | AI | [x] | `.venv` on Python 3.14.3, pinned `requirements.txt`; `streamlit run app.py` answered health check 200 |
| 3 Mandate written and encoded | AI, student approves | [x] | `docs/mandate.md`, `client_mandate.py` (rules M1 to M7), `process.py`, `tests/`. Base case excludes the partial October row: 65/0/0/20/15, 6.54%, 5.29%. Student approved the numbers on 2026-11-23. |
| 4 Baselines and verdicts in the app | AI | [x] | `app.py` rewritten: five tabs, benchmark + equal weight + inverse volatility + constrained portfolio, each with a worded verdict naming the failed rules; bridge, turnover, own-weights checker; `tests/test_app.py` |
| 5 Signal, rule card, data card | AI | [x] | `signal_rule.py`, `rule-card-dgs10.md` (committed in `e965644` with the result), `docs/data-cards.md`. Holdout net 2.12% against hold-IEF 3.02%: failure rule triggered, signal rejected. Placebo 69.4%. |
| 6 Stress run and stop condition | AI | [x] | Stress tab: 22 runs over estimates, window, costs, constraints; three named scenarios; out-of-sample test; STOP-1, STOP-2, GATE-1, GATE-2 evaluated (both gates fired, so pilot). `tests/test_stress.py` |
| 7 Visible output regenerated | AI | [x] | `python3 make_output.py` writes `output/decision-report.md`, `output/decision-numbers.json` and the lab outputs; five app screenshots in `output/screenshots/`; `tests/test_output.py` fails if the committed output is stale |
| 8 README | AI | [x] | Statements drafted (student rewords), decision frame, one command, Mermaid data flow, repository map, data sources, licensing, limitations |
| 9 Memo and validation record | AI | [x] | Memo and record written from `output/decision-numbers.json`; `tests/test_consistency.py` fails if a quoted number is not in that file. Locked table left exactly as drafted. |
| 10 Cold run from a fresh clone | AI | [x] | Clean: clone of the final code, README commands only, 33 s, 34 tests passed, regenerated output identical. Clone was local; the CI run on GitHub is the second cold run. |
| 11 Video scripts, timestamp index, manifest rows | AI | [x] | `docs/video-scripts.md` (three timed scripts with indexes), `docs/manifest.md` (rows and a pre-submission checklist) |
| F Full-marks additions, tier 1 (section 8) | AI | [x] | Built inside steps 3 to 11. Not done by AI: V7 partner run, V8 (step 12b), C4 transcripts (step 12d) |
| F Full-marks additions, tier 2 | AI | [x] | T6 CI workflow and badge (first run passed), F1 bootstrap, F2 finer-grid check, F3 monitoring triggers in the app, F4 model-risk section |
| F Full-marks additions, tier 3 | AI | [ ] | only if time remains |
| 12a Mandate and decision approved; statements reworded | Student | [x] | Mandate approved 2026-11-23. Student signed off on the decision (pilot the allocation, reject the signal) on 2026-11-23. Statements rewritten from the student's own wording on 2026-11-23 |
| 12b Changed-input run and write-up (AI closed) | Student | [x] | Student ran `backtest.py` at 0.10 and 0.50 on 2026-11-23; the before and after output is in the record and `COST` is back at 0.10. The student wrote "Decision changes?" and "Why it matched"; a session copied the two rows into the file word for word on 2026-11-23 |
| 12c Videos recorded and uploaded | Student | [ ] | |
| 12d Transcripts cleaned and committed | Student + AI | [ ] | |
| 12e Brightspace submission | Student | [ ] | |

**Decisions made** (section 4; fill in as they are settled):

| Decision | Choice |
|---|---|
| 1 Signal | DGS10 (recommended option): a frozen yield-trend rule on real fund returns, `signal_rule.py`, rule card committed before the backtest |
| 2 Mandate numbers | Proposed by AI in `docs/mandate.md`; **approved by the student on 2026-11-23**, no changes |
| 3 Second baseline | Inverse volatility (already coded); the 60/40 benchmark is shown beside it |
| 4 Recommendation | Pilot the allocation, reject the signal; **signed off by the student on 2026-11-23** |
| 5 One app | `app.py` is the product; the other three apps stay in place as lab files |

**Locked Changed-Input Record status:** prediction drafted in commit `97aa33f` (cost 0.10% →
0.50%); **run done by the student on 2026-11-23** (prediction kept on `backtest.py`); output row
filled, and the two written rows completed by the student. The record is closed. The rest of this note is history. No session may run that value or fill in the result. If step 5 changes the
model, note it here so the student rewrites the prediction by hand before the run.

**Step 5 changed the model (2026-11-23).** The decision signal is now the DGS10 rule in
`signal_rule.py`, which has its own `COST = 0.10`. The drafted prediction is about `COST` in
`backtest.py` (the course training rule) and quotes its numbers (−6.09%, −2.09%, 6 and 4
switches). `backtest.py` is unchanged, so that prediction can still be run as written, but it is
no longer on a load-bearing input. Recommended: the student rewrites the prediction by hand for
`COST` in `signal_rule.py` (0.10% → 0.50%), commits and pushes it, then runs
`python3 signal_rule.py` with the new value. Frozen values for that rewrite: holdout gross 3.25%,
net 2.12%, hold-IEF 3.02%, 11 holdout and 19 development switches. No AI session has run either
file at 0.50, and the committed stress output stops at 0.25.

**Open problems and things left mid-way:**

- **Pushed on 2026-11-23** (student instruction) through `e965644`; the first CI run passed in
  1m11s on Ubuntu, Python 3.14. A rewritten Locked prediction must still be committed and pushed
  before its run.
- **Locked Changed-Input:** see the note above. Decide whether to keep the drafted prediction
  (`backtest.py`) or rewrite it by hand for `signal_rule.py`.
- The two statements in the README, memo and validation record are now the student's wording
  (2026-11-23). The videos' opening lines in `docs/video-scripts.md` are still the AI's script.
- The memo is about 1,170 words with tables; trim if it prints past two pages.
- Not done: the Lab 15 partner placeholders, a partner cold run, tier 3. The duplicate
  `cathie-wood` skill and memo folders were removed on 2026-11-23 (student instruction).

How to update: tick the row, put the commit hash or a one-line result in Note, change "Last
updated" and "Next step", and record anything half-finished under open problems.

## 0. Read first

- **Deadline.** The syllabus lists Project 2 as due **Monday, November 23, 2026, 11:59 PM
  Eastern** (300 points). The Brightspace assignment header is the authority; confirm it there.
- **Late policy.** The first late project in the course loses 20% of the earned score per day or
  part of a day, up to four days; five days late earns zero. A second late project earns zero.
  Technical problems do not stop the clock.
- **Visible-output cap.** A submission without visible executed output earns at most 50%.
- **AI does everything it is allowed to** (section 5). The only AI-off work is the Locked
  Changed-Input prediction and its run: the implementation session must not run the changed
  input (`COST = 0.50`) or fill in its result. The student also records the videos and submits.
- **AI is otherwise open from day one.** Project 2 has no Edition A or B and no research-evolution
  file.

## 1. The assignment

Role: portfolio analyst. Build an investment management app a committee could adopt, and
recommend **adopt, allocate to, rebalance, pilot, or reject** the process under the mandate. An
honest reject of a failed process is fully responsive.

### Eight base requirements (all required)

| # | Requirement | Detail from the course pages |
|---|---|---|
| 1 | The app runs | A Python web app a stranger starts from the README and operates alone. A notebook or a one-shot script is not an app. |
| 2 | Your mandate | From Lab 13, for your own client: objective, universe, benchmark, risk measure and limits (plus the hard constraints and the one question for the client). |
| 3 | Two baselines and your portfolio | Equal weight, a second transparent baseline, and the constrained portfolio. Each shows its mandate verdict in the app: pass or fail, and which rule. |
| 4 | One point-in-time signal | With its data card: source and link, what it measures, units, publication lag, revisions, download date. |
| 5 | A stress run | On estimates, window, costs and constraints, plus the condition that stops the process. |
| 6 | One Locked Changed-Input Record | AI-off prediction committed to GitHub before the run, then the result. |
| 7 | A recommendation | With an allocation range and the triggers to monitor. |
| 8 | Two statements | Open the README, the memo and each video: which AI was used and for what, and that the analysis and decision are yours; education, not investment advice. |

### What to submit

| Item | Location and rules |
|---|---|
| GitHub repository | `git@github.com:Jesstran12/Portfolio-Project2-.git`. Public or private, but the instructional team must have access. |
| Decision memo | `docs/decision-memo.md` (Markdown, not PDF). Also attached to Brightspace. |
| Validation and AI use | `docs/validation-and-ai-use.md`, containing the Locked Changed-Input Record. Also attached to Brightspace. |
| Video 1 (≤ 3:00) | How the system and your thinking changed, and one AI output you checked. |
| Video 2 (≤ 5:00) | Code walkthrough: architecture, data flow, key functions, financial logic, how to reproduce; show the validation or changed-input test on the highest-risk claim; name one failure mode. Reading the README or showing only the UI is not enough. |
| Video 3 (≤ 5:00) | Committee presentation, **opening with the app running live**. Lead with the decision; defend range, evidence, assumptions, risks, triggers; end with a committee ask. |
| Transcripts | `docs/transcript-video-1.txt`, `-2.txt`, `-3.txt`, corrected for finance terms, tickers, names and material numbers. Attach them or link them in the repo. |
| Manifest (Brightspace) | Every location a GitHub link except the videos. Repo URL, three video URLs with titles and durations, a timestamp index of each video's required elements, access confirmation. Research-evolution row is marked not required. Deployment link is optional. |

Video rules: YouTube links, not files; Unlisted or Public, never Private; transcripts enabled;
small webcam view; clear audio; 720p or better. Graders stop at the time limit.

### Memo contents (`docs/decision-memo.md`)

Readable without any video, about two pages:

1. the two statements;
2. the decision and recommendation first;
3. an allocation range, not a single point;
4. the strongest supporting evidence and the as-of date;
5. material assumptions and sensitivities;
6. principal risks, failure conditions and monitoring triggers;
7. the action requested from the committee;
8. a pointer to the AI-use record in `docs/validation-and-ai-use.md`.

Every recommendation needs a condition, a reversal trigger and a committee ask.

### Validation record contents (`docs/validation-and-ai-use.md`)

- Sources and the as-of boundary; tests and results; limitations.
- Baseline check, mandate check, stress run, holdout result.
- Named AI uses: tool, model and version, interaction date, and for each load-bearing
  contribution: the task, accept / modify / reject with the reason, the independent check used,
  and the resulting decision.
- The Locked Changed-Input Record: input, old and new values with units, expected direction,
  expected decision effect, timestamp and commit of the prediction, before and after output,
  actual decision effect, and why it matched or not.
- The partner cold-run record (command, first failure, elapsed time, where the result is, fix).

### Repository requirements

- Runnable source and a dependency file.
- README: the two statements, the finance decision, the intended user, setup and **the one
  command that produces the result**, a repository map, data sources, known limitations.
- **Visible executed output**: a grader sees the material inputs, the as-of date and the decision
  numbers on GitHub without running anything.
- Memo, visible output, transcripts and validation record use the same numbers, dates and
  conditions.
- No keys, tokens, credentials, private data or `.env` committed. `.env.example` only if
  credentials are needed (currently none are).

### Grading (300 points, graded strictly)

| Criterion | Weight | Points | Main evidence |
|---|---:|---:|---|
| Problem definition and decision usefulness | 15% | 45 | memo, README, Videos 1 and 3 |
| Data integrity and traceability | 15% | 45 | repo, README, validation record |
| Financial soundness and judgment | 20% | 60 | memo, Video 3 |
| Technical execution and usability | 15% | 45 | repo, executed output, Video 2 |
| Validation, sensitivity and reproducibility | 25% | 75 | validation record, Locked record, Videos 1 and 2 |
| Professional communication | 10% | 30 | all written parts and videos |

"Decision-ready" goes only to an app a committee could adopt. The Brightspace rubric's level
descriptors and the plan to reach the top level on each criterion are in section 8.

## 2. What the repository has now

One commit (`449d699`, 2026-10-22 17:37 -0400). The three script outputs in `output/` match a
fresh run of `backtest.py`, `portfolio.py` and `mandate.py`.

| File | What it does |
|---|---|
| `mandate.py` | Meridian mandate checker: sum to 100, long-only, reserve ≥ 3%, 90% redeemable in 5 days, single company ≤ 8%. Candidates A to E. |
| `portfolio.py` | Engine: covariance, expected return, volatility, three baselines (benchmark 40/60, equal weight, inverse volatility), 5-point grid search for the lowest-risk mix, estimates from monthly prices (all months or last 36). |
| `app.py` | Streamlit app: lowest-risk mix on Meridian or an uploaded `prices.csv`, editable return estimates, objective and reserve controls, 36-month toggle, and the signal backtest with lag and cost controls. |
| `backtest.py`, `rule-card.md` | Frozen rule (signal > 0 → equity next month, else bills), lag 1, cost 0.10% a switch, development 2025 and holdout 2026-01 to 2026-06, on course training data. Holdout net −6.09% against buy-and-hold −2.09%: failure rule triggered. |
| `prices.csv` | 60 months of Adj Close for BIL, IEF, LQD, VTI, VXUS, Nov 2021 to Oct 2026 (Yahoo Finance, downloaded Oct 22, 2026; the last row is a partial month). |
| `asof.py`, `asof_app.py` | Provenance gate on a toy table; FRED against ALFRED as known on a date. |
| `lab-17-as-of-data.md` | DGS10 data card and the call that Project 2 may use it with a one-day lag. |
| `buffett_app.py`, `panel_app.py`, `.claude/skills/`, `memos/` | Labs 18 and 19 investor skills. Not required by Project 2. |
| `docs/decision-memo.md`, `docs/validation-and-ai-use.md` | Skeletons. Headings only, except a drafted Locked Changed-Input prediction. |
| `lab-13…`, `lab-14…`, `lab-15…` | Lab write-ups. Lab 15 holds the own-universe results and the call "pilot, not adopt". |

Lab 15 results on the own universe (objective 6.5%, reserve ≥ 3%):

| Window | BIL / IEF / LQD / VTI / VXUS | Return (estimate) | Volatility |
|---|---|---:|---:|
| All 60 months | 65 / 0 / 0 / 30 / 5 | 6.61 | 5.46 |
| Last 36 months | 85 / 0 / 0 / 5 / 10 | 6.70 | 1.74 |

## 3. Gaps against the eight requirements

| # | Status | What is missing |
|---|---|---|
| 1 App runs | Partial | `app.py` runs from the README command, but it is still titled and laid out as Lab 15, and the repo has four separate apps. Streamlit is not installed in the local Python 3.14, so no cold run has been verified on this machine. |
| 2 Mandate | Missing | No written mandate for the student's own client. The own universe reuses Meridian's 6.5% objective and 3% reserve rule. There is no benchmark, risk measure or risk limit for the own universe, and `mandate.py` only checks Meridian holdings. |
| 3 Baselines and verdicts | Missing in the app | Baselines print only from `portfolio.py`, only for Meridian. The app shows no baseline and no pass/fail verdict naming the rule, for any portfolio. |
| 4 Signal and data card | Mismatched | The backtested signal is a course training series (card-spend change) with no data card. The data card is for DGS10, which no rule uses. The DGS10 hand-check table against FRED is blank. |
| 5 Stress run | Partial | Estimates, window, cost and reserve controls exist but are scattered, with no single stress summary and no stop condition for the portfolio. The only stop rule is the signal's failure rule. |
| 6 Locked record | Prediction drafted | Cost 0.10% → 0.50% prediction is written. Commit link, actual output, decision effect and reconciliation are blank. |
| 7 Recommendation | Missing | Memo is headings only. No allocation range, triggers or committee ask. |
| 8 Two statements | Placeholders | README, memo and validation record all say "your own words". |

Other gaps:

- Visible output has no as-of date and no own-universe result; the decision numbers for the
  student's portfolio are only in `lab-15-lowest-risk-mix.md`.
- README is a lab index. It lacks the finance decision, intended user, data sources and known
  limitations, and it lists eleven commands instead of one.
- No videos, transcripts or manifest.
- Validation record sections are empty: known-answer checks, mandate check, point-in-time and
  leakage, holdout and placebo, stress run, AI output checked, cold run.
- Lab 15 partner question and partner attack are still placeholders.
- `memos/cathie-wood/` and `.claude/skills/cathie-wood/` duplicate the `cathie_wood` versions.
- No automated tests.

## 4. Decisions to make before building

1. **Which signal carries requirement 4.** Either keep the training signal and write an honest
   data card for it (fast, but the data is course-authored, so the process cannot be adopted on
   it), or build a rule on DGS10 with real fund returns from `prices.csv` (the data card exists;
   needs a new frozen rule card committed before the backtest, and a holdout run once).
   Recommended: DGS10 if time allows, because the data card and the as-of evidence are already
   done and it makes the app's signal and portfolio share one universe.
2. **The mandate numbers.** Client, objective, benchmark for the five-fund universe, the risk
   measure (volatility, or a loss limit) and its limit, and the hard constraints. These are the
   student's choices; the app's verdicts are checked against them.
3. **The second baseline.** Inverse volatility is already coded. A fixed benchmark mix is the
   alternative.
4. **The decision.** Lab 15 says "pilot, not adopt" and the signal's failure rule is triggered, so
   the current evidence points to pilot for the allocation and reject for the signal.
5. **One app.** Make `app.py` the product and leave the other three apps as lab files, or move
   them into a `labs/` folder.

If decision 1 or 2 changes the model, the drafted Locked Changed-Input prediction quotes numbers
(−6.09%, −2.09%, 6 and 4 switches) that may no longer apply. Rewrite the prediction by hand
before any run in that case.

## 5. Who does what: AI by default, human only where the course requires it

The course opens AI for Project 2 from the start, so the implementation session does everything
it is allowed to do. The student keeps only the items a course rule reserves for a person.

### Human only (a course rule requires it)

| Task | Why it cannot be AI | Rough time |
|---|---|---|
| Locked Changed-Input prediction | Must be human-authored with AI off, committed and pushed before the run. Already drafted in commit `97aa33f`; rewrite by hand only if the model changes. | 0 to 10 min |
| The changed-input run and its reconciliation | "The run itself is AI closed." Student changes the value, reruns, pastes before and after output, writes whether the decision changes and why. | 10 min |
| Recording the three videos | Webcam view is an identity and ownership check. | 13 min of video plus takes |
| YouTube upload, Brightspace manifest and submission | Student's accounts. Also grant the instructional team repo access. | 20 min |
| Final sign-off on the decision | "The analysis and the decision are yours" is one of the two required statements, so the student must actually make the call. | 5 min |

### AI drafts, student approves or edits

| Task | AI does | Student does |
|---|---|---|
| Mandate (client, objective, benchmark, risk measure, limits) | Proposes a complete mandate for the five-fund universe with reasons | Accepts or changes the numbers |
| Section 4 decisions | Picks the recommended option for each and proceeds | Overrides any before the build |
| Two statements | Drafts both from the real record of which AI did what | Rewrites in own words (the template asks for this) and confirms they are true |
| Decision memo | Writes the full memo from the app's numbers | Reads, edits, owns the recommendation |
| Validation and AI-use record | Fills every section except the Locked record's result rows; logs each AI use with tool, model, date, accept / modify / reject and the check run | Confirms the log is accurate; picks the one AI output to show in Video 1 and re-does that check personally |
| Video scripts | Writes a timed script for each video (3:00, 5:00, 5:00) with the opening statements, the live-demo opening for Video 3, and the manifest's timestamp index | Records from the script; must be able to explain the decision-number code unaided in Video 2 |
| Transcripts | Cleans the YouTube auto-captions the student pastes in: tickers, finance terms, numbers; writes `docs/transcript-video-N.txt` | Supplies the raw captions; spot-checks |
| Manifest | Prepares every row as a GitHub link in a file the student can paste | Adds the video URLs and submits |

### AI only

| Task | Notes |
|---|---|
| All code: mandate rules, baselines and verdicts in the app, signal and rule card, stress section, stop condition | Section 6, steps 2 to 6 |
| Environment setup and running the app | Virtual environment, `requirements.txt`, start and drive the app |
| Visible output in `output/` | Regenerated from the scripts, with inputs and the as-of date |
| README | Everything except the final wording of the two statements |
| Data card for the signal, and the three DGS10 values checked against FRED's CSV download | Automated check recorded in the validation record |
| Known-answer, baseline, mandate, leakage, holdout and stress checks | Run and recorded with their output |
| Cold run from a fresh clone | AI clones into an empty folder, follows only the README, records command, first failure, elapsed time. Recorded as an AI cold run; a partner's run can be added if one happens. |
| Tests, repo cleanup, commits and pushes | Commit only when the student says so; the Locked record depends on commit order |

Every load-bearing AI contribution is disclosed in `docs/validation-and-ai-use.md`; heavy AI use
is allowed, hidden AI use is not.

## 6. Build order for the implementation session

1. Student confirms the Brightspace due date. AI proceeds on the recommended option for each
   section 4 decision unless the student overrides it.
2. Environment: create a virtual environment, install `requirements.txt`, confirm
   `python3 -m streamlit run app.py` starts.
3. Mandate: write the student's mandate as a Markdown file and encode its rules so a function
   returns pass or fail and the failing rule for any weight vector on the five-fund universe.
4. App: show equal weight, the second baseline and the constrained portfolio side by side, each
   with return, volatility and its mandate verdict.
5. Signal: per decision 1, with its data card and the frozen rule shown in the app.
6. Stress run: one section covering estimates, window, costs and constraints, with the stop
   condition stated and evaluated.
7. Visible output: regenerate `output/` with inputs, as-of date and decision numbers for the
   student's own portfolio.
8. README: drafted statements, decision, intended user, one command, repository map, data
   sources, limitations.
9. Memo and validation record written in full from the app's numbers, leaving only the Locked
   record's result rows blank.
10. AI cold run from a fresh clone; fix the first failure.
11. AI writes the three video scripts, the timestamp index and the manifest rows.
12. Student: approve the mandate and decision, reword the statements, do the changed-input run,
    record and upload the videos, paste captions for AI to clean, submit on Brightspace with
    the two `.md` files attached.

Do not touch `COST` in `backtest.py` or the Locked Changed-Input table during steps 2 to 11.

Each step also carries the section 8 items tagged with its number. Commit after every step with
a message that says what changed: the repo has a single "Initial commit", and development
history is the corroborating evidence of ownership.

## 7. Source files

| Topic | File in `/Users/jesstran/FIN43900-Fall2026` |
|---|---|
| Project 2 brief | `projects/project-2-investment-management-application.md` |
| Checklist, video lengths | `projects/major-project-student-checklist.md` |
| Submission bundle, memo and video content, Project 2 rulings | `PROJECT-SUBMISSION-ARCHITECTURE.md` |
| AI rules | `projects/AI-BOUNDARY-CARD.md` |
| Which lab feeds which part, studio checklist | `lessons/week-12/student-handout.md` |
| Readiness test, changed input, cold run | `lessons/week-13/lab-20-project2-readiness.md` |
| Own mandate, own universe | `lessons/week-08/lab-13-portfolio-mandate.md`, `lessons/week-09/lab-14-portfolio-baselines.md` |
| App and stress run | `lessons/week-09/lab-15-portfolio-stability.md` |
| Point-in-time and data card | `lessons/week-10/lab-16-provenance-gate.md`, `lessons/week-10/lab-17-point-in-time.md` |
| Points, due date, criteria weights, late policy | `syllabus/FIN43900-Fall2026-syllabus.pdf` |

## 8. Rubric and the full-marks plan

Target: the "Decision-ready" level on all six criteria (300 of 300). The instructor has said full
marks need work beyond the base requirements. The levels are worth 100%, 85%, 70%, 40% and 0% of
each criterion.

### The Decision-ready descriptors (Brightspace rubric)

| Criterion | Points | Decision-ready means |
|---|---:|---|
| Problem definition and decision usefulness | 45 | Intended user, action, horizon, constraints, Edition A/B boundary and committee ask are explicit; the analysis changes a real decision. |
| Data integrity and traceability | 45 | Material inputs have source, as-of date, definitions, transformations, exclusions and reproducible lineage; revisions, licensing and privacy are handled. |
| Financial soundness and judgment | 60 | Conventions, units, bridges, benchmarks, constraints and scenarios are correct; the recommendation is a defensible range or action with risks and reversal triggers. |
| Technical execution and usability | 45 | A clean user can reproduce the visible result; architecture and data flow are coherent; errors, credentials, dependencies and output are handled safely. |
| Validation, sensitivity and reproducibility | 75 | Known answers, a complete Locked Changed-Input Record (human-authored AI-off prediction, predicted and actual decision effect), robustness and failure tests, AI-output checks and cold-run evidence target the highest-risk claims; limitations drive action. |
| Professional communication | 30 | Memo, README, manifest, transcripts and three distinct videos are accurate, concise, internally consistent, accessible and fit their audiences. |

What drops a criterion one level: one unclear secondary constraint (problem), one traceability
gap (data), one convention or sensitivity needing refinement (finance), one setup defect
(technical), one weak failure mode or reproduction detail (validation), one inconsistency
(communication). So the plan below is mostly about leaving no single gap.

### Tier 1: every word of the top descriptor is visibly covered

Build these inside the numbered steps. Step tags refer to section 6.

**Problem definition (45)**

- P1 (steps 3, 8, 9). A "decision frame" block at the top of the README and memo: intended user,
  the action requested, horizon and rebalancing frequency, every constraint, the committee ask.
- P2 (steps 8, 9). State the editions boundary in one line: Project 2 has no Edition A or B
  (course ruling of 2026-10-14), and say where the equivalent evidence is. Add a short "how the
  system and my thinking changed" section, Lab 13 mandate to final app, which Video 1 follows.
- P3 (step 9). Show the analysis changing a decision: a table of what the committee would have
  done without it against what it should do now (the benchmark that fails its own reserve rule;
  the optimizer's point answer replaced by a range; the signal rejected on its holdout).

**Data integrity (45)**

- D1 (steps 5, 7). A data card for every material input, not only the signal: each ticker in
  `prices.csv`, the signal series, and the inflation assumption behind the objective. Fields:
  source and link, as-of and download date, definition (Adj Close includes distributions),
  units, transformations, exclusions, revisions, licensing, privacy.
- D2 (step 7). Lineage a grader can re-run: a script that rebuilds the estimates from
  `prices.csv`, a SHA-256 of each data file printed in the visible output, and the as-of date
  stamped in the app and in `output/`.
- D3 (step 3). Decide and document the partial October 2026 row (priced Oct 21): exclude it or
  flag it, and show the effect on the result either way. No silent cleaning.
- D4 (step 5). Revisions handled: signal values taken as known on each decision date (ALFRED
  vintage or the documented one-day lag for DGS10); note that Adj Close is restated after each
  distribution, so the file is a dated snapshot.
- D5 (step 8). Licensing and privacy lines: Yahoo Finance and FRED terms of use cited, data used
  for education; no personal data, no keys, nothing in `.env`.

**Financial soundness (60)**

- S1 (steps 3, 4). Conventions and units stated where the numbers appear: arithmetic mean × 12,
  standard deviation × √12, percent per year, long-only, 5-point grid, estimates not forecasts.
- S2 (step 3). A benchmark for the five-fund universe and a measured risk limit that answers
  Lab 13's open loss question, for example worst rolling 12-month loss in the sample and a
  one-year 95% loss estimate, each tested as a mandate rule with pass or fail.
- S3 (step 4). Bridges: benchmark to portfolio (what each weight change adds to return and
  risk), and gross to net for the signal (switches × cost).
- S4 (step 6). Named scenarios beside the parameter sliders: the 2022 rate shock replayed on the
  current weights, an equity drawdown, and stock and bond correlation moving to positive.
- S5 (steps 6, 9). The allocation range derived from evidence, not chosen: the spread of weights
  across the stress runs becomes the range in the memo. Each risk gets a numeric monitoring
  trigger and a reversal trigger.
- S6 (step 4). Turnover and trading cost of moving from the benchmark to the portfolio, and of
  each rebalance.

**Technical execution (45)**

- T1 (step 2). Exact pinned versions in `requirements.txt`, the Python version stated, and one
  command that regenerates everything in `output/`.
- T2 (step 4). One app with clear sections; a Mermaid architecture and data-flow diagram in the
  README; the app holds no copy of the math.
- T3 (step 4). Safe failure: bad uploads, missing columns, infeasible mandates and an invalid
  correlation table each give a plain message, never a traceback. The app runs offline from the
  committed data.
- T4 (step 7). Visible output on GitHub without running anything: text output plus app
  screenshots, with inputs, as-of date and decision numbers.
- T5 (step 8). `.gitignore` covers `.env` and caches; a line in the README confirming no
  credentials are needed.

**Validation (75, the largest criterion)**

- V1 (step 9). A claims table that leads the validation record: each high-risk claim, the test
  aimed at it, the result, and the action it drives. Rank the claims by how easily each could
  reverse the decision.
- V2 (steps 3 to 6). Known answers as automated tests (`pytest`): the Meridian values from Labs
  13 to 15, the hand calculation of the benchmark's 10.46% volatility, the frozen backtest.
- V3 (step 5). Failure tests for the signal: the lag-0 leak shown as a leak, a placebo (shuffled
  signal) run, and the holdout run once.
- V4 (step 6). An out-of-sample test of the portfolio itself: estimate on the first 36 months,
  hold for the last 24, compare realized return and risk with both baselines.
- V5 (step 9). Limitations drive action: every limitation in the record maps to a cap on the
  allocation range, a monitoring trigger or a stop condition in the memo.
- V6 (step 9). AI-output checks: at least three logged, each with the independent check (hand
  calculation, second method, source page), including one AI suggestion rejected or corrected.
- V7 (step 10). Cold-run evidence from more than one source: the AI fresh-clone run, the CI run
  (T6), and a partner's run if one can be had.
- V8 (step 12b). The Locked record complete in every field, with before and after output pasted
  and the prediction commit linked.

**Communication (30)**

- C1 (steps 7, 9). One source of truth for numbers: the scripts write
  `output/decision-numbers.json`, and a test fails if the memo or README quotes a number that
  differs from it.
- C2 (step 11). Three videos that do not overlap: each script answers only its own question
  from the Week 12 handout, and the manifest carries a timestamp index for each.
- C3 (step 9). Memo within two pages, decision first, written for a committee; README written
  for a stranger; validation record written for a challenger.
- C4 (steps 4, 12d). Accessibility: verdicts shown as words and not only colour, alt text on
  screenshots, corrected transcripts committed.

### Tier 2: beyond the requirement, high value for the effort

- T6. GitHub Actions workflow that installs from `requirements.txt`, runs the tests and
  regenerates `output/` on every push, with a status badge in the README. This is a cold run by
  a machine nobody coached.
- F1. Estimation-error analysis: resample the monthly returns (bootstrap), rerun the search each
  time, and show the distribution of each weight. It gives the allocation range a statistical
  basis and directly answers the Lab 15 finding that one point moves 25 points of the portfolio.
- F2. Cross-check the grid search with an independent method (a finer grid or a numerical
  optimizer) and report the difference as a known-answer check on the search itself.
- F3. A monitoring panel in the app: each trigger from the memo with its current value and
  status, so the committee can see today whether any trigger has fired.
- F4. A model-risk section in the validation record using the three headings from the Week 12
  reading: conceptual soundness, outcome analysis, ongoing monitoring.

### Tier 3: only if time remains

- A public deployment (Streamlit Community Cloud) for the manifest's optional row.
- The efficient frontier chart with the baselines, benchmark and portfolio marked.
- A second out-of-sample window or a rolling walk-forward version of V4.
- Screening note from the Lab 19 investor panel on the largest holding in one fund, clearly
  marked as context and not part of the decision.

### Limits of this plan

- Scope is a risk. The syllabus deadline is tonight, the Week 12 guidance is to freeze a must-fix
  list, and each video has a hard time limit. Finish tier 1 before touching tier 2; anything
  built must also be explained and kept consistent across memo, output and videos.
- Every addition must be honest. A failed test or a rejected signal reported plainly scores
  higher than a tuned success, and an honest reject is fully responsive.
- Three top-level items depend on the student and cannot be built: the Locked record's run, the
  videos, and being able to explain the code.

