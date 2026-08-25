"""The control that settles mechanism: identical events, MID fills.

Entry at the midpoint, exit path on the midpoint, no spread paid and no
slippage past the stop. If the rules are a coin flip that loses only to
execution, PF comes back at ~1.00 and the edge over each trade's own geometry
goes to ~0. If the rules are actively anti-predictive, both stay negative.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/qt2/code"); sys.path.insert(0, "research/goldmap/code")
from states import attempts, entries_at_rung, RUNGS, RIDX, DAY_MS
from qt_engine import Book, PTS

DEFS = ("touch", "exc", "ticks", "retest", "dwell")
EXC_I, DWELL_MS, N_TICKS = 500, 60_000, 50
BOOKS = {"A_whole": "whole", "B_comp": "comp"}
HOLD_MS = 6 * 3600 * 1000
TARGETS = [0.50, 1.00, 2.50, 5.00]
DATA = {"2024-25": "research/microq3/data_holdout", "2025-26": "research/microq3/data"}
rows = []
for tag, d in DATA.items():
    b = Book(d, tag)
    k0s, kxs, qs, ups, res = attempts(b)
    ny, mid = b.ny, b.mid
    for i in range(len(k0s)):
        k0, kx, q, up = int(k0s[i]), int(kxs[i]), int(qs[i]), bool(ups[i])
        sgn = 1 if up else -1
        w0, w1 = k0, min(kx + 1, len(ny))
        if w1 - w0 < 5: continue
        m = mid[w0:w1].astype(np.int64)
        prog = (m - q) * sgn
        nyw = ny[w0:w1]
        peak = int(prog.max())
        for book, rung in BOOKS.items():
            r_i = RUNGS[RIDX[rung]][1]
            if peak < r_i: continue
            nxt_i = RUNGS[RIDX[rung] + 1][1]
            ent = entries_at_rung(prog, nyw, r_i, EXC_I, DWELL_MS, N_TICKS)
            for dn in DEFS:
                j = ent[dn]
                if j < 0: continue
                k = w0 + j
                e = int(mid[k])                       # MID entry, no spread
                p1 = min(k + int(np.searchsorted(ny[k:], int(ny[k]) + HOLD_MS, "left")) + 1,
                         len(ny))
                if p1 - k < 2: continue
                ex = mid[k:p1].astype(np.int64)       # MID exit path
                fav = (ex - e) if up else (e - ex)
                rmax = np.maximum.accumulate(fav)
                nrmin = np.maximum.accumulate(-fav)
                n = len(fav)
                to_next = abs((q + nxt_i * sgn) - e); to_lqp = abs(e - q)
                a = int(np.searchsorted(rmax, to_next, "left"))
                bb = int(np.searchsorted(nrmin, to_lqp, "left"))
                st = "TIME" if (a >= n and bb >= n) else ("TP" if a < bb else "SL")
                base = dict(year=tag, book=book, adef=dn, struct=st,
                            p_geom=to_lqp / (to_lqp + to_next), t=int(ny[k]))
                for tv in TARGETS:
                    ti, si = int(tv * PTS), 20_000
                    a2 = int(np.searchsorted(rmax, ti, "left"))
                    b2 = int(np.searchsorted(nrmin, si, "left"))
                    if a2 >= n and b2 >= n: pnl = int(fav[-1])
                    elif a2 < b2: pnl = ti
                    else: pnl = int(fav[b2])
                    rows.append({**base, "tp": tv, "pnl": pnl / PTS})
    del b
D = pd.DataFrame(rows)
D.to_parquet("research/qt2/results/zerocost.parquet", index=False)

def PF(p):
    g, l = p[p > 0].sum(), -p[p < 0].sum(); return g / l if l > 0 else np.inf
print("=" * 100)
print("ZERO-COST CONTROL — mid fills, no spread, no slippage")
print("=" * 100)
u = D.drop_duplicates(["year", "book", "adef", "t"])
print("\n  STRUCTURAL RACE (reach the next rung before losing the LQP)")
print(f"  {'book':>9}{'adef':>9}{'n':>6}{'P(next)':>10}{'p_geom':>9}{'EDGE':>9}{'z':>7}")
for book in ("A_whole", "B_comp"):
    for a in DEFS:
        q = u[(u.book == book) & (u.adef == a)]
        if len(q) < 30: continue
        hit = (q.struct == "TP").mean(); pg = q.p_geom.mean()
        se = np.sqrt(pg * (1 - pg) / len(q))
        print(f"  {book:>9}{a:>9}{len(q):>6}{100*hit:>9.1f}%{100*pg:>8.1f}%"
              f"{100*(hit-pg):>+8.1f}%{(hit-pg)/se:>+7.2f}")
print("\n  TARGET SWEEP at a structural $20 stop, zero cost vs the real-fill result")
print(f"  {'book':>9}{'adef':>9}{'target':>8}{'n':>6}{'WR':>8}{'PF free':>10}{'exp free $':>12}")
for book in ("A_whole", "B_comp"):
    for a in ("touch", "dwell"):
        for tv in TARGETS:
            q = D[(D.book == book) & (D.adef == a) & (D.tp == tv)]
            if len(q) < 30: continue
            print(f"  {book:>9}{a:>9}{tv:>8.2f}{len(q):>6}"
                  f"{100*(q.pnl>0).mean():>7.1f}%{PF(q.pnl.values):>10.3f}"
                  f"{q.pnl.mean():>+12.3f}")
