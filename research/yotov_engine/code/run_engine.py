import sys, time, numpy as np, pandas as pd
sys.path.insert(0, "research/yotov_engine/code")
from engine import Ctx
import families as F

DATA = {"2025-26": "research/microq3/data", "2024-25": "research/microq3/data_holdout"}
PHASE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
TAG = sys.argv[2] if len(sys.argv) > 2 else "round"

allev = []
for year, d in DATA.items():
    t0 = time.time()
    ctx = Ctx(d, year, S=25.0, phase_frac=PHASE)
    ev, att = F.run(ctx)
    ev["year"] = year
    allev.append(ev)
    print(f"\n{'='*100}\n{year}  phase {PHASE:.4f}   "
          f"{len(att)} attempts, {len(ev)} candidate trades   "
          f"({time.time()-t0:.0f}s)\n{'='*100}", flush=True)
    print(f"  {'family':>22}{'n':>7}{'PF':>7}{'WR':>8}{'p_geom':>9}"
          f"{'EDGE':>9}{'exp $':>9}{'net $':>10}{'maxDD':>9}{'med min':>9}")
    for fam in sorted(ev.fam.unique()):
        s = F.stats(ev[ev.fam == fam])
        print(f"  {fam:>22}{s['n']:>7}{s['pf']:>7.2f}{s['wr']:>7.1f}%"
              f"{s['p_geom']:>8.1f}%{s['edge']:>+8.1f}%{s['exp']:>+9.2f}"
              f"{s['net']:>+10.0f}{s['mdd']:>9.0f}{s['med_min']:>9.0f}")
    s = F.stats(ev)
    print(f"  {'ALL':>22}{s['n']:>7}{s['pf']:>7.2f}{s['wr']:>7.1f}%"
          f"{s['p_geom']:>8.1f}%{s['edge']:>+8.1f}%{s['exp']:>+9.2f}"
          f"{s['net']:>+10.0f}{s['mdd']:>9.0f}{s['med_min']:>9.0f}")
    del ctx

E = pd.concat(allev, ignore_index=True)
E.to_csv(f"research/yotov_engine/results/events_{TAG}.csv", index=False)
print(f"\nwritten -> research/yotov_engine/results/events_{TAG}.csv  ({len(E)} rows)")
