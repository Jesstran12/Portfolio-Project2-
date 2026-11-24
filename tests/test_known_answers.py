"""Known answers: the lab values, a hand calculation, and the mandate rules."""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backtest as bt
import client_mandate as cm
import mandate as lab13
import portfolio as p
import process as pr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def meridian():
    names = list(p.SLEEVES)
    return (names, [p.SLEEVES[n][0] for n in names], [p.SLEEVES[n][1] for n in names],
            [p.SLEEVES[n][2] for n in names])


def test_benchmark_volatility_matches_the_hand_calculation():
    # variance = 0.4^2 x 0.06^2 + 0.6^2 x 0.16^2 + 2 x 0.4 x 0.6 x 0.25 x 0.06 x 0.16 = 0.010944
    by_hand = math.sqrt(0.4**2 * 0.06**2 + 0.6**2 * 0.16**2 + 2 * 0.4 * 0.6 * 0.25 * 0.06 * 0.16) * 100
    names, _, vols, _ = meridian()
    cov = p.covariance_matrix(vols, p.CORRELATION)
    got = p.volatility(p.benchmark_weights(names, p.BENCHMARK), cov)
    assert round(by_hand, 2) == 10.46
    assert abs(got - by_hand) < 1e-9


def test_lab14_baselines():
    names, returns, vols, _ = meridian()
    cov = p.covariance_matrix(vols, p.CORRELATION)
    eq = p.equal_weights(4)
    assert round(p.expected_return(eq, returns), 2) == 5.20
    assert round(p.volatility(eq, cov), 2) == 5.21
    iv = p.inverse_vol_weights(vols)
    assert round(p.expected_return(iv, returns), 2) == 3.77
    assert round(p.volatility(iv, cov), 2) == 1.05


def test_lab15_lowest_risk_mix_and_the_one_point_change():
    _, returns, vols, eligible = meridian()
    w, ret, vol = p.lowest_risk_mix(returns, vols, p.CORRELATION, eligible, 6.5, 3.0)
    assert [round(x * 100) for x in w] == [0, 20, 25, 55]
    assert (round(ret, 2), round(vol, 2)) == (6.51, 9.44)
    w, ret, vol = p.lowest_risk_mix(returns[:3] + [7.0], vols, p.CORRELATION, eligible, 6.5, 3.0)
    assert [round(x * 100) for x in w] == [0, 10, 10, 80]
    assert (round(ret, 2), round(vol, 2)) == (6.53, 12.94)


def test_lab13_candidates():
    fails = {name: sum(not ok for _, _, ok in lab13.check(w, lab13.reserve_minimum()))
             for name, w in lab13.CANDIDATES.items()}
    assert fails == {"A": 0, "B": 3, "C": 1, "D": 0, "E": 1}


def test_frozen_training_backtest():
    res = bt.run()  # the frozen lag and cost on the rule card; never another cost here
    assert round(res["Development"]["net"], 2) == 6.13
    assert round(res["Holdout"]["net"], 2) == -6.09
    assert round(res["Holdout"]["buy_and_hold"], 2) == -2.09
    assert res["failure"] is True


# ---------------------------------------------------------------- the client mandate
def test_verdict_names_each_failed_rule():
    base = {"total": 100, "lowest": 0, "reserve": 10, "equity": 50, "return": 7,
            "loss_95": 5, "worst_12m": -5}
    assert cm.verdict(cm.check(base)) == "PASS"
    assert cm.verdict(cm.check({**base, "total": 95})) == "FAIL: M1"
    assert cm.verdict(cm.check({**base, "lowest": -5})) == "FAIL: M2"
    assert cm.verdict(cm.check({**base, "reserve": 3.9})) == "FAIL: M3"
    assert cm.verdict(cm.check({**base, "equity": 75})) == "FAIL: M4"
    assert cm.verdict(cm.check({**base, "return": 6.49})) == "FAIL: M5"
    assert cm.verdict(cm.check({**base, "loss_95": 10.1})) == "FAIL: M6"
    assert cm.verdict(cm.check({**base, "worst_12m": -10.1})) == "FAIL: M7"
    assert cm.verdict(cm.check({**base, "return": 1, "worst_12m": -20})) == "FAIL: M5, M7"


