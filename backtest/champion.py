"""
The champion (`strategies/gold_trend_strategy.pine`) as a research harness.

WHY THIS FILE EXISTS
  The champion's filter stack lives only in the Pine file. `trend.py` has the
  filters but no cooldown and no gap-aware fills; `exit_lab.py` has the exit,
  the cooldown, the pyramiding and the gap-aware fills but takes its entry
  signal from outside. Neither alone is the champion. This module builds the
  signals the way the Pine builds them and runs them through exit_lab, so one
  definition serves the instrument test, the trail sweep and the pyramiding
  rework.

THE ONE REAL DECISION: WHAT "UNCHANGED SETTINGS" MEANS ON A SECOND INSTRUMENT
  Every lookback in the Pine is in BARS, and its auto-scale block converts a
  CALENDAR target into bars assuming the market trades continuously:

      entryLenE = 12h / tf      smaLenE = 8d / tf      regimeLenE = 21d / tf

  That assumption is true for gold (~24h a day) and false for US30 cash
  (~5.8h a day). At 30m gold gives ~32 bars a day and US30 ~11.5. So there
  are two defensible readings of "run it unchanged", and they are different
  experiments:

      BARS   identical integers: 24 / 384 / 1008 / 96.
             The literal instruction. But 384 bars is 8 days of gold and
             ~33 days of US30, so the filters are ~2.8x SLOWER in real time.

      CLOCK  identical calendar horizons: 12h / 8d / 21d / 2d, converted at
             US30's own bars-per-day. This is what the Pine's auto-scale is
             TRYING to do and what it would do if it knew the session length.

  Both are run and both are reported. Claiming one number for "US30 unchanged"
  would be hiding a choice that moves the result.
"""
import numpy as np
import pandas as pd

from backtest import exit_lab

# Champion defaults, 30m basis, straight from the Pine's effective settings.
TRAIL_ATR = 4.24          # 6.0 * sqrt(15/30)
SHORT_RISK = 0.75
RISK_PCT = 1.0
COOLDOWN = 3
ATR_N = 14
COMMISSION, SLIPPAGE = 0.07, 0.20
PYR = dict(pyr_atr=1.5, pyr_max=4)              # Balanced
PYR_CONS = dict(pyr_atr=3.0, pyr_max=2)         # Conservative

# Calendar targets the Pine's auto-scale block encodes.
CAL_HOURS = dict(entry=12.0, sma=8 * 24.0, ema=21 * 24.0, sma2=21 * 24.0,
                 slope=2 * 24.0)


def bars_per_day(df):
    """Median bars in a trading day -- the number the Pine assumes it knows."""
    d = pd.Series(df.index.date, index=df.index)
    return float(d.groupby(d).size().median())


def lookbacks(df, mode="bars", tf_min=30.0):
    """Return the five lookbacks under either reading of 'unchanged'."""
    if mode == "bars":
        return dict(entry=int(CAL_HOURS["entry"] * 60 / tf_min),
                    sma=int(CAL_HOURS["sma"] * 60 / tf_min),
                    ema=int(CAL_HOURS["ema"] * 60 / tf_min),
                    sma2=int(CAL_HOURS["sma2"] * 60 / tf_min),
                    slope=int(CAL_HOURS["slope"] * 60 / tf_min))
    bpd = bars_per_day(df)
    per_hour = bpd / 24.0            # bars per CALENDAR hour on this series
    out = {}
    for k, hrs in CAL_HOURS.items():
        out[k] = max(5, int(round(hrs * per_hour)))
    return out


def signals(df, lb, long_only=False, long_slope=False):
    """The Pine's entry, filters and gates, built exactly as the Pine builds them.

    Donchian uses .shift(1) so the breakout bar cannot set its own trigger --
    the same `[1]` the Pine carries on every ta.highest/ta.lowest call.
    """
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    S = pd.Series
    donHi = S(h).rolling(lb["entry"]).max().shift(1).to_numpy()
    donLo = S(l).rolling(lb["entry"]).min().shift(1).to_numpy()
    ema = S(c).ewm(span=lb["ema"], adjust=False).mean().to_numpy()
    sma = S(c).rolling(lb["sma"]).mean().to_numpy()
    sma2 = S(c).rolling(lb["sma2"]).mean().to_numpy()
    prev = S(ema).shift(lb["slope"]).to_numpy()
    falling = ema < prev
    rising = ema > prev

    trigUp = c > donHi
    trigDn = c < donLo
    okL = (c > ema) & (c > sma) & (c > sma2)
    okS = (c < ema) & (c < sma) & (c < sma2) & falling   # slope gate: shorts only
    if long_slope:
        okL = okL & rising
    sigL = trigUp & okL & np.isfinite(donHi) & np.isfinite(sma2)
    sigS = trigDn & okS & np.isfinite(donLo) & np.isfinite(sma2)
    if long_only:
        sigS = np.zeros(len(c), bool)
    return np.nan_to_num(sigL, nan=0).astype(bool), np.nan_to_num(sigS, nan=0).astype(bool)


def run(df, mode="bars", tf_min=30.0, trail_atr=TRAIL_ATR, risk_pct=RISK_PCT,
        pyr=None, cooldown=COOLDOWN, slippage=SLIPPAGE, stop_atr=None, **kw):
    """One champion run. Returns (trades, lookbacks_used).

    `stop_atr` sets BOTH the initial stop distance and, through it, the
    position size. The Pine ties it to the trail width -- `stopDist =
    atr * trailMultE` is used for the opening stop and for `qty` alike -- so
    it defaults to trail_atr here. Passing it explicitly is what DECOUPLES
    trail width from position sizing: hold stop_atr fixed and sweep trail_atr
    and every arm risks the same fraction of equity on the same initial stop.
    """
    lb = lookbacks(df, mode, tf_min)
    sigL, sigS = signals(df, lb)
    p = PYR if pyr is None else pyr
    tr = exit_lab.run(df, sigL, sigS, trail_mode="chandelier",
                      stop_atr=trail_atr if stop_atr is None else stop_atr,
                      trail_atr=trail_atr, risk_pct=risk_pct,
                      short_risk=SHORT_RISK, cooldown=cooldown, atr_n=ATR_N,
                      commission=COMMISSION, slippage=slippage, **p, **kw)
    return tr, lb


def summarise(tr, label, note=""):
    """Print the full metric set the deliverable asks for, including avg R."""
    s = exit_lab.stats(tr)
    if s["n"] == 0:
        print(f"  {label:<30} no trades"); return s
    p = np.array([t["pnl"] for t in tr])
    # 1R is the risk budget per entry: risk_pct% of equity at the time.
    # exit_lab records it per trade where available; fall back to the
    # median loss, which is what a full stop-out costs.
    losses = -p[p < 0]
    r_unit = float(np.median(losses)) if len(losses) else np.nan
    avg_r = float(p.mean() / r_unit) if r_unit and np.isfinite(r_unit) else np.nan
    print(f"  {label:<30} n={s['n']:>4}  WR={s['wr']:5.1f}%  PF={s['pf']:6.3f}  "
          f"net={s['net_pct']:>+9.1f}%  DD={s['maxdd_pct']:5.2f}%  "
          f"ret/DD={s['rdd']:5.2f}  avgR={avg_r:+5.2f}  bars={s['avg_bars']:4.0f}  {note}")
    s["avg_r"] = avg_r
    return s


def halves(tr, label):
    s = summarise(tr, label)
    if len(tr) >= 40:
        mid = len(tr) // 2
        summarise(tr[:mid], "    first half")
        summarise(tr[mid:], "    OOS half")
    return s
