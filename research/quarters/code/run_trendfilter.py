"""DOES A TREND FILTER RESCUE IT?

The obvious objection to Tests 1-3 is that Yotov never trades quarter points
naked -- webinars 3-5 layer Trend Waves and a discretionary fundamental gate on
top. The fundamental gate is unfalsifiable and cannot be tested. The trend
layer can be, with the crudest possible proxy: only take longs when price is
above where it was N days ago, only shorts when below.

The point is not to build Yotov's system faithfully. It is to answer: if the
quarters system only works with a momentum filter bolted on, is it the quarters
doing the work or the momentum? So the SAME filter is applied on the round grid
and on shifted grids. If both improve equally, the momentum filter is the edge
and the grid is scenery.
"""
import sys, glob, numpy as np, pandas as pd
sys.path.insert(0, "research/quarters/code"); sys.path.insert(0, "research/goldmap/code")
from system import Book, prep, run, stats, PTS
from grid import DATA

LOOKBACK = [1, 3, 10]          # days
SCALES = [50.0, 100.0]
PHASES = [0, 3, 6, 9]


def trend_mask(book, t_ms, days):
    """+1 if price is higher than `days` ago at that instant, -1 if lower."""
    k = np.searchsorted(book.ny, t_ms, "left").clip(0, len(book.ny) - 1)
    kp = np.searchsorted(book.ny, t_ms - days * 86_400_000, "left").clip(0, len(book.ny) - 1)
    return np.where(book.mid[k] > book.mid[kp], 1, -1)


rows = []
for year, d in DATA.items():
    b = Book(d, year)
    print(f"\n{'='*100}\n{year}\n{'='*100}", flush=True)
    for S in SCALES:
        print(f"\n  S = ${S:.0f}")
        print(f"  {'filter':<14}{'phase':>7}{'n':>6}{'PF':>8}{'exp R':>9}{'net R':>9}{'net $':>10}{'WR':>7}")
        for k in PHASES:
            g = prep(b, S, k / 12)
            tr = run(b, S, k / 12, grids=g)
            if not tr:
                continue
            t_ms = np.array([t[0] for t in tr]); dirn = np.array([t[1] for t in tr])
            r = np.array([t[4] for t in tr]); usd = np.array([t[3] for t in tr])
            for lb in [0] + LOOKBACK:
                m = np.ones(len(tr), bool) if lb == 0 else (trend_mask(b, t_ms, lb) == dirn)
                if m.sum() < 10:
                    continue
                rr, uu = r[m], usd[m]
                gp, gl = rr[rr > 0].sum(), -rr[rr < 0].sum()
                name = "none" if lb == 0 else f"{lb}d trend"
                rows.append(dict(year=year, S=S, k=k, round=(k == 0), filt=name,
                                 n=int(m.sum()), pf=(gp/gl if gl > 0 else np.inf),
                                 exp=float(rr.mean()), net_R=float(rr.sum()),
                                 net_usd=float(uu.sum()), wr=100*float((rr > 0).mean())))
                print(f"  {name:<14}{('ROUND' if k==0 else f'{k}/12'):>7}{m.sum():>6}"
                      f"{(gp/gl if gl>0 else np.inf):>8.3f}{rr.mean():>+9.4f}"
                      f"{rr.sum():>+9.1f}{uu.sum():>+10.0f}{100*(rr>0).mean():>6.1f}%",
                      flush=True)
            del g
    del b
pd.DataFrame(rows).to_csv("research/quarters/results/trendfilter.csv", index=False)
print("\nwritten -> research/quarters/results/trendfilter.csv")
