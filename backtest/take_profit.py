"""
Profit-taking engine: fixed targets instead of (or alongside) a trailing stop.

User brief 2026-07-31: "turn it into a profitable profit taking strategy...
see if key levels, quarters or point based profit taking works."

This repo's standing finding is that targets cut winners and destroy trend
systems. That finding was measured on a TREND entry with a 6 ATR stop, where
the target/stop ratio was hopeless. It says nothing about a short-hold entry
paired with a target sized correctly against its stop, which is a different
architecture and deserves its own measurement rather than an argument.

So this engine exists to answer the question properly. Four target modes:

    "atr"      target = N x ATR from entry
    "points"   target = N price points from entry (gold handles)
    "level"    next SpacemanBTC key level at least min_atr away
    "quarter"  next multiple of a fixed price grid (Yotov 250 / JEAFX 2.50)

with an optional runner: take part at the target and trail the rest, which is
the only structure that has ever beaten a pure trail in this repo.

EXECUTION MODEL (identical costs/sizing to trend.py so the ledger compares)
  - entry at the signal bar's close
  - from the NEXT bar, stop and target checked against high/low
  - a bar that touches BOTH is assumed to hit the STOP first, always
  - the stop fill is gap-aware (BUG-018): a bar that opens through the stop
    fills at the open
  - the target fill is NOT gap-aware in the trade's favour: it fills at the
    target price even if the bar gapped past it, which is the conservative
    side for a limit order
  - costs per contract per side, notional capped at equity * max_lev
"""
import numpy as np
import pandas as pd


def _atr(h, l, c, n=14):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1.0 / n, adjust=False).mean().to_numpy()


