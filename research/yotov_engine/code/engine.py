"""YOTOV GOLD QUARTER ENGINE v1 — layers 1-4, tick-exact.

LAYER 1  Yotov quarter state. An ATTEMPT is a crossing of a Large Quarter Point
         (LQP) in some direction. Rungs, as fractions of the $25 quarter:
            0.10 overshoot end | 0.30 HZ end | 0.50 half
            0.80 whole         | 0.90 completion | 1.00 target LQP
         The attempt ends at the target LQP (TARGET) or on losing the
         originating LQP (LOST).
LAYER 2  Spaceman structural levels (levels.py), distance-scored against the
         LQP and against each rung.
LAYER 3  Liquidity events -- sweep of a structural level and reclaim.
LAYER 4  Timing -- the NY session minute of entry, carried as a feature.

THE MEASUREMENT THAT MATTERS. Every rung progression has a closed form: from a
level x of the way through the quarter, with the next rung at y and the origin
at 0, a driftless walk gets there first with probability x/y (H99). So a high
win rate proves nothing on its own. Every event therefore carries `p_geom`, the
gambler's-ruin probability implied by its OWN entry, stop and target:

    p_geom = risk / (risk + reward)

and the only result worth reporting is  observed WR - mean(p_geom).  That is
zero for any rule that is merely re-describing the geometry, whatever its win
rate, and it is what a real edge has to move.

FILL CONVENTION (repo standard, identical to research/insample/code/resolve.py):
long enters ASK and is marked out on BID; short the reverse. The TARGET is a
resting limit filling AT the target -- favourable overshoot is never credited.
The STOP is market-triggered at the real next executable quote, slippage and all.

GRID ARITHMETIC:  price >= line W <=> cell >= W  |  price <= line W <=> cell <= W-1
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/quarters/code"); sys.path.insert(0, "research/goldmap/code")
sys.path.insert(0, "research/yotov_engine/code")
from system import fine, _race, SUB
from qt_engine import Book, PTS
import levels as LV

OVER, HZ, HALF, WHOLE, COMP, TGT = 10, 30, 50, 80, 90, 100
RUNG = dict(over=OVER, hz=HZ, half=HALF, whole=WHOLE, comp=COMP, tgt=TGT)
DAY_MS = 86_400_000


class Ctx:
    """One year of ticks plus the fine grid and the structural levels."""

    def __init__(self, data_dir, year, S=25.0, phase_frac=0.0):
        self.book = Book(data_dir, year)
        self.S_i = int(round(S * PTS))
        self.ph = int(round(phase_frac * self.S_i))
        self.f = self.S_i // SUB
        b = self.book
        self.im, self.cm, _ = fine(b.mid, self.S_i, self.ph)
        self.ib, self.cb, _ = fine(b.bid, self.S_i, self.ph)
        self.ia, self.ca, _ = fine(b.ask, self.S_i, self.ph)
        self.sess = LV.build(f"{data_dir}/bars_1m_ny.parquet")
        # tick index -> session row, via the session's i0/i1 bar bounds
        self.sess_i0 = self.sess.i0.values
        self.sess_rows = [r for _, r in self.sess.iterrows()]

    def px(self, cell):
        return self.ph + cell * self.f

    def session_at(self, k):
        j = int(np.searchsorted(self.sess_i0, k, "right")) - 1
        return self.sess_rows[j] if 0 <= j < len(self.sess_rows) else None


def walk_attempts(ctx, max_open_ms=3 * DAY_MS, attempt_window_ms=DAY_MS):
    """LAYER 1. Every LQP attempt, with the tick index of each rung's first touch."""
    idx, cells, ny = ctx.im, ctx.cm, ctx.book.ny
    n = len(cells)
    out, seen = [], {}
    j = 1
    while j < n:
        c, prev = int(cells[j]), int(cells[j - 1])
        up = c > prev
        if up:
            q = -(-(prev + 1) // SUB) * SUB
            if q > c:
                j += 1; continue
        else:
            q = (prev // SUB) * SUB
            if q < c + 1:
                j += 1; continue
        hi, lo = (q + SUB, q - 1) if up else (q + 1, q - SUB)
        k0, t0 = int(idx[j]), int(ny[idx[j]])
        touch = {}
        peak = 0                       # deepest progress, in fine units
        trough_after = {}              # deepest retrace after each rung, from peak
        res, kx, m_end = "OPEN", k0, j
        for m in range(j, n):
            k = int(idx[m]); v = int(cells[m])
            prog = (v - q) if up else (q - v)
            if prog > peak:
                peak = prog
            for nm, off in RUNG.items():
                if nm not in touch and prog >= off:
                    touch[nm] = k
            # retrace tracking, measured from the running peak
            r = peak - prog
            for nm in ("hz", "half", "whole", "comp"):
                if nm in touch:
                    trough_after[nm] = max(trough_after.get(nm, 0), r)
            if (up and v >= hi) or ((not up) and v <= lo):
                res, kx, m_end = "TARGET", k, m; break
            if (up and v <= lo) or ((not up) and v >= hi):
                res, kx, m_end = "LOST", k, m; break
            if int(ny[k]) - t0 > max_open_ms:
                res, kx, m_end = "STALE", k, m; break
        else:
            m_end, kx = n - 1, int(idx[n - 1])
        # ATTEMPT NUMBER is RECENCY-windowed, not lifetime. The spec's rule is
        # "fresh attempt scores highest"; a lifetime counter makes every trade
        # after the first week attempt 300+, so the rule is never tested.
        key = (q, 1 if up else -1)
        hist = [t for t in seen.get(key, []) if t0 - t <= attempt_window_ms]
        hist.append(t0)
        seen[key] = hist
        out.append(dict(q=q, up=up, k0=k0, kx=kx, res=res, peak=peak,
                        attempt=len(hist), j0=j, jx=m_end,
                        mins=(int(ny[kx]) - t0) / 60000.0,
                        **{f"t_{k}": v for k, v in touch.items()},
                        **{f"rt_{k}": v for k, v in trough_after.items()}))
        while j < n and idx[j] <= kx:
            j += 1
    return pd.DataFrame(out)


def dual_hesitation(att, window_ms, ny):
    """LAYER 1 filter. An LQP is in DUAL HESITATION when both sides of it have
    reached their Hesitation Zone within `window_ms`. Returns a bool per row."""
    flag = np.zeros(len(att), bool)
    last = {}                                    # (q, dir) -> last HZ-touch time
    for i, r in enumerate(att.itertuples()):
        t = int(ny[r.k0])
        opp = last.get((r.q, not r.up))
        if opp is not None and t - opp <= window_ms:
            flag[i] = True
        if not np.isnan(getattr(r, "t_hz", np.nan)):
            last[(r.q, r.up)] = int(ny[int(r.t_hz)])
    return flag


def resolve(ctx, k0, up, stop_cell, tgt_cell, t_end):
    """Race stop vs target on the real quote path. -> (pnl_int, tag, kx)."""
    b = ctx.book
    e = int(b.ask[k0]) if up else int(b.bid[k0])
    stop_px, tgt_px = ctx.px(stop_cell), ctx.px(tgt_cell)
    if up:
        p0 = max(int(np.searchsorted(ctx.ib, k0, "right")) - 1, 0)
        kx, why = _race(ctx.ib, ctx.cb, p0, tgt_cell, stop_cell - 1, True, t_end, b.ny)
        pnl = (tgt_px - e) if why == "WIN" else (int(b.bid[kx]) - e)
    else:
        p0 = max(int(np.searchsorted(ctx.ia, k0, "right")) - 1, 0)
        kx, why = _race(ctx.ia, ctx.ca, p0, stop_cell, tgt_cell - 1, False, t_end, b.ny)
        pnl = (e - tgt_px) if why == "WIN" else (e - int(b.ask[kx]))
    return pnl, {"WIN": "TP", "LOSE": "SL", "TIME": "TIME"}[why], kx, e


def resolve_free(ctx, k0, up, stop_cell, tgt_cell, t_end):
    """ZERO-COST control: enter and exit at the MIDPOINT, no spread, no
    slippage. If a rule is a coin flip that loses only to execution, this comes
    back at PF ~1.00 and edge ~0. If the rule is actively anti-predictive, the
    edge stays negative here too. It is the diagnostic that separates the two."""
    b = ctx.book
    e = int(b.mid[k0])
    stop_px, tgt_px = ctx.px(stop_cell), ctx.px(tgt_cell)
    p0 = max(int(np.searchsorted(ctx.im, k0, "right")) - 1, 0)
    if up:
        kx, why = _race(ctx.im, ctx.cm, p0, tgt_cell, stop_cell - 1, True, t_end, b.ny)
        pnl = (tgt_px - e) if why == "WIN" else (int(b.mid[kx]) - e)
    else:
        kx, why = _race(ctx.im, ctx.cm, p0, stop_cell, tgt_cell - 1, False, t_end, b.ny)
        pnl = (e - tgt_px) if why == "WIN" else (e - int(b.mid[kx]))
    return pnl, {"WIN": "TP", "LOSE": "SL", "TIME": "TIME"}[why]
