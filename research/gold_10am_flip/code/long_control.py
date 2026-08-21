"""Is the long leg the 10:00 candle, or is it just that gold went up 68%?

A_L makes +4.77 points a trade. Over this window gold rose from $3,321 to
$5,597, so ANY long-biased rule with a 25-point target and a 15-point stop will
look profitable. Before the candle gets credit, it has to beat entering long on
the same days with the same exits and NO signal at all.

Two benchmarks, both long-only, both on the identical tick-exact machinery:
  FIXED   long at the first bar after 10:00, every constructible day.
  RANDOM  long at a uniformly chosen bar in the same 10:05-23:00 window,
          resampled many times to give a distribution rather than one draw.

If A_L cannot clear these, the signal is a long-bias detector and nothing more.
"""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "code")
from fastsim import _exit, PTS

SL, TP = 15, 25
sl_i, tp_i = int(SL*PTS), int(TP*PTS)
prep = pickle.load(open("data/prep10.pkl","rb"))
class TK:
    t=np.load("data/tk_t.npy"); bid=np.load("data/tk_bid.npy"); ask=np.load("data/tk_ask.npy")

def run_long(pick):
    out=[]
    for day in prep:
        n=len(day["c"])
        if n==0: continue
        i=pick(day,n)
        if i is None or i>=n: continue
        te=int(day["t_close"][i]); e=int(day["ask_c"][i])
        r=_exit(day,TK,te,e,True,sl_i,tp_i)
        if r is None: continue
        px,why,xt=r
        out.append((px-e)/PTS)
    return np.array(out,float)

fixed = run_long(lambda d,n: 0)
print(f"FIXED long at first bar after 10:00 : n={len(fixed)} exp={fixed.mean():+.3f} "
      f"net={fixed.sum():+.1f} win={100*(fixed>0).mean():.1f}%")

rng=np.random.default_rng(7)
exps=[]
for k in range(400):
    q=run_long(lambda d,n: int(rng.integers(0,n)))
    exps.append(q.mean())
exps=np.array(exps)
OBS=4.765
print(f"RANDOM-TIME long, 400 resamples      : exp mean={exps.mean():+.3f} sd={exps.std():.3f} "
      f"p5={np.percentile(exps,5):+.3f} p95={np.percentile(exps,95):+.3f} max={exps.max():+.3f}")
print(f"\nA_L observed expectancy {OBS:+.3f} pts")
print(f"  vs FIXED  benchmark   {fixed.mean():+.3f}  -> edge over benchmark {OBS-fixed.mean():+.3f}")
print(f"  vs RANDOM distribution -> p = {(exps>=OBS).mean():.4f}")
print(f"  A_L z against random-long null = {(OBS-exps.mean())/exps.std():.2f}")

# how much of the year is simply drift?
rows=[]
for day in prep:
    if len(day["c"])==0: continue
    rows.append(day["dopen"])
rows=np.array(rows)
print(f"\ncontext: 10:00 open first={rows[0]:.1f} last={rows[-1]:.1f} "
      f"drift={100*(rows[-1]/rows[0]-1):+.1f}% over {len(rows)} days")
np.save("results/random_long_exps.npy", exps)
