"""The app runs end to end, shows the verdicts, and fails safely on bad input."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from streamlit.testing.v1 import AppTest


def run_app():
    os.chdir(ROOT)
    return AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=60).run()


def page_text(at):
    parts = [str(x.value) for kind in ("markdown", "caption", "info", "warning", "error", "success")
             for x in getattr(at, kind)]
    return "\n".join(parts)


def test_app_runs_and_shows_verdicts_as_words():
    at = run_app()
    assert not at.exception
    text = page_text(at)
    assert "As of 2026-09-30" in text
    frames = [df.value for df in at.dataframe]
    verdicts = frames[0]["Mandate verdict"].tolist()
    assert verdicts[-1] == "✔ PASS"
    assert all(v.startswith("✘ FAIL: M") for v in verdicts[:-1])


def test_moving_one_limit_changes_the_verdict_without_a_traceback():
    at = run_app()
    at.sidebar.number_input[3].set_value(2.0).run()   # loss limit 2%: nothing can pass
    assert not at.exception
    text = page_text(at)
    assert "What-if mode" in text
    assert "No mix on the 5-point grid passes" in text
