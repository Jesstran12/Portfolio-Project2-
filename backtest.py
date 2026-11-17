"""Lab 18 - the frozen rule on a development period and an untouched holdout, gross and net.

Standard library only. Edit the inputs at the top; everything below is computed from them.
The rule card is rule-card.md. app.py imports run() and shows the frozen result as locked numbers.
Run: python3 backtest.py
"""

# ---------------------------------------------------------------- editable inputs (the rule card)
# month: (signal %, equity fund %); the signal is published by month-end
DATA = {
    "2024-12": (0.8, None),
    "2025-01": (1.2, 2.0), "2025-02": (0.9, 1.5), "2025-03": (1.5, 3.0), "2025-04": (-1.0, -2.5),
    "2025-05": (-0.7, -1.5), "2025-06": (-1.4, -3.0), "2025-07": (1.1, 2.5), "2025-08": (0.6, 1.0),
    "2025-09": (0.9, 2.0), "2025-10": (-0.9, -2.0), "2025-11": (-0.5, -1.0), "2025-12": (1.6, 3.5),
    "2026-01": (-1.1, -2.0), "2026-02": (0.7, 1.5), "2026-03": (-1.3, -3.0), "2026-04": (0.8, 2.0),
    "2026-05": (-0.6, -1.5), "2026-06": (0.5, 1.0),
}
LAG = 1              # months: this month's signal decides the position LAG months later
COST = 0.10          # percent, charged in any month the position switches
BILLS = 0.3          # percent a month
DEVELOPMENT = ("2025-01", "2025-12")
HOLDOUT = ("2026-01", "2026-06")   # run once, never tuned
# ---------------------------------------------------------------- end of inputs

FROZEN = {"lag": LAG, "cost": COST}  # the values committed on the rule card; the app locks these


def months_in(period, data=DATA):
    return [m for m in data if period[0] <= m <= period[1]]


def compound(rets):
    """Compounded return in percent from a list of monthly percent returns."""
    g = 1.0
    for r in rets:
        g *= 1 + r / 100
    return (g - 1) * 100


def run(lag=LAG, cost=COST, bills=BILLS, data=DATA, development=DEVELOPMENT, holdout=HOLDOUT):
    """{'Development': {...}, 'Holdout': {...}, 'failure': bool}. Holdout starts from the position
    held at the end of development; the run starts in bills."""
    months = list(data)
    held = "bills"
    out = {}
    for label, period in (("Development", development), ("Holdout", holdout)):
        gross, net, bh, switches = [], [], [], 0
        for m in months_in(period, data):
            i = months.index(m)
            if i - lag < 0:
                raise ValueError(f"no signal {lag} month(s) before {m}")
            signal = data[months[i - lag]][0]
            position = "equity" if signal > 0 else "bills"   # the rule: signal above 0 -> equity
            equity = data[m][1]
            r = equity if position == "equity" else bills
            switched = position != held
            switches += switched
            held = position
            gross.append(r)
            net.append(r - cost if switched else r)
            bh.append(equity)
        out[label] = {"gross": compound(gross), "net": compound(net),
                      "buy_and_hold": compound(bh), "switches": switches}
    out["failure"] = out["Holdout"]["net"] < out["Holdout"]["buy_and_hold"]
    return out


def main():
    res = run()
    print(f"Lag {LAG} month(s), cost {COST:.2f}% a switch, bills {BILLS:.2f}% a month")
    print(f"{'Period':<13}{'Rule gross':>11}{'Rule net':>10}{'Buy-and-hold':>14}{'Switches':>10}")
    for label in ("Development", "Holdout"):
        r = res[label]
        print(f"{label:<13}{r['gross']:>11.2f}{r['net']:>10.2f}{r['buy_and_hold']:>14.2f}{r['switches']:>10}")
    gap = res["Holdout"]["buy_and_hold"] - res["Holdout"]["net"]
    print(f"Failure rule (stop if holdout net trails buy-and-hold): "
          f"{'TRIGGERED' if res['failure'] else 'not triggered'} ({gap:.2f} points)")


if __name__ == "__main__":
    main()
