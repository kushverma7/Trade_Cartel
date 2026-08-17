"""QUARTER LEVEL -> SWEEP -> MSS -> RETEST. The staged test.

The user's claim: "Never trade a Quarter level just because price reaches or
crosses it. Trade the confirmed failure after liquidity is taken."

That is an A/B/C/D ladder. Each stage ADDS one gate, everything else fixed, so
the marginal value of each gate is read directly off the table:

  A  touch      price reaches the quarter level                (the naive trade)
  B  sweep      price trades THROUGH it (liquidity taken)
  C  + MSS      structure breaks back the other way
  D  + displ.   that break is a displacement bar, not a drift
  E  + retest   price returns to the level and holds     (the full model)

If the claim is right, E beats A by a wide margin. If A ~ E, the gates are
ceremony. Steps 5 (VIX) and 6 (Mag 7) CANNOT be tested — no such data in this
repo — and their absence is reported, not silently dropped.

Quarter grid (yotov_quarters_theory.md convention, ratio 10:1, 4-way):
  large quarter = 250 index points, small quarter = 25 points,
  completion tolerance = one small quarter = 25 points.
"""
import sys, csv, gzip, math, datetime as dt, zoneinfo, statistics as st, itertools
sys.path.insert(0, "/home/user/Trade_Cartel/research/v2")
import engine
from collections import defaultdict

MEL = zoneinfo.ZoneInfo("Australia/Melbourne")
UTC = dt.timezone.utc


