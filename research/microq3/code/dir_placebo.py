"""How much of the edge is the DIRECTION call, and how much is the day?

The random-entry placebo handed the simulation the real trade's direction for
free and still matched it (+14.45 vs +15.47, p 0.21), which shows the 5-minute
body-break TIMING is decorative. It cannot show whether the break's DIRECTION
choice matters, because it was given that answer. Three further nulls separate
the pieces:

  1. random minute, random direction  -> is the day alone enough?
  2. random minute, INVERTED direction -> does the break call the right side?
  3. real timing, inverted direction    -> same, holding timing fixed
"""
import sys, numpy as np
sys.path.insert(0, "research/microq3/code")
import engine as E
import microq3 as M

SL, TP = 15.5, 25.5
BASE = M.signals()
real = E.stats(M.apply(BASE, SL, TP).pnl.tolist())
print(f"REAL: n={real['n']}  PF={real['pf']:.2f}  exp={real['exp']:+.2f}  net={real['net']:+.1f}\n")
rng = np.random.default_rng(31)
days = [(t["day"], t["long"], t["k0"], t["kend"]) for t in BASE]
NR = 2000


def sim(mode):
    out = []
    for _ in range(NR):
        pl = []
        for day, long_, k0r, kend in days:
            if mode.startswith("randtime"):
                hm = 19 * 60 + int(rng.integers(0, 30))
                w = E.window(day, hm, hm + 1)
                if w is None:
                    continue
                k0 = int(E.I0[w[0]])
            else:
                k0 = k0r
            if mode.endswith("randdir"):
                d = bool(rng.integers(0, 2))
            elif mode.endswith("invert"):
                d = not long_
            else:
                d = long_
            if kend is None or k0 >= kend:
                continue
            r = E.resolve(k0, kend, d, SL, TP)
            if r:
                pl.append(r["pnl"])
        if len(pl) >= 15:
            s = E.stats(pl)
            out.append((s["exp"], s["pf"]))
    return np.array(out)


print(f"{'null':<44}{'exp mean':>10}{'sd':>8}{'p95':>9}{'PF mean':>9}{'p vs real':>11}")
for mode, tag in (("randtime_realdir", "random minute, real direction"),
                  ("randtime_randdir", "random minute, RANDOM direction"),
                  ("randtime_invert",  "random minute, INVERTED direction"),
                  ("realtime_randdir", "real minute, RANDOM direction"),
                  ("realtime_invert",  "real minute, INVERTED direction")):
    a = sim(mode)
    p = ((a[:, 0] >= real["exp"]).sum() + 1) / (len(a) + 1)
    print(f"  {tag:<42}{a[:,0].mean():>10.2f}{a[:,0].std():>8.2f}"
          f"{np.percentile(a[:,0],95):>9.2f}{np.nanmean(a[:,1]):>9.2f}{p:>11.4f}")
