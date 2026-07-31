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
        sma_reverse=False, quarter=0.0, q_tol=0.0, q_take=0.0,
        q_trail=False, qt_take=0.0, qt_exit=False, qt_weekly=False,
        use_ema_gate=0, qt_shorts_only=False):
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
    emag = (pd.Series(c).ewm(span=use_ema_gate, adjust=False).mean().to_numpy()
            if use_ema_gate else None)

    # ---- Daye Quarterly Theory: TIME quarters -----------------------------
    # Daily quarters in ET: Q1 Asia 18-00, Q2 London 00-06, Q3 NY AM 06-12,
    # Q4 NY PM 12-18. The source names the behaviour of each:
    #   Q1 range/liquidity build, Q2 expansion, Q3 continuation/pullback,
    #   Q4 REVERSAL / PROFIT-TAKING.
    # Q4 is therefore where the theory says to bank, and that is what is
    # implemented here. Data is UTC; ET is UTC-5, so Q4 12-18 ET is 17-23 UTC.
    # Weekly quarters: Mon=Q1, Tue=Q2, Wed=Q3, Thu=Q4 (Friday excluded).
    hod = df.index.hour.to_numpy()
    dow = df.index.dayofweek.to_numpy()
    in_q4 = ((hod >= 17) & (hod < 23)) if not qt_weekly else (dow == 3)
    q4_start = np.zeros(len(c), bool)
    q4_start[1:] = in_q4[1:] & ~in_q4[:-1]

    # ---- Yotov quarter-point profit taking -------------------------------
    # Yotov's structure on gold: major handles every 1000 (3000/4000/5000),
    # LARGE QUARTER POINTS every 250, small quarters every 25. His core
    # thesis is that a move runs from one large quarter point to the next,
    # and his "successful completion" rule is explicit: reaching within one
    # small quarter of the target counts as completed, whether short of it
    # or overshooting.
    #
    # So the target is the next large quarter point in the trade's
    # direction, and it is treated as hit once price comes within q_tol of
    # it. q_take is scaled off there; the remainder keeps running on the
    # trail, which is what lets a long move continue past a quarter.

    rng = np.random.default_rng(random_seed)
    eq = equity0
    trades = []
    pos = None
    for i in range(max(entry_n, atr_n) + 1, n):
        if pos is not None:
            d = pos["dir"]
            # Daye Q4: the theory's designated profit-taking window
            # qt_shorts_only: bank the counter-trend side, let the with-trend
            # side run. Every symmetric take tested so far removed exactly the
            # size that captures the large move.
            if (qt_take > 0 or qt_exit) and q4_start[i] and not pos.get("qt_done", False) \
                    and not (qt_shorts_only and d > 0):
                frac = 1.0 if qt_exit else qt_take
                qty_out = np.floor(pos["qty"] * frac) if frac < 1.0 else pos["qty"]
                if qty_out >= 1:
                    px = c[i] - d * slippage
                    pnl = d * (px - pos["entry"]) * qty_out - 2 * commission * qty_out
                    eq += pnl
                    pos["banked"] = pos.get("banked", 0.0) + pnl
                    pos["qty"] -= qty_out
                pos["qt_done"] = True
                if pos["qty"] < 1:
                    trades.append({"pnl": pos["banked"], "dir": d, "bar": pos["bar"],
                                   "bars_held": i - pos["bar"]})
                    pos = None
                    continue

            # partial take at the next large quarter point (once per trade)
            if quarter > 0 and q_take > 0 and not pos.get("q_done", False):
                tgt = pos["q_target"]
                reached = (h[i] >= tgt - q_tol) if d > 0 else (l[i] <= tgt + q_tol)
                if reached:
                    qty_out = np.floor(pos["qty"] * q_take)
                    if qty_out >= 1:
                        px = (tgt - q_tol if d > 0 else tgt + q_tol) - d * slippage
                        pnl = d * (px - pos["entry"]) * qty_out - 2 * commission * qty_out
                        eq += pnl
                        pos["banked"] = pos.get("banked", 0.0) + pnl
                        pos["qty"] -= qty_out
                    pos["q_done"] = True
                    if pos["qty"] < 1:
                        trades.append({"pnl": pos["banked"], "dir": d,
                                       "bar": pos["bar"], "bars_held": i - pos["bar"]})
                        pos = None
                        continue
            # trail: ratchet the stop in the trade's favour, never against
            # Quarter theory used as a STOP anchor rather than a target.
            # Yotov's thesis is that a completed large quarter rarely gives
            # back the whole quarter, so once one completes, the preceding
            # quarter point becomes a structural floor. This keeps the
            # let-it-run property that a take-profit destroys.
            if q_trail and quarter > 0:
                if d > 0:
                    done = np.floor((h[i - 1] + q_tol) / quarter) * quarter
                    if done > pos["entry"]:
                        pos["stop"] = max(pos["stop"], done - quarter)
                else:
                    done = np.ceil((l[i - 1] - q_tol) / quarter) * quarter
                    if done < pos["entry"]:
                        pos["stop"] = min(pos["stop"], done + quarter)
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
                    trades.append({"pnl": pnl + pos.get("banked", 0.0), "dir": d,
                                   "bar": pos["bar"], "bars_held": i - pos["bar"]})
                    pos = None
                    continue
            if hit:
                px = pos["stop"] - d * slippage
                pnl = d * (px - pos["entry"]) * pos["qty"] - 2 * commission * pos["qty"]
                eq += pnl
                trades.append({"pnl": pnl + pos.get("banked", 0.0), "dir": d,
                               "bar": pos["bar"], "bars_held": i - pos["bar"]})
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
        if emag is not None and random_p == 0:
            if np.isnan(emag[i]):
                continue
            long_sig = long_sig and c[i] > emag[i]
            short_sig = short_sig and c[i] < emag[i]
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
        qt = 0.0
        if quarter > 0:
            qt = (np.floor(entry / quarter) + 1) * quarter if d > 0 \
                 else (np.ceil(entry / quarter) - 1) * quarter
        pos = {"dir": d, "entry": entry, "stop": entry - d * stop_dist,
               "qty": qty, "bar": i, "q_target": qt, "q_done": False,
               "qt_done": False, "banked": 0.0}
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
