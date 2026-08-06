"""
Mean-reversion lab for AU200 / Gold / US30, directed by the measured variance
ratios rather than by guesswork.

WHY MEAN REVERSION, AND WHY NOW
  Lo-MacKinlay variance ratios on daily closes (>1 trends, <1 reverts):
      AU200  0.910 / 0.884 / 0.866 / 0.779   lag-1 autocorr -0.0909
      GOLD   1.009 / 0.928 / 0.861 / 0.821   lag-1 autocorr +0.0078
      US30   0.832 / 0.844 / 0.825 / 0.838   lag-1 autocorr -0.1692
  Gold is the only one with positive persistence, which is why the trend family
  works there and has failed on the other two across twenty-plus attempts.
  US30 is the MOST negatively autocorrelated of the three. Testing reversion on
  AU200 and US30 is following the instruments' measured behaviour instead of
  fighting it.

INTEGRITY DISCIPLINE (unchanged from the gate)
  Closed-bar signals; fills at the NEXT bar's open; gap-aware stops
  (min(stop, open) long / max(stop, open) short); a bar touching both stop and
  target resolves to the STOP; slippage always adverse and swept, never zero in
  a headline; year-by-year, IS/OOS split and top-10 concentration on anything
  that survives.

WHAT "WIDE STOP" MEANS HERE
  A reversion trade is entered INTO a move, so the stop must sit outside the
  extension that triggered it or it is guaranteed to be hit by the same
  momentum that created the signal. Stops are therefore expressed in ATR and
  floored well beyond the entry z-score, never inside it.
"""
import numpy as np, pandas as pd

COSTS = {"AU200": 1.0, "GOLD": 0.20, "US30": 1.0}      # slippage pts/side
COMM = {"AU200": 0.0, "GOLD": 0.07, "US30": 0.0}


def atr(df, n=14):
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def zscore(c, n):
    s = pd.Series(c)
    return ((s - s.rolling(n).mean()) / s.rolling(n).std(ddof=0)).to_numpy()


def rsi(c, n=2):
    d = pd.Series(c).diff()
    u = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    v = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + u / v.replace(0, np.nan))).to_numpy()


def state_zrev(c, n=20, entry=2.0, exit_z=0.0, long_only=False, trend=None):
    """Fade an extension, hold until price reverts to the mean.

    The exit is a STATE (z crossing back through exit_z), not a price target, so
    it is resolution-independent -- the defect class that produced two false
    AU200 champions cannot occur here.
    """
    z = zscore(c, n)
    d = np.zeros(len(c), np.int8)
    cur = 0
    for i in range(len(c)):
        if not np.isfinite(z[i]):
            d[i] = 0; cur = 0; continue
        if cur == 0:
            if z[i] <= -entry:
                cur = 1
            elif z[i] >= entry and not long_only:
                cur = -1
        elif cur > 0 and z[i] >= exit_z:
            cur = 0
        elif cur < 0 and z[i] <= -exit_z:
            cur = 0
        d[i] = cur
    if trend is not None:
        d = np.where((d > 0) & ~trend, 0, d)
        d = np.where((d < 0) & trend, 0, d)
    return d.astype(np.int8)


def state_rsi(c, n=2, lo=10, hi=90, ma_n=200, long_only=True):
    """Connors-style: RSI(2) extreme in the direction of a long-term filter."""
    r = rsi(c, n)
    m = pd.Series(c).rolling(ma_n).mean().to_numpy()
    d = np.zeros(len(c), np.int8); cur = 0
    for i in range(len(c)):
        if not np.isfinite(r[i]) or not np.isfinite(m[i]):
            d[i] = 0; cur = 0; continue
        if cur == 0:
            if r[i] < lo and c[i] > m[i]:
                cur = 1
            elif r[i] > hi and c[i] < m[i] and not long_only:
                cur = -1
        elif cur > 0 and r[i] > 50:
            cur = 0
        elif cur < 0 and r[i] < 50:
            cur = 0
        d[i] = cur
    return d.astype(np.int8)


def run(df, state, a, slip, comm, stop_atr=0.0, max_bars=0):
    """Next-bar-open fills, gap-aware stops, state exits at the open."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    n = len(c); tr = []; pos = None
    for i in range(1, n - 1):
        if pos is not None:
            d = pos["d"]
            if stop_atr > 0 and ((l[i] <= pos["stop"]) if d > 0 else (h[i] >= pos["stop"])):
                fill = min(pos["stop"], o[i]) if d > 0 else max(pos["stop"], o[i])
                tr.append(dict(pnl=d * (fill - d * slip - pos["e"]) - 2 * comm,
                               bar=pos["bar"], why="stop")); pos = None; continue
            if state[i] != d or (max_bars and i - pos["bar"] >= max_bars):
                tr.append(dict(pnl=d * (o[i + 1] - d * slip - pos["e"]) - 2 * comm,
                               bar=pos["bar"], why="state")); pos = None
        if pos is None and state[i] != 0:
            d = int(state[i]); e = o[i + 1] + d * slip
            pos = dict(d=d, e=e, bar=i + 1,
                       stop=e - d * stop_atr * a[i] if stop_atr > 0 else np.nan)
    return pd.DataFrame(tr)


def stats(t, df=None, cut=None):
    if t is None or len(t) == 0:
        return dict(n=0)
    p = t.pnl.to_numpy()
    gw, gl = p[p > 0].sum(), -p[p < 0].sum()
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
            out["is_pf"] = stats(A)["pf"] if len(A) else np.nan
            out["oos_pf"] = stats(B)["pf"] if len(B) else np.nan
            out["is_n"] = len(A); out["oos_n"] = len(B)
    return out
