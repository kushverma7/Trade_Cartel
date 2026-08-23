"""DO SWING EXTREMES CLUSTER NEAR QUARTER POINTS?

This tests Yotov's rhetorical core directly. Throughout webinars 2 and 5 he
points at a daily or weekly extreme and asks whether it is a coincidence that
it sits close to a quarter point -- 1.4257 is "only 7 pips" from 1.4250,
1.2758 "within only eight pips" of 1.2750, and so on.

The measurement: for every NY day and every calendar week, take the extreme of
mid, and measure its distance to the nearest quarter point as a fraction of S.
Yotov's completion rule counts anything within 0.10*S as a hit.

BASE RATE. The hit band is +/-0.10*S around points spaced S apart = 20% of the
price axis. A uniformly distributed price is a "hit" one time in five. The
round grid must beat both that AND the phase-shifted grids of identical
spacing, which share the same data and the same price distribution.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/quarters/code"); sys.path.insert(0, "research/goldmap/code")
from grid import Book, DATA
from qt_engine import PTS

SCALES = [12.5, 25.0, 50.0, 100.0, 250.0]
NPHASE = 12
TOL = 0.10
rows = []

for year, d in DATA.items():
    b = Book(d, year)
    day = b.ny // 86_400_000
    week = b.ny // (7 * 86_400_000)
    print(f"\n{'='*104}\n{year}: {len(b.mid):,} ticks\n{'='*104}", flush=True)
    ext = {}
    for name, key in (("daily", day), ("weekly", week)):
        # ticks are chronological, so period boundaries are contiguous runs and
        # reduceat does in one pass what ufunc.at does in minutes
        bnd = np.concatenate([[0], np.flatnonzero(key[1:] != key[:-1]) + 1])
        hi = np.maximum.reduceat(b.mid, bnd)
        lo = np.minimum.reduceat(b.mid, bnd)
        ext[name] = np.concatenate([hi, lo])
        print(f"  {name}: {len(bnd)} periods -> {len(ext[name])} extremes", flush=True)
    for name, px in ext.items():
        print(f"\n  {name} extremes, fraction within {TOL:.2f}*S of a quarter point"
              f"   (base rate {2*TOL:.0%})")
        print(f"  {'S':>8}  " + "".join(f"{('ROUND' if k==0 else str(k)+'/12'):>8}" for k in range(NPHASE)))
        for S in SCALES:
            S_i = int(round(S * PTS)); out = []
            for k in range(NPHASE):
                ph = int(round(k / NPHASE * S_i))
                r = np.abs(((px - ph) % S_i) / S_i)
                dist = np.minimum(r, 1 - r)
                hit = float((dist <= TOL).mean())
                out.append(hit)
                rows.append(dict(year=year, kind=name, S=S, k=k, round=(k == 0),
                                 n=len(px), hit=hit))
            best = max(out); rank = sorted(out, reverse=True).index(out[0]) + 1
            print(f"  {S:8.2f}  " + "".join(f"{v:>8.3f}" for v in out)
                  + f"   round ranks {rank}/{NPHASE}", flush=True)
    del b

pd.DataFrame(rows).to_csv("research/quarters/results/extremes.csv", index=False)
print("\nwritten -> research/quarters/results/extremes.csv")
