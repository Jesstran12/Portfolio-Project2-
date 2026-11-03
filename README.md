# Project 2: Portfolio Construction

FIN 43900, Fall 2026. Labs 13–17 and the Project 2 portfolio app.

| Lab | Write-up | Code |
| --- | --- | --- |
| 13: Portfolio mandate | [lab-13-portfolio-mandate.md](lab-13-portfolio-mandate.md) | [mandate.py](mandate.py) |
| 14: Portfolio baselines | [lab-14-portfolio-baselines.md](lab-14-portfolio-baselines.md) | [portfolio.py](portfolio.py) |
| 15: Lowest-risk mix | [lab-15-lowest-risk-mix.md](lab-15-lowest-risk-mix.md) | [app.py](app.py), [prices.csv](prices.csv) |
| 16: As-of panel | (no write-up) | [asof.py](asof.py) |
| 17: As-of data from FRED | [lab-17-as-of-data.md](lab-17-as-of-data.md) | [asof_app.py](asof_app.py) |
| 18: Buffett skill | [memos/](memos/) | [.claude/skills/buffett/](.claude/skills/buffett/) ([SKILL.md](.claude/skills/buffett/SKILL.md), [buffett.py](.claude/skills/buffett/buffett.py)), [buffett_app.py](buffett_app.py) |

Run, from this folder:

```
python3 portfolio.py
python3 mandate.py
python3 -m streamlit run app.py
python3 asof.py
python3 -m streamlit run asof_app.py
python3 .claude/skills/buffett/buffett.py COST
python3 -m streamlit run buffett_app.py
```

Built with AI help; a learning demonstration, not investment advice.
