"""White-style Reality Check: correct for the WHOLE search, not just the anchor.

The earlier permutation compared the real result against the best of a 29-anchor
scan on transplanted data, which corrects for the anchor dimension alone. But
the anchor was not the only thing searched -- body minimum and maximum, quarter
distance, spread cap, signal window and the exit pair were all swept. The
honest null must therefore re-run the ENTIRE search on data where the anchor
carries no information, and compare the real best-of-search against the
distribution of null best-of-search.

NULL: each day keeps its own real intraday price path; it is given the anchor
GEOMETRY of a random other day (body size, direction, edges as offsets),
re-centred on its own anchor close. Filters and execution are untouched.

Uses the post-filter equivalence verified in wf_full.py: body, quarter, spread
and window all SKIP the day and none changes which break is first, so building
once per (anchor, SL, TP) and post-filtering is identical to rebuilding.
"""
import sys, itertools, numpy as np, pandas as pd
sys.path.insert(0, "research/microq3/code")
import engine as E
from engine import PTS

ANCHORS = list(range(18 * 60 + 15, 19 * 60 + 45, 5))
BODYMIN = [0.0, 0.5, 1.0, 1.5, 2.0]
BODYMAX = [6.25, 10.0, None]
QD = [5.0, 6.25, 7.5, None]
SPR = [1.25, 1.5, 2.0, None]
WIN = [15, 30, 60]
SLS = [12.5, 15.5, 20.0]
TPS = [20.0, 25.5, 30.0]
MINN = 10

GRID = list(itertools.product(BODYMIN, BODYMAX, QD, SPR, WIN, SLS, TPS))
print(f"search space: {len(ANCHORS)} anchors x {len(GRID)} parameter points "
      f"= {len(ANCHORS)*len(GRID):,} hypotheses", flush=True)


def anchors_at(start):
    out = {}
    for day in E.DAYS:
        day = int(day)
        a = E.candle(day, start, start + 15, "mid")
        if a is None or a["nmin"] < 5:
            continue
        out[day] = (a["o"] / PTS, a["c"] / PTS)
    return out


def raw_trades(start, donor=None):
    """Every bearish-anchor break with NO filters. -> DataFrame incl. cached paths."""
    A = anchors_at(start)
    rows = []
    for day, (o, c) in A.items():
        if donor is not None:
            dj = donor.get(day)
            if dj is None or dj not in A:
                continue
            o2, c2 = A[dj]
            if c2 >= o2:
                continue
            body = o2 - c2
            bhi, blo = c + body, c            # transplanted geometry, own level
        else:
            if c >= o:
                continue
            body = o - c
            bhi, blo = o, c
        hit = None
        for cd in E.five_min_candles(day, start + 15, start + 15 + max(WIN), "mid"):
            cc = cd["c"] / PTS
            if cc < blo:
                hit = (cd, False); break
            if cc > bhi:
                hit = (cd, True); break
        if hit is None:
            continue
        cd, long_ = hit
        k0 = int(np.searchsorted(E.NY, cd["t_close"], "right"))
        kend = E.session_end_index(day, 17 * 60)
        if kend is None or k0 >= kend:
            continue
        bid, ask = int(E.BID[k0]) / PTS, int(E.ASK[k0]) / PTS
        entry = ask if long_ else bid
        r = entry % 25.0
        ex = E.BID[k0:kend] if long_ else E.ASK[k0:kend]
        e_i = int(E.ASK[k0]) if long_ else int(E.BID[k0])
        fav = (ex.astype(np.int64) - e_i) if long_ else (e_i - ex.astype(np.int64))
        rows.append(dict(body=body, spread=ask - bid, dq=min(r, 25 - r),
                         mins=cd["hm_start"] - (start + 15),
                         rmax=np.maximum.accumulate(fav), rmin=np.minimum.accumulate(fav),
                         fav=fav))
    return rows


def best_of_search(donor=None):
    best = -1e9
    for a in ANCHORS:
        tr = raw_trades(a, donor)
        if len(tr) < MINN:
            continue
        body = np.array([t["body"] for t in tr]); spr = np.array([t["spread"] for t in tr])
        dq = np.array([t["dq"] for t in tr]);     mins = np.array([t["mins"] for t in tr])
        cache = {}
        for (sl, tp) in itertools.product(SLS, TPS):
            sl_i, tp_i = int(sl * 1000), int(tp * 1000)
            v = np.empty(len(tr))
            for i, t in enumerate(tr):
                n = len(t["fav"])
                itp = int(np.searchsorted(t["rmax"], tp_i, "left")); itp = itp if itp < n else 10**9
                isl = int(np.searchsorted(-t["rmin"], sl_i, "left")); isl = isl if isl < n else 10**9
                j = min(itp, isl)
                v[i] = (t["fav"][-1] if j >= 10**9 else t["fav"][j]) / 1000.0
            cache[(sl, tp)] = v
        for bmn, bmx, q, sp, w, sl, tp in GRID:
            m = (body >= bmn) & (mins < w)
            if bmx is not None: m &= (body <= bmx)
            if q is not None:   m &= (dq <= q)
            if sp is not None:  m &= (spr <= sp)
            k = int(m.sum())
            if k < MINN:
                continue
            e = cache[(sl, tp)][m].mean()
            if e > best:
                best = e
    return best


if __name__ == "__main__":
    import time
    NP = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    t0 = time.time()
    real = best_of_search()
    print(f"REAL best-of-search expectancy: {real:+.3f}   ({time.time()-t0:.0f}s per pass)", flush=True)
    days = sorted({int(d) for d in E.DAYS})
    rng = np.random.default_rng(4242)
    nulls = []
    for r in range(NP):
        perm = rng.permutation(days)
        nulls.append(best_of_search({d: int(p) for d, p in zip(days, perm)}))
        if (r + 1) % 10 == 0:
            a = np.array(nulls)
            print(f"  perm {r+1}/{NP} ({time.time()-t0:.0f}s)  null best median {np.median(a):+.2f}  "
                  f">= real: {int((a >= real).sum())}", flush=True)
    a = np.array(nulls)
    pd.DataFrame(dict(null_best=a)).to_csv("research/microq3/results/U_reality_check.csv", index=False)
    p = (int((a >= real).sum()) + 1) / (len(a) + 1)
    print(f"\n{'='*92}\nREALITY CHECK over {len(ANCHORS)*len(GRID):,} hypotheses, {len(a)} permutations\n{'='*92}")
    print(f"  real best-of-search expectancy   {real:+.3f}")
    print(f"  null best-of-search  median {np.median(a):+.3f}   p90 {np.percentile(a,90):+.3f}   max {a.max():+.3f}")
    print(f"\n  DATA-SNOOPING-CORRECTED p = {p:.4f}   ({int((a>=real).sum())} of {len(a)} nulls match or beat it)")
