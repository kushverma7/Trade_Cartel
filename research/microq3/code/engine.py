"""Micro-Q3 execution engine. Signals from completed candles, fills from raw ticks.

EXECUTION CONVENTION (fixed, never varied by any experiment):
  long  enters at the ASK, and its stop/target/EOD are resolved on the BID
  short enters at the BID, and its stop/target/EOD are resolved on the ASK
The round-trip spread is therefore paid at whatever it actually was on the day.
There is no fixed-cost input anywhere in this file.

FIRST PASSAGE, NOT BAR LOGIC. Once an entry exists, stop and target are resolved
by walking the real quote sequence in chronological order and taking whichever
executable price is reached first. Running extremes are monotone, so the first
crossing of either level is found by two searchsorted calls -- exact, not an
approximation, and with no same-bar ambiguity to resolve.

LOOK-AHEAD. A break is actionable only after its 5-minute candle has completed.
The entry tick is the first tick STRICTLY AFTER the candle's closing timestamp,
found by searchsorted(..., side='right'). Candle construction and the filters
that use the entry price are therefore separated in time by construction.
"""
import os, numpy as np, pandas as pd

PTS = 1000.0
# MICROQ3_DATA lets the SAME engine be pointed at the holdout year. Default is
# unchanged, so every result produced before this switch existed is unaffected.
# The frozen specification must run on one engine or the comparison is void.
D = os.environ.get("MICROQ3_DATA", "research/microq3/data")
NY = np.load(f"{D}/ny_ms.npy")
BID = np.load(f"{D}/bid_i.npy")
ASK = np.load(f"{D}/ask_i.npy")
MID = (BID.astype(np.int64) + ASK.astype(np.int64)) // 2
B1 = pd.read_parquet(f"{D}/bars_1m_ny.parquet")

MIN = B1["minute"].to_numpy()
DAY = MIN // 1440                      # NY calendar day number
HM = MIN % 1440                        # minutes past NY midnight
I0 = B1["i0"].to_numpy(); I1 = B1["i1"].to_numpy()
OHLC = {k: B1[f"{k}_{p}"].to_numpy() for k in ("mid", "bid", "ask") for p in "ohlc"
        for k, p in [(k, p)]}
O = {k: B1[f"{k}_o"].to_numpy() for k in ("mid", "bid", "ask")}
H = {k: B1[f"{k}_h"].to_numpy() for k in ("mid", "bid", "ask")}
L = {k: B1[f"{k}_l"].to_numpy() for k in ("mid", "bid", "ask")}
C = {k: B1[f"{k}_c"].to_numpy() for k in ("mid", "bid", "ask")}

DAYS = np.unique(DAY)
_day_lo = np.searchsorted(DAY, DAYS, "left")
_day_hi = np.searchsorted(DAY, DAYS, "right")
DAYSLICE = {int(d): (int(a), int(b)) for d, a, b in zip(DAYS, _day_lo, _day_hi)}


def window(day, hm_start, hm_end):
    """Row indices of the 1-minute bars with hm_start <= HM < hm_end on `day`."""
    a, b = DAYSLICE.get(day, (0, 0))
    if b <= a:
        return None
    h = HM[a:b]
    m = (h >= hm_start) & (h < hm_end)
    if not m.any():
        return None
    k = np.flatnonzero(m) + a
    return k


def candle(day, hm_start, hm_end, px="mid"):
    """-> dict(o,h,l,c,i0,i1,t_close_ms) built from 1-minute bars, or None."""
    k = window(day, hm_start, hm_end)
    if k is None:
        return None
    return dict(o=int(O[px][k[0]]), c=int(C[px][k[-1]]),
                h=int(H[px][k].max()), l=int(L[px][k].min()),
                i0=int(I0[k[0]]), i1=int(I1[k[-1]]),
                t_close=int(NY[int(I1[k[-1]]) - 1]), nmin=len(k))


def five_min_candles(day, hm_from, hm_to, px="mid"):
    """Completed 5-minute candles fully inside [hm_from, hm_to). -> list of dicts."""
    out = []
    for s in range(hm_from, hm_to, 5):
        c = candle(day, s, s + 5, px)
        if c is not None:
            c["hm_start"], c["hm_end"] = s, s + 5
            out.append(c)
    return out


def session_end_index(day, end_hm=17 * 60, max_days=3):
    """Tick index of the first tick at/after `end_hm` NY on the next calendar day
    that has data -- gold's 17:00 NY settlement stop. Falls back to the last tick
    of the last available day."""
    for k in range(1, max_days + 1):
        a, b = DAYSLICE.get(day + k, (0, 0))
        if b <= a:
            continue
        h = HM[a:b]
        j = np.flatnonzero(h >= end_hm)
        if len(j):
            return int(I0[a + int(j[0])])
        return int(I1[b - 1])
    a, b = DAYSLICE.get(day, (0, 0))
    return int(I1[b - 1]) if b > a else None


def resolve(k0, kend, long_, sl_pts, tp_pts):
    """Tick-exact first passage from entry tick k0 to kend.

    -> dict(entry, exit, pnl, reason, mfe, mae, t_entry, t_exit, bars)
    MFE/MAE are measured on the SAME side the trade would really exit on, so a
    stop cannot truncate the excursion being reported.
    """
    e = int(ASK[k0]) if long_ else int(BID[k0])
    ex = BID[k0:kend] if long_ else ASK[k0:kend]
    if len(ex) == 0:
        return None
    fav = (ex.astype(np.int64) - e) if long_ else (e - ex.astype(np.int64))
    rmax = np.maximum.accumulate(fav)
    rmin = np.minimum.accumulate(fav)
    n = len(fav)
    tp_i = int(round(tp_pts * PTS)); sl_i = int(round(sl_pts * PTS))
    i_tp = int(np.searchsorted(rmax, tp_i, "left"));  i_tp = i_tp if i_tp < n else 10**9
    i_sl = int(np.searchsorted(-rmin, sl_i, "left")); i_sl = i_sl if i_sl < n else 10**9
    j = min(i_tp, i_sl)
    if j >= 10**9:
        pnl, reason, ji = int(fav[-1]), "EOD", n - 1
    else:
        pnl, reason, ji = int(fav[j]), ("TP" if j == i_tp else "SL"), j
    return dict(entry=e / PTS, exit=(e + (pnl if long_ else -pnl)) / PTS,
                pnl=pnl / PTS, reason=reason,
                mfe=int(rmax[-1]) / PTS, mae=int(rmin[-1]) / PTS,
                t_entry=int(NY[k0]), t_exit=int(NY[k0 + ji]), ticks=n)


def stats(p):
    p = np.asarray(p, float)
    if len(p) == 0:
        return dict(n=0, pf=np.nan, exp=np.nan, net=0.0, wr=np.nan, mdd=np.nan)
    gp, gl = p[p > 0].sum(), -p[p < 0].sum()
    eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    dd = pk - eq
    return dict(n=len(p), pf=(gp / gl if gl > 0 else np.inf), exp=p.mean(), net=p.sum(),
                wr=100 * (p > 0).mean(), mdd=float(dd.max()), gp=gp, gl=gl)
