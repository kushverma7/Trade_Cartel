"""
The multi-timeframe trend-break plan, tested where it differs from what is
already built.

WHAT THE PLAN ASKS FOR AND WHAT IS ALREADY THERE
  Daily highs/lows as the breakout levels          -> the champion's Donchian
                                                      already is this
  4-hour trend, confirmed by a 20-period MA        -> NEW. The champion's
                                                      filter stack (EMA, SMA,
                                                      slow SMA, slope) is all
                                                      built on the 30-minute
                                                      series. An explicit
                                                      higher-timeframe
                                                      agreement gate is not.
  Entry on a lower-timeframe break with volume     -> volume tested (it hurt:
                                                      net/DD 10.87 vs 27.26)
  Candlestick confirmation (engulfing, pin bar)    -> NEW as a GATE on the
                                                      champion. Pin bars were
                                                      tested standalone and
                                                      were flat, which is not
                                                      the same question.
  Stop just below previous resistance              -> already tested and it is
                                                      the worst result of the
                                                      session: net/DD 2.71
                                                      against 27.26, because
                                                      the median distance from
                                                      a breakout close back to
                                                      the broken level is 0.38
                                                      ATR. That is inside the
                                                      noise; it stops out
                                                      almost everything.
  Risk-reward at least 1:2                         -> NEW as a hard target
  Partial exits, trail the remainder               -> the champion already
                                                      trails; partials at
                                                      pivots were tested above

  So four things are actually new and each is run as a matched-drawdown
  variant. The reversals note that arrived with it is descriptive -- it defines
  what a reversal is and warns they are hard to predict -- and states no
  mechanical rule, so there is nothing in it to falsify. Recorded, not tested.
"""
import numpy as np, pandas as pd

from backtest.io import load_csv
from backtest import champion
from research.scalp_checklist import bollinger, solve_risk_kw, report
from research.source_battery import pin_bars


def htf_trend(df, hours=4, ma=20):
    """4-hour close vs its own 20-period MA, mapped back onto 30m bars.

    Resampled with label='right'/closed='right' and then SHIFTED, so a 30m bar
    only ever sees 4-hour candles that have already completed. Reading the
    in-progress 4-hour bar would be lookahead and would flatter every result.
    """
    h4 = df["close"].resample(f"{hours}h", label="right", closed="right").last().dropna()
    m = h4.rolling(ma).mean()
    up = (h4 > m).shift(1)                    # completed bars only
    return up.reindex(df.index, method="ffill").fillna(False).to_numpy().astype(bool)


def engulfing(df):
    o, c = df["open"].to_numpy(float), df["close"].to_numpy(float)
    po, pc = np.r_[np.nan, o[:-1]], np.r_[np.nan, c[:-1]]
    bull = (c > o) & (pc < po) & (c >= po) & (o <= pc)
    bear = (c < o) & (pc > po) & (c <= po) & (o >= pc)
    return np.nan_to_num(bull, nan=0).astype(bool), np.nan_to_num(bear, nan=0).astype(bool)


def main():
    df = load_csv("data/xauusd_15m.csv.gz", rule="30min")
    _ma, bw = bollinger(df)
    sq = np.nan_to_num(bw < np.nanquantile(bw, 0.40), nan=0).astype(bool)
    up4 = htf_trend(df)
    eb, es = engulfing(df)
    pb, pr = pin_bars(df)
    confirm = eb | es | pb | pr

    out = []
    print("=" * 104)
    print("MTF PLAN -- every variant dialled by bisection to 25% MAX DRAWDOWN")
    print("=" * 104)
    r, s, _ = solve_risk_kw(df); report("baseline champion", r, s, out)

    # The 4h gate has to be DIRECTIONAL: it should allow longs only when the
    # 4-hour trend is up. A symmetric mask would not be the plan's rule.
    lb = champion.lookbacks(df, "bars", 30.0)
    sigL, sigS = champion.signals(df, lb)
    from backtest import exit_lab

    def run_dir(maskL, maskS, **kw):
        tr = exit_lab.run(df, sigL & maskL, sigS & maskS,
                          trail_mode="chandelier", stop_atr=champion.TRAIL_ATR,
                          trail_atr=champion.TRAIL_ATR, short_risk=champion.SHORT_RISK,
                          cooldown=champion.COOLDOWN, atr_n=champion.ATR_N,
                          commission=champion.COMMISSION, slippage=champion.SLIPPAGE,
                          **champion.PYR, **kw)
        return tr

    def solve_dir(label, maskL, maskS, **kw):
        lo, hi, best = 0.05, 12.0, None
        for _ in range(22):
            mid = (lo + hi) / 2
            tr = run_dir(maskL, maskS, risk_pct=mid, **kw)
            st = exit_lab.stats(tr)
            best = (mid, st)
            if st["n"] == 0 or st["maxdd_pct"] > 25.0:
                hi = mid
            else:
                lo = mid
        report(label, best[0], best[1], out)

    solve_dir("4h trend agreement (directional)", up4, ~up4)
    solve_dir("4h trend DISagreement (control)", ~up4, up4)
    solve_dir("candle confirmation on the break", confirm, confirm)
    solve_dir("4h agree + squeeze", up4 & sq, ~up4 & sq)

    # risk-reward 1:2 as a hard target on the plan's own terms
    for rr, pct in ((2.0, 1.0), (2.0, 0.5), (3.0, 0.5)):
        r, s, _ = solve_risk_kw(df, tp1_mode="rr", tp1_val=rr, tp1_pct=pct)
        report(f"hard target {rr:.0f}R on {int(pct*100)}% of size", r, s, out)

    pd.DataFrame(out).to_csv("research/mtf_plan.csv", index=False)
    best = max(out, key=lambda d: d["net_dd"])
    print("\n  BEST BY net/DD: %s (%.2f)" % (best["arm"], best["net_dd"]))


if __name__ == "__main__":
    main()
