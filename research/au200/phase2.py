"""AU200 Phase 2 — first-passage (ordering) analysis. Logic A entry unchanged.

The whole point: MFE/MAE symmetry does NOT settle direction. A trade can reach
+20 first and -30 later. This measures WHICH BARRIER IS TOUCHED FIRST.

AMBIGUITY IS RESOLVED ON 1-MINUTE DATA, not assumed. A 5-minute bar touching
both barriers is walked at 1-minute resolution. Only if a single 1-MINUTE bar
touches both does the trade become AMBIGUOUS - never resolved favourably.

For each trade and each X we record only WHICH SIDE WAS TOUCHED FIRST:
    UP | DOWN | NONE (neither by 15:55) | AMB
Everything else derives: a LONG wins on UP, a SHORT wins on DOWN. That also
makes the 10,000-run placebo cheap, because direction is just a relabelling.
"""
import csv, gzip, datetime as dt, random, statistics as st
from zoneinfo import ZoneInfo
from collections import defaultdict

UTC = dt.timezone.utc
MEL = ZoneInfo("Australia/Melbourne")
SESS_EXIT = 955
RAW1M = "data/raw_dukascopy_au200_1m.csv.gz"


def load_1m():
    d = defaultdict(list)
    for r in csv.DictReader(gzip.open(RAW1M, "rt")):
        t = dt.datetime.fromisoformat(r["timestamp"]).astimezone(MEL)
        d[t.date()].append((t.hour * 60 + t.minute, float(r["open"]), float(r["high"]),
                            float(r["low"]), float(r["close"])))
    for k in d:
        d[k].sort()
    return d


def first_touch(path, entry, x):
    """path = list of (minute,o,h,l,c) strictly after the entry bar closes.
    Returns (side, minute) with side in UP/DOWN/NONE/AMB."""
    up, dn = entry + x, entry - x
    for m, o, h, l, c in path:
        hi = h >= up
        lo = l <= dn
        if hi and lo:
            return "AMB", m
        if hi:
            return "UP", m
        if lo:
            return "DOWN", m
    return "NONE", None


def build_matrix(trades, m1, xs):
    """trades: dicts with date, entry_m (5m bar START), entry price.
    Path begins at entry_m+5, i.e. after the signal candle has CLOSED."""
    out = []
    for t in trades:
        bars = m1.get(t["date"], [])
        path = [b for b in bars if t["entry_m"] + 5 <= b[0] <= SESS_EXIT]
        row = {}
        for x in xs:
            row[x] = first_touch(path, t["entry"], x)
        out.append(dict(t, ft=row))
    return out
