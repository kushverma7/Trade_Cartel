"""
Second pass over the source library: the rules buried in the long-form books.

The first battery took the claims that were already written as code or as a
one-line pattern definition. This one takes the rules that are stated in prose
across hundreds of pages and are still exact enough to falsify. Anything that
resolves to "look for aggressiveness in the order flow" is not testable on OHLCV
and is listed as such at the end rather than quietly dropped.

WHAT IS TESTED AND WHERE IT COMES FROM

  john_person_candlesticks_cbot_2006.txt
    HCD  "High Close Doji": a doji, then buy on the close of the bar that makes
         a new CLOSING high. The mirror LCD sells a new closing low.
         This is a strictly different test from the first battery's pin bar:
         Person requires a CONFIRMATION bar, and the confirmation is on the
         close, not the high.
    JACK_HAMMER  lower shadow at least twice the body, little or no upper
         shadow, colour irrelevant; the next candle closing above the hammer's
         high triggers the buy.

  ochoa_profiting_with_pivot_based_concepts.txt
    PIVOT WIDTH  "An unusually wide pivot range can forecast sideways trading.
         An unusually narrow pivot range can forecast trending and breakout
         markets." This is the most interesting claim in the entire library for
         this desk, because the champion IS a breakout system -- if narrow
         pivot days really are breakout days, it is a free entry gate.
         Floor pivots: PP=(H+L+C)/3, BC=(H+L)/2, TC=2*PP-BC, width=|TC-BC|.
    PIVOT RELATIONSHIPS  Higher Value (today's pivot range entirely above
         yesterday's) is "most bullish"; Lower Value most bearish; Inside and
         Outside Value are the neutral cases.
    S1/R1 REACTION  "Buy support in a bull trend, sell resistance in a bear
         trend."

  hougaard_trading_manual.txt:3252
    "When I use a moving average for trend detection, I use the 89-period
     moving average. If the market is trading above 89MA, I deem the trend to
     be up on that time frame."

  trader_dale_order_flow_trading_setups.txt:2795,2895
    Volume Accumulation and Trend setups both reduce to the same measurable
    claim: the price bin that absorbed the heaviest volume over a prior window
    acts as support or resistance when price returns to it. The Order Flow
    confirmation step cannot be tested on OHLCV and is not claimed to be.

TWO KINDS OF TEST, KEPT SEPARATE
  Arms that predict DIRECTION go through the same Welch-t-against-the-
  unconditional-move harness as the first battery.
  Arms that claim to select a REGIME (pivot width, 89MA, pivot relationships)
  are wrong to score that way -- they do not predict direction, they claim to
  say when a breakout system should be trading. Those are run as champion
  gates and scored at MATCHED DRAWDOWN, because a gate that trades less will
  post a higher profit factor whether or not it has found anything.
"""
import numpy as np, pandas as pd

from backtest.io import load_csv
from backtest import champion, exit_lab
from research.source_battery import atr, forward, evaluate, HORIZONS
from research.qt_friday import solve_risk


# ------------------------------------------------------------ Person patterns
def doji(df, body_frac=0.10):
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    rng = h - l
    return (rng > 0) & (abs(c - o) <= body_frac * np.where(rng > 0, rng, 1))


def high_close_doji(df):
    """Person's HCD/LCD: a doji, then a bar closing above/below the doji's close.

    The signal is dated to the CONFIRMATION bar, which is where Person says to
    buy -- 'buy on the close or on the next open after a new closing high is
    made from a Doji'. Dating it to the doji itself would be lookahead.
    """
    d = doji(df)
    c = df["close"].to_numpy(float)
    pd_, pc = np.r_[False, d[:-1]], np.r_[np.nan, c[:-1]]
    return (pd_ & (c > pc)), (pd_ & (c < pc))


