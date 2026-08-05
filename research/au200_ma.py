"""
AU200 moving-average family, under the identical protocol used for AU200-BASE.

PROTOCOL PARITY (stated so the comparison is legitimate)
  Data      data/au200_15m.csv.gz (47,283 native 15m bars) for SIGNALS,
            data/au200_5m.csv.gz (139,898 bars) for the EXIT PATH.
            Both 2020-08-05 -> 2026-08-04, Australia/Sydney.
  Costs     commission 1.0 AUD/contract/side (2.0 per round turn, as the user's
            Pine sets it) and slippage swept at 0 / 1.0 / 1.5 / 2.0 pt per side.
            1.0 pt is the floor for any headline claim.
  Path      Stops and trails are walked on the 5-MINUTE series. This is the
            discipline that broke AU200-BASE: its 0.5-pt trail lost 78% of its
            profit when the path was resolved 3x finer. Per the brief, no
            sub-point trails are used here -- the narrowest is 10 points.
  Direction The cross itself is a 15m close event, so it is resolution-
            independent; only the stop/trail arms need the finer path.

WHY THE CROSS STATE IS FORWARD-FILLED ONTO THE 5m GRID
  A dual-MA system is always in a state, not just at cross bars. Building a
  target-direction series on the 15m bars and forward-filling it to 5m lets the
  engine reverse exactly when the 15m bar that produced the cross CLOSES -- never
  earlier. Reading the 5m bars to anticipate a 15m cross would be lookahead.
"""
import numpy as np, pandas as pd
from research.au200_lab import load

COMM = 1.0                      # AUD per contract per side
SLIPS = (0.0, 1.0, 1.5, 2.0)
PAIRS = ((5, 20), (8, 21), (10, 30), (20, 50), (50, 200))


def sma(x, n): return pd.Series(x).rolling(n).mean().to_numpy()
def ema(x, n): return pd.Series(x).ewm(span=n, adjust=False).mean().to_numpy()
MA = {"SMA": sma, "EMA": ema}


def atr(df, n=14):
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def cross_state(d15, fast, slow, ftype="EMA", stype=None, long_only=False,
                win=None, trend=None, rising=False):
    """Target direction per 15m bar: +1 long, -1 short, 0 flat.

    `win` restricts NEW entries to a local-time window but never blocks an exit;
    a system that can enter but not leave is not a system.
    """
    c = d15["close"].to_numpy(float)
    stype = stype or ftype
    f, s = MA[ftype](c, fast), MA[stype](c, slow)
    d = np.where(f > s, 1, np.where(f < s, -1, 0)).astype(np.int8)
    if trend is not None:
        tf, tn = trend
        t = MA[tf](c, tn)
        d = np.where((d > 0) & (c <= t), 0, d)
        d = np.where((d < 0) & (c >= t), 0, d)
    if rising:
        d = np.where((d > 0) & (s <= np.r_[np.nan, s[:-1]]), 0, d)
        d = np.where((d < 0) & (s >= np.r_[np.nan, s[:-1]]), 0, d)
    if long_only:
        d = np.where(d > 0, d, 0)
    d = np.where(np.isfinite(f) & np.isfinite(s), d, 0).astype(np.int8)
    if win is not None:
        hh = d15.index.hour.to_numpy(); mm = d15.index.minute.to_numpy()
        t = hh * 60 + mm
        ok = (t >= win[0]) & (t < win[1])
        # entries only inside the window; an existing state may persist out of it
        out = np.zeros_like(d); cur = 0
        for i in range(len(d)):
            if d[i] != cur:
                if d[i] == 0 or ok[i]:
                    cur = d[i]
            out[i] = cur
        d = out
    return pd.Series(d, index=d15.index)


