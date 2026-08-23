"""AUDIT: "Micro-Q3 Smoother — GOLD [Recovered Research Logic]" Pine script.

The script's quarter filter is wired as a SEARCH, not a filter -- BUG-047, the
same defect found in the 10AM Quarter Matrix v1 in Phase 7 of this branch.

    tradePermission = ... and quarterOK and ... not tradedThisAnchor
    aShort = enableAShort and tradePermission and close < bodyLow

`tradedThisAnchor` is set only when a trade actually FIRES. So if the first
completed close below the body low is too far from a $25 level, no trade fires,
the day stays open, and the script keeps scanning 19:10, 19:15, 19:20 ... until
a break lands near a quarter. The rule it implements is therefore "wait until
price is near a quarter, THEN take a break", not the researched rule.

The researched rule (research/microq3/code/microq3.py) takes the FIRST break and
then, if it fails the quarter or spread test, CONSUMES THE DAY.

This measures the difference on the same ticks, fills and exits.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/microq3/code")
import engine as E
from engine import PTS
import microq3 as M


def signals_pine(**kw):
    """Identical to microq3.signals EXCEPT the day is not consumed by a break
    that fails the quarter/spread test -- scanning continues."""
    p = dict(M.DEF); p.update(kw)
    out = []
    for day in E.DAYS:
        day = int(day)
        a = E.candle(day, p["anchor_start"], p["anchor_start"] + p["anchor_len"], p["px"])
        if a is None or a["nmin"] < max(3, p["anchor_len"] // 3):
            continue
        o, c = a["o"] / PTS, a["c"] / PTS
        body = abs(c - o)
        bear = c < o
        if not bear or body < p["body_min"] or body > p["body_max"]:
            continue
        bhi, blo = o, c

        for cd in E.five_min_candles(day, p["win_from"], p["win_to"], p["px"]):
            cc = cd["c"] / PTS
            long_ = None
            if cc < blo:
                long_ = False
            elif cc > bhi:
                long_ = True
            if long_ is None:
                continue                        # not a break at all -- keep scanning
            k0 = int(np.searchsorted(E.NY, cd["t_close"], "right"))
            kend = E.session_end_index(day, p["eod_hm"])
            if kend is None or k0 >= kend:
                break
            bid, ask = int(E.BID[k0]) / PTS, int(E.ASK[k0]) / PTS
            entry = ask if long_ else bid
            r = (entry - p["grid_phase"]) % p["grid"]
            dq = min(r, p["grid"] - r)
            if dq > p["qdist"]:
                continue                        # <-- BUG-047: keep scanning
            ex = E.BID[k0:kend] if long_ else E.ASK[k0:kend]
            e_i = int(E.ASK[k0]) if long_ else int(E.BID[k0])
            fav = (ex.astype(np.int64) - e_i) if long_ else (e_i - ex.astype(np.int64))
            out.append(dict(
                day=day, date=pd.Timestamp(day * 86400000, unit="ms").date(),
                anchor_open=o, anchor_close=c, anchor_high=a["h"] / PTS,
                anchor_low=a["l"] / PTS, anchor_body=body,
                anchor_range=(a["h"] - a["l"]) / PTS, anchor_dir="BEAR",
                body_high=bhi, body_low=blo,
                sig_hm=cd["hm_start"], sig_open=cd["o"] / PTS, sig_close=cc,
                t_sig_close=cd["t_close"],
                kind="FLIP_LONG" if long_ else "A_SHORT",
                long=long_, t_entry=int(E.NY[k0]), entry_bid=bid, entry_ask=ask,
                entry_spread=ask - bid, entry=entry,
                nearest25=round(entry / p["grid"]) * p["grid"], dist25=dq,
                k0=k0, kend=kend, fav=fav,
                rmax=np.maximum.accumulate(fav), rmin=np.minimum.accumulate(fav),
                tms=E.NY[k0:kend]))
            break                               # one trade per anchor, once taken
    out.sort(key=lambda r: r["t_entry"])
    return out


SL, TP, HOLD = 15.5, 25.5, 720                  # the Pine's settings, 12h clock

print("=" * 100)
print("SELECTION RULE: researched (first break consumes the day) vs Pine (keep scanning)")
print("  same ticks, same fills, same SL 15.5 / TP 25.5, same 12h time stop")
print(f"  DATA: {E.D}")
print("=" * 100)
rows = []
for name, sig, spr in (("researched, spread<=1.50", M.signals(), 1.50),
                       ("researched, NO spread filter", M.signals(spread_max=None), None),
                       ("PINE as written (BUG-047)", signals_pine(), None)):
    d = M.apply(sig, SL, TP, time_stop_min=HOLD)
    s = E.stats(d.pnl.values)
    rows.append((name, s, d))
    print(f"\n  {name}")
    print(f"    n={s['n']:>3}  PF={s['pf']:>6.3f}  WR={s['wr']:>5.1f}%  "
          f"exp={s['exp']:+.2f}  net={s['net']:+.1f}  maxDD={s['mdd']:.1f}")
    print(f"    exits: {d.exit_reason.value_counts().to_dict()}")
    print(f"    signal minutes used: {sorted(d.sig_hm.unique().tolist())}")

print("\n" + "=" * 100)
print("WHAT THE SUBSTITUTED DAYS ARE WORTH")
print("=" * 100)
pine_d = rows[2][2]


def extra_of(base, label, dump=None):
    ex = pine_d[~pine_d.date.isin(set(base.date))]
    print(f"\n  vs {label}: {len(ex)} day(s) the Pine trades and it does not")
    if not len(ex):
        return
    s = E.stats(ex.pnl.values)
    print(f"    PF={s['pf']:.3f}  WR={s['wr']:.1f}%  exp={s['exp']:+.2f}  "
          f"net={s['net']:+.1f}")
    if dump:
        ex[["date", "sig_hm", "kind", "entry", "dist25", "exit_reason",
            "pnl"]].to_csv(dump, index=False)
        print(f"    -> {dump}")


# vs the full researched rule this mixes two causes (quarter substitution AND
# the unreproducible spread filter). vs the no-spread control it isolates
# BUG-047 alone: same filters, same fills, only the selection rule differs.
TAG = "holdout" if "holdout" in E.D else "insample"
extra_of(rows[0][2], "researched WITH spread filter (mixed cause)")
extra_of(rows[1][2], "researched NO spread filter (BUG-047 alone)",
         dump=f"research/microq3/results/bug047_extra_{TAG}.csv")

# On the days both rules trade, does the Pine pick the same break?
both = pine_d.merge(rows[1][2][["date", "sig_hm", "pnl"]], on="date",
                    suffixes=("_pine", "_ref"))
diff = both[both.sig_hm_pine != both.sig_hm_ref]
print(f"\n  shared days: {len(both)}   of which a DIFFERENT break was taken: "
      f"{len(diff)}")
if len(diff):
    print(f"    pine {diff.pnl_pine.sum():+.1f} vs ref {diff.pnl_ref.sum():+.1f} "
          f"on those days")

print("\n" + "=" * 100)
print("WAS WAITING FOR THE QUARTER WORTH IT?")
print("=" * 100)
# On a substituted day the researched rule saw a break and REJECTED it for
# sitting more than $6.25 from a $25 line. That rejected trade is the honest
# control: if 'wait for a near-quarter break' carries information, the
# substitute the Pine takes must beat the first break it passed over.
first = M.apply(M.signals(qdist=None, spread_max=None), SL, TP,
                time_stop_min=HOLD)
sub = pine_d[~pine_d.date.isin(set(rows[1][2].date))]
cmp_ = sub[["date", "sig_hm", "dist25", "pnl"]].merge(
    first[["date", "sig_hm", "dist25", "pnl"]], on="date",
    suffixes=("_wait", "_first"))
print(f"  {'date':>12}{'wait@':>7}{'dist':>7}{'pnl':>9}   "
      f"{'first@':>7}{'dist':>7}{'pnl':>9}")
for _, r in cmp_.iterrows():
    print(f"  {str(r.date):>12}"
          f"{int(r.sig_hm_wait)//60:>4}:{int(r.sig_hm_wait)%60:02d}"
          f"{r.dist25_wait:>7.2f}{r.pnl_wait:>+9.2f}   "
          f"{int(r.sig_hm_first)//60:>4}:{int(r.sig_hm_first)%60:02d}"
          f"{r.dist25_first:>7.2f}{r.pnl_first:>+9.2f}")
print(f"\n  wait-for-quarter  net {cmp_.pnl_wait.sum():+8.1f} on {len(cmp_)}")
print(f"  take first break  net {cmp_.pnl_first.sum():+8.1f} on {len(cmp_)}")

print("\n" + "=" * 100)
print("WHICH MINUTE THE TRADE COMES FROM")
print("=" * 100)
print(f"  {'minute':>8}{'researched':>13}{'PINE':>8}{'pine net $':>13}")
for hm in sorted(set(rows[1][2].sig_hm) | set(pine_d.sig_hm)):
    a = (rows[1][2].sig_hm == hm).sum()
    p = pine_d[pine_d.sig_hm == hm]
    print(f"  {hm // 60:02d}:{hm % 60:02d}   {a:>10}{len(p):>8}"
          f"{p.pnl.sum():>+13.1f}")
