"""
The Market Traders Institute set (5 PDFs), tested where anything is testable.

WHAT ARRIVED AND WHAT IS IN IT
  5_Beginner_Mistakes.pdf        8pp   psychology/marketing. No mechanical rule.
  5_Tips_Market_Volatility.pdf  17pp   narrative about media noise, plus a
                                       vendor pitch for VantagePoint. No rule.
  15_FXProfit_Hacks.pdf         56pp   fifteen "hacks". Two are exact.
  15_FXProfit_Hacks1.pdf        56pp   BYTE-IDENTICAL DUPLICATE of the above
                                       (md5 2da1a431dd8d9e34b34ecde7af49ba8c on
                                       both extractions). Not counted twice.
  25_Trading_Tips.pdf            8pp   image-only PDF, rendered and read as
                                       pages. Twenty-five aphorisms, zero
                                       mechanical rules.

  So of ~145 pages, four claims are specified precisely enough to falsify. The
  rest is advice, and advice is not a hypothesis. That is the finding for those
  documents and it is stated rather than padded out.

THE FOUR TESTABLE CLAIMS

  HACK #4  "Never risk more than two to five percent of your overall account in
           any given trade."
           -> This is the one that matters, because it is a claim about the
           user's real account. The champion, solved to a 25% drawdown budget,
           risks 0.72% per trade. MTI's floor is 2.8x that and its ceiling is
           6.9x. The test is simply: run the champion at 1, 2, 3, 4 and 5
           percent and report the drawdown and the terminal equity. Position
           sizing is the one part of a system where the answer is arithmetic
           rather than opinion.

  HACK #6  "There is a very easy way to see when the market is going to fall or
           rise, and that is known as the Stochastic RSI ... a market outside
           of the top and bottom levels is expected to u-turn."
           -> Standard StochRSI(14,14,3,3), bands at 80/20, tested for the
           u-turn against the unconditional forward move.

  HACK #11 "When one session ends, and another begins, the opposite reversal
           point typically forms."
           -> Do session boundaries produce the session's extreme, and a
           reversal, more often than the rest of the session does?

  TIP #5   "Watch out for wildcard candlesticks the closer we get to the end of
           the month."
           -> Are month-end bars more erratic: bigger ranges, more sign flips?

  Hack #1 (multiple timeframes) and Hack #3 (candlestick formations) were
  already tested this session -- 4h agreement scored net/DD 11.30 against the
  baseline's 27.26, and candle confirmation 6.35. Not re-run.
"""
import numpy as np, pandas as pd

from backtest.io import load_csv
from backtest import champion, exit_lab
from research.source_battery import atr, forward, evaluate, HORIZONS
from research.qt_corrected import to_local


