"""Reconstruct 09:45-12:00 for named dates and characterise the setup.

Purpose: decide whether hand-picked examples are representative of coded
Logic A, or whether the discretionary eye is applying an UNENCODED condition.
No filters are proposed here. This only measures and compares.
"""
import sys, math, statistics as st
sys.path.insert(0, "research/au200")
import phase1 as P1, phase2 as P2

WIN_START, WIN_END = 585, 720          # 09:45 .. 12:00


def sequence(days, d):
    D = days.get(d)
    if not D:
        return None
    return [(m,) + D[m] for m in sorted(D) if WIN_START <= m <= WIN_END]


def describe(days, m1, d):
    """Everything the strategy uses, plus the structural facts it ignores."""
    D = days.get(d)
    if not D:
        return dict(date=d, error="no data")
    s = P1.setup(D)
    if s is None:
        return dict(date=d, error="missing 09:50 or 10:00 candle")
    do, bh, bl, side = s
    r = dict(date=d, daily_open=do, body_hi=bh, body_lo=bl, side=side,
             c0950=D[P1.REF], c1000=D[P1.BODY],
             body=bh - bl, rng1000=D[P1.BODY][1] - D[P1.BODY][2])
    a = P1.logic_a(D, s)
    if not a:
        r["signal"] = None
        return r
    sd, em, entry = a
    r.update(signal=("LONG" if sd > 0 else "SHORT"), entry_m=em, entry=entry,
             bars_to_entry=(em - P1.BODY) // 5)
    bo, bhi, blo, bc = D[em]
    r.update(brk_o=bo, brk_h=bhi, brk_l=blo, brk_c=bc,
             brk_body=abs(bc - bo), brk_range=bhi - blo,
             brk_ratio=(abs(bc - bo) / (bhi - blo)) if bhi > blo else 0.0,
             beyond=(entry - bh) if sd > 0 else (bl - entry))

    # ---- structural facts the CODE DOES NOT USE ----
    pre = [m for m in sorted(D) if P1.BODY < m < em]
    # 1. did price attack the OPPOSITE side of the body before breaking out?
    opp_touch = any((D[m][2] <= bl) if sd > 0 else (D[m][1] >= bh) for m in pre)
    opp_close = any((D[m][3] < bl) if sd > 0 else (D[m][3] > bh) for m in pre)
    # 2. sweep/rejection: wick beyond the opposite edge but close back inside
    sweep = any((((D[m][2] < bl) and (D[m][3] > bl)) if sd > 0
                 else ((D[m][1] > bh) and (D[m][3] < bh))) for m in pre)
    # 3. where the 10:00 candle sits versus the 09:45-09:55 prior action
    prior = [D[m] for m in (585, 590, 595) if m in D]
    ph = max(x[1] for x in prior) if prior else None
    pl = min(x[2] for x in prior) if prior else None
    r.update(opp_touched_first=opp_touch, opp_closed_first=opp_close, sweep_before=sweep,
             prior_high=ph, prior_low=pl,
             body_above_prior=(bl > ph) if ph is not None else None,
             body_below_prior=(bh < pl) if pl is not None else None,
             breaks_prior_high=(entry > ph) if ph is not None else None,
             breaks_prior_low=(entry < pl) if pl is not None else None)
    # 4. displacement of the breakout candle versus the session so far
    rr = [D[m][1] - D[m][2] for m in sorted(D) if P1.BODY <= m <= em]
    r["displacement_x"] = ((bhi - blo) / st.mean(rr)) if rr and st.mean(rr) > 0 else None

    # ---- outcome ----
    path = [b for b in m1.get(d, []) if em + 5 <= b[0] <= P1.SESS_EXIT]
    mfe = mae = 0.0
    firsts = {}
    for m, o, h, l, c in path:
        up = (h - entry) if sd > 0 else (entry - l)
        dn = (entry - l) if sd > 0 else (h - entry)
        mfe = max(mfe, up); mae = max(mae, dn)
        for t in (10, 20, 30):
            if t not in firsts and up >= t:
                firsts[t] = m
    fl = P1.first_flip(D, s, sd, em)
    r.update(mfe=mfe, mae=mae, first10=firsts.get(10), first20=firsts.get(20),
             first30=firsts.get(30),
             opp_close_m=(fl[0] if fl else None), opp_close_px=(fl[1] if fl else None))
    ft = P2.first_touch(path, entry, 20)
    r["pm20"] = ft[0]
    return r


def print_sequence(days, d):
    seq = sequence(days, d)
    print(f"\n  09:45-12:00 sequence, {d}")
    print(f"  {'time':>6} {'open':>9} {'high':>9} {'low':>9} {'close':>9}  note")
    D = days[d]; s = P1.setup(D)
    a = P1.logic_a(D, s) if s else None
    for m, o, h, l, c in seq:
        note = ""
        if m == P1.REF: note = "<- 09:50  DAILY_OPEN = open"
        elif m == P1.BODY: note = "<- 10:00  body candle"
        elif a and m == a[1]: note = f"<- LOGIC A {'LONG' if a[0]>0 else 'SHORT'} entry @ close"
        print(f"  {m//60:02d}:{m%60:02d} {o:>9.1f} {h:>9.1f} {l:>9.1f} {c:>9.1f}  {note}")


def report(days, m1, d):
    r = describe(days, m1, d)
    if "error" in r:
        print(f"\n=== {d} === {r['error']}"); return r
    print(f"\n{'='*94}\n=== {d} ===")
    print(f"  09:50 OHLC   {r['c0950'][0]:.1f} / {r['c0950'][1]:.1f} / {r['c0950'][2]:.1f} / {r['c0950'][3]:.1f}")
    print(f"  10:00 OHLC   {r['c1000'][0]:.1f} / {r['c1000'][1]:.1f} / {r['c1000'][2]:.1f} / {r['c1000'][3]:.1f}")
    print(f"  DAILY_OPEN   {r['daily_open']:.1f}      BODY_HIGH {r['body_hi']:.1f}   BODY_LOW {r['body_lo']:.1f}"
          f"   body {r['body']:.1f}   10:00 range {r['rng1000']:.1f}")
    print(f"  SIDE         {r['side']}")
    if not r.get("signal"):
        print("  LOGIC A      no qualifying close before 15:50"); return r
    print(f"  LOGIC A      {r['signal']} at {r['entry_m']//60:02d}:{r['entry_m']%60:02d}  entry {r['entry']:.1f}"
          f"   ({r['bars_to_entry']} candles after 10:00, {r['beyond']:.1f} pts beyond the body)")
    print(f"  breakout     body {r['brk_body']:.1f} / range {r['brk_range']:.1f} = ratio {r['brk_ratio']:.2f}"
          f"   displacement {r['displacement_x']:.2f}x mean session candle")
    f = lambda x: f"{x//60:02d}:{x%60:02d}" if x else "never"
    print(f"  MFE {r['mfe']:.1f}   MAE {r['mae']:.1f}   +10 {f(r['first10'])}   +20 {f(r['first20'])}   +30 {f(r['first30'])}")
    print(f"  first opposite-body close: {f(r['opp_close_m'])}"
          + (f" @ {r['opp_close_px']:.1f}" if r['opp_close_px'] else ""))
    print(f"  +-20 first passage: {r['pm20']}")
    print(f"  -- structure the CODE IGNORES --")
    print(f"     price attacked the opposite body edge before entry : {r['opp_touched_first']}")
    print(f"     ...and CLOSED beyond it before entry               : {r['opp_closed_first']}")
    print(f"     sweep/rejection of the opposite edge before entry  : {r['sweep_before']}")
    print(f"     10:00 body clear of the 09:45-09:55 range          : "
          f"{r['body_above_prior'] if r['signal']=='LONG' else r['body_below_prior']}")
    print(f"     entry also breaks the 09:45-09:55 extreme          : "
          f"{r['breaks_prior_high'] if r['signal']=='LONG' else r['breaks_prior_low']}")
    return r
