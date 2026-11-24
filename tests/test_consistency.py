"""One source of truth: every number quoted in the memo, the README and the validation record
must be a number in output/decision-numbers.json (or a stated constant)."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import client_mandate as cm
import process as pr

with open(os.path.join(ROOT, "output", "decision-numbers.json")) as f:
    N = json.load(f)


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def all_numbers(node, out):
    if isinstance(node, bool):
        return out
    if isinstance(node, (int, float)):
        out.add(f"{abs(node):.2f}")
    elif isinstance(node, str):
        out.update(re.findall(r"(\d+\.\d\d)%", node))
    elif isinstance(node, dict):
        for v in node.values():
            all_numbers(v, out)
    elif isinstance(node, list):
        for v in node:
            all_numbers(v, out)
    return out


KNOWN = all_numbers(N, set())
# constants and lab known answers that are quoted on purpose and are not decision numbers
ALLOWED = {
    "10.46", "5.20", "5.21", "3.77", "1.05", "6.51", "9.44", "6.53", "12.94", "6.13", "6.09",  # labs
    "0.50",                       # the Locked Changed-Input value, named but never run
    f"{N['estimates']['BIL']['return'] - pr.ESTIMATE_SHOCK:.2f}",   # the BIL trigger: estimate - 1 point
    f"{cm.RULES['objective']:.2f}", f"{pr.TRADE_COST:.2f}",
}


def quoted(text):
    return set(re.findall(r"(\d+\.\d\d)%", text))


def test_every_two_decimal_percentage_is_in_the_numbers_file():
    for parts in (("docs", "decision-memo.md"), ("README.md",), ("docs", "validation-and-ai-use.md")):
        text = read(*parts)
        if parts[-1].startswith("validation"):   # the student's locked prediction quotes the training rule
            text = text.split("## 10. Locked Changed-Input Record")[0] + text.split("## 11. Cold run")[1]
        unknown = quoted(text) - KNOWN - ALLOWED
        assert not unknown, f"{parts[-1]} quotes numbers that are not in decision-numbers.json: {unknown}"


def test_headline_numbers_match():
    c = N["portfolios"]["Constrained portfolio"]
    target = " / ".join(f"{t} {w:.0f}" for t, w in c["weights"].items())
    plain = " / ".join(f"{w:.0f}" for w in c["weights"].values())
    eq, bil = N["allocation_range"]["Equity (VTI + VXUS)"], N["allocation_range"]["BIL"]
    sig = N["signal"]
    memo, readme, record = read("docs", "decision-memo.md"), read("README.md"), read("docs", "validation-and-ai-use.md")
    for text in (memo, readme):
        assert target in text
        assert f"{c['return']:.2f}%" in text and f"{c['volatility']:.2f}%" in text
        assert N["as_of"] in text
        assert f"{eq['low']}% to {eq['high']}%" in text and f"{bil['low']}% to {bil['high']}%" in text
    assert plain in memo
    for text in (memo, record):
        assert f"{sig['holdout']['net']:.2f}%" in text and f"{sig['holdout']['buy_and_hold']:.2f}%" in text
        assert f"{sig['holdout_gap']:.2f} points" in text
        assert f"{sig['placebo']['share_at_least_actual']:.1f}%" in text
        assert f"{N['largest_move']['points']:.0f} points" in text
    assert c["verdict"] == "PASS" and N["process_status"].startswith("PILOT")
    assert sig["failure_rule_triggered"] is True


def test_the_two_statements_open_each_written_part():
    for parts in (("README.md",), ("docs", "decision-memo.md"), ("docs", "validation-and-ai-use.md")):
        head = read(*parts)[:1500]
        assert "AI announcement." in head and "Education, not investment advice." in head