def load(path, tzname):
    tz = zoneinfo.ZoneInfo(tzname)
    rows = []
    with gzip.open(path, "rt") as f:
        for r in csv.DictReader(f):
            t = dt.datetime.strptime(r["timestamp"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
            rows.append((t.astimezone(tz), float(r["open"]), float(r["high"]),
                         float(r["low"]), float(r["close"])))
    rows.sort()
    return rows


def atr(bars, n=14):
    out, tr, a = [], [], None
    for i, b in enumerate(bars):
        x = b[2] - b[3] if i == 0 else max(b[2]-b[3], abs(b[2]-bars[i-1][4]), abs(b[3]-bars[i-1][4]))
        tr.append(x)
        if i < n - 1:
            out.append(None); continue
        a = sum(tr[:n]) / n if a is None else (a * (n - 1) + x) / n
        out.append(a)
    return out


def swings(bars, n):
    """confirmed swing highs / lows: index -> latest confirmed value"""
    hi = [None] * len(bars)
    lo = [None] * len(bars)
    ch = cl = None
    for i in range(len(bars)):
        j = i - n
        if j >= n:
            w = bars[j-n:j+n+1]
            if bars[j][2] == max(b[2] for b in w):
                ch = bars[j][2]
            if bars[j][3] == min(b[3] for b in w):
                cl = bars[j][3]
        hi[i] = ch
        lo[i] = cl
    return hi, lo


def run(bars, stage, large=250.0, tol=25.0, swing_n=5, displ=1.2,
        retest_bars=24, mss_bars=24, rr=2.0, cost=2.0, target="quarter",
        stop_pad=2.0, min_r=3.0, max_r=200.0):
    A = atr(bars)
    SH, SL = swings(bars, swing_n)
    trades = []
    state = 0            # 0 idle, +-1 swept, +-2 mss confirmed
    swept_lvl = swept_ext = mss_ref = None
    t0 = 0
    for i in range(swing_n * 2 + 20, len(bars) - 1):
        t, o, h, l, c = bars[i]
        a = A[i]
        if a is None or a <= 0:
            continue
        # nearest large quarter level
        lvl = round(c / large) * large
        near = abs(c - lvl) <= tol

        if state == 0:
            if not near:
                continue
            # ---- A: touch. the naive entry, taken immediately at the level ----
            if stage == "A":
                s = 1 if c < lvl else -1          # fade toward the level
                stop = (l - stop_pad) if s > 0 else (h + stop_pad)
                _emit(trades, bars, i, s, c, stop, lvl, large, rr, cost, target, min_r, max_r)
                continue
            # ---- B onward: require the level to be SWEPT ----
            if l < lvl - 0.0 and c > lvl:         # sell-side sweep, closed back above
                state, swept_lvl, swept_ext, t0 = 1, lvl, l, i
                mss_ref = SH[i]
            elif h > lvl + 0.0 and c < lvl:       # buy-side sweep, closed back below
                state, swept_lvl, swept_ext, t0 = -1, lvl, h, i
                mss_ref = SL[i]
            if state != 0 and stage == "B":
                s = state
                stop = (swept_ext - stop_pad) if s > 0 else (swept_ext + stop_pad)
                _emit(trades, bars, i, s, c, stop, swept_lvl, large, rr, cost, target, min_r, max_r)
                state = 0
            continue

        if abs(state) == 1:
            swept_ext = min(swept_ext, l) if state > 0 else max(swept_ext, h)
            if i - t0 > mss_bars:
                state = 0
                continue
            if mss_ref is None:
                mss_ref = SH[i] if state > 0 else SL[i]
                continue
            broke = (c > mss_ref) if state > 0 else (c < mss_ref)
            if not broke:
                continue
            # ---- D: the break must be a displacement bar ----
            if stage in ("D", "E") and (h - l) < displ * a:
                continue
            if stage in ("C", "D"):
                s = state
                stop = (swept_ext - stop_pad) if s > 0 else (swept_ext + stop_pad)
                _emit(trades, bars, i, s, c, stop, swept_lvl, large, rr, cost, target, min_r, max_r)
                state = 0
                continue
            state = 2 * (1 if state > 0 else -1)
            t0 = i
            continue

        if abs(state) == 2:
            s = 1 if state > 0 else -1
            if i - t0 > retest_bars:
                state = 0
                continue
            back = (l <= swept_lvl + tol) if s > 0 else (h >= swept_lvl - tol)
            hold = (c > swept_lvl) if s > 0 else (c < swept_lvl)
            if back and hold:
                stop = (min(swept_ext, l) - stop_pad) if s > 0 else (max(swept_ext, h) + stop_pad)
                _emit(trades, bars, i, s, c, stop, swept_lvl, large, rr, cost, target, min_r, max_r)
                state = 0
            elif not hold:
                state = 0
    return trades


def _emit(trades, bars, i, s, entry, stop, lvl, large, rr, cost, target, min_r, max_r):
    risk = (entry - stop) if s > 0 else (stop - entry)
    if not (min_r <= risk <= max_r):
        return
    if target == "quarter":
        tgt = lvl + s * large * 0.5
    else:
        tgt = entry + s * risk * rr
    rew = (tgt - entry) if s > 0 else (entry - tgt)
    if rew <= 0:
        return
    pnl = None
    for j in range(i + 1, min(i + 500, len(bars))):
        _, _, hh, ll, cc = bars[j]
        adv = ll if s > 0 else hh
        fav = hh if s > 0 else ll
        if s * (adv - stop) <= 0:
            pnl = s * (stop - entry) - cost; break
        if s * (fav - tgt) >= 0:
            pnl = s * (tgt - entry) - cost; break
    if pnl is None:
        j = min(i + 499, len(bars) - 1)
        pnl = s * (bars[j][4] - entry) - cost
    trades.append(dict(day=bars[i][0].date(), s=s, pnl=pnl, risk=risk))


if __name__ == "__main__":
    SETS = [("AU200 5m",  "data/au200_5m.csv.gz",  "Australia/Melbourne", 250.0, 25.0, 2.0),
            ("US30 15m",  "data/us30_15m.csv.gz",  "America/New_York",    250.0, 25.0, 3.0),
            ("XAUUSD 15m","data/xauusd_15m.csv.gz","America/New_York",     25.0,  2.5, 0.5)]
    for name, path, tzn, large, tol, cost in SETS:
        bars = load(path, tzn)
        print(f"\n{'='*84}\n{name}  —  {len(bars):,} bars  {bars[0][0].date()} .. {bars[-1][0].date()}")
        print(f"large quarter = {large}, tolerance = {tol}, cost = {cost}")
        print(f"{'='*84}")
        print(f"{'stage':44} {'n':>6} {'PF':>7} {'win%':>6} {'net':>10} {'avg':>7} {'t':>7}")
        for stage, label in (("A", "A  touch the quarter level (naive)"),
                             ("B", "B  + liquidity swept"),
                             ("C", "C  + market structure shift"),
                             ("D", "D  + displacement on the MSS bar"),
                             ("E", "E  + retest holds  (the full model)")):
            tr = run(bars, stage, large=large, tol=tol, cost=cost)
            m = engine.metrics(tr, min_n=25, strict=False)
            if m:
                print(f"{label:44} {m['n']:>6} {m['pf']:>7.3f} {m['win']:>5.1f}% "
                      f"{m['net']:>10.1f} {m['avg']:>+7.2f} {m['t']:>+7.2f}")
            else:
                print(f"{label:44} {len(tr):>6}  (under 25 trades — not reported)")
