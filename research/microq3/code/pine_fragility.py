"""AUDIT part 3: how much does ONE trade move the headline?

The Pine will run on TradingView's XAUUSD feed, not Dukascopy. The two agree on
the shape of the day but not tick for tick, so a trade that came close to
touching BOTH its stop and its target can land either way on a different feed.
This prices that.

NOTE on excursions. microq3.apply() reports mfe/mae over the trade's WHOLE
window (rmax[-1] / rmin[-1]), deliberately, so a stop cannot truncate the
excursion being reported. That is the wrong statistic for this question -- a
winner showing mae -73 simply means the market fell apart AFTER the target was
paid. What matters here is the excursion BEFORE the exit, recomputed below.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/microq3/code")
import engine as E, microq3 as M
from engine import PTS

SL, TP, HOLD = 15.5, 25.5, 720
sl_i, tp_i = int(SL * PTS), int(TP * PTS)
sig = M.signals()

rows = []
for t in sig:
    tms, fav = t["tms"], t["fav"]
    n = int(np.searchsorted(tms, tms[0] + HOLD * 60_000, "right"))
    fav = fav[:n]
    rmax, rmin = np.maximum.accumulate(fav), np.minimum.accumulate(fav)
    i_tp = int(np.searchsorted(rmax, tp_i, "left"));  i_tp = i_tp if i_tp < n else 10**9
    i_sl = int(np.searchsorted(-rmin, sl_i, "left")); i_sl = i_sl if i_sl < n else 10**9
    j = min(i_tp, i_sl)
    if j >= 10**9:
        pnl, why, j = int(fav[-1]), "TIME", n - 1
    else:
        pnl, why = int(fav[j]), ("TP" if j == i_tp else "SL")
    # excursion strictly BEFORE the exit -- the only part the trade lived through
    rows.append(dict(date=t["date"], kind=t["kind"], why=why, pnl=pnl / PTS,
                     pre_mae=int(rmin[j]) / PTS, pre_mfe=int(rmax[j]) / PTS))
d = pd.DataFrame(rows)
p = d.pnl.values
s = E.stats(p)
print("=" * 92)
print(f"FRAGILITY OF THE HEADLINE   DATA: {E.D}")
print(f"  as researched: n={s['n']}  PF={s['pf']:.3f}  WR={s['wr']:.1f}%  "
      f"net={s['net']:+.1f}")
print("=" * 92)

print("\nHOW CLOSE EACH WINNER CAME TO ITS STOP BEFORE PAYING  (stop -15.50)")
w = d[d.why == "TP"].sort_values("pre_mae")
print(f"  {'date':>12}{'kind':>11}{'worst before TP':>17}{'room left':>11}")
for _, r in w.iterrows():
    print(f"  {str(r.date):>12}{r.kind:>11}{r.pre_mae:>17.2f}{SL + r.pre_mae:>11.2f}")
close = w[SL + w.pre_mae <= 3.0]
print(f"  {len(close)} of {len(w)} winners had <= $3.00 of room left")

print("\nHOW CLOSE EACH LOSER CAME TO ITS TARGET BEFORE STOPPING  (target +25.50)")
l = d[d.why == "SL"].sort_values("pre_mfe", ascending=False)
print(f"  {'date':>12}{'kind':>11}{'best before SL':>16}{'short by':>10}")
for _, r in l.iterrows():
    print(f"  {str(r.date):>12}{r.kind:>11}{r.pre_mfe:>16.2f}{TP - r.pre_mfe:>10.2f}")

print("\nFLIP THE CLOSEST CALLS  (winners with the least room, turned into stops)")
for k in (1, 2, 3):
    q = p.copy()
    for i in w.index[:k]:
        q[d.index.get_loc(i)] = -SL
    t = E.stats(q)
    print(f"  closest {k} -> stop:  PF={t['pf']:.3f}  WR={t['wr']:.1f}%  "
          f"net={t['net']:+.1f}")

print("\nBOOTSTRAP  (resample the 25 trades with replacement, 20000 draws)")
print("  measures SAMPLING error only -- it cannot see selection, so it says")
print("  nothing about whether the rule repeats. The holdout does that.")
rng = np.random.default_rng(7)
b = rng.choice(p, (20000, len(p)))
gl = np.abs(b.clip(max=0)).sum(1)
pf = np.divide(b.clip(min=0).sum(1), gl, out=np.full(len(b), np.inf), where=gl > 0)
net = b.sum(1)
fin = np.isfinite(pf)
print(f"  PF   median {np.median(pf[fin]):.2f}   5th {np.percentile(pf[fin],5):.2f}"
      f"   95th {np.percentile(pf[fin],95):.2f}")
print(f"  net  median {np.median(net):+.0f}   5th {np.percentile(net,5):+.0f}"
      f"   95th {np.percentile(net,95):+.0f}")