def stoch_rsi(df, rsi_n=14, stoch_n=14, k=3, d=3):
    c = pd.Series(df["close"].to_numpy(float))
    delta = c.diff()
    up = delta.clip(lower=0).ewm(alpha=1 / rsi_n, adjust=False).mean()
    dn = (-delta.clip(upper=0)).ewm(alpha=1 / rsi_n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    lo = rsi.rolling(stoch_n).min(); hi = rsi.rolling(stoch_n).max()
    st = 100 * (rsi - lo) / (hi - lo).replace(0, np.nan)
    K = st.rolling(k).mean()
    return K.to_numpy(), K.rolling(d).mean().to_numpy()


def main():
    df = load_csv("data/xauusd_15m.csv.gz", rule="30min")
    a = atr(df)
    f = forward(df, a, HORIZONS)
    loc = to_local(df.index, "ny")

    # ---------------------------------------------------------- HACK #4
    print("=" * 100)
    print("HACK #4 -- 'never risk more than two to five percent per trade'")
    print("  The champion, solved to a 25% drawdown budget, risks 0.72%.")
    print("  What MTI's range actually does to it:")
    print("=" * 100)
    rows = []
    for rp in (0.5, 0.72, 1.0, 2.0, 3.0, 4.0, 5.0):
        tr, _ = champion.run(df, risk_pct=rp)
        s = exit_lab.stats(tr)
        # terminal equity multiple, and the worst peak-to-trough in percent
        mult = (1 + s["net_pct"] / 100)
        rows.append(dict(risk_pct=rp, n=s["n"], pf=s["pf"], net_pct=s["net_pct"],
                         maxdd_pct=s["maxdd_pct"], equity_multiple=mult))
        flag = ""
        if s["maxdd_pct"] > 60:
            flag = "  <-- unrecoverable in practice"
        if s["maxdd_pct"] > 90:
            flag = "  <-- ACCOUNT DESTROYED"
        print(f"  risk={rp:4.2f}%  n={s['n']:<4} PF={s['pf']:6.3f}  "
              f"net={s['net_pct']:>+12.1f}%  maxDD={s['maxdd_pct']:6.2f}%"
              f"  x{mult:>10.2f}{flag}")
    pd.DataFrame(rows).to_csv("research/mti_risk_sizing.csv", index=False)
    print("\n  Drawdown is what decides whether an account survives to collect the")
    print("  return. The 21.7% win rate means losing runs are long, and a long")
    print("  losing run at 5% per trade compounds down hard.")

    # ---------------------------------------------------------- HACK #6
    K, D = stoch_rsi(df)
    ob, os_ = K > 80, K < 20
    cross_dn = np.r_[False, (K[1:] < D[1:]) & (K[:-1] >= D[:-1])] & ob
    cross_up = np.r_[False, (K[1:] > D[1:]) & (K[:-1] <= D[:-1])] & os_
    arms = [("STOCHRSI_overbought_short", np.nan_to_num(ob, nan=0).astype(bool), -1),
            ("STOCHRSI_oversold_long", np.nan_to_num(os_, nan=0).astype(bool), +1),
            ("STOCHRSI_ob_cross_short", np.nan_to_num(cross_dn, nan=0).astype(bool), -1),
            ("STOCHRSI_os_cross_long", np.nan_to_num(cross_up, nan=0).astype(bool), +1)]
    rows = []
    for nm, s, d in arms:
        rows += evaluate(nm, s, np.float64(d), f, HORIZONS)
    t = pd.DataFrame(rows)
    print("\n" + "=" * 100)
    print("HACK #6 -- StochRSI: 'a market outside the top and bottom levels is")
    print("  expected to u-turn'. Forward move vs the unconditional move, in ATR.")
    print("=" * 100)
    print(t.to_string(index=False, float_format=lambda v: f"{v:9.4f}"))
    t.to_csv("research/mti_stochrsi.csv", index=False)

    # ---------------------------------------------------------- HACK #11
    print("\n" + "=" * 100)
    print("HACK #11 -- 'when one session ends and another begins, the opposite")
    print("  reversal point typically forms'")
    print("=" * 100)
    mins = loc.hour * 60 + loc.minute
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    r = np.r_[np.nan, np.diff(c)]
    prev_up = np.r_[np.nan, r[:-1]] > 0
    flip = (r > 0) != prev_up
    ok = np.isfinite(r) & np.isfinite(np.r_[np.nan, r[:-1]])
    day = pd.Series(loc.date, index=df.index)
    # NY-anchored session opens: Asia 18:00, London 03:00, NY 08:00
    for nm, st in (("Asia open 18:00", 18 * 60), ("London open 03:00", 3 * 60),
                   ("NY open 08:00", 8 * 60)):
        win = (mins >= st) & (mins < st + 120)          # first two hours
        # does the session-open window contain the DAY's high or low?
        dh = df.groupby(day)["high"].transform("max").to_numpy()
        dl = df.groupby(day)["low"].transform("min").to_numpy()
        sets = ((h >= dh) | (l <= dl))
        base = win.mean()
        print(f"  {nm:<20} bars={win.sum():<6} "
              f"sets day extreme: {sets[win].mean():.3f} vs {sets[~win].mean():.3f} elsewhere  |  "
              f"flip rate {flip[win & ok].mean():.3f} vs {flip[~win & ok].mean():.3f}  |  "
              f"share of bars {base:.3f}")
    print("  A genuine 'reversal point' needs the flip rate to be HIGHER at the")
    print("  boundary. Setting the extreme more often is a volatility fact, and")
    print("  a volatility fact on its own is not a trade.")

    # ---------------------------------------------------------- TIP #5
    print("\n" + "=" * 100)
    print("TIP #5 -- 'watch out for wildcard candlesticks the closer we get to")
    print("  the end of the month'")
    print("=" * 100)
    dom = pd.Series(loc.day, index=df.index).to_numpy()
    dim = pd.Series(loc.days_in_month, index=df.index).to_numpy()
    tail = dom > dim - 4                                   # last three days
    rng_atr = (h - l) / a
    print(f"  last 3 days of month : n={tail.sum():<6} mean range {np.nanmean(rng_atr[tail]):.4f} ATR"
          f"   flip rate {flip[tail & ok].mean():.4f}")
    print(f"  rest of the month    : n={(~tail).sum():<6} mean range {np.nanmean(rng_atr[~tail]):.4f} ATR"
          f"   flip rate {flip[~tail & ok].mean():.4f}")

    print("\n" + "=" * 100)
    print("NOT TESTABLE, and this IS the finding for these five files")
    print("=" * 100)
    for s in ("5_Beginner_Mistakes.pdf (8pp): psychology and a course pitch. No rule.",
              "5_Tips_Market_Volatility.pdf (17pp): media-noise narrative plus a "
              "vendor pitch for VantagePoint's proprietary indicator. No rule.",
              "25_Trading_Tips.pdf (8pp): 25 aphorisms. Zero mechanical content.",
              "15_FXProfit_Hacks1.pdf: byte-identical duplicate of 15_FXProfit_Hacks.pdf.",
              "Hacks 2,7,8,9,12,13,14,15: workflow, psychology, basket trading on "
              "FX pairs (no application to a single gold instrument), or teasers "
              "with no content in the ebook."):
        print(f"  - {s}")


if __name__ == "__main__":
    main()
