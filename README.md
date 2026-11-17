# Project 2: Portfolio Construction

> **AI announcement.** _(Your own words: which AI tools you used and for what, and that the analysis, the checks and the decision are yours.)_
>
> **Education, not investment advice.** _(Your own words: a course project for FIN 43900, a learning demonstration, not investment advice.)_

## Run it

From this folder, with Python 3:

```
pip install -r requirements.txt
python3 -m streamlit run app.py
```

The app shows the lowest-risk mix and its mandate check, and the frozen signal rule's holdout
result, gross and net, with the lag and the cost as controls. To use your own funds, upload
`prices.csv` in the sidebar; BIL and IEF start ticked as reserve-eligible.

## Results without running anything

- [output/backtest.txt](output/backtest.txt): the frozen rule, development and holdout, gross and net
- [output/portfolio.txt](output/portfolio.txt): the baselines (benchmark 40/60, equal weight, inverse volatility)
- [output/mandate.txt](output/mandate.txt): the mandate check
- [docs/decision-memo.md](docs/decision-memo.md) and [docs/validation-and-ai-use.md](docs/validation-and-ai-use.md)

## Repository map

| Lab | Write-up | Code |
| --- | --- | --- |
| 13: Portfolio mandate | [lab-13-portfolio-mandate.md](lab-13-portfolio-mandate.md) | [mandate.py](mandate.py) |
| 14: Portfolio baselines | [lab-14-portfolio-baselines.md](lab-14-portfolio-baselines.md) | [portfolio.py](portfolio.py) |
| 15: Lowest-risk mix | [lab-15-lowest-risk-mix.md](lab-15-lowest-risk-mix.md) | [app.py](app.py), [prices.csv](prices.csv) |
| 16: As-of panel | (no write-up) | [asof.py](asof.py) |
| 17: As-of data from FRED | [lab-17-as-of-data.md](lab-17-as-of-data.md) | [asof_app.py](asof_app.py) |
| 18: Buffett skill | [memos/](memos/) | [.claude/skills/buffett/](.claude/skills/buffett/) ([SKILL.md](.claude/skills/buffett/SKILL.md), [buffett.py](.claude/skills/buffett/buffett.py)), [buffett_app.py](buffett_app.py) |
| Holdout test (Week 12 join) | [rule-card.md](rule-card.md) | [backtest.py](backtest.py), shown in [app.py](app.py) |
| 19: Legend panel | [memos/](memos/) ([cathie_wood/](memos/cathie_wood/), [burry/](memos/burry/)) | [cathie_wood](.claude/skills/cathie_wood/), [burry](.claude/skills/burry/), [panel_app.py](panel_app.py) |

Run, from this folder:

```
python3 backtest.py
python3 portfolio.py
python3 mandate.py
python3 -m streamlit run app.py
python3 asof.py
python3 -m streamlit run asof_app.py
python3 .claude/skills/buffett/buffett.py COST
python3 -m streamlit run buffett_app.py
python3 .claude/skills/cathie_wood/cathie_wood.py COST
python3 .claude/skills/burry/burry.py COST
python3 -m streamlit run panel_app.py
```

Built with AI help; a learning demonstration, not investment advice.
