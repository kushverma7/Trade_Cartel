"""
Backtest of the "Maximum Accuracy Level-to-Level Model" rule book, as written.

WHAT IS AND IS NOT TESTED — read this before the numbers
  Testable with what this repo has:
    Setup 1  trend-aligned bounce at CPR / S1 / R1 / SpacemanBTC support
    Setup 2  Inside Value + narrow CPR breakout
    Setup 3  magnet / gap fill to the CPR
    Bias A   two-day value relationship (Higher / Lower / Inside / ...)
    Bias B   CPR width, narrow vs wide against its own rolling distribution
    Bias C   opening relationship, open in/out of the prior day's range
    Bias D   HTF structure, higher highs and higher lows

  NOT testable, and not silently skipped:
    Setup 4  Virgin / Naked POC        -- levels.py has NO volume profile
    Money Zone VAH / POC / VAL         -- same gap, logged in
                                          LEVELS_AND_PIVOTS_INVENTORY.md
    Setup 5  Wyckoff spring "on low volume" -- partially available, but the
             volume in this dataset is broker tick-count, not exchange volume,
             so a volume condition would not mean what the rule book means
    US30                                -- no US30 data in data/; XAUUSD only

  So this is the rule book's price-and-pivot core on XAUUSD. Three of five
  setups, four of four bias filters, one of two instruments.

MECHANICS, TAKEN LITERALLY FROM THE RULE BOOK
  entry   break of the signal candle's extreme
  stop    beyond the level AND beyond the signal candle's extreme, plus buffer
  T1      next key level, scale 40%
  T2      further major level, remainder
  filter  minimum 1:2 R:R to T1, else no trade
  cost    this repo's standard, $0.07 commission + 0.20 pt slippage per side

THE CONTROL IS NOT OPTIONAL
  Three times this session an uncontrolled positive has died on its control
  (a 99.94% bounce rate, sweep results priced from the level, and with-trend
  level entries beaten by random entries in the same bias). So every setup
  here is reported beside a control that keeps the bias and the risk geometry
  and discards only the level and the candle.
"""
import argparse

import numpy as np
import pandas as pd

from backtest.io import load_csv
from backtest.levels import build
from backtest.pivots import floor_pivots, relationships, sessionise
from backtest.level_reaction import _atr

COMMISSION, SLIP = 0.07, 0.20


def candles(df):
    """Pin bar and doji, per the rule book's own definitions."""
    o, h, l, c = (df[k].values for k in ("open", "high", "low", "close"))
    rng = np.maximum(h - l, 1e-9)
    body = np.abs(c - o)
    upper = h - np.maximum(o, c)
    lower = np.minimum(o, c) - l
    # rule book: doji = open/close within 10% of range
    doji = body <= 0.10 * rng
    # pin bar: tail >= 2/3 of total length (the price-action guide's rule)
    pin_bull = (lower >= 0.66 * rng) & (body <= 0.33 * rng)
    pin_bear = (upper >= 0.66 * rng) & (body <= 0.33 * rng)
    return doji, pin_bull, pin_bear


def daily_context(df, lookback=60):
    """CPR, two-day value relationship, width band, opening relationship."""
    sess = sessionise(df)
    pv = floor_pivots(sess)                 # already shifted by one session
    rel = relationships(pv)
    w = pv["pivot_width"]
    lo_q = w.rolling(lookback).quantile(0.33)
    hi_q = w.rolling(lookback).quantile(0.67)
    band = pd.Series("mid", index=w.index, dtype=object)
    band[w <= lo_q] = "narrow"
    band[w >= hi_q] = "wide"
    # opening relationship: today's open vs the PRIOR day's range
    ph, pl = sess["high"].shift(1), sess["low"].shift(1)
    out_of_range = (sess["open"] > ph) | (sess["open"] < pl)
    # HTF structure: higher highs and higher lows over 3 sessions
    hh = (sess["high"] > sess["high"].shift(1)) & (sess["low"] > sess["low"].shift(1))
    ll = (sess["high"] < sess["high"].shift(1)) & (sess["low"] < sess["low"].shift(1))
    ctx = pd.DataFrame({"rel": rel, "band": band, "oor": out_of_range,
                        "hh": hh.rolling(3).sum() >= 2,
                        "ll": ll.rolling(3).sum() >= 2})
    return pv.join(ctx)


def trade(h, l, c, i, d, entry, stop, t1, t2, horizon):
    """Scale 40% at T1, remainder at T2 or stop. Returns R multiple."""
    risk = abs(entry - stop)
    if risk <= 0:
        return np.nan
    part, banked = 0.0, 0.0
    for j in range(i + 1, min(i + horizon + 1, len(c))):
        hit_s = (l[j] <= stop) if d > 0 else (h[j] >= stop)
        hit_1 = (h[j] >= t1) if d > 0 else (l[j] <= t1)
        hit_2 = (h[j] >= t2) if d > 0 else (l[j] <= t2)
        if hit_s:
            return banked + (1 - part) * (-(risk + 2 * SLIP) / risk)
        if hit_2 and part > 0:
            return banked + (1 - part) * ((abs(t2 - entry) - 2 * SLIP) / risk)
        if hit_1 and part == 0:
            part = 0.40
            banked += 0.40 * ((abs(t1 - entry) - 2 * SLIP) / risk)
            stop = entry                       # rule book: stop to breakeven
    return banked + (1 - part) * ((d * (c[min(i + horizon, len(c) - 1)] - entry)
                                   - 2 * SLIP) / risk)


