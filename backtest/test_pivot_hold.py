"""
THE ONE STRATEGY WORTH TESTING FROM EVERYTHING IN THIS ARCHIVE.

HYPOTHESIS (H-PIVOT-HOLD)
  On sessions preceded by a NARROW London/NY-overlap pivot range, hold the
  champion's trailing stop WIDER. Change nothing else.

WHY THIS AND NOT SOMETHING ELSE
  Three independent measurements in this repo converge on it:

  1. BELIEF_REGISTER "the edge is an exponent gap": MAE diffuses at 0.493
     against a random walk's 0.500 -- entry geometry is a coin flip. MFE
     diffuses at 0.558. The +0.065 gap accrues to HOLD TIME, not to the entry.
     So any real improvement must act on the exit, and specifically on how
     long the trade is allowed to live.

  2. BELIEF_REGISTER "pivot-range WIDTH forecasts next-session directionality":
     narrow prior pivot range precedes a more directional session. t=+3.07 on
     the LDN/NY overlap, stable across 30 parameter combinations (t 2.20-3.80),
     replicates out of sample (+2.00 / +2.06 on halves). It is a REGIME
     forecaster, which is the only level-derived quantity that has ever
     survived a test here.

  3. LEVELS_AND_PIVOTS_INVENTORY: levels are dead as targets (BUG-017 measured
     target/stop 0.077 -> live PF 0.702; BUG-027 measured 0.065) and
     near-worthless as entries. Extending holds is the one use consistent with
     every measurement made.

  Put together: use the pivot-width regime to decide WHEN TO HOLD LONGER.

WHAT THIS DELIBERATELY DOES NOT DO
  - does not change the entry (the entry is a coin flip; changing it is noise)
  - does not add a target (measured twice as destructive)
  - does not add a filter that removes trades (filters raise PF and lower
    return -- measured here and independently in the AU200 archive)

  It only widens the leash on sessions the pivot width says will run.

FALSIFICATION
  If widening the trail on narrow-pivot sessions does not beat the unmodified
  champion on return AND drawdown, on the same window and costs, the
  hypothesis is dead and the pivot finding stays a curiosity rather than an
  edge. Both halves are reported so the answer cannot be cherry-picked.
"""
import numpy as np
import pandas as pd

from backtest.io import load_csv
from backtest import exit_lab
from backtest.pivots import floor_pivots

# champion settings, read off strategies/gold_trend_strategy.pine
ENTRY_N = 50          # "Breakout lookback (bars)"
TRAIL_ATR_15M = 6.0   # "Trailing stop (x ATR, 15m basis)"
STOP_ATR = 6.0
ATR_N = 14
RISK = 1.0
SHORT_RISK = 0.75
COOLDOWN = 3
PYR_ATR, PYR_MAX = 1.5, 4   # Balanced profile
COMMISSION, SLIPPAGE = 0.07, 0.20   # repo standard, BUG-021 corrected


def build(rule="30min"):
    df = load_csv("data/xauusd_15m.csv.gz", rule=rule)
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    hi = pd.Series(h).rolling(ENTRY_N).max().shift(1).values
    lo = pd.Series(l).rolling(ENTRY_N).min().shift(1).values
    sigL = c > hi
    sigS = c < lo
    return df, sigL, sigS


def pivot_regime(df, lookback=60, narrow_q=0.25):
    """Per-bar boolean: is the CURRENT session's prior pivot width narrow?

    Built from the LDN/NY overlap session only, shifted by a session inside
    floor_pivots(), so no value is ever available before the session that
    produced it has closed.
    """
    t = df.index
    hh = t.hour + t.minute / 60.0
    ov = df[(hh >= 13.5) & (hh < 16.5)].copy()
    ov["date"] = ov.index.date
    g = ov.groupby("date")
    sess = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(),
                         "low": g["low"].min(), "close": g["close"].last()})
    sess.index = pd.to_datetime(sess.index)
    sess = sess[sess.index.dayofweek < 5]
    w = floor_pivots(sess)["pivot_width"]
    thr = w.rolling(lookback).quantile(narrow_q)
    narrow = (w <= thr)
    # map session flag onto every intraday bar of the FOLLOWING session
    m = pd.Series(narrow.values, index=narrow.index)
    key = pd.Series(pd.to_datetime(df.index.date), index=df.index)
    return key.map(m).fillna(False).values.astype(bool)


def run_one(df, sigL, sigS, trail_series=None, trail=TRAIL_ATR_15M):
    return exit_lab.run(
        df, sigL, sigS, stop_atr=STOP_ATR, trail_mode="chandelier",
        trail_atr=trail, trail_atr_series=trail_series,
        pyr_atr=PYR_ATR, pyr_max=PYR_MAX,
        risk_pct=RISK, short_risk=SHORT_RISK, cooldown=COOLDOWN,
        atr_n=ATR_N, commission=COMMISSION, slippage=SLIPPAGE)


def report(name, tr):
    s = exit_lab.stats(tr)
    print(f"  {name:<34} n={s['n']:>5}  PF={s['pf']:>5.3f}  "
          f"net={s['net_pct']:>+9.1f}%  DD={s['maxdd_pct']:>5.2f}%  "
          f"ret/DD={s['rdd']:>5.2f}")
    return s


def main():
    rule = "30min"
    df, sigL, sigS = build(rule)
    # trail scales with sqrt(timeframe), as the champion's auto-scale does
    trail = TRAIL_ATR_15M * np.sqrt(30.0 / 15.0)
    narrow = pivot_regime(df)
    print(f"{len(df):,} bars on {rule}   trail = {trail:.2f} ATR")
    print(f"narrow-pivot bars: {narrow.mean() * 100:.1f}%\n")

    halves = [("FULL", slice(None)),
              ("first half", slice(0, len(df) // 2)),
              ("second half (OOS)", slice(len(df) // 2, None))]

    for label, sl in halves:
        d = df.iloc[sl]
        L, S, nw = sigL[sl], sigS[sl], narrow[sl]
        print(f"--- {label} ---")
        base = run_one(d, L, S, trail=trail)
        b = report("champion (fixed trail)", base)
        for mult in (1.25, 1.5, 2.0):
            ts = np.where(nw, trail * mult, trail)
            t = run_one(d, L, S, trail_series=ts, trail=trail)
            a = report(f"widen x{mult} on narrow pivot", t)
            print(f"      delta vs champion: net {a['net_pct'] - b['net_pct']:+.1f}pp"
                  f"   DD {a['maxdd_pct'] - b['maxdd_pct']:+.2f}pp"
                  f"   PF {a['pf'] - b['pf']:+.3f}")
        print()


if __name__ == "__main__":
    main()
