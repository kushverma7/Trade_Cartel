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
        use_ema_gate=0, qt_shorts_only=False,
        short_trail=0.0, short_risk=1.0, slope_len=0,
        kl=None, kl_take=0.0, kl_flip=False, kl_tol_atr=0.10,
        kl_shorts_only=False,
        kl_entry_atr=0.0, sma2_len=0, sma2_mode="gate", conf_min=0,
        conf_size=0.0, kl_min_atr=0.0, gap_fill=False,
        pyr_atr=0.0, pyr_max=0, pyr_risk=1.0):
    # PYRAMIDING (off by default). A trend system's return comes from a
    # handful of long moves, and a single fixed-size entry captures each
    # one only once. pyr_atr: add another unit every N ATR of favourable
    # movement; pyr_max: how many adds; pyr_risk: each add's size as a
    # fraction of the original risk. Entry price becomes the VWAP of the
    # stack and the shared trailing stop covers the whole thing.
    # kl_min_atr: the target level must be at least this many ATR beyond
    #   the entry. WITHOUT it the "next key level" is a joke of a target --
    #   on the 33 levels the chart actually draws, the median one sits
    #   0.46 ATR away while the stop is 6 ATR away. Banking 75% there
    #   risks 6 to make 0.46. That is what produced a live PF of 0.702 on
    #   a config the research had at 1.385.
    # CONFLUENCE (all off by default):
    #   kl_entry_atr  entry only when a drawn key level sits within this
    #                 many ATR of the entry price -- the breakout has to
    #                 happen AT a level, not in open space
    #   sma2_len      a second, longer SMA (2000 = ~3 weeks on 15m) used
    #                 as an additional directional gate
    #   sma2_mode     "gate"  both filters must agree (AND)
    #                 "score" neither is mandatory; see conf_min
    #   conf_min      in score mode, how many of {SMA750, SMA2000, level}
    #                 must agree before the trade is taken (0 = off)
    #   conf_size     extra risk multiplier per agreeing condition beyond
    #                 conf_min (0 = flat sizing)
    # kl: (n x k) array of SpacemanBTC key-level prices per bar, from
    # backtest.levels.build. Three uses, all default OFF so every result
    # already in the ledger reproduces unchanged:
    #   kl_take  bank this fraction at the first level reached in the
    #            trade's favour -- "key level to key level"
    #   kl_flip  a level tagged AGAINST the open position closes it and
    #            opens the opposite side on the same bar (the user's
    #            "reverse the signal as it touches the key level")
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
    sma2 = (pd.Series(c).rolling(sma2_len).mean().to_numpy() if sma2_len else None)
    emag = (pd.Series(c).ewm(span=use_ema_gate, adjust=False).mean().to_numpy()
            if use_ema_gate else None)
    # Slope of the long EMA. Price below a flat EMA happens constantly in an
    # uptrend's pullbacks; the EMA actually FALLING is a much rarer state and
    # is what a bear regime looks like. Gating shorts on slope rather than on
    # position keeps them almost silent in bull markets - which is the whole
    # point, since counter-trend shorts are what bleed away the long-only edge.
    slope_dn = None
    if slope_len and emag is not None:
        sh_ = np.full(len(c), np.nan)
        sh_[slope_len:] = emag[:-slope_len]
        slope_dn = emag < sh_

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

    KL = None if kl is None else np.asarray(kl, float)

    rng = np.random.default_rng(random_seed)
    eq = equity0
    trades = []
    pos = None
    # set when a key level flips the book; consumed by the entry section on
    # the FOLLOWING bar, because the flip exits inside the management block.
    # A one-bar delay on the re-entry is the conservative side of the trade.
    force_dir = 0
    for i in range(max(entry_n, atr_n) + 1, n):
        if pos is not None:
            d = pos["dir"]
            # ---- key level reached in the trade's direction --------------
            # The level that was nearest ahead of the entry. Reaching it is
            # either where profit is banked (kl_take) or where the book
            # turns around (kl_flip) -- the user's "reverse the signal as it
            # touches the key level".
            if KL is not None and (kl_take > 0 or kl_flip) \
                    and not np.isnan(pos.get("kl_target", np.nan)) \
                    and not pos.get("kl_done", False) \
                    and not (kl_shorts_only and d > 0):
                tgt = pos["kl_target"]
                ktol = atr[i] * kl_tol_atr
                reached = (h[i] >= tgt - ktol) if d > 0 else (l[i] <= tgt + ktol)
                if reached:
                    pos["kl_done"] = True
                    frac = 1.0 if kl_flip else kl_take
                    qty_out = pos["qty"] if frac >= 1.0 else np.floor(pos["qty"] * frac)
                    if qty_out >= 1:
                        px = (tgt - ktol if d > 0 else tgt + ktol) - d * slippage
                        pnl = d * (px - pos["entry"]) * qty_out - 2 * commission * qty_out
                        eq += pnl
                        pos["banked"] = pos.get("banked", 0.0) + pnl
                        pos["qty"] -= qty_out
                    if pos["qty"] < 1:
                        trades.append({"pnl": pos["banked"], "dir": d, "bar": pos["bar"],
                                       "bars_held": i - pos["bar"]})
                        pos = None
                        if kl_flip:
                            force_dir = -d
                        continue
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
            if quarter > 0 and q_take > 0 and not pos.get("q_done", False) \
                    and not (qt_shorts_only and d > 0):
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
            # ---- add to a winner -------------------------------------
            if pyr_atr > 0 and pyr_max > 0 and pos.get("adds", 0) < pyr_max:
                step = atr[i] * pyr_atr
                nxt = pos["last_add"] + d * step
                if (h[i] >= nxt) if d > 0 else (l[i] <= nxt):
                    add_stop = atr[i] * (trail_atr if d > 0 else (short_trail or trail_atr))
                    add_risk = (risk_pct if d > 0 else risk_pct * short_risk) * pyr_risk
                    add_qty = min(eq * add_risk / 100.0 / add_stop,
                                  eq * max_lev / c[i] - pos["qty"])
                    add_qty = float(np.floor(max(add_qty, 0)))
                    if add_qty >= 1:
                        px_add = nxt + d * slippage
                        newq = pos["qty"] + add_qty
                        pos["entry"] = (pos["entry"] * pos["qty"] + px_add * add_qty) / newq
                        pos["qty"] = newq
                        pos["banked"] = pos.get("banked", 0.0) - commission * add_qty
                        pos["adds"] = pos.get("adds", 0) + 1
                        pos["last_add"] = nxt
            tr_mult = trail_atr if d > 0 else (short_trail or trail_atr)
            if d > 0:
                pos["stop"] = max(pos["stop"], h[i - 1] - atr[i] * tr_mult)
                hit = l[i] <= pos["stop"]
            else:
                pos["stop"] = min(pos["stop"], l[i - 1] + atr[i] * tr_mult)
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
                # gap_fill: a bar can OPEN through the stop, and then the
                # fill is the open, not the stop. TradingView models this;
                # this engine did not, which is why its worst loss on the
                # 30m cross-check was 124.16 against TradingView's 240.77.
                # Off by default so every ledger row still reproduces.
                px = pos["stop"]
                if gap_fill:
                    px = min(px, o[i]) if d > 0 else max(px, o[i])
                px -= d * slippage
                pnl = d * (px - pos["entry"]) * pos["qty"] - 2 * commission * pos["qty"]
                eq += pnl
                trades.append({"pnl": pnl + pos.get("banked", 0.0), "dir": d,
                               "bar": pos["bar"], "bars_held": i - pos["bar"]})
                pos = None
        if pos is not None or np.isnan(atr[i]) or atr[i] <= 0:
            continue
        if force_dir != 0:
            # a key level turned the book around; that IS the signal
            long_sig = force_dir > 0
            short_sig = force_dir < 0 and not long_only
            if not (long_sig or short_sig):
                force_dir = 0
                continue
        elif random_p > 0:
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
            if slope_dn is not None:
                short_sig = short_sig and bool(slope_dn[i])
        if not (long_sig or short_sig):
            force_dir = 0        # a blocked flip is dropped, not queued
            continue
        d = 1 if long_sig else -1

        # ---- confluence layer ---------------------------------------
        # Each optional filter votes for or against the direction the
        # breakout already chose. In "gate" mode every one of them must
        # agree, which is exactly the old AND-of-filters behaviour and is
        # why every ledger row still reproduces. In "score" mode conf_min
        # of them have to agree, and conf_size pays extra size for each
        # one beyond that.
        conf = []
        if sma is not None and not sma_reverse and random_p == 0:
            if np.isnan(sma[i]):
                force_dir = 0
                continue
            conf.append(c[i] > sma[i] if d > 0 else c[i] < sma[i])
        if sma2 is not None and random_p == 0:
            if np.isnan(sma2[i]):
                force_dir = 0
                continue
            conf.append(c[i] > sma2[i] if d > 0 else c[i] < sma2[i])
        if kl_entry_atr > 0 and KL is not None and random_p == 0:
            krow = KL[i]
            krow = krow[~np.isnan(krow)]
            conf.append(bool(krow.size and
                             np.abs(krow - c[i]).min() <= atr[i] * kl_entry_atr))
        n_agree = int(sum(conf))
        need = conf_min if (sma2_mode == "score" and conf_min > 0) else len(conf)
        if conf and n_agree < need:
            force_dir = 0
            continue
        force_dir = 0
        # asymmetric management: the counter-trend side may run a tighter
        # trail and smaller size than the with-trend side
        eff_trail = trail_atr if d > 0 else (short_trail or trail_atr)
        eff_risk = risk_pct if d > 0 else risk_pct * short_risk
        if conf_size > 0 and conf:
            eff_risk *= 1.0 + conf_size * max(0, n_agree - need)
        stop_dist = atr[i] * eff_trail
        entry = c[i] + d * slippage
        qty = min(eq * eff_risk / 100.0 / stop_dist, eq * max_lev / c[i])
        qty = float(np.floor(max(qty, 0)))
        if qty < 1:
            continue
        qt = 0.0
        if quarter > 0:
            qt = (np.floor(entry / quarter) + 1) * quarter if d > 0 \
                 else (np.ceil(entry / quarter) - 1) * quarter
        # nearest key level strictly ahead of the entry, in the trade's
        # direction. NaN when the row has none -- then the trade simply
        # runs on the trail, which is the pre-key-level behaviour.
        klt = np.nan
        if KL is not None:
            row = KL[i]
            floor_ = atr[i] * kl_min_atr
            fwd = (row[row > entry + floor_] if d > 0
                   else row[row < entry - floor_])
            fwd = fwd[~np.isnan(fwd)]
            if fwd.size:
                klt = fwd.min() if d > 0 else fwd.max()
        pos = {"dir": d, "entry": entry, "stop": entry - d * stop_dist,
               "qty": qty, "bar": i, "q_target": qt, "q_done": False,
               "qt_done": False, "banked": 0.0,
               "kl_target": klt, "kl_done": False,
               "adds": 0, "last_add": entry}
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
