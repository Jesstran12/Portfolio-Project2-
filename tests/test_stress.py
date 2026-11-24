"""The stress run, the scenarios, the out-of-sample test and the stop condition."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import client_mandate as cm
import process as pr

os.chdir(ROOT)
B = pr.build(signal_failed=True)
RUNS = {r["label"]: r["weights"] for r in B["stress"]}


def test_stress_run_known_answers():
    assert RUNS["Base case"] == [65, 0, 0, 20, 15]
    assert RUNS["Last 36 months"] == [85, 0, 0, 5, 10]
    assert RUNS["All 59 months, partial month included"] == [65, 0, 0, 30, 5]   # the Lab 15 answer
    assert RUNS["Loss limit 5%"] is None
    assert {r["group"] for r in B["stress"]} == {"base", "estimates", "window", "costs", "constraints"}


def test_every_feasible_stress_answer_is_a_whole_portfolio():
    for weights in RUNS.values():
        if weights is not None:
            assert sum(weights) == 100 and min(weights) >= 0


def test_allocation_range_is_the_spread_of_the_stress_run():
    assert B["ranges"]["BIL"] == (60, 85)
    assert B["ranges"]["Equity (VTI + VXUS)"] == (15, 40)
    assert B["ranges"]["IEF"] == (0, 0) and B["ranges"]["LQD"] == (0, 0)


def test_stop_conditions():
    s = {x["id"]: x["fired"] for x in B["stops"]}
    assert s == {"STOP-1": False, "STOP-2": False, "GATE-1": True, "GATE-2": True, "SIGNAL": True}


def test_2022_replay_matches_the_history_rule():
    replay = B["scenarios"][0]["results"]
    assert round(replay["Benchmark 60/40"], 2) == -17.37
    assert round(replay["Constrained portfolio"], 2) == -5.33
    assert replay["Constrained portfolio"] >= B["judged"]["Constrained portfolio"]["measures"]["worst_12m"] - 1e-9


def test_out_of_sample_uses_no_later_data():
    o = B["out_of_sample"]
    assert o["estimation"].startswith("2021-12 to 2024-11") and o["holding"].startswith("2024-12 to 2026-09")
    chosen = o["results"]["Constrained portfolio (estimated on the early window)"]
    assert chosen["weights"] == [60.0, 0.0, 0.0, 40.0, 0.0]
    assert round(chosen["annual_return"], 2) == 8.19 and round(chosen["volatility"], 2) == 5.15
    # the early-window answer must not change when the later prices change
    rows, _ = pr.complete_rows(pr.validate_rows(pr.read_rows()))
    bent = [rows[0]] + rows[1:38] + [[r[0]] + [x * 2 for x in r[1:]] for r in rows[38:]]
    assert pr.out_of_sample(bent)["results"][
        "Constrained portfolio (estimated on the early window)"]["weights"] == chosen["weights"]


def test_turnover_and_cost():
    assert pr.one_way_turnover([0, .2, .2, .4, .2], [.65, 0, 0, .2, .15]) == 65.0
    assert abs(pr.trading_cost([0, .2, .2, .4, .2], [.65, 0, 0, .2, .15], cost=0.10) - 0.13) < 1e-9
    assert max(B["turnover"]["rebalance"]) < B["turnover"]["budget"]


def test_finer_grid_cross_check():
    g = pr.grid_check(B["estimates"])
    assert g["coarse_weights"] == [65.0, 0.0, 0.0, 20.0, 15.0]
    assert g["fine_volatility"] <= g["coarse_volatility"] + 1e-9    # a finer grid can only do as well or better
    assert g["coarse_volatility"] - g["fine_volatility"] < 0.25     # and the 5-point grid costs little risk
    fine = [w / 100 for w in g["fine_weights"]]
    assert pr.judge(fine, B["estimates"])["verdict"] == "PASS"


def test_bootstrap_is_reproducible_and_brackets_the_base_case():
    small = pr.bootstrap(B["estimates"], runs=40)
    assert small == pr.bootstrap(B["estimates"], runs=40)
    eq = small["weights"]["Equity (VTI + VXUS)"]
    assert eq["p05"] <= 35 <= eq["p95"]


def test_monitoring_triggers_are_quiet_today():
    assert [t["fired"] for t in pr.monitoring(B)] == [False] * 6
