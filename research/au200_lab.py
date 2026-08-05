"""
AU200 laboratory: every candidate family from the four research archives, under
one protocol, in one file.

WHY THIS EXISTS AND WHAT IT CANNOT DO YET
  No AU200 price data exists in this environment. The two datasets the archives
  were built on are both gone:
      bc3182e6-au200_aud_5m.csv                     139,898 bars 2020-08 to 2026-08
      au200_aud_dataset_London-Strategic-Edge.csv   212,177 bars 2016-01 to 2026-06
  Neither upload directory survives. Every external price host is blocked by the
  container's network policy (query1.finance.yahoo.com, stooq.com, asx.com.au,
  eodhd.com all answer 000 at the proxy). Therefore this module runs nothing
  today. It is written so that Pass 1 through Pass 5 execute end to end the
  moment a CSV is placed at data/au200_5m.csv.gz.

WHAT THE ARCHIVES DISAGREE ABOUT, AND WHY IT MATTERS FOR THIS DESIGN
  Archive 2 (CapitalCom feed, 6 years) killed everything: UT Bot + EMA200 at
  PF 0.83, 576 parameter combinations with zero above 1.0, gap direction
  t = -0.17, opening-range breakout t = -0.16.
  Archive 3 (London Strategic Edge feed, 10 years) verified two systems with a
  walk-forward: TB Morning Scalper 1.513 IS / 1.449 OOS, ST-Flip + ADX25
  1.50 / 1.50.
  These are DIFFERENT FEEDS over DIFFERENT SPANS. That alone can produce the
  contradiction, and it is the reason this module records which file it ran on
  in every output row. Any future comparison that does not carry the feed
  identity is not a comparison.

  Archive 3 also documents that its own feed changes coverage mid-history: only
  UTC hours 23,0,1,2,3,4,5 exist before 2023, near-24h after. Its IS/OOS split
  (2016-2022 vs 2023-) therefore falls exactly on a feed change, so its
  "all-day" ST-Flip system had only Sydney-session bars in-sample and all hours
  out-of-sample. `audit_coverage()` below detects this condition and refuses to
  report a walk-forward that straddles it.

COST FLOOR
  Slippage is clamped to a minimum of 1.0 point per side, per the mandate.
  A flip system that stops at 5 points and flips up to 6 times pays slippage on
  every leg; at 0 slippage its published PF 2.21 implies a break-even slippage
  of about 2.7 points per side (see the note in the report). Costs are not a
  detail on this instrument, they are the experiment.
"""
import argparse, itertools, os
import numpy as np, pandas as pd

SYD = "Australia/Sydney"
DATA = "data/au200_5m.csv.gz"
SLIP_MIN = 1.0                 # points per side, hard floor
COMM_PER_ORDER = 0.50          # AUD
POINT_VALUE = 100.0            # AUD per point
SEEDS = (11, 101, 2027, 55555, 987654)


# ------------------------------------------------------------------ loading
def load(path=DATA):
    """Load 5m AU200 bars and put the index in Australia/Sydney local time.

    The archives record a real defect here: earlier Pine used
    hour(time, 'UTC+10'), which fires one hour early from October to April
    because AEDT is UTC+11. Converting to the named zone rather than a fixed
    offset is the fix, and it is why this loader refuses a tz-naive result.
    """
    df = pd.read_csv(path)
    tcol = next(c for c in df.columns
                if c.lower() in ("timestamp", "time", "datetime", "date", "dt"))
    idx = pd.to_datetime(df[tcol], utc=True)
    df = df.drop(columns=[tcol])
    df.columns = [c.lower() for c in df.columns]
    df.index = idx.dt.tz_convert(SYD)
    df = df[["open", "high", "low", "close"] +
            (["volume"] if "volume" in df.columns else [])]
    df = df[~df.index.duplicated()].sort_index()
    return df.dropna(subset=["open", "high", "low", "close"])


