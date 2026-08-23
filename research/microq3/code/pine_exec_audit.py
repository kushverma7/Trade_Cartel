"""AUDIT part 2: what the Pine's EXECUTION MODEL changes, holding entries fixed.

Four differences between the pasted script and the tick research, each measured
on the same 25 signal days:

  1. TARGET OVERSHOOT. microq3.apply() books fav[j] -- the first real quote at
     or beyond the target -- so favourable overshoot is credited. The repo's
     other engines (research/quarters/code/system.py) treat the target as a
     resting limit filling AT the price. This measures my own reference number's
     optimism, not the Pine's.
  2. ZERO COST. The Pine declares no commission and no slippage, and
     process_orders_on_close fills at the bar CLOSE, which is a mid/last print.
     The research pays the real ask (long) or bid (short). This prices that gap.
  3. STALE ANCHOR. synthOpen/anchorReady/tradedThisAnchor are `var` and reset
     ONLY on the 18:45 bar. If 18:45 is missing but 18:55 is present, line 334
     ("if isAnchorLast and not na(synthOpen)") builds a body from a PREVIOUS
     day's open. Counts how often that can happen.
  4. MISSING DATA GATE. The research requires >= 5 one-minute bars inside
     18:45-19:00 (a["nmin"]). The Pine has no such check.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/microq3/code")
import engine as E, microq3 as M
from engine import PTS

SL, TP, HOLD = 15.5, 25.5, 720
sig = M.signals()
print("=" * 96)
print(f"EXECUTION MODEL AUDIT   DATA: {E.D}   n={len(sig)} signals")
print("=" * 96)


def resolve(trades, sl, tp, hold, cap_tp=False, mid_entry=False):
    """Same first-passage as microq3.apply, with two switches:
    cap_tp     -- book the target at exactly +tp, never the overshoot
    mid_entry  -- enter at the midpoint (the Pine's bar close) instead of
                  paying the ask/bid, and mark out on the midpoint too."""
    sl_i, tp_i = int(round(sl * PTS)), int(round(tp * PTS))
    out = []
    for t in trades:
        if mid_entry:
            k0, kend, long_ = t["k0"], t["kend"], t["long"]
            e = (int(E.BID[k0]) + int(E.ASK[k0])) // 2
            mid = (E.BID[k0:kend].astype(np.int64) +
                   E.ASK[k0:kend].astype(np.int64)) // 2
            fav = (mid - e) if long_ else (e - mid)
        else:
            fav = t["fav"]
        tms = t["tms"]
        n = int(np.searchsorted(tms, tms[0] + hold * 60_000, "right"))
        if n <= 0:
            continue
        fav = fav[:n]
        rmax, rmin = np.maximum.accumulate(fav), np.minimum.accumulate(fav)
        i_tp = int(np.searchsorted(rmax, tp_i, "left"));  i_tp = i_tp if i_tp < n else 10**9
        i_sl = int(np.searchsorted(-rmin, sl_i, "left")); i_sl = i_sl if i_sl < n else 10**9
        j = min(i_tp, i_sl)
        if j >= 10**9:
            pnl, why = int(fav[-1]), "TIME"
        elif j == i_tp:
            pnl, why = (tp_i if cap_tp else int(fav[j])), "TP"
        else:
            pnl, why = int(fav[j]), "SL"
        out.append(dict(date=t["date"], pnl=pnl / PTS, why=why))
    return pd.DataFrame(out)


def line(label, d):
    s = E.stats(d.pnl.values)
    print(f"  {label:<44}n={s['n']:>3}  PF={s['pf']:>6.3f}  WR={s['wr']:>5.1f}%"
          f"  net={s['net']:>+8.1f}  maxDD={s['mdd']:>5.1f}")
    return s


print("\n1 + 2. FILL MODEL, entries held fixed")
base = line("research: pay spread, credit TP overshoot", resolve(sig, SL, TP, HOLD))
cap = line("research: pay spread, TP as resting limit",
           resolve(sig, SL, TP, HOLD, cap_tp=True))
mid = line("PINE:     mid fill, credit TP overshoot",
           resolve(sig, SL, TP, HOLD, mid_entry=True))
midcap = line("PINE:     mid fill, TP as resting limit",
              resolve(sig, SL, TP, HOLD, cap_tp=True, mid_entry=True))
print(f"\n  target overshoot is worth   {base['net'] - cap['net']:+.2f} "
      f"over {base['n']} trades ({(base['net']-cap['net'])/base['n']:+.3f}/trade)")
print(f"  not paying the spread worth {mid['net'] - base['net']:+.2f} "
      f"over {base['n']} trades ({(mid['net']-base['net'])/base['n']:+.3f}/trade)")
print(f"  both together              {mid['net'] - cap['net']:+.2f}  "
      f"-> PF {cap['pf']:.3f} becomes {mid['pf']:.3f}")

sp = np.array([t["entry_spread"] for t in sig])
print(f"\n  entry spread on the 25 signals: median ${np.median(sp):.3f}  "
      f"mean ${sp.mean():.3f}  max ${sp.max():.3f}")

print("\n3. STALE-ANCHOR EXPOSURE  (18:55 present but 18:45 missing)")
n1845 = n1855 = stale = short_anchor = 0
for day in E.DAYS:
    day = int(day)
    a = E.candle(day, 18 * 60 + 45, 18 * 60 + 50)
    c = E.candle(day, 18 * 60 + 55, 19 * 60)
    full = E.candle(day, 18 * 60 + 45, 19 * 60)
    n1845 += a is not None
    n1855 += c is not None
    if c is not None and a is None:
        stale += 1
    if full is not None and full["nmin"] < 5:
        short_anchor += 1
print(f"  days with an 18:45 candle : {n1845}")
print(f"  days with an 18:55 candle : {n1855}")
print(f"  18:55 without 18:45       : {stale}   <- stale synthetic body fires here")

print("\n4. DATA-QUALITY GATE THE PINE LACKS  (research needs >=5 one-minute bars)")
print(f"  days where 18:45-19:00 has <5 minutes of ticks: {short_anchor}")