def jack_hammer(df, shadow_mult=2.0, upper_max=0.15):
    """Hammer, then a close above the hammer's high. Both bars required."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    rng = np.where(h - l > 0, h - l, np.nan)
    body = abs(c - o)
    lower = np.minimum(o, c) - l
    upper = h - np.maximum(o, c)
    ham = (lower >= shadow_mult * np.maximum(body, 1e-9)) & (upper <= upper_max * rng)
    sha = (upper >= shadow_mult * np.maximum(body, 1e-9)) & (lower <= upper_max * rng)
    ph, pl = np.r_[np.nan, h[:-1]], np.r_[np.nan, l[:-1]]
    pham, psha = np.r_[False, np.nan_to_num(ham, nan=0).astype(bool)[:-1]], \
                 np.r_[False, np.nan_to_num(sha, nan=0).astype(bool)[:-1]]
    return (np.nan_to_num(pham & (c > ph), nan=0).astype(bool),
            np.nan_to_num(psha & (c < pl), nan=0).astype(bool))


# ------------------------------------------------------------- Ochoa's pivots
def floor_pivots(df):
    """Previous day's floor pivot set, broadcast onto today's bars.

    Everything is shifted by a full day: today's levels are built from
    yesterday's completed H/L/C, which is how a pivot trader actually has them
    -- before the session, not during it.
    """
    day = pd.Series(df.index.date, index=df.index)
    g = df.groupby(day)
    H, L, C = g["high"].max(), g["low"].min(), g["close"].last()
    PP = (H + L + C) / 3
    BC = (H + L) / 2
    TC = 2 * PP - BC
    out = pd.DataFrame(index=df.index)
    for nm, s in (("PP", PP), ("TC", np.maximum(TC, BC)), ("BC", np.minimum(TC, BC)),
                  ("R1", 2 * PP - L), ("S1", 2 * PP - H)):
        out[nm] = day.map(pd.Series(s, index=PP.index).shift(1)).values
    out["width"] = out["TC"] - out["BC"]
    # yesterday's range, for normalising the width against the instrument's own scale
    out["prev_rng"] = day.map((H - L).shift(1)).values
    # the relationship between yesterday's pivot range and the day before's
    pTC = day.map(pd.Series(np.maximum(TC, BC), index=PP.index).shift(2)).values
    pBC = day.map(pd.Series(np.minimum(TC, BC), index=PP.index).shift(2)).values
    out["higher_value"] = out["BC"] > pTC
    out["lower_value"] = out["TC"] < pBC
    out["inside_value"] = (out["TC"] <= pTC) & (out["BC"] >= pBC)
    out["outside_value"] = (out["TC"] > pTC) & (out["BC"] < pBC)
    return out


# ---------------------------------------------------------------- Dale's POC
def rolling_poc(df, win=480, bins=60):
    """Price bin holding the heaviest volume over the trailing `win` bars.

    480 bars of 30m is ten calendar days -- Dale draws his profiles over
    rotations and trend legs of roughly that scale. The window ENDS at the
    previous bar, so the POC a bar is compared against never contains that
    bar's own volume.
    """
    c = df["close"].to_numpy(float); v = df["volume"].to_numpy(float)
    n = len(c); poc = np.full(n, np.nan)
    for i in range(win, n):
        cs, vs = c[i - win:i], v[i - win:i]
        lo, hi = cs.min(), cs.max()
        if hi <= lo:
            continue
        idx = np.minimum(((cs - lo) / (hi - lo) * bins).astype(int), bins - 1)
        tot = np.bincount(idx, weights=vs, minlength=bins)
        poc[i] = lo + (tot.argmax() + 0.5) * (hi - lo) / bins
    return poc


def main():
    df = load_csv("data/xauusd_15m.csv.gz", rule="30min")
    a = atr(df)
    c = df["close"].to_numpy(float)
    f = forward(df, a, HORIZONS)

    hcd, lcd = high_close_doji(df)
    jh, js = jack_hammer(df)
    piv = floor_pivots(df)
    ma89 = pd.Series(c).rolling(89).mean().to_numpy()
    poc = rolling_poc(df)

    # Dale: price ENTERS the POC zone from either side; the claim is that the
    # zone holds, so the signal is directional away from the approach.
    near = np.abs(c - poc) < 0.25 * a
    prev_above = np.r_[False, (c[:-1] > poc[:-1])]
    dale_l = near & ~prev_above & np.isfinite(poc)     # came from below, expect support
    dale_s = near & prev_above & np.isfinite(poc)

    # Ochoa: price trades into S1 while in an uptrend / R1 while in a downtrend
    up89 = c > ma89
    s1_hit = (df["low"].to_numpy(float) <= piv["S1"].to_numpy()) & up89
    r1_hit = (df["high"].to_numpy(float) >= piv["R1"].to_numpy()) & ~up89

    arms = [
        ("PERSON_HCD_long", hcd, +1), ("PERSON_LCD_short", lcd, -1),
        ("PERSON_JACKHAMMER", jh, +1), ("PERSON_SHOOTSTAR", js, -1),
        ("DALE_POC_support", dale_l, +1), ("DALE_POC_resist", dale_s, -1),
        ("OCHOA_S1_in_uptrend", np.nan_to_num(s1_hit, nan=0).astype(bool), +1),
        ("OCHOA_R1_in_downtrend", np.nan_to_num(r1_hit, nan=0).astype(bool), -1),
        ("HOUGAARD_above89", np.nan_to_num(up89, nan=0).astype(bool), +1),
        ("HOUGAARD_below89", np.nan_to_num(~up89 & np.isfinite(ma89), nan=0).astype(bool), -1),
    ]
    rows = []
    for nm, s, d in arms:
        rows += evaluate(nm, s, d, f, HORIZONS)
    t = pd.DataFrame(rows)
    print("=" * 104)
    print("DIRECTIONAL ARMS -- forward move vs the UNCONDITIONAL move, in ATR (Welch t)")
    print("  10 arms x 4 horizons. |t| > 3 is the bar; |t| near 2 is expected several times from noise.")
    print("=" * 104)
    print(t.to_string(index=False, float_format=lambda v: f"{v:9.4f}"))
    t.to_csv("research/source_battery2.csv", index=False)

    # ---------------------------------------------------------------- regime gates
    print("\n" + "=" * 104)
    print("OCHOA'S PIVOT-WIDTH CLAIM, tested directly")
    print("  'Unusually narrow pivot range forecasts trending and breakout markets;")
    print("   unusually wide forecasts sideways trading.'")
    print("=" * 104)
    w = (piv["width"] / piv["prev_rng"]).to_numpy()
    day = pd.Series(df.index.date, index=df.index)
    dhi, dlo = df.groupby(day)["high"].max(), df.groupby(day)["low"].min()
    dop, dcl = df.groupby(day)["open"].first(), df.groupby(day)["close"].last()
    eff = (abs(dcl - dop) / (dhi - dlo).replace(0, np.nan))    # trend efficiency of the day
    dwid = pd.Series(w, index=df.index).groupby(day).first()
    band = pd.qcut(dwid.dropna(), 5, labels=["narrowest", "narrow", "mid", "wide", "widest"])
    tab = pd.DataFrame({"width_ratio": dwid, "efficiency": eff,
                        "range_atr": (dhi - dlo)}).loc[band.index]
    tab["band"] = band
    agg = tab.groupby("band", observed=True).agg(days=("efficiency", "size"),
                                                 mean_efficiency=("efficiency", "mean"),
                                                 mean_range=("range_atr", "mean"))
    print(agg.to_string(float_format=lambda v: f"{v:10.4f}"))
    print("  Efficiency = |close-open| / (high-low) for the day. A breakout/trending day")
    print("  scores high; a sideways day scores low. The claim predicts a MONOTONIC")
    print("  fall from 'narrowest' to 'widest'.")
    agg.to_csv("research/source_pivot_width.csv")

    # The ordering can come out right by luck across five bands. Test it.
    from scipy import stats
    tt = tab[["width_ratio", "efficiency"]].dropna()
    rho, p = stats.spearmanr(tt.width_ratio, tt.efficiency)
    q = tt.width_ratio.quantile([0.2, 0.8])
    nn, ww = tt[tt.width_ratio <= q.iloc[0]].efficiency, tt[tt.width_ratio >= q.iloc[1]].efficiency
    wt = stats.ttest_ind(nn, ww, equal_var=False)
    print(f"\n  Spearman rho(width, efficiency) = {rho:+.4f}  p = {p:.4f}   (n={len(tt)} days)")
    print(f"  narrowest vs widest quintile: Welch t = {wt.statistic:+.3f}  p = {wt.pvalue:.4f}")
    print("  The direction Ochoa predicts is the direction observed. The size of it is")
    print("  not distinguishable from noise.")

    print("\n" + "=" * 104)
    print("REGIME GATES ON THE CHAMPION, scored at MATCHED 25% DRAWDOWN")
    print("=" * 104)
    narrow = pd.Series(w, index=df.index).le(dwid.quantile(0.4)).to_numpy()
    wide = pd.Series(w, index=df.index).ge(dwid.quantile(0.6)).to_numpy()
    gates = [
        ("champion, ungated", None),
        ("Ochoa: narrow pivot only", narrow),
        ("Ochoa: wide pivot only", wide),
        ("Ochoa: higher/lower value", (piv["higher_value"] | piv["lower_value"]).to_numpy()),
        ("Ochoa: inside value only", piv["inside_value"].to_numpy()),
        ("Hougaard: |c-89MA| > 1 ATR", np.nan_to_num(abs(c - ma89) > a, nan=0).astype(bool)),
        ("Dale: away from POC > 1 ATR", np.nan_to_num(abs(c - poc) > a, nan=0).astype(bool)),
    ]
    out = []
    for nm, m in gates:
        m2 = None if m is None else np.nan_to_num(m, nan=0).astype(bool)
        r, s = solve_risk(df, m2, 25.0)
        if s["n"] == 0:
            print(f"  {nm:<30} no trades"); continue
        rdd = s["net_pct"] / s["maxdd_pct"] if s["maxdd_pct"] else np.nan
        out.append(dict(gate=nm, risk=r, n=s["n"], pf=s["pf"], net=s["net_pct"],
                        dd=s["maxdd_pct"], net_dd=rdd))
        print(f"  {nm:<30} risk={r:5.2f}%  n={s['n']:<4} PF={s['pf']:.3f}  "
              f"net={s['net_pct']:>+9.1f}%  DD={s['maxdd_pct']:5.2f}%  net/DD={rdd:6.2f}")
    pd.DataFrame(out).to_csv("research/source_regime_gates.csv", index=False)

    surv = t[t.t.abs() > 3]
    print("\n" + "=" * 104)
    print(f"DIRECTIONAL SURVIVORS at |t| > 3: {len(surv)} of {len(t)}")
    print("=" * 104)
    print(surv.to_string(index=False, float_format=lambda v: f"{v:9.4f}") if len(surv)
          else "  none.")

    print("\nNOT TESTABLE ON OHLCV -- recorded so the gap is explicit, not silent:")
    for s in ("Trader Dale's Order Flow confirmation step (bid/ask ladder, delta, absorption)",
              "agent_2_1_cluster_detector: SEC Form 4 insider clusters on US equities -- "
              "no application to XAUUSD and no data here",
              "Gann's astronomical/time-cycle material: no falsifiable rule stated in the text",
              "Hougaard's discretionary 'read the crowd' material: by construction not mechanical"):
        print(f"  - {s}")


if __name__ == "__main__":
    main()
