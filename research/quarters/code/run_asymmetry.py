"""THE DECISIVE MEASUREMENT — P(continuation) from a quarter-point crossing.

For every grid scale S and every phase, measure: having just crossed quarter
point Q, does price reach Q+S before Q-S? H99 says 0.50 for a driftless walk
starting at a boundary, on ANY grid, in ANY market.

The round grid (phase 0) is compared against 11 grids of IDENTICAL spacing at
non-round phases. They share the same data, the same drift and the same
volatility, so any advantage the round grid shows over them is attributable to
roundness and nothing else. This is the GL03 phase-shift control applied to
Yotov's own premise.
"""
import sys, time, numpy as np
sys.path.insert(0, "research/quarters/code"); sys.path.insert(0, "research/goldmap/code")
from grid import Book, cell_sequence, first_passage, DATA
from qt_engine import PTS

SCALES = [2.5, 5.0, 10.0, 12.5, 25.0, 50.0, 100.0, 250.0]
NPHASE = 12                      # phase 0 = round, then k/12 for k=1..11
rows = []

for year, d in DATA.items():
    t0 = time.time()
    b = Book(d, year)
    print(f"\n{'='*100}\n{year}: {len(b.mid):,} ticks, "
          f"${b.mid.min()/PTS:,.2f} .. ${b.mid.max()/PTS:,.2f}  (load {time.time()-t0:.0f}s)")
    net = (b.mid[-1] - b.mid[0]) / PTS
    print(f"  net drift over the year: {net:+,.2f}  "
          f"({100*net/(b.mid[0]/PTS):+.1f}%) -- drift biases continuation UP, "
          f"which is why the phase controls matter")
    print(f"{'='*100}")
    print(f"  {'S':>8}  {'phase':>6}  {'n':>10}  {'P(cont)':>9}  {'up':>9}  {'down':>9}")
    for S in SCALES:
        S_i = int(round(S * PTS))
        for k in range(NPHASE):
            ph = int(round(k / NPHASE * S_i))
            idx, cells = cell_sequence(b.mid, S_i, ph)
            pos, dirn, out = first_passage(cells)
            m = out != 0
            if m.sum() < 50:
                continue
            res, up = out[m] == 1, dirn[m] == 1
            r = dict(year=year, S=S, k=k, round=(k == 0), n=int(m.sum()),
                     p=float(res.mean()),
                     p_up=float(res[up].mean()), p_dn=float(res[~up].mean()),
                     unres=int((out == 0).sum()))
            rows.append(r)
            tag = "ROUND" if k == 0 else f"{k}/12"
            print(f"  {S:8.2f}  {tag:>6}  {r['n']:>10,}  {r['p']:>9.4f}  "
                  f"{r['p_up']:>9.4f}  {r['p_dn']:>9.4f}", flush=True)
    del b

import pandas as pd
df = pd.DataFrame(rows)
df.to_csv("research/quarters/results/asymmetry.csv", index=False)
print(f"\nwritten: {len(df)} rows -> research/quarters/results/asymmetry.csv")