def run(state15, d5, slip=1.0, stop_pts=0.0, stop_atr=0.0, trail_pts=0.0,
        arm_pts=0.0, flat_hour=0, a5=None):
    """Walk the 5m path. Exit on opposite state, and optionally on a stop or a
    wide trail. Every fill pays slippage against the trade."""
    o, h, l, c = (d5[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    # BUG, found 2026-08-05. The 15m index stamp is the bar's OPEN time, so a
    # state derived from that bar's CLOSE is only known at stamp + 15 minutes.
    # Forward-filling from the stamp itself applied the state to the three 5m
    # bars INSIDE the still-forming 15m bar -- up to 10 minutes of lookahead on
    # every signal. Shifting the state index forward by one full 15m bar makes
    # it available exactly when it becomes knowable, and not before.
    st_shift = state15.copy()
    st_shift.index = st_shift.index + pd.Timedelta(minutes=15)
    tgt = st_shift.reindex(d5.index, method="ffill").fillna(0).to_numpy().astype(np.int8)
    hh = d5.index.hour.to_numpy(); day = d5.index.normalize().to_numpy()
    tr = []; pos = None
    for i in range(1, len(c)):
        if pos is not None:
            d, e = pos["d"], pos["e"]
            pos["pk"] = max(pos["pk"], h[i]) if d > 0 else min(pos["pk"], l[i])
            stop = pos["stop"]
            if trail_pts > 0:
                if not pos["armed"] and (pos["pk"] - e) * d >= arm_pts:
                    pos["armed"] = True
                if pos["armed"]:
                    cand = pos["pk"] - d * trail_pts
                    stop = max(stop, cand) if d > 0 else min(stop, cand)
                    pos["stop"] = stop
            if np.isfinite(stop) and ((l[i] <= stop) if d > 0 else (h[i] >= stop)):
                # GAP-AWARE STOP FILL. Filling at the stop price assumes the
                # level was crossed DURING the bar. If the bar OPENED beyond it
                # the level was never available and the real fill is the open.
                # Without this the engine flatters every loss, which showed up
                # as a +0.15 PF bias on a return-shuffled null where the true
                # value is 1.0.
                fill = min(stop, o[i]) if d > 0 else max(stop, o[i])
                px = fill - d * slip
                tr.append(dict(pnl=d * (px - e) - 2 * COMM, day=pos["day"], why="stop"))
                pos = None
            elif tgt[i] != d:
                px = o[i] - d * slip
                tr.append(dict(pnl=d * (px - e) - 2 * COMM, day=pos["day"], why="cross"))
                pos = None
            elif flat_hour and (hh[i] >= flat_hour or day[i] != pos["day"]):
                px = c[i] - d * slip
                tr.append(dict(pnl=d * (px - e) - 2 * COMM, day=pos["day"], why="eod"))
                pos = None
        if pos is None and tgt[i] != 0:
            d = int(tgt[i])
            st = np.nan
            if stop_pts > 0:
                st = o[i] - d * stop_pts
            elif stop_atr > 0 and a5 is not None:
                st = o[i] - d * stop_atr * a5[i]
            # FILL FIDELITY: the state becomes knowable at the 15m bar's close,
            # which is exactly the OPEN of this 5m bar. Filling at this bar's
            # open reproduces process_orders_on_close; filling at its close
            # would penalise the system by a further 5 minutes it never waited.
            pos = dict(d=d, e=o[i] + d * slip, pk=o[i], stop=st,
                       armed=False, day=day[i])
    return pd.DataFrame(tr)


def stat(t, label, extra=None):
    if t is None or len(t) == 0:
        return dict(arm=label, n=0, pf=np.nan, net=np.nan)
    p = t.pnl.to_numpy()
    gw, gl = p[p > 0].sum(), -p[p < 0].sum()
    eq = np.cumsum(p)
    dd = float(np.max(np.maximum.accumulate(eq) - eq))
    ps = np.sort(p)[::-1]
    tot = p.sum()
    r = dict(arm=label, n=len(p), wr=100 * float((p > 0).mean()),
             pf=float(gw / gl) if gl > 0 else np.inf, net=float(tot),
             maxdd=dd, top10=float(100 * ps[:10].sum() / tot) if tot else np.nan)
    if "day" in t:
        y = pd.to_datetime(t["day"]).dt.year
        for yy, g in pd.DataFrame({"y": y, "p": p}).groupby("y"):
            w, ll = g.p[g.p > 0].sum(), -g.p[g.p < 0].sum()
            r[f"pf{int(yy)}"] = round(float(w / ll) if ll > 0 else np.inf, 2)
    if extra:
        r.update(extra)
    return r
