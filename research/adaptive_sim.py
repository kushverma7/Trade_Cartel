"""
ADAPTIVE HYBRID v2 -- single integrated simulator.

v1 separated signal-state from execution; the stop fired in the executor but the
state array still showed the old direction, so the engine re-entered the same
trade on the very next bar and churned (WR 0.2%, n=4585). That was a bug, not a
result. Here position, stop and exit live in ONE loop, so a stopped-out trade
cannot re-open until the entry condition fires again from flat.

INTEGRITY
  Signals read bar i (closed), fills happen at open of bar i+1, stops are checked
  intrabar with gap-aware fills, slippage is always adverse, and the regime
  estimate is lagged one bar.
"""
import numpy as np, pandas as pd

TREND, REVERT, FLAT = 1, -1, 0


def atr(df, n=14):
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def rolling_ac1(c, win):
    r = pd.Series(np.r_[np.nan, np.diff(np.log(c))])
    return r.rolling(win).corr(r.shift(1)).shift(1).to_numpy()


def regime(c, win=500, thr=0.02):
    ac = rolling_ac1(c, win)
    g = np.where(ac > thr, TREND, np.where(ac < -thr, REVERT, FLAT))
    return np.where(np.isfinite(ac), g, FLAT).astype(np.int8), ac


def simulate(df, reg, slip, entry_len=20, trail_atr=4.0, z_len=50, entry_z=2.5,
             rev_stop_atr=6.0, allow_trend=True, allow_revert=True):
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    n = len(c); a = atr(df, 14); S = pd.Series
    don_hi = S(h).rolling(entry_len).max().shift(1).to_numpy()
    don_lo = S(l).rolling(entry_len).min().shift(1).to_numpy()
    m = S(c).rolling(z_len).mean().to_numpy()
    sd = S(c).rolling(z_len).std(ddof=0).to_numpy()
    z = np.where(sd > 0, (c - m) / np.where(sd > 0, sd, 1.0), np.nan)

    tr = []; pos = None; pend = None
    for i in range(n - 1):
        # --- manage an open position on bar i -------------------------------
        if pos is not None:
            d = pos["d"]
            hit = (l[i] <= pos["stop"]) if d > 0 else (h[i] >= pos["stop"])
            if hit:
                fill = (min(pos["stop"], o[i]) if d > 0 else max(pos["stop"], o[i])) - d * slip
                tr.append(dict(pnl=d * (fill - pos["e"]), bar=pos["bar"], mode=pos["mode"],
                               d=d, why="stop")); pos = None
            elif pos["mode"] == REVERT and np.isfinite(z[i]) and (
                    (d > 0 and z[i] >= 0) or (d < 0 and z[i] <= 0)):
                pos["exit_next"] = True
            elif pos["mode"] == TREND:  # chandelier ratchet off the closed bar
                cand = (h[i] - trail_atr * a[i]) if d > 0 else (l[i] + trail_atr * a[i])
                pos["stop"] = max(pos["stop"], cand) if d > 0 else min(pos["stop"], cand)
            if pos is not None and pos.get("exit_next"):
                d = pos["d"]; fill = o[i + 1] - d * slip
                tr.append(dict(pnl=d * (fill - pos["e"]), bar=pos["bar"], mode=pos["mode"],
                               d=d, why="state")); pos = None

        # --- fill a pending entry at the open of bar i+1 ---------------------
        if pos is None and pend is not None:
            d, mode = pend
            e = o[i + 1] + d * slip
            st = e - d * (trail_atr if mode == TREND else rev_stop_atr) * a[i]
            pos = dict(d=d, e=e, stop=st, bar=i + 1, mode=mode)
            pend = None

        # --- generate a signal from the closed bar i -------------------------
        pend = None
        if pos is None and np.isfinite(a[i]) and a[i] > 0:
            mode = reg[i]
            if mode == TREND and allow_trend and np.isfinite(don_hi[i]):
                if c[i] > don_hi[i]: pend = (1, TREND)
                elif c[i] < don_lo[i]: pend = (-1, TREND)
            elif mode == REVERT and allow_revert and np.isfinite(z[i]):
                if z[i] <= -entry_z: pend = (1, REVERT)
                elif z[i] >= entry_z: pend = (-1, REVERT)
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
            out["is_pf"] = stats(t[dt < cut])["pf"]; out["oos_pf"] = stats(t[dt >= cut])["pf"]
    return out
