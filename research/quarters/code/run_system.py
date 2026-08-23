"""THE BACKTEST — Yotov's Hesitation Zone system on gold, tick-exact.

Round grid vs 11 phase-shifted grids of identical spacing, both tick years,
four large-quarter scales, plus config variants that isolate each component.

Every number here is a real backtest with real bid/ask fills, not a statistic
about price geometry.
"""
import sys, time, itertools, numpy as np, pandas as pd
sys.path.insert(0, "research/quarters/code"); sys.path.insert(0, "research/goldmap/code")
from system import Book, prep, run, stats
from grid import DATA

SCALES = [25.0, 50.0, 100.0, 250.0]
NPHASE = 12
CONFIGS = {                       # name -> kwargs overriding the baseline
    "yotov":        dict(),                       # zone .30 / stop Q / tgt 1.0 / 3d
    "no-filter":    dict(decisive=False),         # does the 75-pip filter earn its keep?
    "tol-target":   dict(tgt=0.90),               # credit the 25-pip completion tolerance
    "wide-stop":    dict(stop_at=0.10),           # stop one overshoot area past Q
    "long-clock":   dict(days=10),                # relax the Three-Day Rule
}
rows = []
for year, d in DATA.items():
    t0 = time.time()
    b = Book(d, year)
    print(f"\n{'#'*112}\n{year}: {len(b.mid):,} ticks  (load {time.time()-t0:.0f}s)\n{'#'*112}", flush=True)
    for S in SCALES:
        print(f"\n  S = ${S:.2f}   [1R = the realised entry-to-stop distance]")
        print(f"  {'config':<12}{'phase':>7}{'n':>7}{'PF':>8}{'exp R':>9}{'net R':>10}"
              f"{'net $':>11}{'WR':>7}{'DD R':>8}{'TP/SL/T':>16}{'hold':>7}")
        for k in range(NPHASE):
            g = prep(b, S, k / NPHASE)
            for cname, kw in CONFIGS.items():
                if k > 0 and cname != "yotov":
                    continue                      # phase sweep only for the baseline
                tr = run(b, S, k / NPHASE, grids=g, **kw)
                s = stats(tr)
                if s is None:
                    continue
                rows.append(dict(year=year, S=S, k=k, round=(k == 0), config=cname, **s))
                tag = "ROUND" if k == 0 else f"{k}/12"
                mix = "%d/%d/%d" % (s['tp'], s['sl'], s['time'])
                print(f"  {cname:<12}{tag:>7}{s['n']:>7}{s['pf']:>8.3f}{s['exp']:>+9.4f}"
                      f"{s['net_R']:>+10.1f}{s['net_usd']:>+11.1f}{s['wr']:>6.1f}%"
                      f"{s['dd']:>8.1f}{mix:>16}{s['hold']:>7.0f}m", flush=True)
            del g
    del b

df = pd.DataFrame(rows)
df.to_csv("research/quarters/results/system.csv", index=False)
print(f"\nwritten: {len(df)} rows -> research/quarters/results/system.csv")
