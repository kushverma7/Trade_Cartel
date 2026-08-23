"""Step 4/5 — the target x stop race, tick-exact, for every acceptance definition.

An MAE quantile measured over a fixed window is order-blind: it counts adverse
moves that happen AFTER the target would already have paid. So stops are not
chosen from that distribution directly. Instead every (target, stop) pair is
RACED on the real quote path, which is the only thing that answers "which came
first".

    long  enters ASK, marked out on BID   short enters BID, marked out on ASK
    TP    resting limit, fills AT the target, no overshoot credited
    SL    market-triggered at the real next executable quote, slippage included
    else  marked at the 6-hour cap

Also raced per event: the structural pair (target = next rung, stop = origin
LQP), whose geometric baseline is to_lqp/(to_lqp+to_next) -- the number every
acceptance definition has to beat to be worth anything.
"""
import sys, time, numpy as np, pandas as pd
sys.path.insert(0, "research/qt2/code"); sys.path.insert(0, "research/goldmap/code")
from states import attempts, entries_at_rung, RUNGS, RIDX, DAY_MS
from qt_engine import Book, PTS

DEFS = ("touch", "exc", "dwell", "ticks", "retest")
EXC_I, DWELL_MS, N_TICKS = 500, 60_000, 50
BOOKS = {"A_whole": "whole", "B_comp": "comp"}
HOLD_MS = 6 * 3600 * 1000
TARGETS = [0.50, 0.75, 1.00, 1.25, 1.50, 2.00, 2.50, 3.00, 4.00, 5.00]
STOPS = [1.00, 1.50, 2.00, 2.50, 3.00, 4.00, 5.00, 7.50, 10.00, 20.00]
T_I = [int(t * PTS) for t in TARGETS]
S_I = [int(s * PTS) for s in STOPS]
DATA = {"2024-25": "research/microq3/data_holdout", "2025-26": "research/microq3/data"}


def race(rmax, nrmin, fav, t_i, s_i):
    """-> (pnl_int, tag). rmax/nrmin are running max of fav and running max of -fav."""
    n = len(fav)
    a = int(np.searchsorted(rmax, t_i, "left"))
    b = int(np.searchsorted(nrmin, s_i, "left"))
    if a >= n and b >= n:
        return int(fav[-1]), "TIME"
    if a < b:
        return t_i, "TP"
    return int(fav[b]), "SL"


def run(tag, d):
    b = Book(d, tag)
    k0s, kxs, qs, ups, res = attempts(b)
    print(f"  {tag}: {len(k0s):,} attempts", flush=True)
    ny, bid, ask, mid = b.ny, b.bid, b.ask, b.mid
    ev, sw = [], []
    seen = {}
    t0 = time.time()
    for i in range(len(k0s)):
        k0, kx, q, up = int(k0s[i]), int(kxs[i]), int(qs[i]), bool(ups[i])
        sgn = 1 if up else -1
        t_start = int(ny[k0])
        hist = [t for t in seen.get((q, sgn), []) if t_start - t <= DAY_MS]
        hist.append(t_start); seen[(q, sgn)] = hist
        attempt_no = len(hist)
        w0, w1 = k0, min(kx + 1, len(ny))
        if w1 - w0 < 5:
            continue
        m = mid[w0:w1].astype(np.int64)
        prog = (m - q) * sgn
        nyw = ny[w0:w1]
        peak = int(prog.max())
        for book, rung in BOOKS.items():
            r_i = RUNGS[RIDX[rung]][1]
            if peak < r_i:
                continue
            nxt_i = RUNGS[RIDX[rung] + 1][1]
            ent = entries_at_rung(prog, nyw, r_i, EXC_I, DWELL_MS, N_TICKS)
            for dn in DEFS:
                j = ent[dn]
                if j < 0:
                    continue
                k = w0 + j
                e = int(ask[k]) if up else int(bid[k])
                p1 = min(k + int(np.searchsorted(ny[k:], int(ny[k]) + HOLD_MS, "left")) + 1,
                         len(ny))
                if p1 - k < 2:
                    continue
                ex = (bid[k:p1] if up else ask[k:p1]).astype(np.int64)
                fav = (ex - e) if up else (e - ex)
                rmax = np.maximum.accumulate(fav)
                nrmin = np.maximum.accumulate(-fav)
                eid = len(ev)
                to_next = abs((q + nxt_i * sgn) - e)
                to_lqp = abs(e - q)
                # the structural race: does it reach the next rung before the LQP?
                _, stag = race(rmax, nrmin, fav, to_next, to_lqp)
                ev.append(dict(
                    eid=eid, year=tag, book=book, adef=dn, t=int(ny[k]), up=up,
                    q=q / PTS, attempt=attempt_no, entry=e / PTS,
                    spread=(int(ask[k]) - int(bid[k])) / PTS,
                    to_next=to_next / PTS, to_lqp=to_lqp / PTS,
                    p_geom_struct=to_lqp / (to_lqp + to_next),
                    struct=stag, mfe=int(rmax[-1]) / PTS, mae=-int(nrmin[-1]) / PTS,
                    major100=(q % 100_000 == 0),
                    hm=(int(ny[k]) // 60000) % 1440,
                    dow=int(pd.Timestamp(int(ny[k]), unit="ms").dayofweek),
                    mins_in=(int(ny[k]) - t_start) / 60000.0))
                for ti, tv in zip(T_I, TARGETS):
                    for si, sv in zip(S_I, STOPS):
                        pnl, tg = race(rmax, nrmin, fav, ti, si)
                        sw.append((eid, tv, sv, pnl / PTS, tg))
        if i % 30000 == 0 and i:
            print(f"    {i:,}  {len(ev):,} events  ({time.time()-t0:.0f}s)", flush=True)
    del b
    return pd.DataFrame(ev), pd.DataFrame(
        sw, columns=["eid", "tp", "sl", "pnl", "tag"])


EV, SW, off = [], [], 0
for tag, d in DATA.items():
    e, s = run(tag, d)
    e["eid"] += off; s["eid"] += off
    off += len(e) + 10
    EV.append(e); SW.append(s)
E = pd.concat(EV, ignore_index=True); S = pd.concat(SW, ignore_index=True)
E.to_parquet("research/qt2/results/events.parquet", index=False)
S.to_parquet("research/qt2/results/sweep.parquet", index=False)
print(f"\nwritten: {len(E):,} events, {len(S):,} sweep outcomes")
