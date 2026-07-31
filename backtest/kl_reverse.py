"""
Key-level stop-and-reverse engine.

USER SPEC (2026-07-31): "i want you to enter and exit the trade on key
levels. reverse the signal as it touches the key level."

So the level is the ONLY thing that moves the book. There is no Donchian
breakout, no EMA cross, no time stop. One rule:

    price touches a key level  ->  take the position that faces AWAY from
                                   the side price arrived from

Arriving from below and tagging the level is a rejection setup: close any
long, open a short. Arriving from above: close the short, open a long.
The exit of one trade IS the entry of the next -- "key level to key
level" literally. The book is always in the market once the first level
is tagged.

Two variants are implemented because the spec's assumption (levels
reject) is exactly the thing that has to be tested, not assumed:

    mode="reverse"  fade the level (the user's spec)
    mode="break"    trade WITH the break instead (the null of the spec --
                    if this wins, levels are continuation points, not
                    reversal points, and the spec is backwards)

The levels themselves come from backtest.levels.build, which is the port
of the same SpacemanBTC module the Pine host embeds, so a level tagged
here is a level drawn on the chart.

EXECUTION MODEL (identical costs/sizing to engine.py and trend.py so the
ledger stays comparable)
  - a level is tagged when the bar's range contains it (within tol)
  - the fill is the bar's CLOSE, not the level: the rule is confirmed on
    bar close, and filling at the level would credit an intrabar limit
    this engine never places
  - protective ATR stop, ratcheting; the reversal usually gets there first
  - a level is ignored while it sits within min_gap ATRs of the level that
    produced the current position, otherwise a cluster of near-identical
    levels (PDH/P4HH/LONH stacked) flips the book every bar
  - costs charged per contract per side, slippage in price
  - notional capped at equity * max_lev (BUG-012)
"""
import numpy as np
import pandas as pd

FIELDS = ("open", "high", "low", "close")


def run(df, lv, levels=None, mode="reverse", tol_atr=0.10, min_gap_atr=1.0,
        stop_atr=6.0, always_in=True, ema_gate=0, slope_len=0,
        short_risk=1.0, cooldown=0,
        risk_pct=1.0, equity0=10000.0, commission=0.07, slippage=0.05,
        max_lev=20, atr_n=14, random_p=0.0, random_seed=0):
    o, h, l, c = (df[k].to_numpy(float) for k in FIELDS)
    n = len(c)
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    atr = pd.Series(tr).ewm(alpha=1 / atr_n, adjust=False).mean().to_numpy()

    cols = list(levels) if levels else list(lv.columns)
    L = lv[cols].to_numpy(float)

    ema = (pd.Series(c).ewm(span=ema_gate, adjust=False).mean().to_numpy()
           if ema_gate else None)
    slope_dn = None
    if slope_len and ema is not None:
        sh = np.full(n, np.nan)
        sh[slope_len:] = ema[:-slope_len]
        slope_dn = ema < sh

    rng = np.random.default_rng(random_seed)
    eq = equity0
    trades = []
    pos = None
    last_bar = -10 ** 9

    for i in range(atr_n + 2, n):
        a = atr[i]
        if np.isnan(a) or a <= 0:
            continue
        tol = a * tol_atr
        gap = a * min_gap_atr

        # ---- which level, if any, does this bar tag? ----------------
        # nearest-to-the-previous-close wins, so a bar that sweeps several
        # stacked levels is attributed to the first one it would have met.
        row = L[i]
        sig = 0
        hit_px = np.nan
        if random_p > 0:
            if rng.random() < random_p:
                sig = 1 if rng.random() < 0.5 else -1
                hit_px = c[i]
        else:
            best = np.inf
            for j in range(row.shape[0]):
                p = row[j]
                if np.isnan(p):
                    continue
                if not (l[i] - tol <= p <= h[i] + tol):
                    continue
                if pos is not None and abs(p - pos["level"]) < gap:
                    continue
                d0 = abs(c[i - 1] - p)
                if d0 >= best:
                    continue
                # the side price arrived from decides the signal
                if c[i - 1] < p:
                    s = -1 if mode == "reverse" else 1      # tagged from below
                elif c[i - 1] > p:
                    s = 1 if mode == "reverse" else -1      # tagged from above
                else:
                    continue
                best, sig, hit_px = d0, s, p

        # ---- manage the open position --------------------------------
        if pos is not None:
            d = pos["dir"]
            if d > 0:
                pos["stop"] = max(pos["stop"], h[i - 1] - a * stop_atr)
                stopped = l[i] <= pos["stop"]
            else:
                pos["stop"] = min(pos["stop"], l[i - 1] + a * stop_atr)
                stopped = h[i] >= pos["stop"]
            # the protective stop is checked BEFORE the reversal: if a bar
            # both blows the stop and tags a level, the stop is assumed
            # first. Never flatters the result.
            if stopped:
                px = pos["stop"] - d * slippage
                pnl = d * (px - pos["entry"]) * pos["qty"] - 2 * commission * pos["qty"]
                eq += pnl
                trades.append({"pnl": pnl, "dir": d, "bar": pos["bar"],
                               "bars_held": i - pos["bar"], "exit": "stop"})
                pos = None
            elif sig != 0 and sig != d:
                px = c[i] - d * slippage
                pnl = d * (px - pos["entry"]) * pos["qty"] - 2 * commission * pos["qty"]
                eq += pnl
                trades.append({"pnl": pnl, "dir": d, "bar": pos["bar"],
                               "bars_held": i - pos["bar"], "exit": "level"})
                pos = None
            elif sig == d:
                sig = 0                       # already positioned that way

        if pos is not None or sig == 0 or i - last_bar < cooldown:
            continue

        # ---- regime filter (optional) --------------------------------
        if ema is not None and random_p == 0:
            if np.isnan(ema[i]):
                continue
            if sig > 0 and c[i] < ema[i]:
                continue
            if sig < 0:
                if c[i] > ema[i]:
                    continue
                if slope_dn is not None and not bool(slope_dn[i]):
                    continue

        d = sig
        stop_dist = a * stop_atr
        entry = c[i] + d * slippage
        eff_risk = risk_pct if d > 0 else risk_pct * short_risk
        qty = min(eq * eff_risk / 100.0 / stop_dist, eq * max_lev / c[i])
        qty = float(np.floor(max(qty, 0)))
        if qty < 1:
            continue
        pos = {"dir": d, "entry": entry, "stop": entry - d * stop_dist,
               "qty": qty, "bar": i, "level": hit_px}
        last_bar = i

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
