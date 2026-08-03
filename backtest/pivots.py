"""
Floor pivots, the Ochoa pivot RANGE, Camarilla — and a test of the one claim
in the source material that is actually falsifiable.

SOURCE
  Frank Ochoa (PivotBoss), "Profiting with Pivot-Based Concepts", 2011,
  archived at trader_playbooks/sources/ochoa_profiting_with_pivot_based_concepts.pdf

  Read it for what it is: a 48-slide webinar deck that ends on a $69.96 book
  offer and three testimonials. It contains no win rate, no sample size, no
  backtest, and every claim is illustrated with a hand-annotated chart marked
  "Buy Here" / "Sell Here". This repo already has a name for that
  (BELIEF_REGISTER, voice #11 FX Master Pattern: "hindsight-annotated
  screenshots, no forward-testable rules").

  But two of its mechanisms ARE mechanical, and one of them is the exact thing
  this repo is missing, so they get measured rather than dismissed.

WHY THIS FILE EXISTS AT ALL
  As of 2026-08-02 this repo had no floor pivots anywhere — verified by
  searching every .pine and .py for (H+L+C)/3. See
  trader_playbooks/LEVELS_AND_PIVOTS_INVENTORY.md.

  It also has two measurements saying price GRIDS do not work as targets:
  BUG-017 (level targets, median target/stop 0.077, live PF 0.702) and
  BUG-027 (quarter grid, 0.065). So floor pivots are NOT built here as
  targets. R1/R2/S1/S2 are provided for completeness and should be treated as
  failing the BUG-017 gate until someone shows otherwise.

  What is built here for USE is the PIVOT RANGE WIDTH, because it is a regime
  forecaster rather than a price target, and regime is the one level-derived
  quantity consistent with this repo's exponent-gap finding (BELIEF_REGISTER:
  MAE diffuses at 0.493, the edge is +0.065 and accrues to HOLD TIME).

THE OCHOA PIVOT RANGE
    PP = (H + L + C) / 3          the classic floor pivot
    BC = (H + L) / 2              bottom central
    TC = 2*PP - BC                top central
  The RANGE is [min(TC,BC), max(TC,BC)]; its WIDTH is the signal.

THE FALSIFIABLE CLAIM (deck, "Forecasting with Pivot Width")
    "An unusually WIDE pivot range can forecast sideways trading."
    "An unusually NARROW pivot range can forecast trending and breakout
     markets."

  That is testable in one pass and `claim_test()` below does it: classify each
  session's pivot width against its own trailing distribution, then measure
  what the NEXT session actually did. No charts, no annotation.
"""
import argparse

import numpy as np
import pandas as pd


def floor_pivots(daily: pd.DataFrame) -> pd.DataFrame:
    """Classic floor pivots + Ochoa pivot range, from the PRIOR session.

    `daily` needs open/high/low/close indexed by session date. Everything is
    shifted by one session, so a value is only ever available on the day AFTER
    the session that produced it -- no lookahead by construction.
    """
    h, l, c = daily["high"], daily["low"], daily["close"]
    pp = (h + l + c) / 3.0
    bc = (h + l) / 2.0
    tc = 2.0 * pp - bc
    out = pd.DataFrame(index=daily.index)
    out["PP"] = pp
    out["TC"] = np.maximum(tc, bc)   # the deck draws TC as the upper edge
    out["BC"] = np.minimum(tc, bc)
    out["R1"] = 2 * pp - l
    out["S1"] = 2 * pp - h
    out["R2"] = pp + (h - l)
    out["S2"] = pp - (h - l)
    out["R3"] = h + 2 * (pp - l)
    out["S3"] = l - 2 * (h - pp)
    # Camarilla — the deck's third indicator
    rng = h - l
    out["H3"] = c + rng * 1.1 / 4.0
    out["H4"] = c + rng * 1.1 / 2.0
    out["L3"] = c - rng * 1.1 / 4.0
    out["L4"] = c - rng * 1.1 / 2.0
    out["pivot_width"] = out["TC"] - out["BC"]
    out["prior_range"] = rng
    return out.shift(1)              # available only on the following session


