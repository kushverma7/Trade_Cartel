"""Identical structure, moved. Micro quarters, session quarters, grid phases.

The 22.5-minute micro-quarter boundaries (18:00, 18:22:30, 18:45, 19:07:30) do
not land on minute marks, so anchors here are built straight from the tick
stream at millisecond precision rather than from 1-minute bars. The 18:45 case
is checked against the bar-built version to confirm the two agree.

Nothing is tuned. Every run uses the frozen specification: bearish 15-minute
anchor, body in [1.00, 6.25], first completed 5-minute break in the following
30 minutes, entry within $6.25 of a $25 level, spread <= $1.50, SL 15.50 /
TP 25.50, liquidation 17:00 NY.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/microq3/code")
import engine as E
from engine import PTS

SL, TP = 15.5, 25.5
MID = (E.BID.astype(np.int64) + E.ASK.astype(np.int64)) // 2
pd.set_option("display.width", 240)

# day -> (first tick index, last+1) so slices never cross a day boundary
_DAYIDX = {}
for d in E.DAYS:
    d = int(d)
    a, b = E.DAYSLICE.get(d, (0, 0))
    if b > a:
        _DAYIDX[d] = (int(E.I0[a]), int(E.I1[b - 1]))


def tick_candle(day, s0, s1):
    """OHLC from ticks between s0 and s1 SECONDS past NY midnight on `day`."""
    rng = _DAYIDX.get(day)
    if rng is None:
        return None
    lo, hi = rng
    t0 = day * 86_400_000 + int(s0 * 1000)
    t1 = day * 86_400_000 + int(s1 * 1000)
    i = int(np.searchsorted(E.NY[lo:hi], t0, "left")) + lo
    j = int(np.searchsorted(E.NY[lo:hi], t1, "left")) + lo
    if j - i < 20:                       # need a real candle, not two prints
        return None
    seg = MID[i:j]
    return dict(o=int(seg[0]), c=int(seg[-1]), h=int(seg.max()), l=int(seg.min()),
                t_close=int(E.NY[j - 1]), n=j - i)


def run(anchor_s, alen_s=900, win_s=1800, step_s=300, phase=0.0,
        body_min=1.00, body_max=6.25, qd=6.25, spr=1.50):
    pnl, dates = [], []
    for day in _DAYIDX:
        a = tick_candle(day, anchor_s, anchor_s + alen_s)
        if a is None:
            continue
        o, c = a["o"] / PTS, a["c"] / PTS
        if c >= o:
            continue
        body = o - c
        if body < body_min or (body_max is not None and body > body_max):
            continue
        bhi, blo = o, c
        hit = None
        for s in range(anchor_s + alen_s, anchor_s + alen_s + win_s, step_s):
            cd = tick_candle(day, s, s + step_s)
            if cd is None:
                continue
            cc = cd["c"] / PTS
            if cc < blo:
                hit = (cd, False); break
            if cc > bhi:
                hit = (cd, True); break
        if hit is None:
            continue
        cd, long_ = hit
        k0 = int(np.searchsorted(E.NY, cd["t_close"], "right"))
        kend = E.session_end_index(day, 17 * 60)
        if kend is None or k0 >= kend:
            continue
        bid, ask = int(E.BID[k0]) / PTS, int(E.ASK[k0]) / PTS
        if spr is not None and ask - bid > spr:
            continue
        entry = ask if long_ else bid
        r = (entry - phase) % 25.0
        if qd is not None and min(r, 25.0 - r) > qd:
            continue
        res = E.resolve(k0, kend, long_, SL, TP)
        if res:
            pnl.append(res["pnl"]); dates.append(day)
    return E.stats(pnl), pnl


def line(tag, s, extra=""):
    if s["n"] == 0:
        return f"  {tag:<38}{0:>5}{'--':>9}{'--':>9}{'--':>9}{'--':>8}{'--':>9}  {extra}"
    return (f"  {tag:<38}{s['n']:>5}{s['pf']:>9.2f}{s['exp']:>9.2f}{s['net']:>9.1f}"
            f"{s['wr']:>7.0f}%{s['mdd']:>9.1f}  {extra}")


HDR = f"  {'':<38}{'n':>5}{'PF':>9}{'exp':>9}{'net':>9}{'WR':>8}{'maxDD':>9}"

print("VALIDATION — the tick-built anchor must reproduce the bar-built one")
s, _ = run(18 * 3600 + 45 * 60)
print(line("18:45 via millisecond tick candles", s, "bar-built: n=25 PF 5.13 net +386.7"))

print("\n" + "=" * 118)
print("MICRO QUARTERS — the 90-minute Q1 (18:00-19:30 NY) split into four 22.5-minute quarters.")
print("Identical structure at each: 15-minute anchor from the quarter's open, 30-minute window.")
print("=" * 118)
print(HDR)
MQ = [("MQ1  18:00:00", 18 * 3600), ("MQ2  18:22:30", 18 * 3600 + 22 * 60 + 30),
      ("MQ3  18:45:00", 18 * 3600 + 45 * 60), ("MQ4  19:07:30", 19 * 3600 + 7 * 60 + 30)]
rows = []
for nm, s0 in MQ:
    st, _ = run(s0)
    print(line(nm, st, "  <-- THE CLAIMED ONE" if "18:45" in nm else ""))
    rows.append(dict(quarter=nm, **{k: st[k] for k in ("n", "pf", "exp", "net", "wr", "mdd")}))
pd.DataFrame(rows).to_csv("research/microq3/results/S_microquarters.csv", index=False)

print("\n" + "=" * 118)
print("SESSION QUARTERS — the NY daily cycle's four 6-hour quarters, same 45-minute offset into each.")
print("Q1 18:00 Asia · Q2 00:00 London · Q3 06:00 NY AM · Q4 12:00 NY PM")
print("=" * 118)
print(HDR)
SESS = [("Q1 Asia      18:45", 18 * 3600 + 45 * 60), ("Q2 London    00:45", 45 * 60),
        ("Q3 NY AM     06:45", 6 * 3600 + 45 * 60), ("Q4 NY PM     12:45", 12 * 3600 + 45 * 60)]
rows = []
for nm, s0 in SESS:
    st, _ = run(s0)
    print(line(nm, st, "  <-- THE CLAIMED ONE" if "18:45" in nm else ""))
    rows.append(dict(session=nm, **{k: st[k] for k in ("n", "pf", "exp", "net", "wr", "mdd")}))
print("\n  and 45 minutes after each session's conventional open:")
for nm, s0 in (("Tokyo open   19:45", 19 * 3600 + 45 * 60), ("London open  03:45", 3 * 3600 + 45 * 60),
               ("NY open      10:15", 10 * 3600 + 15 * 60)):
    st, _ = run(s0)
    print(line(nm, st))
    rows.append(dict(session=nm, **{k: st[k] for k in ("n", "pf", "exp", "net", "wr", "mdd")}))
pd.DataFrame(rows).to_csv("research/microq3/results/S_sessions.csv", index=False)

print("\n" + "=" * 118)
print("PRICE-GRID PHASE — the identical $25 filter, grid slid off round numbers in $1 steps")
print("=" * 118)
print(HDR)
rows = []
for ph in range(0, 25):
    st, _ = run(18 * 3600 + 45 * 60, phase=float(ph))
    rows.append(dict(phase=ph, **{k: st[k] for k in ("n", "pf", "exp", "net", "wr", "mdd")}))
    if ph % 2 == 0 or ph == 23:
        print(line(f"grid at 25n + {ph}", st, "  <-- TRUE ROUND GRID" if ph == 0 else ""))
P = pd.DataFrame(rows); P.to_csv("research/microq3/results/S_gridphase.csv", index=False)
t = P[P.phase == 0].iloc[0]; o = P[P.phase != 0]
print(f"\n  round grid  PF {t.pf:.2f}   exp {t.exp:+.2f}   n {int(t.n)}")
print(f"  24 shifted  PF {o.pf.mean():.2f} +- {o.pf.std():.2f}   range {o.pf.min():.2f}..{o.pf.max():.2f}")
print(f"  shifted grids matching or beating the round one:  PF {int((o.pf>=t.pf).sum())} of 24"
      f"   ·  expectancy {int((o.exp>=t.exp).sum())} of 24")
print(f"  empirical p for roundness = {(int((o.pf>=t.pf).sum())+1)/25:.3f}")
print(f"  NOTE: adjacent phases share most of their trades, so these 24 are far from"
      f"\n        independent draws; the p above is optimistic, not conservative.")
