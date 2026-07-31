"""
Fast bar-loop backtester for the Key Levels strategy.

WHY NOT BACKTRADER FOR THE SEARCH: backtrader is event-driven Python and
runs roughly 10k bars/sec/config. A greedy selection over 18 levels is
~150 configs; a naive full subset search would be 262,144. This loop does
one config over 20k bars in well under a second, which makes the search
tractable. backtrader is kept for cross-validating a single config
(validate_bt.py) -- two independent implementations agreeing is the check
that this one is not quietly wrong.

EXECUTION MODEL (matches the Pine build's process_orders_on_close=true)
  - entry filled at the signal bar's close
  - from the NEXT bar onward, stop and targets are checked against
    high/low; if a bar touches both the stop and a target, the STOP is
    assumed first (conservative, never flatters the result)
  - TP1 closes q1, the remainder runs to TP2 or the stop
  - costs charged per contract per side, plus slippage in price
  - BUG-012 guard: notional is capped at equity * max_leverage
"""
import numpy as np

FIELDS = ("open", "high", "low", "close")


class Config:
    def __init__(self, levels, mode="both", tol_atr=0.25, buf_atr=0.30,
                 min_sl=1.0, max_sl=2.5, cooldown=3, vol_min=0.7,
                 tp_mode="levels", tp1_r=1.5, tp2_r=3.0, tp1_pct=60,
                 min_tp_r=1.0, brk_lb=12, risk_pct=1.0, max_lev=20,
                 max_day=6, time_stop=36, session=True,
                 commission=0.07, slippage=0.05, equity0=10000.0,
                 random_p=0.0, random_seed=0):
        # random_p > 0 replaces the SIGNAL with a coin flip fired at that
        # per-bar probability, leaving every other rule -- filters, stops,
        # targets, sizing, costs -- untouched. That is the only honest
        # reference for a strategy: not "did it make money", but "did it
        # beat random entries wearing the same exit machinery".
        self.__dict__.update(locals()); del self.__dict__["self"]


