"""Step 3b — build the event table for Books A and B, all six acceptance defs.

One row per (attempt, rung, acceptance-definition) that actually fired, with the
executable entry, the excursion distribution from that entry, and the features
the brief asks for. Exits are NOT applied here: the target/stop sweep runs
against the cached excursion path so that no exit choice can change which events
exist.

FILL CONVENTION: long enters ASK and is marked out on BID; short the reverse.
"""
import sys, time, numpy as np, pandas as pd
sys.path.insert(0, "research/qt2/code"); sys.path.insert(0, "research/goldmap/code")
from states import attempts, entries_at_rung, RUNGS, RIDX, Q_I, DAY_MS
from qt_engine import Book, PTS

DEFS = ("touch", "exc", "dwell", "ticks", "retest")
EXC_I, DWELL_MS, N_TICKS = 500, 60_000, 50      # $0.50 beyond / 60s / 50 ticks
BOOKS = {"A_whole": "whole", "B_comp": "comp"}
HOLD_MS = 6 * 3600 * 1000                        # excursion path cached 6h out

DATA = {"2024-25": "research/microq3/data_holdout", "2025-26": "research/microq3/data"}


def run(tag, d):
    b = Book(d, tag)
    t0 = time.time()
    k0s, kxs, qs, ups, res = attempts(b)
    print(f"  {tag}: {len(k0s):,} attempts located ({time.time()-t0:.0f}s)", flush=True)
    ny, bid, ask, mid = b.ny, b.bid, b.ask, b.mid
    rows = []
    # recency-windowed attempt counter, 24h, keyed on (LQP, direction)
    seen = {}
    for i in range(len(k0s)):
        k0, kx, q, up = int(k0s[i]), int(kxs[i]), int(qs[i]), bool(ups[i])
        sgn = 1 if up else -1
        key = (q, sgn)
        t_start = int(ny[k0])
        hist = [t for t in seen.get(key, []) if t_start - t <= DAY_MS]
        hist.append(t_start); seen[key] = hist
        attempt_no = len(hist)

        w0, w1 = k0, min(kx + 1, len(ny))
        if w1 - w0 < 5:
            continue
        m = mid[w0:w1].astype(np.int64)
        prog = (m - q) * sgn                       # signed progress, thousandths
        nyw = ny[w0:w1]
        peak = int(prog.max())

        for book, rung in BOOKS.items():
            r_i = RUNGS[RIDX[rung]][1]
            if peak < r_i:
                continue
            nxt_i = RUNGS[RIDX[rung] + 1][1]
            ent = entries_at_rung(prog, nyw, r_i, EXC_I, DWELL_MS, N_TICKS)
            for dname in DEFS:
                j = ent[dname]
                if j < 0:
                    continue
                k = w0 + j
                e = int(ask[k]) if up else int(bid[k])
                # cached excursion path from THIS entry, on the exit side
                p1 = min(k + 1 + int(np.searchsorted(ny[k:], int(ny[k]) + HOLD_MS, "left")),
                         len(ny))
                ex = (bid[k:p1] if up else ask[k:p1]).astype(np.int64)
                fav = (ex - e) if up else (e - ex)
                if len(fav) < 2:
                    continue
                rmax = int(fav.max()); rmin = int(fav.min())
                # distance from the executable entry to the next rung, in dollars
                nxt_px = q + nxt_i * sgn
                to_next = abs(nxt_px - e)
                lqp_dist = abs(e - q)
                rows.append(dict(
                    year=tag, book=book, adef=dname, t=int(ny[k]), k=k,
                    up=up, q=q / PTS, attempt=attempt_no,
                    entry=e / PTS, spread=(int(ask[k]) - int(bid[k])) / PTS,
                    prog_at_entry=int(prog[j]) / PTS,
                    to_next=to_next / PTS, to_lqp=lqp_dist / PTS,
                    mfe=rmax / PTS, mae=rmin / PTS,
                    major100=(q % 100_000 == 0),
                    mins_in=(int(ny[k]) - t_start) / 60000.0,
                    hm=(int(ny[k]) // 60000) % 1440,
                    dow=int(pd.Timestamp(int(ny[k]), unit="ms").dayofweek),
                    res=res[i], k_end=int(p1),
                ))
        if i % 20000 == 0 and i:
            print(f"    {i:,}/{len(k0s):,}  {len(rows):,} rows"
                  f"  ({time.time()-t0:.0f}s)", flush=True)
    del b
    return pd.DataFrame(rows)


out = []
for tag, d in DATA.items():
    out.append(run(tag, d))
E = pd.concat(out, ignore_index=True).sort_values("t").reset_index(drop=True)
E.to_parquet("research/qt2/results/events.parquet", index=False)
print(f"\nwritten -> research/qt2/results/events.parquet   {len(E):,} rows")
print(E.groupby(["book", "adef"]).size().unstack(fill_value=0))
