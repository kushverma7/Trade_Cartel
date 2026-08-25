"""Where does PF 1.81 differ from the reported 2.115 on the same 59 trades?"""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Trade_Cartel/research/gold_exit_eng/code")
from entry_universe import build, splits, label
from exits import resolve, stats

prep = pickle.load(open("/home/user/Trade_Cartel/research/gold_10am_flip/data/prep10.pkl", "rb"))
BODY = {pd.Timestamp(d["date"]): d["bhi"] - d["blo"] for d in prep}
q = lambda p: min((p % 25.0), 25.0 - (p % 25.0))

def sel(win, body_min=1.0, tol=7.5, spread=2.0):
    tr = build(win, spread)
    for t in tr: t["body"] = BODY[t["date"]]
    return [t for t in tr if t["body"] >= body_min and q(t["entry"]) <= tol]

print(f"{'entry window':<16}{'n':>5}{'PF':>8}{'net':>10}{'WR':>8}{'DD':>8}")
for win in (1100, 1200, 1400, 2400):
    s = sel(win)
    p = [resolve(t, sl=15, tp=25)[0] for t in s]
    a = stats(p)
    print(f"{'through '+str(win):<16}{a['n']:>5}{a['pf']:>8.3f}{a['net']:>10.1f}{a['wr']:>7.1f}%{a['mdd']:>8.1f}")

s = sel(1100)
p = [resolve(t, sl=15, tp=25)[0] for t in s]
a = stats(p)
print(f"\nreported: n=59  PF=2.115  net=+435  exp=+7.37  WR=55.9%  DD=45")
print(f"measured: n={a['n']}  PF={a['pf']:.3f}  net={a['net']:+.1f}  exp={a['exp']:+.2f}  "
      f"WR={a['wr']:.1f}%  DD={a['mdd']:.1f}")
w = sum(1 for v in p if v > 0)
print(f"\nwinners {w}/{len(p)} = {100*w/len(p):.1f}%   reported 55.9% => {round(0.559*59)} winners "
      f"({round(0.559*59)-w} more than measured)")

# what SL/TP would a 55.9% win rate on these 59 need?
print(f"\nthe reported win rate on THIS trade set requires a different exit or a different fill:")
for sl, tp in ((15, 25), (15, 22), (18, 25), (15, 27), (20, 25)):
    pp = [resolve(t, sl=sl, tp=tp)[0] for t in s]; aa = stats(pp)
    print(f"   SL{sl:>3}/TP{tp:<3} PF={aa['pf']:.3f} net={aa['net']:+7.1f} WR={aa['wr']:.1f}% DD={aa['mdd']:.1f}")

# their split convention: 60/20/20 across the FILTERED set's own dates
ds = sorted({t["date"] for t in s}); n = len(ds)
d1, d2 = ds[int(n * .6)], ds[int(n * .8)]
for t in s: t["split"] = "DEV" if t["date"] < d1 else ("VAL" if t["date"] < d2 else "HOLD")
print(f"\nsplit on the FILTERED set's own dates (their convention, 60/20/20):")
for sp in ("DEV", "VAL", "HOLD"):
    aa = stats([resolve(t, sl=15, tp=25)[0] for t in s if t["split"] == sp])
    print(f"   {sp:<5} n={aa['n']:<4} PF={aa['pf']:.2f}  exp={aa['exp']:+.2f}")
