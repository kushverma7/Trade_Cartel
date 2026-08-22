"""Anchor-transplant null, run through the WHOLE selection procedure.

Everything downstream of the anchor looked robust: the body surface has no cell
below PF 1.0, the exit surface is 94% positive, and the quarter/spread/window
sweeps are smooth. But those sweeps are all measured on largely the SAME 25
days. If those 25 days were selected by a lucky anchor, secondary parameters
would look stable exactly like this. So the anchor is the thing to attack.

NULL: keep each day's real intraday price path, and keep the population of
anchor shapes, but sever the link between them. Day i is given the anchor
GEOMETRY of a random other day j -- same body size, same direction, same body
edges as offsets -- re-centred on day i's own anchor close so the levels sit
where day i's price actually is. Every filter and the execution are unchanged.

Then re-run the FULL 29-anchor scan on the permuted data and record the best PF
it finds. That is the honest comparison: the real 18:45 result was itself the
best of a 29-anchor scan, so it must be compared against the distribution of
best-of-29, not against a single cell.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/microq3/code")
import engine as E
from engine import PTS
import microq3 as M

SL, TP = 15.5, 25.5
ANCHORS = list(range(17 * 60 + 45, 20 * 60 + 15, 5))


def anchors_for(start, px="mid"):
    """-> dict day -> (open, close, body, bear, close_level)"""
    out = {}
    for day in E.DAYS:
        day = int(day)
        a = E.candle(day, start, start + 15, px)
        if a is None or a["nmin"] < 5:
            continue
        o, c = a["o"] / PTS, a["c"] / PTS
        out[day] = (o, c, abs(c - o), c < o)
    return out


def run_scan(start, donor=None, sl=SL, tp=TP):
    """One anchor start. donor: dict day->donor_day, or None for the real thing."""
    A = anchors_for(start)
    pnl = []
    for day, (o, c, body, bear) in A.items():
        if donor is not None:
            dj = donor.get(day)
            if dj is None or dj not in A:
                continue
            o2, c2, body, bear = A[dj]
            # transplant GEOMETRY, re-centre on this day's own anchor close
            off_hi = (max(o2, c2) - c2)
            off_lo = (min(o2, c2) - c2)
            bhi, blo = c + off_hi, c + off_lo
        else:
            bhi, blo = (o, c) if bear else (c, o)
        if not bear or body < 1.00 or body > 6.25:
            continue
        hit = None
        for cd in E.five_min_candles(day, start + 15, start + 45, "mid"):
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
        if ask - bid > 1.50:
            continue
        entry = ask if long_ else bid
        r = entry % 25.0
        if min(r, 25.0 - r) > 6.25:
            continue
        rr = E.resolve(k0, kend, long_, sl, tp)
        if rr:
            pnl.append(rr["pnl"])
    return E.stats(pnl)


if __name__ == "__main__":
    import json, time
    NPERM = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    # sanity: the real 18:45 scan must reproduce the base result exactly
    s = run_scan(18 * 60 + 45)
    print(f"sanity — real 18:45 via this code path: n={s['n']} PF={s['pf']:.3f} net={s['net']:+.1f}")
    real = [run_scan(a) for a in ANCHORS]
    real_best = max((r["pf"] for r in real if r["n"] >= 10), default=np.nan)
    real_bexp = max((r["exp"] for r in real if r["n"] >= 10), default=np.nan)
    print(f"real best-of-scan (n>=10): PF {real_best:.3f}   exp {real_bexp:+.2f}\n")

    days = sorted({int(d) for d in E.DAYS})
    rng = np.random.default_rng(20260822)
    rows = []
    t0 = time.time()
    for r in range(NPERM):
        perm = rng.permutation(days)
        donor = {d: int(p) for d, p in zip(days, perm)}
        res = [run_scan(a, donor) for a in ANCHORS]
        ok = [x for x in res if x["n"] >= 10]
        rows.append(dict(perm=r,
                         best_pf=max((x["pf"] for x in ok), default=np.nan),
                         best_exp=max((x["exp"] for x in ok), default=np.nan),
                         median_pf=float(np.median([x["pf"] for x in ok])) if ok else np.nan,
                         n_cells=len(ok)))
        if (r + 1) % 10 == 0:
            df = pd.DataFrame(rows)
            print(f"  perm {r+1}/{NPERM}  ({time.time()-t0:.0f}s)  "
                  f"best_pf median {df.best_pf.median():.2f}  "
                  f">= real: {int((df.best_pf >= real_best).sum())}", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv("research/microq3/results/R_permutation.csv", index=False)
    n = int(df.best_pf.notna().sum())
    ge_pf = int((df.best_pf >= real_best).sum())
    ge_ex = int((df.best_exp >= real_bexp).sum())
    print(f"\n{'='*90}\nANCHOR-TRANSPLANT NULL, {n} permutations, full 29-anchor scan each\n{'='*90}")
    print(f"real best-of-scan PF  {real_best:.3f}   null best-of-scan PF  "
          f"median {df.best_pf.median():.2f}  p90 {df.best_pf.quantile(.9):.2f}  max {df.best_pf.max():.2f}")
    print(f"real best-of-scan exp {real_bexp:+.2f}   null best exp median "
          f"{df.best_exp.median():+.2f}  p90 {df.best_exp.quantile(.9):+.2f}  max {df.best_exp.max():+.2f}")
    print(f"\nempirical p (PF):  {(ge_pf+1)/(n+1):.4f}   ({ge_pf} of {n} nulls match or beat it)")
    print(f"empirical p (exp): {(ge_ex+1)/(n+1):.4f}   ({ge_ex} of {n} nulls match or beat it)")
