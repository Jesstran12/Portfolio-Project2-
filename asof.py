"""As-of panel: a provenance gate on published prices, then each fund's signal.

Standard library only. Edit the inputs at the top; everything below is computed from them.
Run: python3 asof.py
"""

# ---------------------------------------------------------------- editable inputs
DECISION_DATE = "2026-03-31"  # a row is knowable only if published on or before this day

# row, ticker, month measured, published on, price (per 100 face, one-year zero)
TABLE = [
    (1,  "AAA", "2026-01", "2026-02-10", 101.0),
    (2,  "AAA", "2026-02", "2026-03-10", 104.0),
    (3,  "AAA", "2026-03", "2026-04-10", 109.0),
    (4,  "AAA", "2026-02", "2026-03-25", 103.0),
    (5,  "BBB", "2026-01", "2026-02-10", 98.0),
    (6,  "BBB", "2026-02", "2026-03-10", 97.0),
    (7,  "BBB", "2026-02", "2026-03-10", 97.0),
    (8,  "BBB", "2026-03", "2026-04-10", 92.0),
    (9,  "CCC", "2026-01", "2026-02-10", 110.0),
    (10, "CCC", "2026-02", "2026-04-05", 112.0),
    (11, "",    "2026-02", "2026-03-10", 99.0),
    (12, "CCC", "2026-02", "2026-03-10", 111.0),
]
# ---------------------------------------------------------------- end of inputs


def quarantine_no_ticker(rows):
    """Rule 1: set aside any row with no ticker."""
    return [r for r in rows if r[1].strip()], [r for r in rows if not r[1].strip()]


def remove_exact_duplicates(rows):
    """Rule 2: drop a row identical to an earlier one in every field but its row number."""
    seen, kept, removed = set(), [], []
    for r in rows:
        (removed if r[1:] in seen else kept).append(r)
        seen.add(r[1:])
    return kept, removed


def remove_published_after(rows, date):
    """Rule 3: drop rows published after the decision date (ISO dates compare as text)."""
    return [r for r in rows if r[3] <= date], [r for r in rows if r[3] > date]


def keep_latest_publication(rows):
    """Rule 4: for each ticker and month, keep only the latest publication (a revision)."""
    latest = {}
    for r in rows:
        key = (r[1], r[2])
        if key not in latest or r[3] > latest[key][3]:
            latest[key] = r
    kept = [r for r in rows if latest[(r[1], r[2])] is r]
    return kept, [r for r in rows if latest[(r[1], r[2])] is not r]


def signals(rows):
    """Per ticker: (latest month, previous month, percent change), or None if under two months."""
    out = {}
    for ticker in sorted({r[1] for r in rows}):
        by_month = sorted((r[2], r[4]) for r in rows if r[1] == ticker)
        if len(by_month) < 2:
            out[ticker] = None
            continue
        (prev_m, prev_p), (last_m, last_p) = by_month[-2], by_month[-1]
        out[ticker] = (last_m, prev_m, (last_p / prev_p - 1) * 100)
    return out


def print_rows(rows):
    print(f"  {'Row':>3}  {'Ticker':<6}  {'Month':<7}  {'Published':<10}  {'Price':>6}")
    for r in sorted(rows):
        print(f"  {r[0]:>3}  {r[1] or '-':<6}  {r[2]:<7}  {r[3]:<10}  {r[4]:>6.1f}")


def print_signals(title, sig):
    print(title)
    for ticker, s in sig.items():
        if s is None:
            print(f"  {ticker}: fewer than two months, no signal")
        else:
            last_m, prev_m, pct = s
            print(f"  {ticker}: {pct:+.2f}%  ({prev_m} -> {last_m})")


def main():
    rules = [
        ("1 quarantine: no ticker", quarantine_no_ticker),
        ("2 remove: exact duplicate", remove_exact_duplicates),
        (f"3 remove: published after {DECISION_DATE}", lambda rs: remove_published_after(rs, DECISION_DATE)),
        ("4 remove: superseded by a later revision", keep_latest_publication),
    ]
    rows = list(TABLE)
    print(f"Row funnel (decision date {DECISION_DATE})")
    print(f"  start: {len(rows)} rows")
    for name, rule in rules:
        rows, out = rule(rows)
        nums = ", ".join(str(r[0]) for r in out) or "none"
        print(f"  rule {name}: {len(out)} row(s) [{nums}] -> {len(rows)} left")

    print(f"\nAs-of panel ({len(rows)} rows)")
    print_rows(rows)
    print()
    print_signals(f"Signal as of {DECISION_DATE} (knowable rows only)", signals(rows))

    # naive: same cleaning, but no date gate - every ticker-month's latest publication ever
    naive = TABLE
    for rule in (quarantine_no_ticker, remove_exact_duplicates, keep_latest_publication):
        naive, _ = rule(naive)
    print()
    print_signals("Naive signal (latest publication of every row, publication date ignored)",
                  signals(naive))


if __name__ == "__main__":
    main()
