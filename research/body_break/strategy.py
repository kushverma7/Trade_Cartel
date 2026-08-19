"""10 AM Body Break — signal generation. Rules exactly as specified.

NO SUBSTITUTIONS. DAILY_OPEN is the OPEN of the 09:50 Melbourne candle and
nothing else. If that candle is absent the day is UNTESTABLE and is excluded
and counted, never silently replaced. Substituting a differently-named "daily
open" is BUG-039 in this repo: it turned a simulated PF 5.03 into a live 0.444.

Timezone: zoneinfo Australia/Melbourne, which is DST-correct. Fixed UTC offsets
are forbidden — that is BUG-037, which split one rule into two apparent setups
for half of every year.
"""
from __future__ import annotations
import csv, gzip, datetime as dt
from dataclasses import dataclass, field
from zoneinfo import ZoneInfo
from collections import defaultdict

UTC = dt.timezone.utc
MEL = ZoneInfo("Australia/Melbourne")

REF_MIN   = 9 * 60 + 50      # 09:50 — DAILY_OPEN candle
BODY_MIN  = 10 * 60          # 10:00 — reference body candle
CUTOFF    = 16 * 60          # no new Logic A / flip signal at or after 16:00


@dataclass
class Bar:
    m: int          # minutes past midnight, Melbourne
    o: float; h: float; l: float; c: float
    t: dt.datetime  # UTC


@dataclass
class Day:
    date: dt.date
    bars: list
    daily_open: float | None = None
    body_hi: float | None = None
    body_lo: float | None = None
    body_open: float | None = None
    body_close: float | None = None
    body_high_wick: float | None = None
    body_low_wick: float | None = None
    side: str = "UNTESTABLE"        # ABOVE | BELOW | STRADDLE | UNTESTABLE
    reason: str = ""


def load(path: str) -> dict:
    op = gzip.open if path.endswith(".gz") else open
    byday = defaultdict(list)
    seen = set()
    dup = 0
    with op(path, "rt") as f:
        for r in csv.DictReader(f):
            ts = r["timestamp"].strip()
            try:
                t = dt.datetime.fromisoformat(ts)
            except ValueError:
                t = dt.datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
            if t.tzinfo is None:
                raise ValueError(f"naive timestamp {ts!r} — a fixed offset cannot be assumed")
            t = t.astimezone(UTC)
            if t in seen:
                dup += 1
                continue
            seen.add(t)
            lt = t.astimezone(MEL)          # DST-correct conversion, per bar
            byday[lt.date()].append(Bar(lt.hour * 60 + lt.minute,
                                        float(r["open"]), float(r["high"]),
                                        float(r["low"]), float(r["close"]), t))
    for d in byday:
        byday[d].sort(key=lambda b: b.m)
    return dict(days=byday, duplicates=dup)


def build_day(date, bars) -> Day:
    d = Day(date, bars)
    ref  = next((b for b in bars if b.m == REF_MIN), None)
    body = next((b for b in bars if b.m == BODY_MIN), None)
    if ref is None:
        d.reason = "no 09:50 candle"; return d
    if body is None:
        d.reason = "no 10:00 candle"; return d
    d.daily_open = ref.o                       # THE reference. Nothing else.
    d.body_open, d.body_close = body.o, body.c
    d.body_high_wick, d.body_low_wick = body.h, body.l
    d.body_hi = max(body.o, body.c)
    d.body_lo = min(body.o, body.c)
    if d.body_lo > d.daily_open:
        d.side = "ABOVE"
    elif d.body_hi < d.daily_open:
        d.side = "BELOW"
    else:
        d.side = "STRADDLE"
    return d


def logic_a(d: Day):
    """First completed close beyond the body in the SIDE direction. One per day."""
    if d.side not in ("ABOVE", "BELOW"):
        return None
    for b in d.bars:
        if b.m <= BODY_MIN or b.m >= CUTOFF:
            continue
        if d.side == "ABOVE" and b.c > d.body_hi:
            return (1, b)
        if d.side == "BELOW" and b.c < d.body_lo:
            return (-1, b)
    return None


def logic_b(d: Day):
    """The 10:00 candle itself."""
    if d.daily_open is None or d.body_open is None:
        return None
    b = next((x for x in d.bars if x.m == BODY_MIN), None)
    if b is None:
        return None
    if b.c > b.o and b.c > d.daily_open:
        return (1, b)
    if b.c < b.o and b.c < d.daily_open:
        return (-1, b)
    return None


def first_flip(d: Day, side: int, after_m: int):
    """One flip per day, opposite body boundary, completed close, before 16:00."""
    for b in d.bars:
        if b.m <= after_m or b.m >= CUTOFF:
            continue
        if side > 0 and b.c < d.body_lo:
            return b
        if side < 0 and b.c > d.body_hi:
            return b
    return None


def confirm(d: Day, flip_bar: Bar, flip_side: int, method: str):
    """C3 confirmations. Returns the entry bar, or None if never confirmed."""
    bars = [b for b in d.bars if b.m > flip_bar.m and b.m < CUTOFF]
    lvl = d.body_lo if flip_side < 0 else d.body_hi
    if method == "A":            # two consecutive closes beyond the boundary
        run = 1 if ((flip_bar.c < lvl) if flip_side < 0 else (flip_bar.c > lvl)) else 0
        for b in bars:
            ok = (b.c < lvl) if flip_side < 0 else (b.c > lvl)
            run = run + 1 if ok else 0
            if run >= 2:
                return b
        return None
    if method == "B":            # next candle also closes in the flip direction
        if not bars:
            return None
        b = bars[0]
        ok = (b.c < flip_bar.c) if flip_side < 0 else (b.c > flip_bar.c)
        return b if ok else None
    if method == "C":            # break beyond the flip candle's extreme
        ext = flip_bar.l if flip_side < 0 else flip_bar.h
        for b in bars:
            if (b.l < ext) if flip_side < 0 else (b.h > ext):
                return b
        return None
    raise ValueError(method)
