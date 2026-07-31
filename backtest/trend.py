"""
Trend-following engine — the family this project never tried.

Everything built here for four months was mean-reversion or scalping:
sweep-and-reclaim, break-and-retest, fixed 1R/2R targets, a 36-bar time
stop. On XAUUSD over 2019-2026 that architecture returned PF 0.86 while
the asset itself rose 179%. Longs alone reached only PF 0.912 -- losing
money on the long side of a market that nearly tripled.

That is not a bad entry rule. It is an exit structure that cannot hold a
position long enough to capture a trend. A fixed 2R target caps every
winner at twice the stop while losers run to the stop, in a market whose
entire return came from a handful of multi-month moves.

This engine inverts the design:
  entry   N-bar breakout (Donchian), the oldest trend rule there is
  exit    ATR trailing stop ONLY -- no profit target, no time stop
  hold    unlimited; winners are allowed to run
Costs, slippage and notional caps are identical to engine.py, so results
are directly comparable to everything already in the ledger.
"""
import numpy as np
import pandas as pd


def run(df, entry_n=100, trail_atr=3.0, atr_n=14, long_only=False,
        random_p=0.0, random_seed=0,
        risk_pct=1.0, equity0=10000.0, commission=0.07, slippage=0.05,
        max_lev=20, regime_ema=0, sma_len=0, exit_on_cross=False,
        sma_reverse=False):
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    n = len(c)
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    atr = pd.Series(tr).ewm(alpha=1 / atr_n, adjust=False).mean().to_numpy()
    hi = pd.Series(h).rolling(entry_n).max().shift(1).to_numpy()
    lo = pd.Series(l).rolling(entry_n).min().shift(1).to_numpy()
    ema = (pd.Series(c).ewm(span=regime_ema, adjust=False).mean().to_numpy()
           if regime_ema else None)
    # long-horizon SMA. On 15m bars a 2000 period is ~3 weeks of price, so
    # it defines the prevailing trend rather than a swing. Used three ways:
    #   gate    -- only take longs above it, shorts below
    #   exit    -- close when price crosses back through it
    #   reverse -- the cross IS the signal; always in the market
    sma = (pd.Series(c).rolling(sma_len).mean().to_numpy() if sma_len else None)

    rng = np.random.default_rng(random_seed)
    eq = equity0
    trades = []
    pos = None
    for i in range(max(entry_n, atr_n) + 1, n):
        if pos is not None:
            d = pos["dir"]
            # trail: ratchet the stop in the trade's favour, never against
            if d > 0:
                pos["stop"] = max(pos["stop"], h[i - 1] - atr[i] * trail_atr)
                hit = l[i] <= pos["stop"]
            else:
                pos["stop"] = min(pos["stop"], l[i - 1] + atr[i] * trail_atr)
                hit = h[i] >= pos["stop"]
            # exit on a close back through the SMA, before the trail check
            if not hit and exit_on_cross and sma is not None and not np.isnan(sma[i]):
                if (d > 0 and c[i] < sma[i]) or (d < 0 and c[i] > sma[i]):
                    px = c[i] - d * slippage
                    pnl = d * (px - pos["entry"]) * pos["qty"] - 2 * commission * pos["qty"]
                    eq += pnl
                    trades.append({"pnl": pnl, "dir": d, "bar": pos["bar"],
                                   "bars_held": i - pos["bar"]})
                    pos = None
                    continue
            if hit:
                px = pos["stop"] - d * slippage
                pnl = d * (px - pos["entry"]) * pos["qty"] - 2 * commission * pos["qty"]
                eq += pnl
                trades.append({"pnl": pnl, "dir": d, "bar": pos["bar"],
                               "bars_held": i - pos["bar"]})
                pos = None
        if pos is not None or np.isnan(atr[i]) or atr[i] <= 0:
            continue
        if random_p > 0:
            # coin-flip entry at a matched rate, IDENTICAL trailing exit,
            # sizing and costs. The null for a trend system must inherit the
            # exit, because the exit is where trend systems make their money.
            if rng.random() >= random_p:
                continue
            long_sig = True
            short_sig = False if long_only else (rng.random() < 0.5)
            if short_sig:
                long_sig = False
        elif sma_reverse and sma is not None:
            if np.isnan(sma[i]) or np.isnan(sma[i - 1]):
                continue
            long_sig = c[i] > sma[i] and c[i - 1] <= sma[i - 1]
            short_sig = (not long_only) and c[i] < sma[i] and c[i - 1] >= sma[i - 1]
        else:
            long_sig = c[i] > hi[i]
            short_sig = (not long_only) and c[i] < lo[i]
        if ema is not None and random_p == 0:
            long_sig = long_sig and c[i] > ema[i]
            short_sig = short_sig and c[i] < ema[i]
        if sma is not None and not sma_reverse and random_p == 0:
            if np.isnan(sma[i]):
                continue
            long_sig = long_sig and c[i] > sma[i]
            short_sig = short_sig and c[i] < sma[i]
        if not (long_sig or short_sig):
            continue
        d = 1 if long_sig else -1
        stop_dist = atr[i] * trail_atr
        entry = c[i] + d * slippage
        qty = min(eq * risk_pct / 100.0 / stop_dist, eq * max_lev / c[i])
        qty = float(np.floor(max(qty, 0)))
        if qty < 1:
            continue
        pos = {"dir": d, "entry": entry, "stop": entry - d * stop_dist,
               "qty": qty, "bar": i}
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