def relationships(pv: pd.DataFrame) -> pd.Series:
    """The deck's two-day pivot range relationships, as a categorical state."""
    tc, bc = pv["TC"], pv["BC"]
    ptc, pbc = tc.shift(1), bc.shift(1)
    s = pd.Series("unchanged", index=pv.index, dtype=object)
    s[(bc > ptc)] = "higher"                       # completely above
    s[(tc < pbc)] = "lower"                        # completely below
    s[(tc <= ptc) & (bc >= pbc)] = "inside"        # completely within
    s[(tc >= ptc) & (bc <= pbc)] = "outside"
    s[(bc > pbc) & (bc <= ptc) & (tc > ptc)] = "overlap_higher"
    s[(tc < ptc) & (tc >= pbc) & (bc < pbc)] = "overlap_lower"
    return s


def sessionise(df: pd.DataFrame) -> pd.DataFrame:
    """Intraday bars -> one row per session."""
    d = df.copy()
    d["date"] = d.index.date
    g = d.groupby("date")
    out = pd.DataFrame({
        "open": g["open"].first(), "high": g["high"].max(),
        "low": g["low"].min(), "close": g["close"].last(),
    })
    out.index = pd.to_datetime(out.index)
    return out


def claim_test(daily: pd.DataFrame, lookback: int = 60, narrow_q: float = 0.25,
               wide_q: float = 0.75) -> pd.DataFrame:
    """Test the deck's forecasting claim on real sessions.

    Regime of the FOLLOWING session is measured two ways, both standard:
      efficiency  |close-open| / (high-low)  -- 1.0 = pure trend, 0 = pure chop
      range_ratio (high-low) / trailing mean range -- did it expand?
    """
    pv = floor_pivots(daily)
    w = pv["pivot_width"]
    # classify width against its OWN trailing distribution, not a fixed number
    lo = w.rolling(lookback).quantile(narrow_q)
    hi = w.rolling(lookback).quantile(wide_q)
    band = pd.Series("mid", index=w.index, dtype=object)
    band[w <= lo] = "narrow"
    band[w >= hi] = "wide"

    rng = daily["high"] - daily["low"]
    eff = (daily["close"] - daily["open"]).abs() / rng.replace(0, np.nan)
    rr = rng / rng.rolling(lookback).mean()

    out = pd.DataFrame({"band": band, "efficiency": eff, "range_ratio": rr}).dropna()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", default="data/xauusd_15m.csv.gz")
    ap.add_argument("--lookback", type=int, default=60)
    a = ap.parse_args()

    from backtest.io import load_csv
    df = load_csv(a.csv)
    daily = sessionise(df)
    print(f"{len(df):,} bars -> {len(daily):,} sessions "
          f"({daily.index[0].date()} to {daily.index[-1].date()})")

    t = claim_test(daily, lookback=a.lookback)
    print(f"\nOCHOA'S CLAIM: narrow pivot range -> trending; wide -> sideways")
    print(f"classified against a rolling {a.lookback}-session distribution\n")
    g = t.groupby("band")[["efficiency", "range_ratio"]].agg(["mean", "count"])
    print(g.to_string(float_format=lambda v: f"{v:7.3f}"))

    n = t[t.band == "narrow"]["efficiency"]
    w = t[t.band == "wide"]["efficiency"]
    if len(n) > 30 and len(w) > 30:
        from math import sqrt
        d = n.mean() - w.mean()
        se = sqrt(n.var(ddof=1) / len(n) + w.var(ddof=1) / len(w))
        print(f"\nnext-session efficiency, narrow minus wide: {d:+.4f}"
              f"   (t = {d / se:+.2f})")
        print("claim predicts a POSITIVE difference — narrow days should be"
              " followed by\nmore directional sessions than wide days.")
        verdict = ("SUPPORTED" if d / se > 2 else
                   "REJECTED" if d / se < -2 else "NOT SUPPORTED (inside noise)")
        print(f"\nVERDICT: {verdict}")


if __name__ == "__main__":
    main()
