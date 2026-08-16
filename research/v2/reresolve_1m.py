"""STEP 5 — 1-minute re-resolution. The decisive execution check.

The sweep resolves exits on 5-minute bars, which means the order of the high and
the low inside a bar is unknown and the engine assumes the adverse extreme comes
first. That assumption is conservative but crude. This re-runs the SAME signals
and the SAME stop/target levels against the 1-minute series on the sessions where
1-minute data exists, so the intrabar path is known rather than assumed.

If a configuration's edge does not survive here, it was an artifact of the
5-minute resolution and must not be traded.
"""
import sys, csv, datetime as dt, zoneinfo, statistics as st
sys.path.insert(0, "/home/user/Trade_Cartel/research/v2")
import engine
from collections import defaultdict

UTC = dt.timezone.utc
MEL = zoneinfo.ZoneInfo("Australia/Melbourne")
M1 = "/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/c1e55d1f-au200_aud_1m_4.csv"

fine = defaultdict(list)
for r in csv.DictReader(open(M1)):
    t = dt.datetime.strptime(r["timestamp"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC).astimezone(MEL)
    mn = t.hour * 60 + t.minute
    if 600 <= mn < 960:
        fine[t.date()].append((mn, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
for d in fine:
    fine[d].sort()


def resolve_1m(day, entry_min, s, entry, stop, tp, trail, be_at, deadline, cost):
    """Same rules as engine.resolve, but walking the 1-minute path. The path
    starts at entry_min + 5, i.e. after the 5-minute signal bar has CLOSED."""
    path = [b for b in fine[day] if b[0] >= entry_min + 5]
    if not path:
        return None
    peak, cur, moved = entry, stop, False
    for mn, o, h, l, c in path:
        adv = l if s > 0 else h
        fav = h if s > 0 else l
        if s * (adv - cur) <= 0:
            return s * (cur - entry) - cost
        if tp is not None and s * (fav - tp) >= 0:
            return s * (tp - entry) - cost
        if be_at is not None and not moved and s * (fav - (entry + s * be_at)) >= 0:
            if s * (entry - cur) > 0:
                cur = entry
            moved = True
        if trail is not None:
            if s * (c - peak) > 0:
                peak = c
            t2 = peak - s * trail
            if s * (t2 - cur) > 0:
                cur = t2
        if mn >= deadline:
            return s * (c - entry) - cost
    return s * (path[-1][4] - entry) - cost
