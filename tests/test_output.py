"""The committed visible output is what the code produces today."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import make_output as mo

os.chdir(ROOT)
FRESH = mo.numbers()


def test_committed_numbers_are_not_stale():
    with open(os.path.join(ROOT, "output", "decision-numbers.json")) as f:
        committed = json.load(f)
    assert committed == json.loads(json.dumps(FRESH))


def test_committed_report_is_not_stale():
    with open(os.path.join(ROOT, "output", "decision-report.md"), encoding="utf-8") as f:
        assert f.read() == mo.report(FRESH)


def test_report_shows_inputs_as_of_date_and_decision_numbers():
    text = mo.report(FRESH)
    for needle in ("As of 2026-09-30", "prices.csv", "SHA-256", "65 / 0 / 0 / 20 / 15", "**PASS**",
                   "FAIL: M6, M7", "Process status: PILOT", "Failure rule: TRIGGERED"):
        assert needle in text


def test_no_output_was_made_at_the_locked_changed_input_value():
    # The Locked Changed-Input run (cost 0.50) is the student's, AI closed. Nothing here runs it.
    assert 0.5 not in mo.SIGNAL_COSTS
    assert all(c["cost"] != 0.5 for c in FRESH["signal"]["cost_sensitivity"])