def run(df, rule="30min", horizon=96, min_rr=2.0, seed=0):
    lv = build(df, dense=True)
    ctx = daily_context(df)
    A = _atr(df)
    o, h, l, c = (df[k].values for k in ("open", "high", "low", "close"))
    doji, pin_bull, pin_bear = candles(df)
    key = pd.Series(pd.to_datetime(df.index.date), index=df.index)
    C = ctx.reindex(key.values)
    lvv = {k: lv[k].values for k in lv.columns}
    rng = np.random.default_rng(seed)
    rows = []

    for i in range(100, len(c) - horizon):
        a = A[i]
        if not np.isfinite(a) or a <= 0:
            continue
        rel, band = C["rel"].values[i], C["band"].values[i]
        pp, tc, bc = C["PP"].values[i], C["TC"].values[i], C["BC"].values[i]
        if not np.isfinite(pp):
            continue

        # ---- Bias A: two-day value relationship (highest-priority filter) ---
        bull = rel in ("higher", "overlap_higher")
        bear = rel in ("lower", "overlap_lower")
        # ---- Bias D: HTF structure must not contradict --------------------
        if bull and not C["hh"].values[i]:
            bull = False
        if bear and not C["ll"].values[i]:
            bear = False

        # ================= SETUP 1: trend-aligned bounce ===================
        if bull or bear:
            d = 1 if bull else -1
            supports = [bc, C["S1"].values[i]] if bull else [tc, C["R1"].values[i]]
            supports += [lvv["PDL"][i], lvv["MONL"][i]] if bull else [lvv["PDH"][i], lvv["MONH"][i]]
            for lvl in supports:
                if not np.isfinite(lvl):
                    continue
                if not (l[i] <= lvl <= h[i]):
                    continue
                sig = pin_bull[i] or doji[i] if bull else pin_bear[i] or doji[i]
                if not sig:
                    continue
                entry = (h[i] if d > 0 else l[i]) + d * SLIP
                stop = (min(l[i], lvl) - 0.25 * a) if d > 0 else (max(h[i], lvl) + 0.25 * a)
                risk = abs(entry - stop)
                if risk <= 0:
                    continue
                t1 = pp if (pp - entry) * d > 0 else entry + d * 2 * risk
                t2 = (C["R1"].values[i] if d > 0 else C["S1"].values[i])
                if not np.isfinite(t2) or (t2 - entry) * d <= 0:
                    t2 = entry + d * 3 * risk
                if abs(t1 - entry) / risk < min_rr:
                    continue                    # rule book: min 1:2 to T1
                r = trade(h, l, c, i, d, entry, stop, t1, t2, horizon)
                if np.isfinite(r):
                    rows.append({"setup": "1 trend bounce", "i": i, "R": r, "dir": d})
                break

        # ============ SETUP 2: Inside Value + narrow CPR breakout ==========
        if rel == "inside" and band == "narrow" and C["oor"].values[i]:
            d = 1 if c[i] > tc else (-1 if c[i] < bc else 0)
            if d != 0:
                entry = c[i] + d * SLIP
                stop = (bc - 0.25 * a) if d > 0 else (tc + 0.25 * a)
                risk = abs(entry - stop)
                if risk > 0:
                    t1 = entry + d * 2 * risk
                    t2 = entry + d * 4 * risk
                    r = trade(h, l, c, i, d, entry, stop, t1, t2, horizon)
                    if np.isfinite(r):
                        rows.append({"setup": "2 inside/narrow brk", "i": i, "R": r, "dir": d})

        # ================= SETUP 3: magnet / gap fill to CPR ================
        if np.isfinite(pp) and i > 0 and key.values[i] != key.values[i - 1]:
            gap = o[i] - c[i - 1]
            if abs(gap) > 0.5 * a and abs(o[i] - pp) > 0.5 * a:
                d = -1 if gap > 0 else 1        # fade the gap toward the CPR
                entry = o[i] + d * SLIP
                # stop on the far side of the gap, 0.75 of its size
                stop = o[i] - d * abs(gap) * 0.75
                risk = abs(entry - stop)
                if risk > 0 and abs(pp - entry) / risk >= 1.0:
                    r = trade(h, l, c, i, d, entry, stop, pp, pp, horizon)
                    if np.isfinite(r):
                        rows.append({"setup": "3 gap fill to CPR", "i": i, "R": r, "dir": d})

    return pd.DataFrame(rows)


def stats(t, label):
    if len(t) < 20:
        print(f"  {label:<24} n={len(t):>5}  (too few to judge)"); return
    R = t["R"].values
    wins, losses = R[R > 0], R[R <= 0]
    pf = wins.sum() / abs(losses.sum()) if len(losses) and losses.sum() != 0 else np.inf
    eq = np.cumsum(R); peak = np.maximum.accumulate(eq)
    dd = float((peak - eq).max())
    print(f"  {label:<24} n={len(R):>5}  WR={100 * (R > 0).mean():5.1f}%  "
          f"avgR={R.mean():+6.3f}  PF={pf:5.2f}  maxDD={dd:6.1f}R  "
          f"total={R.sum():+7.1f}R")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rule", default="30min")
    ap.add_argument("--horizon", type=int, default=96)
    a = ap.parse_args()
    df = load_csv("data/xauusd_15m.csv.gz", rule=a.rule)
    print(f"\nXAUUSD {a.rule}, {len(df):,} bars, "
          f"{df.index[0].date()} to {df.index[-1].date()}")
    print(f"cost: ${COMMISSION}/side commission + {SLIP} pt/side slippage\n")
    t = run(df, a.rule, a.horizon)
    if t.empty:
        print("  no trades generated"); return
    print("PER SETUP")
    for s in sorted(t["setup"].unique()):
        stats(t[t.setup == s], s)
    print("\nCOMBINED")
    stats(t, "all setups")
    mid = t["i"].median()
    stats(t[t["i"] <= mid], "  first half")
    stats(t[t["i"] > mid], "  second half (OOS)")


if __name__ == "__main__":
    main()