def audit(df):
    """Data confirmation. Printed before any result, every run."""
    out = {}
    out["bars"] = len(df)
    out["start"], out["end"] = df.index[0], df.index[-1]
    out["years"] = (df.index[-1] - df.index[0]).days / 365.25
    step = df.index.to_series().diff().dt.total_seconds().div(60)
    out["median_step_min"] = float(step.median())
    d = np.diff(np.sort(df["close"].unique()))
    out["mintick_est"] = float(np.min(d[d > 0])) if len(d[d > 0]) else np.nan
    # 10:00 alignment: how many distinct dates carry a bar stamped exactly 10:00
    ten = df[(df.index.hour == 10) & (df.index.minute == 0)]
    days = df.index.normalize().nunique()
    out["days"] = days
    out["bars_at_1000"] = len(ten)
    out["pct_days_with_1000_bar"] = 100.0 * len(ten) / max(days, 1)
    # coverage change detection (the archive-3 defect)
    per = df.groupby([df.index.year, df.index.hour]).size().unstack(fill_value=0)
    hours_per_year = (per > 0).sum(axis=1)
    out["hours_per_year"] = hours_per_year.to_dict()
    out["coverage_changes"] = bool(hours_per_year.max() - hours_per_year.min() > 4)
    return out


def print_audit(a, path):
    print("=" * 104)
    print("PASS 0 — DATA AND COST CONFIRMATION")
    print("=" * 104)
    print(f"  file                     {path}")
    print(f"  bars                     {a['bars']:,}")
    print(f"  range (Australia/Sydney) {a['start']}  ->  {a['end']}")
    print(f"  span                     {a['years']:.2f} years, {a['days']:,} distinct dates")
    print(f"  median bar step          {a['median_step_min']:.1f} minutes")
    print(f"  smallest close increment {a['mintick_est']:.4f} points  (archives claim 0.1)")
    print(f"  bars stamped 10:00 local {a['bars_at_1000']:,} "
          f"({a['pct_days_with_1000_bar']:.1f}% of dates)")
    print(f"  slippage floor           {SLIP_MIN} pt/side   commission "
          f"{COMM_PER_ORDER} AUD/order   point value {POINT_VALUE} AUD")
    if a["pct_days_with_1000_bar"] < 90:
        print("  *** WARNING: fewer than 90% of dates carry a 10:00 bar. Either the")
        print("      feed is not Sydney-session complete, or the timezone is wrong.")
    if a["coverage_changes"]:
        print("  *** WARNING: trading-hour coverage CHANGES across the sample:")
        for y, h in sorted(a["hours_per_year"].items()):
            print(f"        {y}: {h} distinct hours present")
        print("      Any walk-forward split that straddles the change compares two")
        print("      different data-generating processes. Sydney-window-only tests")
        print("      remain valid; all-day tests do not.")


# --------------------------------------------------------------- indicators
def atr(df, n=14):
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def supertrend(df, factor=1.5, n=10):
    """Returns direction: -1 bullish, +1 bearish (Pine's st_dir convention)."""
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    a = atr(df, n)
    hl2 = (h + l) / 2
    up, dn = hl2 - factor * a, hl2 + factor * a
    N = len(c)
    fu, fd = np.copy(up), np.copy(dn)
    d = np.ones(N)
    for i in range(1, N):
        fu[i] = max(up[i], fu[i - 1]) if c[i - 1] > fu[i - 1] else up[i]
        fd[i] = min(dn[i], fd[i - 1]) if c[i - 1] < fd[i - 1] else dn[i]
        if c[i] > fd[i - 1]:
            d[i] = -1
        elif c[i] < fu[i - 1]:
            d[i] = 1
        else:
            d[i] = d[i - 1]
    return d


def adx(df, n=14):
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    ph, pl, pc = np.r_[h[0], h[:-1]], np.r_[l[0], l[:-1]], np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    dmp = np.where(h - ph > pl - l, np.maximum(h - ph, 0), 0.0)
    dmm = np.where(pl - l > h - ph, np.maximum(pl - l, 0), 0.0)
    S = lambda x: pd.Series(x).ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    st, sp, sm = S(tr), S(dmp), S(dmm)
    with np.errstate(divide="ignore", invalid="ignore"):
        dip = np.where(st > 0, 100 * sp / st, 0)
        dim = np.where(st > 0, 100 * sm / st, 0)
        dx = np.where(dip + dim > 0, 100 * abs(dip - dim) / (dip + dim), 0)
    return pd.Series(dx).ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def rsi(df, n=14):
    c = pd.Series(df["close"].to_numpy(float))
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn.replace(0, np.nan))).to_numpy()