def atr(h, l, c, n=14):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    out = np.full(len(tr), np.nan)
    if len(tr) > n:
        out[n] = tr[1:n + 1].mean()
        for i in range(n + 1, len(tr)):
            out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def run(df, lv, cfg, in_session, sigL_ext=None, sigS_ext=None):
    """Returns (trades, stats). trades: list of dicts with pnl + attribution."""
    o, h, l, c = (df[k].to_numpy(float) for k in FIELDS)
    n = len(c)
    A = atr(h, l, c, 14)
    Aavg = np.convolve(np.nan_to_num(A), np.ones(20) / 20, mode="full")[:n]
    L = lv[cfg.levels].to_numpy(float) if cfg.levels else np.zeros((n, 0))
    ids = [lv.columns.get_loc(x) for x in cfg.levels]

    lowLB = np.full(n, np.nan); highLB = np.full(n, np.nan)
    for i in range(cfg.brk_lb, n):
        lowLB[i] = l[i - cfg.brk_lb:i].min()
        highLB[i] = h[i - cfg.brk_lb:i].max()

    rng = np.random.default_rng(cfg.random_seed)
    eq = cfg.equity0
    trades = []
    pos = None
    last_sig = -10 ** 9
    day_key = df.index.normalize().to_numpy()
    day_trades = 0; cur_day = None

    for i in range(1, n):
        if cur_day is None or day_key[i] != cur_day:
            cur_day = day_key[i]; day_trades = 0

        # ---- manage an open position on this bar ----
        if pos is not None:
            d = pos["dir"]
            hit_stop = (l[i] <= pos["sl"]) if d > 0 else (h[i] >= pos["sl"])
            hit_tp1 = (h[i] >= pos["tp1"]) if d > 0 else (l[i] <= pos["tp1"])
            hit_tp2 = (h[i] >= pos["tp2"]) if d > 0 else (l[i] <= pos["tp2"])
            closed = False
            if hit_stop:                                   # stop first, always
                px = pos["sl"] - d * cfg.slippage
                pnl = d * (px - pos["entry"]) * pos["qty_open"]
                pnl -= pos["qty_open"] * cfg.commission
                pos["pnl"] += pnl; closed = True
            else:
                if hit_tp1 and pos["q1"] > 0:
                    px = pos["tp1"] - d * cfg.slippage
                    pos["pnl"] += d * (px - pos["entry"]) * pos["q1"] - pos["q1"] * cfg.commission
                    pos["qty_open"] -= pos["q1"]; pos["q1"] = 0
                if hit_tp2 and pos["qty_open"] > 0:
                    px = pos["tp2"] - d * cfg.slippage
                    pos["pnl"] += d * (px - pos["entry"]) * pos["qty_open"] - pos["qty_open"] * cfg.commission
                    pos["qty_open"] = 0; closed = True
                elif pos["qty_open"] == 0:
                    closed = True
            if not closed and i - pos["bar"] >= cfg.time_stop:
                px = c[i] - d * cfg.slippage
                pos["pnl"] += d * (px - pos["entry"]) * pos["qty_open"] - pos["qty_open"] * cfg.commission
                pos["qty_open"] = 0; closed = True
            if closed:
                eq += pos["pnl"]
                trades.append({"pnl": pos["pnl"], "lvl": pos["lvl"],
                               "sweep": pos["sweep"], "retest": pos["retest"],
                               "dir": d, "bar": pos["bar"],
                               # full plan, so an independent backtester can
                               # replay this trade exactly (validate_bt.py)
                               "qty": pos["qty0"], "q1": pos["q1_0"],
                               "sl": pos["sl"], "tp1": pos["tp1"],
                               "tp2": pos["tp2"], "entry": pos["entry"]})
                pos = None

        if pos is not None or np.isnan(A[i]) or A[i] <= 0:
            continue
        if cfg.session and not in_session[i]:
            continue
        if A[i] <= Aavg[i] * cfg.vol_min:
            continue
        if i - last_sig <= cfg.cooldown or day_trades >= cfg.max_day:
            continue

        tol = A[i] * cfg.tol_atr
        row = L[i]
        ok = ~np.isnan(row)
        if not ok.any():
            continue
        vals = row[ok]

        swL = ((l[i] < vals) & (c[i] > vals)).any() and c[i] > o[i]
        swS = ((h[i] > vals) & (c[i] < vals)).any() and c[i] < o[i]
        rtL = rtS = False
        if not np.isnan(lowLB[i]):
            rtL = ((c[i] > vals) & (l[i] <= vals + tol) & (l[i] > vals - tol) & (lowLB[i] < vals)).any()
            rtS = ((c[i] < vals) & (h[i] >= vals - tol) & (h[i] < vals + tol) & (highLB[i] > vals)).any()
        if cfg.random_p > 0:
            if rng.random() >= cfg.random_p:
                continue
            d0 = 1 if rng.random() < 0.5 else -1
            cand0 = (vals < c[i]) if d0 > 0 else (vals > c[i])
            if not cand0.any():
                continue
            sel0 = np.flatnonzero(ok)[cand0]
            j = int(np.argmin(np.abs(c[i] - vals[cand0])))
            defend = vals[cand0][j]
            lvl_id = ids[sel0[j]]
            d = d0
            raw = (c[i] - defend if d > 0 else defend - c[i]) + A[i] * cfg.buf_atr
            sl_dist = min(max(raw, A[i] * cfg.min_sl), A[i] * cfg.max_sl)
            if sl_dist <= 0:
                continue
            entry = c[i] + d * cfg.slippage
            sl = entry - d * sl_dist
            tp1 = entry + d * sl_dist * cfg.tp1_r
            tp2 = entry + d * sl_dist * cfg.tp2_r
            qty = min(eq * cfg.risk_pct / 100.0 / sl_dist, eq * cfg.max_lev / c[i])
            qty = float(np.floor(max(qty, 0)))
            if qty < 1:
                continue
            q1 = min(max(float(np.floor(qty * cfg.tp1_pct / 100.0)), 0), qty)
            pos = {"dir": d, "entry": entry, "sl": sl, "tp1": tp1, "tp2": tp2,
                   "qty_open": qty, "q1": q1, "pnl": -qty * cfg.commission,
                   "bar": i, "lvl": lvl_id, "qty0": qty, "q1_0": q1,
                   "sweep": False, "retest": False}
            last_sig = i; day_trades += 1
            continue

        if sigL_ext is not None:
            # externally supplied signal (e.g. the 22-voice conviction score).
            # Everything downstream -- defended level, stop, targets, sizing,
            # costs -- is unchanged, so voice results are directly comparable
            # to the key-level results and to the random null.
            sigL, sigS = bool(sigL_ext[i]), bool(sigS_ext[i])
        else:
            can_sw = cfg.mode in ("sweep", "both")
            can_rt = cfg.mode in ("retest", "both")
            sigL = (can_sw and swL) or (can_rt and rtL)
            sigS = (can_sw and swS) or (can_rt and rtS)
        if sigL == sigS:                                   # none, or ambiguous
            continue

        d = 1 if sigL else -1
        cand = (l[i] < vals) & (c[i] > vals) if d > 0 else (h[i] > vals) & (c[i] < vals)
        if not cand.any() and sigL_ext is not None:
            cand = (vals < c[i]) if d > 0 else (vals > c[i])   # nearest level to defend
        if not cand.any():
            continue
        idx_ok = np.flatnonzero(ok)[np.flatnonzero(cand[np.flatnonzero(cand)] | True)]
        sel = np.flatnonzero(ok)[cand]
        defend = vals[cand][np.argmin(np.abs(c[i] - vals[cand]))]
        lvl_id = ids[sel[int(np.argmin(np.abs(c[i] - vals[cand])))]]

        raw = (c[i] - defend if d > 0 else defend - c[i]) + A[i] * cfg.buf_atr
        sl_dist = min(max(raw, A[i] * cfg.min_sl), A[i] * cfg.max_sl)
        if sl_dist <= 0:
            continue
        entry = c[i] + d * cfg.slippage
        sl = entry - d * sl_dist

        tp1 = tp2 = np.nan
        if cfg.tp_mode == "levels":
            above = np.sort(vals[vals > c[i]]) if d > 0 else np.sort(vals[vals < c[i]])[::-1]
            need = sl_dist * cfg.min_tp_r
            far = [x for x in above if abs(x - c[i]) >= need and abs(x - c[i]) <= A[i] * 8]
            if far:
                tp1 = far[0]
                nxt = [x for x in far[1:] if abs(x - tp1) >= sl_dist * 0.5]
                tp2 = nxt[0] if nxt else np.nan
        if np.isnan(tp1):
            tp1 = entry + d * sl_dist * cfg.tp1_r
        if np.isnan(tp2):
            tp2 = entry + d * sl_dist * cfg.tp2_r

        qty = min(eq * cfg.risk_pct / 100.0 / sl_dist, eq * cfg.max_lev / c[i])
        qty = float(np.floor(max(qty, 0)))
        if qty < 1:
            continue
        q1 = float(np.floor(qty * cfg.tp1_pct / 100.0))
        q1 = min(max(q1, 0), qty)

        pos = {"dir": d, "entry": entry, "sl": sl, "tp1": tp1, "tp2": tp2,
               "qty_open": qty, "q1": q1, "pnl": -qty * cfg.commission,
               "bar": i, "lvl": lvl_id, "qty0": qty, "q1_0": q1,
               "sweep": bool(swL if d > 0 else swS) if sigL_ext is None else False,
               "retest": bool(rtL if d > 0 else rtS) if sigL_ext is None else False}
        last_sig = i; day_trades += 1

    return trades, stats(trades, cfg.equity0)


def stats(trades, equity0=10000.0):
    if not trades:
        return {"n": 0, "wr": float("nan"), "pf": float("nan"),
                "net": 0.0, "net_pct": 0.0, "maxdd_pct": float("nan")}
    p = np.array([t["pnl"] for t in trades])
    gw, gl = p[p > 0].sum(), -p[p < 0].sum()
    curve = equity0 + np.cumsum(p)
    peak = np.maximum.accumulate(curve)
    dd = (peak - curve) / peak
    return {"n": len(p), "wr": float((p > 0).mean() * 100),
            "pf": float(gw / gl) if gl > 0 else float("inf"),
            "net": float(p.sum()), "net_pct": float(p.sum() / equity0 * 100),
            "maxdd_pct": float(dd.max() * 100)}