def test_boundary_values_pass():
    edge = {"total": 100, "lowest": 0, "reserve": 4.0, "equity": 70.0, "return": 6.5,
            "loss_95": 10.0, "worst_12m": -10.0}
    assert cm.verdict(cm.check(edge)) == "PASS"


def test_worst_12_month_return_by_hand():
    # one fund, 13 months: twelve at -1% then one at +5%; the worst window is the first twelve
    monthly = [[-0.01]] * 12 + [[0.05]]
    assert abs(cm.worst_12_month_return([1.0], monthly) - ((0.99**12 - 1) * 100)) < 1e-9
    assert abs(cm.loss_estimate_95(6.0, 10.0) - 10.45) < 1e-9


def test_mandate_file_and_code_agree():
    text = open(os.path.join(ROOT, "docs", "mandate.md"), encoding="utf-8").read()
    r = cm.RULES
    assert f"BIL + IEF ≥ {r['reserve_min']:.1f}%" in text
    assert f"VTI + VXUS ≤ {r['equity_max']:.0f}%" in text
    assert f"Return estimate ≥ {r['objective']:.1f}%" in text
    assert f"loss estimate ≤ {r['loss_limit']:.0f}%" in text
    assert "BIL 0 / IEF 20 / LQD 20 / VTI 40 / VXUS 20" in text
    assert [cm.BENCHMARK[t] for t in cm.TICKERS] == [0, 20, 20, 40, 20]


# ---------------------------------------------------------------- the pipeline on the committed data
def test_constrained_portfolio_passes_and_is_the_lowest_risk_passing_mix():
    rows, dropped = pr.complete_rows(pr.validate_rows(pr.read_rows(os.path.join(ROOT, "prices.csv"))))
    assert [r[0] for r in dropped] == ["2026-10-01"]
    est = pr.estimate(rows)
    w = pr.constrained_portfolio(est)
    assert pr.judge(w, est)["verdict"] == "PASS"
    vol = p.volatility(w, est["cov"])
    for other in p.long_only_mixes(5, 5):   # brute force: nothing that passes has lower risk
        if p.volatility(other, est["cov"]) < vol - 1e-9:
            assert pr.judge(other, est)["verdict"] != "PASS"


def test_bridge_adds_up():
    rows, _ = pr.complete_rows(pr.validate_rows(pr.read_rows(os.path.join(ROOT, "prices.csv"))))
    est = pr.estimate(rows)
    a, b = cm.benchmark_weights(), pr.constrained_portfolio(est)
    rows_ = pr.bridge(a, b, est)
    assert abs(sum(r["return_added"] for r in rows_)
               - (p.expected_return(b, est["returns"]) - p.expected_return(a, est["returns"]))) < 1e-9
    assert abs(sum(r["risk_added"] for r in rows_)
               - (p.volatility(b, est["cov"]) - p.volatility(a, est["cov"]))) < 1e-9


def test_bad_price_files_give_plain_messages():
    import pytest
    good = pr.read_rows(os.path.join(ROOT, "prices.csv"))
    for bad, words in (
            ([], "no price rows"),
            ([["date", "BIL", "IEF"]] + [r[:3] for r in good[1:]], "missing column"),
            (good[:5], "at least 25"),
            ([good[0]] + [good[2], good[1]] + good[3:], "oldest first"),
            ([good[0]] + [[good[1][0], "abc"] + good[1][2:]] + good[2:], "not a price"),
            ([good[0]] + [[good[1][0], "-1"] + good[1][2:]] + good[2:], "above zero")):
        with pytest.raises(ValueError, match=words):
            pr.validate_rows(bad)


