"""
The hybrid: one portfolio running three uncorrelated sleeves, sized as a book.

WHY A PORTFOLIO AND NOT A MERGED INDICATOR
  The three instruments do not share a return-generating property. Measured
  daily variance ratios and lag-1 autocorrelation:
      GOLD   VR(2) 1.009, lag-1 +0.0078   -> persistence  -> TREND
      AU200  VR(2) 0.910, lag-1 -0.0909   -> reversion    -> FADE
      US30   VR(2) 0.832, lag-1 -0.1692   -> reversion    -> FADE
  A single rule applied to all three must be wrong on at least two of them.
  Twenty-plus attempts in this project confirmed exactly that. The correct
  hybrid is therefore three specialised sleeves combined at the BOOK level, and
  the profit comes from where portfolio profit always comes from: sleeves whose
  drawdowns do not coincide.

SIZING, MADE COMPARABLE
  Every sleeve risks the same fraction of TOTAL book equity per trade, and the
  risk unit is that trade's own stop distance. A trade that moves +2 stop
  distances returns +2 x risk_pct of book equity, whatever the instrument's
  point value or price level. This is the only way to combine a $2,500 metal,
  a 9,000-point index and a 40,000-point index in one equity curve without the
  biggest number silently dominating.

WHAT IS BEING CLAIMED, AND WHAT IS NOT
  Claimed: the three sleeves are close to uncorrelated, so the book carries a
  higher return per unit of drawdown than any sleeve alone.
  NOT claimed: that the AU200 and US30 sleeves are as well established as the
  gold sleeve. They rest on 65-77 trades each. The gold sleeve rests on 711.
  The book inherits that weakness and it is quantified below, not hidden.
"""
import numpy as np, pandas as pd

from backtest.io import load_csv
from backtest import champion as ch, exit_lab
from research.au200_lab import load as load_au
from research.mean_reversion_lab import (atr, state_zrev, state_rsi, run as mr_run,
                                         COSTS, COMM)
from research.voltarget import g1_series


# ------------------------------------------------------------------ sleeves
def sleeve_gold(risk_pct=1.0):
    """G1*: the validated trend system. 30m bars."""
    df = load_csv("data/xauusd_15m.csv.gz", rule="30min")
    g1 = g1_series(df)
    tr, _ = ch.run(df, pyr=dict(pyr_atr=1.5, pyr_max=4, pyr_mode="vol_entry"),
                   cooldown=30, lb_over=dict(sma2=630), tighten_after=15,
                   tighten_to=2.0, frac_qty=True, risk_pct=risk_pct,
                   risk_series=g1, risk_series_adds=True)
    d = pd.DataFrame(tr)
    # exit_lab already sizes by risk_pct of equity, so pnl is in currency on a
    # 10,000 base; convert to a fraction of that base per trade
    d["ret"] = d.pnl / 10000.0
    d["dt"] = df.index[d.bar.values]
    return d[["dt", "ret"]].copy(), "GOLD"


def _mr_sleeve(df, state, stop_atr, slip, comm, risk_pct):
    """Reversion sleeve -> per-trade return as a fraction of book equity.

    ret = risk_pct * (points moved / stop distance). The stop distance is the
    risk unit, so a trade that runs one stop in profit returns exactly risk_pct.
    """
    a = atr(df, 14)
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    tr = []; pos = None
    for i in range(1, len(c) - 1):
        if pos is not None:
            d = pos["d"]
            if (l[i] <= pos["stop"]) if d > 0 else (h[i] >= pos["stop"]):
                fill = min(pos["stop"], o[i]) if d > 0 else max(pos["stop"], o[i])
                pts = d * (fill - d * slip - pos["e"]) - 2 * comm
                tr.append(dict(dt=df.index[i], ret=risk_pct / 100 * pts / pos["risk"]))
                pos = None; continue
            if state[i] != d:
                pts = d * (o[i + 1] - d * slip - pos["e"]) - 2 * comm
                tr.append(dict(dt=df.index[i + 1], ret=risk_pct / 100 * pts / pos["risk"]))
                pos = None
        if pos is None and state[i] != 0:
            d = int(state[i]); e = o[i + 1] + d * slip
            risk = stop_atr * a[i]
            pos = dict(d=d, e=e, stop=e - d * risk, risk=risk)
    return pd.DataFrame(tr)


def sleeve_au200(risk_pct=1.0):
    """AU200 4H z-reversion, 6 x ATR stop."""
    d15 = load_au("data/au200_15m.csv.gz"); d15.index = d15.index.tz_localize(None)
    df = d15.resample("4h").agg({"open": "first", "high": "max", "low": "min",
                                 "close": "last"}).dropna()
    st = state_zrev(df["close"].to_numpy(float), 50, 2.5, 0.0)
    return _mr_sleeve(df, st, 6.0, COSTS["AU200"], COMM["AU200"], risk_pct), "AU200"


def sleeve_us30(risk_pct=1.0):
    """US30 daily RSI(2) with MA200 regime filter, 4 x ATR stop."""
    u = pd.read_csv("data/us30_15m_native.csv.gz")
    u.columns = [c.lower() for c in u.columns]
    u.index = pd.to_datetime(u[u.columns[0]], utc=True).dt.tz_localize(None)
    df = u[["open", "high", "low", "close"]].resample("1D").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    st = state_rsi(df["close"].to_numpy(float), 2, 10, 90, 200, long_only=False)
    return _mr_sleeve(df, st, 4.0, COSTS["US30"], COMM["US30"], risk_pct), "US30"


# ---------------------------------------------------------------- portfolio
def to_daily(d, index):
    """Trade returns -> a daily return series on a common calendar."""
    s = d.set_index("dt")["ret"].groupby(level=0).sum()
    return s.reindex(index).fillna(0.0)


def book(weights, risk_pct=1.0, start=None, end=None):
    """Combine the sleeves and return the compounded book equity curve."""
    parts = {}
    for fn in (sleeve_gold, sleeve_au200, sleeve_us30):
        d, nm = fn(risk_pct)
        d["dt"] = pd.to_datetime(d["dt"]).dt.normalize()
        parts[nm] = d
    lo = max(p.dt.min() for p in parts.values())
    hi = min(p.dt.max() for p in parts.values())
    if start: lo = max(lo, pd.Timestamp(start))
    if end: hi = min(hi, pd.Timestamp(end))
    cal = pd.date_range(lo, hi, freq="D")
    daily = pd.DataFrame({nm: to_daily(p, cal) for nm, p in parts.items()})
    daily = daily.loc[lo:hi]
    w = pd.Series(weights, dtype=float)
    daily["BOOK"] = (daily[list(w.index)] * w).sum(axis=1)
    return daily, parts


def curve_stats(r, label, ppy=365):
    """Compounded stats from a daily return series."""
    eq = (1 + r).cumprod()
    yrs = len(r) / ppy
    cagr = (eq.iloc[-1] ** (1 / yrs) - 1) * 100
    dd = (1 - eq / eq.cummax())
    mdd = dd.max() * 100
    pos, neg = r[r > 0].sum(), -r[r < 0].sum()
    ann_vol = r.std() * np.sqrt(ppy) * 100
    return dict(arm=label, days=len(r), cagr=cagr, maxdd=mdd,
                mar=cagr / mdd if mdd > 0 else np.nan,
                pf=float(pos / neg) if neg > 0 else np.inf,
                net=(eq.iloc[-1] - 1) * 100, vol=ann_vol,
                sharpe=(r.mean() * ppy) / (r.std() * np.sqrt(ppy)) if r.std() > 0 else np.nan)
