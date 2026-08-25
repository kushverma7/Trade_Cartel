"""The five trade families the spec prioritises, built on engine.py's layers.

Each family returns candidate events with an entry tick, a stop cell, a target
cell, and the features needed to score them (confluence, timing, attempt
number, dual hesitation, $100 transition state).

Every event carries p_geom = risk/(risk+reward), the driftless probability of
reaching the target before the stop. A family is only interesting if its
realised win rate beats the mean p_geom of its own trades.

    F1  QUARTER SWEEP REVERSAL   a structural level sits near the LQP; price
        sweeps through both, fails to clear the far Hesitation Zone, then
        reclaims the LQP. Enter on the reclaim, stop beyond the sweep low,
        target the opposite HZ end.
    F2  QUARTER ACCEPTANCE       HZ cleared, price pulls back without losing
        the LQP, then reclaims its high. Enter there, stop at the LQP, target
        the Half point.
    F3  WHOLE -> COMPLETION      the quarter has reached the Whole. Enter,
        stop at the Half, target the Completion Zone.
    F4  FAILED COMPLETION        price reached Completion but loses the Whole.
        Enter short-side, stop back at Completion, target the Half.
    F5  MAJOR TRANSITION         the first $25 quarter of a new $100 range
        completes AND the $100 boundary holds on the pullback. Enter, stop at
        the $100 boundary, target the next LQP.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/yotov_engine/code")
from engine import (Ctx, walk_attempts, dual_hesitation, resolve, resolve_free,
                    OVER, HZ, HALF, WHOLE, COMP, TGT, SUB, DAY_MS)
from qt_engine import PTS
import levels as LV

HOLD_MS = 12 * 3600 * 1000          # intraday clock; the 3-day rule is separate


def _first_cross_after(idx, cells, jstart, want, up, ny, t_end):
    """First position at/after jstart where cell crosses `want` in direction up."""
    for m in range(jstart, len(cells)):
        if int(ny[idx[m]]) > t_end:
            return None
        v = int(cells[m])
        if (up and v >= want) or ((not up) and v <= want - 1):
            return m
    return None


def _features(ctx, k0, q, up, att_row, dual):
    """Layer 2 + 4 features for one candidate."""
    b = ctx.book
    t = int(b.ny[k0])
    px = int(b.mid[k0])
    row = ctx.session_at(k0)
    hm = (t // 60000) % 1440
    best_nm, best_d = "", 1e18
    if row is not None:
        for nm, lvl, ready in LV.levels_for(row):
            if ready and hm < ready and not (hm >= 18 * 60):
                continue                       # Asia not complete yet
            d = abs(lvl - px)
            if d < best_d:
                best_nm, best_d = nm, d
    return dict(t=t, hm=hm, entry_mid=px / PTS,
                conf_level=best_nm, conf_dist=best_d / PTS,
                attempt=int(att_row.attempt), dual=bool(dual),
                spread=(int(b.ask[k0]) - int(b.bid[k0])) / PTS)


def _emit(ctx, fam, k0, up, q, entry_cell, stop_cell, tgt_cell, att_row, dual):
    """Build one event, resolve it, and score it against its own geometry."""
    b = ctx.book
    risk_c, rew_c = abs(entry_cell - stop_cell), abs(tgt_cell - entry_cell)
    if risk_c <= 0 or rew_c <= 0:
        return None
    e_px = int(b.ask[k0]) if up else int(b.bid[k0])
    # entry must sit strictly between its own stop and target
    if up and not (ctx.px(stop_cell) < e_px < ctx.px(tgt_cell)):
        return None
    if (not up) and not (ctx.px(tgt_cell) < e_px < ctx.px(stop_cell)):
        return None
    t_end = int(b.ny[k0]) + HOLD_MS
    pnl, tag, kx, e = resolve(ctx, k0, up, stop_cell, tgt_cell, t_end)
    pnl0, tag0 = resolve_free(ctx, k0, up, stop_cell, tgt_cell, t_end)
    risk_real = abs(e - ctx.px(stop_cell))
    if risk_real < ctx.f:
        return None
    return dict(fam=fam, up=up, q=q, entry=e / PTS,
                stop=ctx.px(stop_cell) / PTS, target=ctx.px(tgt_cell) / PTS,
                risk=risk_real / PTS, reward=abs(ctx.px(tgt_cell) - e) / PTS,
                p_geom=risk_real / (risk_real + abs(ctx.px(tgt_cell) - e)),
                p_geom_free=(abs(int(b.mid[k0]) - ctx.px(stop_cell)) /
                             (abs(int(b.mid[k0]) - ctx.px(stop_cell)) +
                              abs(ctx.px(tgt_cell) - int(b.mid[k0])))),
                pnl=pnl / PTS, R=pnl / risk_real, why=tag,
                pnl_free=pnl0 / PTS, why_free=tag0,
                mins=(int(b.ny[kx]) - int(b.ny[k0])) / 60000.0,
                k0=k0, kx=kx, **_features(ctx, k0, q, up, att_row, dual))


def run(ctx, sweep_max=6.25, retrace_min=10, dual_window_h=6):
    """Generate every candidate from every family. Returns a DataFrame."""
    att = walk_attempts(ctx)
    ny, idx, cells = ctx.book.ny, ctx.im, ctx.cm
    dual = dual_hesitation(att, dual_window_h * 3600 * 1000, ny)
    out = []

    for i, r in enumerate(att.itertuples()):
        q, up, d = int(r.q), bool(r.up), (1 if r.up else -1)
        sgn = d
        t_open = int(ny[r.k0])
        t_end = t_open + HOLD_MS

        # ---------- F2  QUARTER ACCEPTANCE ------------------------------
        # HZ cleared, then a retrace of >= retrace_min fine units that does NOT
        # lose the LQP, then price reclaims the pre-retrace high.
        t_hz = getattr(r, "t_hz", np.nan)
        if t_hz == t_hz and getattr(r, "rt_hz", 0) >= retrace_min:
            jh = int(np.searchsorted(idx, int(t_hz), "left"))
            peak, jre = HZ, None
            for m in range(jh, r.jx + 1):
                prog = (int(cells[m]) - q) * sgn
                if prog <= 0:
                    break                                  # LQP lost, no setup
                if prog > peak:
                    peak = prog
                if peak - prog >= retrace_min:
                    jre = _first_cross_after(idx, cells, m, q + peak * sgn,
                                             up, ny, t_end)
                    break
            if jre is not None:
                ev = _emit(ctx, "F2_acceptance", int(idx[jre]), up, q,
                           q + peak * sgn, q, q + HALF * sgn, r, dual[i])
                if ev: out.append(ev)

        # ---------- F3  WHOLE -> COMPLETION -----------------------------
        t_w = getattr(r, "t_whole", np.nan)
        if t_w == t_w:
            ev = _emit(ctx, "F3_whole_comp", int(t_w), up, q,
                       q + WHOLE * sgn, q + HALF * sgn, q + COMP * sgn, r, dual[i])
            if ev: out.append(ev)

        # ---------- F4  FAILED COMPLETION -------------------------------
        # reached Completion, then loses the Whole -> trade the other way
        t_c = getattr(r, "t_comp", np.nan)
        if t_c == t_c:
            jc = int(np.searchsorted(idx, int(t_c), "left"))
            jf = _first_cross_after(idx, cells, jc, q + WHOLE * sgn, not up,
                                    ny, t_end)
            if jf is not None:
                ev = _emit(ctx, "F4_failed_comp", int(idx[jf]), (not up), q,
                           q + WHOLE * sgn, q + COMP * sgn, q + HALF * sgn,
                           r, dual[i])
                if ev: out.append(ev)

        # ---------- F1  QUARTER SWEEP REVERSAL --------------------------
        # a structural level within sweep_max of the LQP, price sweeps past
        # both but fails to clear the far HZ, then reclaims the LQP.
        if r.peak < HZ and r.res == "LOST":
            row = ctx.session_at(r.k0)
            if row is not None:
                qpx = ctx.px(q)
                near = [(nm, lv) for nm, lv, rd in LV.levels_for(row)
                        if abs(lv - qpx) <= sweep_max * PTS]
                if near:
                    jr = _first_cross_after(idx, cells, r.jx, q, not up, ny, t_end)
                    if jr is not None:
                        ev = _emit(ctx, "F1_sweep_reclaim", int(idx[jr]),
                                   (not up), q, q, q + r.peak * sgn,
                                   q - HZ * sgn, r, dual[i])
                        if ev:
                            ev["sweep_level"] = near[0][0]
                            ev["sweep_depth"] = r.peak / SUB * 25.0
                            out.append(ev)

        # ---------- F5  MAJOR TRANSITION --------------------------------
        # the LQP is also a $100 boundary, the first quarter completes, and
        # the boundary holds on the pullback.
        if r.res == "TARGET" and (q % (4 * SUB) == 0):
            nq = q + TGT * sgn
            jt = int(np.searchsorted(idx, r.kx, "left"))
            jpb = None
            for m in range(jt, len(cells)):
                if int(ny[idx[m]]) > t_end:
                    break
                prog = (int(cells[m]) - q) * sgn
                if prog <= 0:
                    break                                   # boundary lost
                if prog <= TGT - HZ:                        # pulled back into it
                    jpb = m; break
            if jpb is not None:
                jre = _first_cross_after(idx, cells, jpb, nq, up, ny, t_end)
                if jre is not None:
                    ev = _emit(ctx, "F5_major_transition", int(idx[jre]), up, q,
                               nq, q, nq + HALF * sgn, r, dual[i])
                    if ev: out.append(ev)

    df = pd.DataFrame(out)
    if len(df):
        df = df.sort_values("t").reset_index(drop=True)
    return df, att


def stats(d):
    if not len(d):
        return None
    p = d.pnl.values
    gp, gl = p[p > 0].sum(), -p[p < 0].sum()
    wr = float((p > 0).mean())
    pg = float(d.p_geom.mean())
    eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
    return dict(n=len(p), pf=(gp / gl if gl > 0 else np.inf), wr=100 * wr,
                p_geom=100 * pg, edge=100 * (wr - pg), net=float(p.sum()),
                exp=float(p.mean()), expR=float(d.R.mean()),
                mdd=float((pk - eq).max()), med_min=float(d.mins.median()))