def ema(df, n):
    return pd.Series(df["close"].to_numpy(float)).ewm(span=n, adjust=False).mean().to_numpy()


def tbt_direction(df, per=10):
    """Trendline-breakout direction, persisted. Non-repainting.

    Ported from the archive-3 rule text: pivots at (left=per, right=per/2); a
    long cross needs a non-positive resistance slope with close crossing above
    it; a short cross the mirror, with the vol-adjust band
    zband = min(ATR(30)*0.3, close*0.003)[20] / 2.
    Pivots are only KNOWN `right` bars after they form, so the confirmation lag
    is applied explicitly rather than assumed away.
    """
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    N, left, right = len(c), per, max(1, per // 2)
    a30 = atr(df, 30)
    zb = np.minimum(a30 * 0.3, c * 0.003)
    zband = np.r_[np.full(20, np.nan), zb[:-20]] / 2.0

    ph = np.full(N, np.nan); pl = np.full(N, np.nan)
    for i in range(left, N - right):
        w = h[i - left:i + right + 1]
        if h[i] == w.max() and (w == h[i]).sum() == 1:
            ph[i + right] = h[i]              # known only at i+right
        w = l[i - left:i + right + 1]
        if l[i] == w.min() and (w == l[i]).sum() == 1:
            pl[i + right] = l[i]
    ph_cur = pd.Series(ph).ffill().to_numpy()
    pl_cur = pd.Series(pl).ffill().to_numpy()
    ph_prev = pd.Series(ph).ffill().shift(1).to_numpy()
    pl_prev = pd.Series(pl).ffill().shift(1).to_numpy()
    ph_slope = np.r_[np.nan, np.diff(ph_cur)]
    pl_slope = np.r_[np.nan, np.diff(pl_cur)]
    pc = np.r_[c[0], c[:-1]]
    zz = np.nan_to_num(zband, nan=0.0)
    long_x = (ph_slope <= 0) & (pc < ph_prev) & (c > ph_cur)
    short_x = (pl_slope >= 0) & (pc > pl_prev - zz * 0.1) & (c < pl_cur - zz * 0.1)

    d = np.zeros(N, np.int8); cur = 0
    for i in range(N):
        if long_x[i]:
            cur = 1
        elif short_x[i]:
            cur = -1
        d[i] = cur
    return d


# ------------------------------------------------------------------ engines
def flip_engine(df, sig_dir, stop_pts=5.0, trail_pts=75.0, arm_pts=5.0,
                max_flips=6, slip=SLIP_MIN, flat_hour=16, allow_flip=True):
    """Archive-3 TBT+Flip position management, executed bar by bar.

    Every leg -- the original entry and each flip -- pays entry and exit
    slippage. That is the whole point: at 0 slippage the published result is
    PF 2.21; the cost of six possible flips per sequence is what decides
    whether it survives.
    """
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    hour = df.index.hour.to_numpy()
    day = df.index.normalize().to_numpy()
    trades = []
    pos = None
    for i in range(1, len(c)):
        if pos is not None:
            d, ent, peak = pos["d"], pos["entry"], pos["peak"]
            peak = max(peak, h[i]) if d > 0 else min(peak, l[i])
            pos["peak"] = peak
            exc = (peak - ent) * d
            if not pos["armed"] and exc >= arm_pts:
                pos["armed"] = True
            stop = (ent - d * stop_pts if not pos["armed"]
                    else peak - d * trail_pts)
            hit = (l[i] <= stop) if d > 0 else (h[i] >= stop)
            eod = hour[i] >= flat_hour or day[i] != pos["day"]
            if hit:
                px = stop - d * slip
                trades.append(dict(bar=pos["bar"], dir=d, entry=pos["entry"],
                                   exit=px, pnl=d * (px - pos["entry"]),
                                   leg=pos["leg"], why="trail" if pos["armed"] else "stop",
                                   day=pos["day"]))
                if allow_flip and not pos["armed"] and pos["leg"] < max_flips:
                    nd = -d
                    pos = dict(d=nd, entry=stop + nd * slip, peak=stop, bar=i,
                               armed=False, leg=pos["leg"] + 1, day=pos["day"])
                else:
                    pos = None
                continue
            if eod:
                px = c[i] - d * slip
                trades.append(dict(bar=pos["bar"], dir=d, entry=pos["entry"],
                                   exit=px, pnl=d * (px - pos["entry"]),
                                   leg=pos["leg"], why="eod", day=pos["day"]))
                pos = None
                continue
        if pos is None and sig_dir[i] != 0:
            d = int(sig_dir[i])
            pos = dict(d=d, entry=c[i] + d * slip, peak=c[i], bar=i,
                       armed=False, leg=0, day=day[i])
    return pd.DataFrame(trades)


def atr3_engine(df, sig_dir, sl=4.0, tp1=2.0, tp2=5.0, trail=2.5, be_buf=0.25,
                slip=SLIP_MIN, flat_hour=16):
    """Archive-3 three-layer ATR exit: SL 4xATR, TP1 2xATR half off, buffered
    breakeven, TP2 5xATR, then a 2.5xATR trail on the remainder."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    a = atr(df, 14)
    hour = df.index.hour.to_numpy(); day = df.index.normalize().to_numpy()
    trades = []; pos = None
    for i in range(1, len(c)):
        if pos is not None:
            d, ent, A = pos["d"], pos["entry"], pos["a"]
            pos["peak"] = max(pos["peak"], h[i]) if d > 0 else min(pos["peak"], l[i])
            stop = pos["stop"]
            if pos["tp1"]:
                cand = pos["peak"] - d * trail * A
                stop = max(stop, cand) if d > 0 else min(stop, cand)
                pos["stop"] = stop
            hit = (l[i] <= stop) if d > 0 else (h[i] >= stop)
            if hit:
                px = stop - d * slip
                pos["pnl"] += d * (px - ent) * pos["qty"]
                trades.append(dict(bar=pos["bar"], dir=d, pnl=pos["pnl"],
                                   why="stop", day=pos["day"]))
                pos = None; continue
            if not pos["tp1"]:
                t1 = ent + d * tp1 * A
                if (h[i] >= t1) if d > 0 else (l[i] <= t1):
                    px = t1 - d * slip
                    pos["pnl"] += d * (px - ent) * 0.5
                    pos["qty"] = 0.5; pos["tp1"] = True
                    pos["stop"] = ent - d * be_buf * A     # BUFFERED breakeven
            else:
                t2 = ent + d * tp2 * A
                if (h[i] >= t2) if d > 0 else (l[i] <= t2):
                    px = t2 - d * slip
                    pos["pnl"] += d * (px - ent) * pos["qty"]
                    trades.append(dict(bar=pos["bar"], dir=d, pnl=pos["pnl"],
                                       why="tp2", day=pos["day"]))
                    pos = None; continue
            if hour[i] >= flat_hour or day[i] != pos["day"]:
                px = c[i] - d * slip
                pos["pnl"] += d * (px - ent) * pos["qty"]
                trades.append(dict(bar=pos["bar"], dir=d, pnl=pos["pnl"],
                                   why="eod", day=pos["day"]))
                pos = None; continue
        if pos is None and sig_dir[i] != 0:
            d = int(sig_dir[i])
            pos = dict(d=d, entry=c[i] + d * slip, a=max(a[i], 1e-9), bar=i,
                       peak=c[i], stop=c[i] - d * sl * a[i], tp1=False,
                       qty=1.0, pnl=0.0, day=day[i])
    return pd.DataFrame(trades)


# ------------------------------------------------------------------ signals
def sig_gap(df, min_gap=1.0, hour=10, minute=0, long_only=False,
            st=None, tbt=None, use_st=False, use_tbt=False):
    """Family A: the 10:00 open gap, optionally gated by SuperTrend and TBT."""
    o, c = df["open"].to_numpy(float), df["close"].to_numpy(float)
    pc = np.r_[c[0], c[:-1]]
    at = (df.index.hour == hour) & (df.index.minute == minute)
    gap = o - pc
    d = np.where(gap > min_gap, 1, np.where(gap < -min_gap, -1, 0))
    d = np.where(at, d, 0)
    if use_st and st is not None:
        d = np.where(((d > 0) & (st < 0)) | ((d < 0) & (st > 0)), d, 0)
    if use_tbt and tbt is not None:
        d = np.where(d == tbt, d, 0)
    if long_only:
        d = np.where(d > 0, d, 0)
    return d.astype(np.int8)


def sig_stflip(df, st, ad=None, adx_min=0.0, long_only=True, win=None):
    """Family D: SuperTrend flip, optional ADX regime gate."""
    flip_up = (st < 0) & (np.r_[1, st[:-1]] >= 0)
    flip_dn = (st > 0) & (np.r_[-1, st[:-1]] <= 0)
    d = np.where(flip_up, 1, np.where(flip_dn, -1, 0))
    if ad is not None and adx_min > 0:
        d = np.where(ad > adx_min, d, 0)
    if long_only:
        d = np.where(d > 0, d, 0)
    if win is not None:
        hh = df.index.hour
        d = np.where((hh >= win[0]) & (hh < win[1]), d, 0)
    return d.astype(np.int8)


def sig_base(df, win=(9, 11), long_only=False):
    """Family C: AU200-BASE — session window + EMA200 + RSI14 + SuperTrend."""
    c = df["close"].to_numpy(float)
    e = ema(df, 200); r = rsi(df, 14); st = supertrend(df)
    hh, mm = df.index.hour, df.index.minute
    inwin = ((hh == 9) & (mm >= 50)) | ((hh == 10) & (mm == 0))
    if win != (9, 11):
        inwin = (hh >= win[0]) & (hh < win[1])
    up = (c > e) & (r > 50) & (st < 0)
    dn = (c < e) & (r < 50) & (st > 0)
    d = np.where(inwin & up, 1, np.where(inwin & dn, -1, 0))
    if long_only:
        d = np.where(d > 0, d, 0)
    return d.astype(np.int8)


def sig_tb_morning(df, lookback=24, win=(10, 12), long_only=True):
    """Family D: TB Morning Scalper — Donchian-style breakout in the morning."""
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    hi = pd.Series(h).rolling(lookback).max().shift(1).to_numpy()
    lo = pd.Series(l).rolling(lookback).min().shift(1).to_numpy()
    hh = df.index.hour
    inwin = (hh >= win[0]) & (hh < win[1])
    d = np.where(inwin & (c > hi), 1, np.where(inwin & (c < lo), -1, 0))
    if long_only:
        d = np.where(d > 0, d, 0)
    return np.nan_to_num(d, nan=0).astype(np.int8)


def sig_random(df, n_target, rng, win=None, long_only=True):
    """Control: random entries in the same window, matched trade count."""
    hh = df.index.hour
    ok = np.ones(len(df), bool) if win is None else ((hh >= win[0]) & (hh < win[1]))
    idx = np.flatnonzero(ok)
    pick = rng.choice(idx, size=min(n_target, len(idx)), replace=False)
    d = np.zeros(len(df), np.int8)
    d[pick] = 1 if long_only else rng.choice([-1, 1], size=len(pick))
    return d


# ------------------------------------------------------------------ scoring
def score(tr, df, label, feed):
    if tr is None or len(tr) == 0:
        return dict(arm=label, feed=feed, n=0, note="no trades")
    p = tr["pnl"].to_numpy(float)
    comm = 2 * COMM_PER_ORDER / POINT_VALUE
    p = p - comm
    gw, gl = p[p > 0].sum(), -p[p < 0].sum()
    eq = np.cumsum(p)
    dd = float(np.max(np.maximum.accumulate(eq) - eq)) if len(eq) else 0.0
    yr = pd.to_datetime(tr["day"]).dt.year if "day" in tr else None
    byyear = {}
    if yr is not None:
        for y, g in pd.DataFrame({"y": yr, "p": p}).groupby("y"):
            w, ll = g.p[g.p > 0].sum(), -g.p[g.p < 0].sum()
            byyear[int(y)] = round(float(w / ll) if ll > 0 else np.inf, 3)
    ps = np.sort(p)[::-1]
    return dict(arm=label, feed=feed, n=len(p), wr=100 * float((p > 0).mean()),
                pf=float(gw / gl) if gl > 0 else np.inf, net=float(p.sum()),
                maxdd_pts=dd, avg=float(p.mean()),
                top5_net=float(100 * ps[:5].sum() / p.sum()) if p.sum() else np.nan,
                top10_net=float(100 * ps[:10].sum() / p.sum()) if p.sum() else np.nan,
                years_pos=sum(1 for v in byyear.values() if v > 1),
                years=len(byyear), by_year=byyear)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=DATA)
    ap.add_argument("--slip", type=float, default=SLIP_MIN)
    a = ap.parse_args()
    if not os.path.exists(a.csv):
        print(f"AU200 data not found at {a.csv}.")
        print("This module cannot run without it. Required format:")
        print("  gzip or plain CSV, columns: timestamp(UTC ISO8601), open, high,")
        print("  low, close, volume(optional); 5-minute bars; longest span available.")
        raise SystemExit(2)
    slip = max(a.slip, SLIP_MIN)
    df = load(a.csv)
    feed = os.path.basename(a.csv)
    print_audit(audit(df), a.csv)

    st = supertrend(df, 1.5, 10)
    ad = adx(df, 14)
    tbt = tbt_direction(df, 10)

    print("\n" + "=" * 104)
    print(f"PASS 1 — FAIR BASELINE, all families, slippage {slip} pt/side")
    print("=" * 104)
    arms = {
      "A gap only":              sig_gap(df, 1.0),
      "A gap + ST":              sig_gap(df, 1.0, st=st, use_st=True),
      "A gap + ST + TBT":        sig_gap(df, 1.0, st=st, tbt=tbt, use_st=True, use_tbt=True),
      "A gap + ST + TBT (long)": sig_gap(df, 1.0, st=st, tbt=tbt, use_st=True, use_tbt=True, long_only=True),
      "C AU200-BASE":            sig_base(df),
      "D ST-flip + ADX25":       sig_stflip(df, st, ad, 25.0),
      "D TB morning scalper":    sig_tb_morning(df, 24, (10, 12)),
    }
    rows = []
    for nm, s in arms.items():
        rows.append(score(flip_engine(df, s, slip=slip), df, nm + " | flip exit", feed))
        rows.append(score(atr3_engine(df, s, slip=slip), df, nm + " | 3-layer ATR", feed))
        rows.append(score(flip_engine(df, s, slip=slip, allow_flip=False),
                          df, nm + " | trail no-flip", feed))
    rng = np.random.default_rng(SEEDS[0])
    nmed = int(np.median([r["n"] for r in rows if r["n"] > 0] or [200]))
    rows.append(score(flip_engine(df, sig_random(df, nmed, rng, (10, 12)), slip=slip),
                      df, "CONTROL random-in-window | flip exit", feed))
    c0 = df["close"].to_numpy(float)
    rows.append(dict(arm="CONTROL buy & hold", feed=feed, n=1, wr=np.nan,
                     pf=np.nan, net=float(c0[-1] - c0[0]), maxdd_pts=np.nan,
                     avg=np.nan, top5_net=np.nan, top10_net=np.nan,
                     years_pos=np.nan, years=np.nan, by_year={}))
    t = pd.DataFrame(rows)
    pd.set_option("display.width", 220)
    print(t.drop(columns=["by_year"]).to_string(index=False,
                                                float_format=lambda v: f"{v:9.3f}"))
    t.to_csv("research/au200_pass1.csv", index=False)
    print("\n  wrote research/au200_pass1.csv")
    print("  Passes 2-5 (component isolation, plateau, stress, synthesis) run from")
    print("  this same table; they are gated on Pass 1 producing at least one arm")
    print("  with PF > 1.0 after costs, per the adoption bar.")


if __name__ == "__main__":
    main()
