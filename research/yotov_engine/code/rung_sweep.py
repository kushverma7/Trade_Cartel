"""All eight trade families from the spec, as one generic rung-to-rung sweep.

Every family in the spec is "enter at rung A, stop at rung B, target rung C"
inside a $25 quarter. Rather than hand-code six more variants of the same
geometry, this enumerates them, so families 1-8 and their natural controls come
out of one pass with identical fills.

Rungs, in hundredths of the quarter, measured from the originating LQP:
    lqp 0 | over 10 | hz 30 | half 50 | whole 80 | comp 90 | tgt 100
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/yotov_engine/code")
from engine import Ctx, walk_attempts, resolve, resolve_free, SUB
from qt_engine import PTS

HOLD_MS = 12 * 3600 * 1000
R = dict(lqp=0, over=10, hz=30, half=50, whole=80, comp=90, tgt=100)

# (label, enter_at, stop_at, target_at)  -- the spec's families 1-8
PLAN = [
    ("1 HZ->Half",            "hz",   "lqp",  "half"),
    ("2 Half->Whole",         "half", "hz",   "whole"),
    ("3 Whole->Completion",   "whole", "half", "comp"),
    ("4 Completion->LQP",     "comp", "whole", "tgt"),
    ("  over->HZ (control)",  "over", "lqp",  "hz"),
    ("  Half->Whole wide",    "half", "lqp",  "whole"),
    ("  Whole->Comp wide",    "whole", "lqp",  "comp"),
    ("  Comp->LQP wide",      "comp", "lqp",  "tgt"),
]
# reversal families 5-7: entered on losing a rung, traded back down the quarter
REV = [
    ("5 Failed HZ->LQP",      "hz",   "half", "lqp"),
    ("6 Failed Half->HZ",     "half", "whole", "hz"),
    ("7 Failed Whole->Half",  "whole", "comp", "half"),
]

PHASE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
TAG = sys.argv[2] if len(sys.argv) > 2 else "round"
DATA = {"2025-26": "research/microq3/data", "2024-25": "research/microq3/data_holdout"}
rows = []
for year, dd in DATA.items():
    ctx = Ctx(dd, year, S=25.0, phase_frac=PHASE)
    att = walk_attempts(ctx)
    idx, cells, ny, b = ctx.im, ctx.cm, ctx.book.ny, ctx.book
    print(f"\n{year}: {len(att)} attempts", flush=True)

    def emit(label, k0, up, q, stop_off, tgt_off, sgn):
        stop_c, tgt_c = q + stop_off * sgn, q + tgt_off * sgn
        e = int(b.ask[k0]) if up else int(b.bid[k0])
        sp, tp = ctx.px(stop_c), ctx.px(tgt_c)
        if up and not (sp < e < tp):    return
        if (not up) and not (tp < e < sp): return
        t_end = int(ny[k0]) + HOLD_MS
        pnl, tag, kx, e = resolve(ctx, k0, up, stop_c, tgt_c, t_end)
        pnl0, tag0 = resolve_free(ctx, k0, up, stop_c, tgt_c, t_end)
        risk = abs(e - sp); rew = abs(tp - e)
        if risk < ctx.f: return
        m = int(b.mid[k0]); rf, wf = abs(m - sp), abs(tp - m)
        rows.append(dict(year=year, fam=label, pnl=pnl / PTS, why=tag,
                         pnl_free=pnl0 / PTS, target=rew / PTS,
                         spread=(int(b.ask[k0]) - int(b.bid[k0])) / PTS,
                         p_geom=risk / (risk + rew), p_geom_free=rf / (rf + wf)))

    for r in att.itertuples():
        q, up = int(r.q), bool(r.up); sgn = 1 if up else -1
        for label, ent, stp, tgt in PLAN:
            t = getattr(r, f"t_{ent}", np.nan) if ent != "lqp" else r.k0
            if t == t:
                emit(label, int(t), up, q, R[stp], R[tgt], sgn)
        for label, lost, stp, tgt in REV:
            t = getattr(r, f"t_{lost}", np.nan)
            if t != t: continue
            j = int(np.searchsorted(idx, int(t), "left"))
            hit = None
            for m in range(j, min(j + 400000, len(cells))):
                if int(ny[idx[m]]) > int(ny[int(t)]) + HOLD_MS: break
                if (int(cells[m]) - q) * sgn < R[lost]:
                    hit = int(idx[m]); break
            if hit is not None:
                emit(label, hit, (not up), q, R[stp], R[tgt], sgn)
    del ctx

D = pd.DataFrame(rows)
D.to_csv(f"research/yotov_engine/results/rung_sweep_{TAG}.csv", index=False)
print(f"\n{'='*116}\nALL EIGHT SPEC FAMILIES — real fills vs zero-cost, both years pooled\n{'='*116}")
print(f"  {'family':>24}{'n':>7}{'tgt $':>8}{'PF':>7}{'WR':>8}{'p_geom':>9}{'EDGE':>8}"
      f"{'| PF free':>11}{'WR free':>9}{'EDGE free':>11}{'exp $':>9}")
for f in [p[0] for p in PLAN] + [p[0] for p in REV]:
    q = D[D.fam == f]
    if len(q) < 30: continue
    def PF(p):
        g, l = p[p > 0].sum(), -p[p < 0].sum(); return g / l if l > 0 else np.inf
    wr, pg = (q.pnl > 0).mean(), q.p_geom.mean()
    wf, pgf = (q.pnl_free > 0).mean(), q.p_geom_free.mean()
    print(f"  {f:>24}{len(q):>7}{q.target.median():>8.2f}{PF(q.pnl.values):>7.2f}"
          f"{100*wr:>7.1f}%{100*pg:>8.1f}%{100*(wr-pg):>+7.1f}%"
          f"{PF(q.pnl_free.values):>11.3f}{100*wf:>8.1f}%{100*(wf-pgf):>+10.1f}%"
          f"{q.pnl.mean():>+9.2f}")

print(f"\n{'='*116}\nCOST DRAG vs TARGET SIZE — why 'small target, high win rate' is the worst trade on gold\n{'='*116}")
D["bkt"] = pd.cut(D.target, [0, 2, 4, 7, 12, 20, 100])
print(f"  {'target $':>14}{'n':>8}{'WR':>8}{'exp free $':>13}{'exp real $':>13}"
      f"{'cost $/trade':>15}{'cost as % of target':>21}")
for k, q in D.groupby("bkt", observed=True):
    c = q.pnl_free.mean() - q.pnl.mean()
    print(f"  {str(k):>14}{len(q):>8}{100*(q.pnl>0).mean():>7.1f}%"
          f"{q.pnl_free.mean():>+13.3f}{q.pnl.mean():>+13.3f}{c:>15.3f}"
          f"{100*c/q.target.median():>20.1f}%")
