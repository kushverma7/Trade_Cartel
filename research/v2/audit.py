"""STEP 1 — DATA AUDIT. Nothing is swept until this runs and is read.

This exists because of BUG-039: a proxy level was used for three years of
"backtesting" without anyone checking what it resolved to, or on how many
sessions it was even defined.
"""
import csv, datetime as dt, zoneinfo, statistics as st
from collections import defaultdict, Counter

UTC = dt.timezone.utc
MEL = zoneinfo.ZoneInfo("Australia/Melbourne")
U = "/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/"
FILES = {"1m": U + "c1e55d1f-au200_aud_1m_4.csv",
         "5m": U + "30348eaf-au200_aud_5m.csv",
         "5m_b": U + "38c3a0f5-au200_aud_5m.csv",
         "15m": U + "0f9625c9-au200_aud_15m.csv"}


def load(path):
    out = []
    for r in csv.DictReader(open(path)):
        t = dt.datetime.strptime(r["timestamp"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
        out.append((t.astimezone(MEL), float(r["open"]), float(r["high"]),
                    float(r["low"]), float(r["close"]), float(r["volume"] or 0)))
    out.sort()
    return out


def audit(tag, rows):
    byday = defaultdict(list)
    for r in rows:
        byday[r[0].date()].append(r)
    days = sorted(byday)
    hours = Counter(r[0].hour for r in rows)
    firsts = Counter(min(b[0] for b in byday[d]).strftime("%H:%M") for d in days)
    overnight = [d for d in days if min(b[0] for b in byday[d]).hour < 9]
    print(f"\n=== {tag} ===")
    print(f"  bars {len(rows):,}   sessions {len(days)}   {days[0]} .. {days[-1]}")
    print(f"  Melbourne hours present: {sorted(hours)}")
    print(f"  session first bar (top 5): {firsts.most_common(5)}")
    print(f"  sessions with pre-09:00 bars: {len(overnight)}"
          + (f"  ({overnight[0]} .. {overnight[-1]})" if overnight else ""))
    # weekday-only sanity
    wk = Counter(d.weekday() for d in days)
    print(f"  weekday counts (Mon=0): {dict(sorted(wk.items()))}")
    # duplicate / gap check inside the cash session
    dup = sum(1 for d in days if len({b[0] for b in byday[d]}) != len(byday[d]))
    print(f"  sessions containing duplicate timestamps: {dup}")
    # ANCHOR TABLE — the check that was missing
    print("  anchor availability and distance from the 10:00 open:")
    anchors = {"00:00": 0, "05:00": 300, "07:00": 420, "09:00": 540,
               "09:50": 590, "10:00": 600}
    for lab, mn in anchors.items():
        vals = []
        defined = 0
        for d in days:
            bs = byday[d]
            a = next((b[1] for b in bs if b[0].hour * 60 + b[0].minute >= mn), None)
            t10 = next((b[1] for b in bs if b[0].hour * 60 + b[0].minute >= 600), None)
            # anchor must be at or BEFORE 10:00 to be usable as a reference
            exact = next((b[1] for b in bs if b[0].hour * 60 + b[0].minute == mn), None)
            if exact is not None:
                defined += 1
            if a is not None and t10 is not None:
                vals.append(abs(a - t10))
        med = st.median(vals) if vals else float("nan")
        mean = st.mean(vals) if vals else float("nan")
        print(f"    {lab}: exact bar on {defined:5d}/{len(days)} sessions"
              f"   |anchor - 10:00 open| median {med:6.2f}  mean {mean:6.2f}")
    return byday


if __name__ == "__main__":
    for tag, path in FILES.items():
        try:
            audit(tag, load(path))
        except Exception as e:
            print(f"\n=== {tag} === FAILED: {e}")