# ---------------------------------------------------------------- the signal rule, on made-up data
def test_signal_rule_by_hand():
    import signal_rule as sr
    signal = {"2030-01": -1.0, "2030-02": 1.0, "2030-03": -1.0, "2030-04": -1.0, "2030-05": 0.0}
    returns = {m: {"IEF": r, "BIL": 0.3} for m, r in
               (("2030-02", 2.0), ("2030-03", -1.0), ("2030-04", 3.0), ("2030-05", 1.0))}
    res = sr.run(signal, returns, lag=1, cost=0.10, development=("2030-02", "2030-03"),
                 holdout=("2030-04", "2030-05"))
    dev, hold = res["Development"], res["Holdout"]
    assert dev["switches"] == 2 and hold["switches"] == 1          # BIL->IEF, IEF->BIL, then BIL->IEF
    assert abs(dev["gross"] - (1.02 * 1.003 - 1) * 100) < 1e-9
    assert abs(dev["net"] - (1.019 * 1.002 - 1) * 100) < 1e-9
    assert abs(hold["net"] - (1.029 * 1.01 - 1) * 100) < 1e-9
    assert abs(hold["buy_and_hold"] - (1.03 * 1.01 - 1) * 100) < 1e-9
    assert res["failure"] is True                                   # the switch cost puts it behind


def test_signal_uses_only_published_values():
    import signal_rule as sr
    obs = [("2030-01-29", 4.00), ("2030-01-30", 4.10), ("2030-01-31", 9.99),
           ("2030-02-26", 4.30), ("2030-02-27", 4.05), ("2030-02-28", 9.99)]
    known = sr.known_at_month_end(obs)
    assert known["2030-01"] == ("2030-01-30", 4.10)                # the last day's value is not yet out
    assert abs(sr.signals(known)["2030-02"] - (4.05 - 4.10)) < 1e-9


# ---------------------------------------------------------------- the signal rule, on the real files
def _signal():
    import signal_rule as sr
    os.chdir(ROOT)
    signal, returns, known = sr.load()
    return sr, signal, returns, known


def test_frozen_dgs10_rule_known_answer():
    sr, signal, returns, _ = _signal()
    res = sr.run(signal, returns)          # the frozen lag and cost on the rule card
    dev, hold = res["Development"], res["Holdout"]
    assert (dev["months"], hold["months"]) == (37, 21)
    assert (round(dev["gross"], 2), round(dev["net"], 2), dev["switches"]) == (-3.33, -5.16, 19)
    assert (round(hold["gross"], 2), round(hold["net"], 2), hold["switches"]) == (3.25, 2.12, 11)
    assert round(hold["buy_and_hold"], 2) == 3.02
    assert res["failure"] is True


def test_lag_zero_is_a_leak_and_looks_like_one():
    sr, signal, returns, _ = _signal()
    honest, leak = sr.run(signal, returns), sr.run(signal, returns, lag=0)
    assert leak["Holdout"]["net"] > honest["Holdout"]["net"] + 10
    assert leak["Development"]["net"] > honest["Development"]["net"] + 40


def test_placebo_is_reproducible_and_the_signal_does_not_beat_it():
    sr, signal, returns, _ = _signal()
    pl = sr.placebo(signal, returns)
    assert pl == sr.placebo(signal, returns)
    assert round(pl["share_at_least_actual"], 1) == 69.4
    assert pl["median"] > pl["actual"]


def test_dgs10_is_point_in_time():
    sr, _, _, known = _signal()
    today = dict(sr.read_dgs10())
    assert (today["2026-10-01"], today["2026-10-15"], today["2026-10-28"]) == (5.24, 5.10, 5.05)
    rev = sr.revision_check()
    assert rev["revised"] == 0 and rev["missing_today"] == 0
    assert rev["vintage_last_date"] == "2026-09-29"     # on 2026-09-30 the newest value was the 29th
    assert known["2026-09"] == ("2026-09-29", 5.26)     # and that is the one the rule uses
    for month, (date, _) in known.items():
        assert date[:7] == month