def run(df, sigL, sigS, target_mode="atr", target_val=2.0, stop_atr=2.0,
        min_target_atr=0.0, max_target_atr=0.0, kl=None, grid=0.0,
        partial_pct=0.0, trail_after=0.0, time_stop=0, breakeven_atr=0.0,
        cooldown=0, atr_n=14, risk_pct=1.0, equity0=10000.0,
        commission=0.07, slippage=0.05, max_lev=20, long_only=False):
    o = df["open"].to_numpy(float); h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float);  c = df["close"].to_numpy(float)
    n = len(c)
    A = _atr(h, l, c, atr_n)
    KL = None if kl is None else np.asarray(kl, float)

    eq = equity0
    trades = []
    pos = None
    last_exit = -10 ** 9

    def pick_target(entry, d, i):
        a = A[i]
        floor_ = a * min_target_atr
        if target_mode == "atr":
            return entry + d * a * target_val
        if target_mode == "points":
            return entry + d * target_val
        if target_mode == "pct":
            # scale-invariant version of "points". Gold ran 1450 -> 4100 over
            # this sample, so a FIXED point target is silently a shrinking
            # percentage target. This mode separates "a target of about this
            # size works" from "this particular number fitted this price path".
            return entry * (1.0 + d * target_val / 100.0)
        if target_mode == "rr":
            return entry + d * a * stop_atr * target_val
        if target_mode == "quarter":
            base = entry + d * floor_
            return ((np.floor(base / grid) + 1) * grid if d > 0
                    else (np.ceil(base / grid) - 1) * grid)
        if target_mode == "level":
            if KL is None:
                return np.nan
            row = KL[i]
            base = entry + d * floor_
            fwd = row[row > base] if d > 0 else row[row < base]
            fwd = fwd[~np.isnan(fwd)]
            if not fwd.size:
                return np.nan
            t = fwd.min() if d > 0 else fwd.max()
            if max_target_atr > 0 and abs(t - entry) > a * max_target_atr:
                return np.nan
            return t
        raise ValueError(target_mode)

    for i in range(max(atr_n, 210) + 1, n):
        if pos is not None:
            d = pos["dir"]
            a = A[i]
            # move the stop to breakeven once the trade is far enough ahead
            if breakeven_atr > 0 and not pos["be"]:
                far = ((h[i] >= pos["entry"] + a * breakeven_atr) if d > 0
                       else (l[i] <= pos["entry"] - a * breakeven_atr))
                if far:
                    pos["stop"] = pos["entry"]
                    pos["be"] = True
            # the runner trails once the partial is banked
            if trail_after > 0 and pos["part_done"]:
                cand = (h[i - 1] - a * trail_after if d > 0
                        else l[i - 1] + a * trail_after)
                pos["stop"] = (max(pos["stop"], cand) if d > 0
                               else min(pos["stop"], cand))
            hit_stop = (l[i] <= pos["stop"]) if d > 0 else (h[i] >= pos["stop"])
            hit_tgt = (not np.isnan(pos["tgt"]) and not pos["part_done"] and
                       ((h[i] >= pos["tgt"]) if d > 0 else (l[i] <= pos["tgt"])))
            closed = False
            if hit_stop:                       # stop always assumed first
                px = pos["stop"]
                px = min(px, o[i]) if d > 0 else max(px, o[i])
                px -= d * slippage
                pnl = d * (px - pos["entry"]) * pos["qty"] - 2 * commission * pos["qty"]
                eq += pnl
                trades.append({"pnl": pnl + pos["banked"], "dir": d,
                               "bar": pos["bar"], "bars_held": i - pos["bar"],
                               "why": "stop"})
                closed = True
            elif hit_tgt:
                px = pos["tgt"] - d * slippage
                frac = partial_pct if (partial_pct > 0 and trail_after > 0) else 1.0
                qout = pos["qty"] if frac >= 1.0 else float(np.floor(pos["qty"] * frac))
                if qout < 1:
                    qout = pos["qty"]
                pnl = d * (px - pos["entry"]) * qout - 2 * commission * qout
                eq += pnl
                pos["banked"] += pnl
                pos["qty"] -= qout
                pos["part_done"] = True
                if pos["qty"] < 1:
                    trades.append({"pnl": pos["banked"], "dir": d, "bar": pos["bar"],
                                   "bars_held": i - pos["bar"], "why": "target"})
                    closed = True
            elif time_stop and i - pos["bar"] >= time_stop:
                px = c[i] - d * slippage
                pnl = d * (px - pos["entry"]) * pos["qty"] - 2 * commission * pos["qty"]
                eq += pnl
                trades.append({"pnl": pnl + pos["banked"], "dir": d, "bar": pos["bar"],
                               "bars_held": i - pos["bar"], "why": "time"})
                closed = True
            if closed:
                pos = None
                last_exit = i

        if pos is not None or np.isnan(A[i]) or A[i] <= 0:
            continue
        if i - last_exit < cooldown:
            continue
        d = 1 if sigL[i] else (-1 if (sigS[i] and not long_only) else 0)
        if d == 0:
            continue
        sdist = A[i] * stop_atr
        entry = c[i] + d * slippage
        tgt = pick_target(entry, d, i)
        if np.isnan(tgt) or (d > 0 and tgt <= entry) or (d < 0 and tgt >= entry):
            continue
        qty = float(np.floor(max(min(eq * risk_pct / 100.0 / sdist,
                                     eq * max_lev / c[i]), 0)))
        if qty < 1:
            continue
        pos = {"dir": d, "entry": entry, "qty": qty, "bar": i,
               "stop": entry - d * sdist, "tgt": tgt, "banked": 0.0,
               "part_done": False, "be": False}
    return trades


def stats(trades, equity0=10000.0):
    if not trades:
        return {"n": 0, "wr": np.nan, "pf": np.nan, "net_pct": 0.0,
                "maxdd_pct": np.nan, "avg_bars": np.nan}
    p = np.array([t["pnl"] for t in trades])
    gw, gl = p[p > 0].sum(), -p[p < 0].sum()
    curve = equity0 + np.cumsum(p)
    peak = np.maximum.accumulate(curve)
    return {"n": len(p), "wr": float((p > 0).mean() * 100),
            "pf": float(gw / gl) if gl > 0 else float("inf"),
            "net_pct": float(p.sum() / equity0 * 100),
            "maxdd_pct": float(((peak - curve) / peak).max() * 100),
            "avg_bars": float(np.mean([t["bars_held"] for t in trades]))}
