"""STEP 1b — which reference levels ACTUALLY exist, conditioned on presence.

The naive version of this check reports median 0.00 for every anchor, because
`the first bar at or after 07:00` falls through to the 10:00 bar on sessions
that have no overnight data. That fall-through IS bug-039. Condition on the
anchor genuinely existing, and report coverage alongside distance.
"""
import csv, datetime as dt, zoneinfo, statistics as st
from collections import defaultdict

UTC = dt.timezone.utc
MEL = zoneinfo.ZoneInfo("Australia/Melbourne")
SRC = "/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/30348eaf-au200_aud_5m.csv"

byday = defaultdict(list)
for r in csv.DictReader(open(SRC)):
    t = dt.datetime.strptime(r["timestamp"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC).astimezone(MEL)
    byday[t.date()].append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
for d in byday:
    byday[d].sort()

# a CASH session = has a 10:00 bar and at least 60 bars from 10:00 to 16:00
def cash(d):
    bs = [b for b in byday[d] if 600 <= b[0].hour * 60 + b[0].minute < 960]
    return bs if bs and bs[0][0].hour * 60 + bs[0][0].minute == 600 and len(bs) >= 60 else None

DAYS = [d for d in sorted(byday) if cash(d)]
print(f"cash sessions (10:00 bar present, >=60 bars to 16:00): {len(DAYS)}  "
      f"{DAYS[0]} .. {DAYS[-1]}")

prev_close = {}
prev = None
for d in DAYS:
    if prev is not None:
        prev_close[d] = cash(prev)[-1][4]
    prev = d

print("\nanchor                       defined on      |anchor - 10:00 open|")
print("                             (of %d)     median   mean    p90" % len(DAYS))
rows = []
for lab, mn in [("00:00 open", 0), ("05:00 open", 300), ("07:00 open", 420), ("09:50 open", 590)]:
    v = []
    for d in DAYS:
        a = next((b[1] for b in byday[d] if b[0].hour * 60 + b[0].minute == mn), None)
        if a is not None:
            v.append(abs(a - cash(d)[0][1]))
    rows.append((lab, len(v), v))
v = [abs(prev_close[d] - cash(d)[0][1]) for d in DAYS if d in prev_close]
rows.append(("PREV CASH CLOSE", len(v), v))
for lab, n, v in rows:
    if v:
        print("  %-26s %5d      %6.2f %6.2f %6.2f"
              % (lab, n, st.median(v), st.mean(v), sorted(v)[int(.9 * len(v)) - 1]))
    else:
        print("  %-26s %5d      --" % (lab, n))
