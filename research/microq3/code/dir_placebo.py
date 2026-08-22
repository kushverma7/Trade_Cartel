"""How much of the edge is the DIRECTION call, and how much is just the day?

The random-entry placebo handed the simulation the real trade's direction for
free and still matched it (+14.45 vs +15.47, p 0.21), showing the 5-minute
body-break TIMING is decorative. It cannot show whether the break's DIRECTION
choice matters, because it was given that answer. These nulls separate them.

Every (day, entry minute, direction) outcome is resolved ONCE and cached --
there are only 25 x 30 x 2 of them -- so the simulations are then just draws
from an exact table rather than 50,000 repeated tick walks.
"""
import sys, numpy as np
sys.path.insert(0, "research/microq3/code")
import engine as E
import microq3 as M

SL, TP = 15.5, 25.5
BASE = M.signals()
real = E.stats(M.apply(BASE, SL, TP).pnl.tolist())
print(f"REAL: n={real['n']}  PF={real['pf']:.2f}  exp={real['exp']:+.2f}  net={real['net']:+.1f}\n")

days = [(t["day"], t["long"], t["k0"], t["kend"]) for t in BASE]
print("caching every (day, minute, direction) outcome ...", flush=True)
tbl = {}          # (day, minute or 'real', dir) -> pnl
for day, long_, k0r, kend in days:
    for d in (True, False):
        r = E.resolve(k0r, kend, d, SL, TP)
        tbl[(day, "real", d)] = r["pnl"] if r else np.nan
        for mi in range(30):
            w = E.window(day, 19 * 60 + mi, 19 * 60 + mi + 1)
            if w is None:
                tbl[(day, mi, d)] = np.nan; continue
            k0 = int(E.I0[w[0]])
            rr = E.resolve(k0, kend, d, SL, TP) if k0 < kend else None
            tbl[(day, mi, d)] = rr["pnl"] if rr else np.nan
print(f"  {len(tbl):,} outcomes cached\n")

rng = np.random.default_rng(31)
NR = 20000


def sim(rand_time, dirmode):
    out = np.empty(NR)
    for s in range(NR):
        pl = []
        for day, long_, _, _ in days:
            key = rng.integers(0, 30) if rand_time else "real"
            d = (bool(rng.integers(0, 2)) if dirmode == "rand"
                 else (not long_) if dirmode == "inv" else long_)
            v = tbl.get((day, key if rand_time else "real", d), np.nan)
            if np.isfinite(v):
                pl.append(v)
        out[s] = np.mean(pl) if len(pl) >= 15 else np.nan
    return out[np.isfinite(out)]


print(f"{'null':<44}{'exp mean':>10}{'sd':>8}{'p95':>9}{'p vs real':>11}")
for rt, dm, tag in ((True, "real", "random minute, real direction"),
                    (True, "rand", "random minute, RANDOM direction"),
                    (True, "inv",  "random minute, INVERTED direction"),
                    (False, "rand", "real minute, RANDOM direction"),
                    (False, "inv",  "real minute, INVERTED direction")):
    a = sim(rt, dm)
    p = ((a >= real["exp"]).sum() + 1) / (len(a) + 1)
    print(f"  {tag:<42}{a.mean():>10.2f}{a.std():>8.2f}{np.percentile(a,95):>9.2f}{p:>11.4f}")
print(f"\n  REAL (break timing AND break direction): {real['exp']:+.2f}")
