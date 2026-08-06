"""
ADAPTIVE HYBRID — one rule set, three instruments, engine chosen by measurement.

THE IDEA
  The three instruments differ in ONE measurable property and that property
  decides which engine can work:
      GOLD   daily lag-1 autocorrelation  +0.0078   persistence -> TREND
      AU200                               -0.0909   reversion   -> FADE
      US30                                -0.1692   reversion   -> FADE
  Rather than hard-coding "gold = trend, indices = fade", the strategy MEASURES
  autocorrelation on a rolling window and selects its own engine. The same file,
  the same parameters, runs on all three -- and would adapt if an instrument
  changed character.

  TREND MODE      Donchian(entryLen) breakout with a chandelier trail.
  REVERSION MODE  fade |z| >= entryZ against SMA(zLen), exit at z = 0.
  NEUTRAL         no position.

WHY THIS IS NOT CURVE-FITTING THE SWITCH
  The switch reads only past returns, on a window far longer than any trade, and
  it is the SAME threshold on all three instruments. It is not selected per
  instrument. If the mechanism is real the switch should put gold in trend mode
  most of the time and the indices in reversion mode most of the time WITHOUT
  being told which is which -- and that is reported below as a diagnostic before
  any P&L is shown.

INTEGRITY
  Closed-bar signals, next-bar-open fills, gap-aware stops, slippage always
  adverse, and the regime estimate is lagged one bar so it can never read the
  bar it is acting on.
"""
import numpy as np, pandas as pd

TREND, REVERT, FLAT = 1, -1, 0


def atr(df, n=14):
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def rolling_ac1(c, win):
    """Rolling lag-1 autocorrelation of log returns, lagged one bar.

    Shifted so the value used on bar i is built only from returns up to i-1.
    """
    r = pd.Series(np.r_[np.nan, np.diff(np.log(c))])
    ac = r.rolling(win).corr(r.shift(1))
    return ac.shift(1).to_numpy()


def regime(c, win=500, thr=0.02):
    """+1 trend, -1 revert, 0 neutral. One threshold, all instruments."""
    ac = rolling_ac1(c, win)
    g = np.where(ac > thr, TREND, np.where(ac < -thr, REVERT, FLAT))
    return np.where(np.isfinite(ac), g, FLAT).astype(np.int8), ac


def state(df, reg, entry_len=20, trail_atr=4.0, z_len=50, entry_z=2.5,
          rev_stop_atr=6.0, long_only=False):
    """Target direction per bar, plus the active stop, under the chosen engine."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    n = len(c); a = atr(df, 14)
    S = pd.Series
    don_hi = S(h).rolling(entry_len).max().shift(1).to_numpy()
    don_lo = S(l).rolling(entry_len).min().shift(1).to_numpy()
    m = S(c).rolling(z_len).mean().to_numpy()
    sd = S(c).rolling(z_len).std(ddof=0).to_numpy()
    z = np.where(sd > 0, (c - m) / np.where(sd > 0, sd, 1), np.nan)

    d = np.zeros(n, np.int8); stop = np.full(n, np.nan)
    cur = 0; ext = np.nan; mode = 0
    for i in range(n):
        if not np.isfinite(a[i]) or a[i] <= 0:
            d[i] = cur; stop[i] = ext; continue
        if cur == 0:
            mode = reg[i]
            if mode == TREND and np.isfinite(don_hi[i]):
                if c[i] > don_hi[i]:
                    cur, ext = 1, c[i] - trail_atr * a[i]
                elif c[i] < don_lo[i] and not long_only:
                    cur, ext = -1, c[i] + trail_atr * a[i]
            elif mode == REVERT and np.isfinite(z[i]):
                if z[i] <= -entry_z:
                    cur, ext = 1, c[i] - rev_stop_atr * a[i]
                elif z[i] >= entry_z and not long_only:
                    cur, ext = -1, c[i] + rev_stop_atr * a[i]
        else:
            if mode == TREND:
                cand = (h[i - 1] - trail_atr * a[i]) if cur > 0 else (l[i - 1] + trail_atr * a[i])
                ext = max(ext, cand) if cur > 0 else min(ext, cand)
            else:
                if (cur > 0 and z[i] >= 0) or (cur < 0 and z[i] <= 0):
                    cur, ext = 0, np.nan
        d[i] = cur; stop[i] = ext
    return d, stop, z


def backtest(df, d, stop, slip, comm=0.0):
    """Next-bar-open fills, gap-aware stops, state exits at the open."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    tr = []; pos = None
    for i in range(1, len(c) - 1):
        if pos is not None:
            dd = pos["d"]; st = stop[i] if np.isfinite(stop[i]) else pos["stop"]
            if (l[i] <= st) if dd > 0 else (h[i] >= st):
                fill = min(st, o[i]) if dd > 0 else max(st, o[i])
                tr.append(dict(pnl=dd * (fill - dd * slip - pos["e"]) - 2 * comm,
                               bar=pos["bar"], why="stop")); pos = None; continue
            if d[i] != dd:
                tr.append(dict(pnl=dd * (o[i + 1] - dd * slip - pos["e"]) - 2 * comm,
                               bar=pos["bar"], why="state")); pos = None
            else:
                pos["stop"] = st
        if pos is None and d[i] != 0:
            dd = int(d[i])
            pos = dict(d=dd, e=o[i + 1] + dd * slip, bar=i + 1, stop=stop[i])
    return pd.DataFrame(tr)


def stats(t, df=None, cut=None):
    if t is None or len(t) == 0:
        return dict(n=0, pf=np.nan, net=np.nan, wr=np.nan, maxdd=np.nan, top10=np.nan)
    p = t.pnl.to_numpy(); gw, gl = p[p > 0].sum(), -p[p < 0].sum()
    eq = np.cumsum(p); ps = np.sort(p)[::-1]
    out = dict(n=len(p), wr=100 * float((p > 0).mean()),
               pf=float(gw / gl) if gl > 0 else np.inf, net=float(p.sum()),
               maxdd=float(np.max(np.maximum.accumulate(eq) - eq)),
               top10=float(100 * ps[:10].sum() / p.sum()) if p.sum() else np.nan)
    if df is not None:
        dt = df.index[t.bar.values]
        yv = pd.Series(p).groupby(dt.year).sum()
        out["yrs_pos"] = int((yv > 0).sum()); out["yrs"] = len(yv)
        out["by_year"] = {int(k): round(float(v), 1) for k, v in yv.items()}
        if cut is not None:
            A, B = t[dt < cut], t[dt >= cut]
            out["is_pf"] = stats(A)["pf"]; out["oos_pf"] = stats(B)["pf"]
    return out
