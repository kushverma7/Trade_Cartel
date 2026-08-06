"""
The 30-Minute Breakout + LWMA 21 system from the playbook, measured on US30.

RULE, TAKEN VERBATIM FROM THE PLAYBOOK
  Market   US30, US session only, 09:30-16:00 ET.
  Entry    price breaks the 30-minute opening range (09:30-10:00 ET) high/low
           AND closes above/below LWMA 21 in the breakout direction
           AND LWMA slope > 8 points over 5 bars
           AND distance from LWMA > 20 points.
  Exit     stop 1.5 x ATR(14), target 3 x ATR(14).

DECISIONS THE PLAYBOOK LEAVES OPEN, AND HOW THEY ARE RESOLVED
  Entry timeframe is not stated. 15-minute bars are used -- the only US30
  resolution available here -- so the 30-minute opening range is the first TWO
  bars of the session and entries are evaluated from the third bar onward.
  Whether "breaks" means a close or a wick is stated in the playbook's own
  checklist ("a genuine close beyond the 30-min range, not a wick"), so a CLOSE
  is required.
  One entry per side per day is assumed; without that the rule re-fires on
  every bar that remains beyond the range.

INTEGRITY DISCIPLINE (same gate the AU200 work had to pass)
  - Every condition is evaluated on the CLOSED 15m bar; the fill is the NEXT
    bar's open. No same-bar-close entries.
  - Stop fills are gap-aware: min(stop, open) long / max(stop, open) short.
  - A bar that touches BOTH the stop and the target resolves to the STOP. With
    only 15m data the intrabar path is unknown, and this is the pessimistic
    reading. The frequency of those ambiguous bars is reported, because it
    bounds how much the result depends on the assumption.
  - Slippage swept 0 / 1 / 2 / 3 points per side; 1.0 is the floor for any
    headline claim.
"""
import numpy as np, pandas as pd

NY = "America/New_York"
COMM = 0.0          # Trade Nation CFDs are spread-only; cost is carried in slippage


def load_us30(path="data/us30_15m_native.csv.gz"):
    d = pd.read_csv(path)
    d.columns = [c.lower() for c in d.columns]
    t = pd.to_datetime(d[d.columns[0]], utc=True)
    d = d.drop(columns=[d.columns[0]])
    d.index = t.dt.tz_convert(NY)
    return d[["open", "high", "low", "close"]].sort_index()


def lwma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return pd.Series(x).rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True).to_numpy()


def atr(df, n=14):
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def build(df, lwma_len=21, slope_pts=8.0, slope_bars=5, dist_pts=20.0):
    """Signals, opening range and the filter components, all closed-bar."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    idx = df.index
    mins = idx.hour * 60 + idx.minute
    day = pd.Series(idx.normalize(), index=idx)
    in_sess = (mins >= 570) & (mins < 960)              # 09:30 - 16:00 ET
    in_or = (mins >= 570) & (mins < 600)                # 09:30 - 10:00 ET

    orh = pd.Series(np.where(in_or, h, np.nan), index=idx).groupby(day).cummax()
    orl = pd.Series(np.where(in_or, l, np.nan), index=idx).groupby(day).cummin()
    orh = orh.groupby(day).ffill().to_numpy()
    orl = orl.groupby(day).ffill().to_numpy()

    m = lwma(c, lwma_len)
    slope = m - np.r_[np.full(slope_bars, np.nan), m[:-slope_bars]]
    dist = c - m

    okL = (c > orh) & (c > m) & (slope > slope_pts) & (dist > dist_pts)
    okS = (c < orl) & (c < m) & (slope < -slope_pts) & (dist < -dist_pts)
    live = in_sess & ~in_or                             # entries only after the OR completes
    return (np.nan_to_num(okL & live, nan=0).astype(bool),
            np.nan_to_num(okS & live, nan=0).astype(bool),
            orh, orl, m, in_sess, day.to_numpy())


def run(df, sigL, sigS, in_sess, day, a, slip=1.0, sl_mult=1.5, tp_mult=3.0,
        trail_after_r=0.0, one_per_day=True, flat_eod=True):
    """Next-bar-open fills, gap-aware stops, stop-wins-ties."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    n = len(c)
    tr = []; pos = None; taken = {}
    ambiguous = 0
    for i in range(1, n - 1):
        if pos is not None:
            d = pos["d"]
            hit_s = (l[i] <= pos["stop"]) if d > 0 else (h[i] >= pos["stop"])
            hit_t = (h[i] >= pos["tgt"]) if d > 0 else (l[i] <= pos["tgt"])
            if hit_s and hit_t:
                ambiguous += 1
            if hit_s:                                    # STOP WINS TIES
                fill = min(pos["stop"], o[i]) if d > 0 else max(pos["stop"], o[i])
                tr.append(dict(pnl=d * (fill - d * slip - pos["e"]) - COMM,
                               day=pos["day"], hr=pos["hr"], why="stop"))
                pos = None; continue
            if hit_t:
                tr.append(dict(pnl=d * (pos["tgt"] - d * slip - pos["e"]) - COMM,
                               day=pos["day"], hr=pos["hr"], why="target"))
                pos = None; continue
            if trail_after_r > 0:
                pos["pk"] = max(pos["pk"], h[i]) if d > 0 else min(pos["pk"], l[i])
                if (pos["pk"] - pos["e"]) * d >= trail_after_r * pos["risk"]:
                    cand = pos["pk"] - d * pos["risk"]
                    pos["stop"] = max(pos["stop"], cand) if d > 0 else min(pos["stop"], cand)
            if flat_eod and (not in_sess[i] or day[i] != pos["day"]):
                tr.append(dict(pnl=d * (o[i] - d * slip - pos["e"]) - COMM,
                               day=pos["day"], hr=pos["hr"], why="eod"))
                pos = None; continue
        if pos is None and (sigL[i] or sigS[i]):
            d = 1 if sigL[i] else -1
            k = (day[i], d)
            if one_per_day and taken.get(k):
                continue
            e = o[i + 1] + d * slip                      # NEXT bar's open
            risk = sl_mult * a[i]
            pos = dict(d=d, e=e, stop=e - d * risk, tgt=e + d * tp_mult * a[i],
                       risk=risk, pk=e, day=day[i], hr=df.index[i].hour,
                       bar=i + 1)
            taken[k] = True
    return pd.DataFrame(tr), ambiguous


def stats(t):
    if t is None or len(t) == 0:
        return dict(n=0)
    p = t.pnl.to_numpy()
    gw, gl = p[p > 0].sum(), -p[p < 0].sum()
    eq = np.cumsum(p)
    ps = np.sort(p)[::-1]
    return dict(n=len(p), wr=100 * float((p > 0).mean()),
                pf=float(gw / gl) if gl > 0 else np.inf, net=float(p.sum()),
                maxdd=float(np.max(np.maximum.accumulate(eq) - eq)),
                avg=float(p.mean()),
                top10=float(100 * ps[:10].sum() / p.sum()) if p.sum() else np.nan)
