"""Micro-Q3 signal construction. Entry universe only -- exits applied separately.

Signal generation and exit resolution are deliberately split so that an exit
sweep can never alter which trades exist. `signals()` caches the running
extremes of each trade's real quote path once; `apply()` then resolves any
(SL, TP) pair against that cached path by two searchsorted calls.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/microq3/code")
import engine as E
from engine import PTS

DEF = dict(anchor_start=18 * 60 + 45, anchor_len=15, px="mid",
           need_bearish=True, body_min=1.00, body_max=6.25,
           win_from=19 * 60, win_to=19 * 60 + 30,
           grid=25.0, grid_phase=0.0, qdist=6.25,
           spread_max=1.50, eod_hm=17 * 60,
           allow_short=True, allow_long=True)


def signals(**kw):
    p = dict(DEF); p.update(kw)
    out = []
    for day in E.DAYS:
        day = int(day)
        a = E.candle(day, p["anchor_start"], p["anchor_start"] + p["anchor_len"], p["px"])
        if a is None or a["nmin"] < max(3, p["anchor_len"] // 3):
            continue
        o, c = a["o"] / PTS, a["c"] / PTS
        body = abs(c - o)
        bear = c < o
        if p["need_bearish"] is True and not bear:
            continue
        if p["need_bearish"] is False and bear:
            continue
        if body < p["body_min"] or (p["body_max"] is not None and body > p["body_max"]):
            continue
        bhi, blo = (o, c) if bear else (c, o)       # body edges, direction-aware

        cands = E.five_min_candles(day, p["win_from"], p["win_to"], p["px"])
        hit = None
        for cd in cands:
            cc = cd["c"] / PTS
            if cc < blo:
                hit = (cd, False); break            # break DOWN -> short
            if cc > bhi:
                hit = (cd, True); break             # break UP   -> long
        if hit is None:
            continue
        cd, long_ = hit
        if long_ and not p["allow_long"]:
            continue
        if (not long_) and not p["allow_short"]:
            continue

        # entry = first tick STRICTLY AFTER the completed candle
        k0 = int(np.searchsorted(E.NY, cd["t_close"], "right"))
        kend = E.session_end_index(day, p["eod_hm"])
        if kend is None or k0 >= kend:
            continue
        bid, ask = int(E.BID[k0]) / PTS, int(E.ASK[k0]) / PTS
        spread = ask - bid
        entry = ask if long_ else bid
        if p["spread_max"] is not None and spread > p["spread_max"]:
            continue
        r = (entry - p["grid_phase"]) % p["grid"]
        dq = min(r, p["grid"] - r)
        if p["qdist"] is not None and dq > p["qdist"]:
            continue

        ex = E.BID[k0:kend] if long_ else E.ASK[k0:kend]
        e_i = int(E.ASK[k0]) if long_ else int(E.BID[k0])
        fav = (ex.astype(np.int64) - e_i) if long_ else (e_i - ex.astype(np.int64))
        out.append(dict(
            day=day, date=pd.Timestamp(day * 86400000, unit="ms").date(),
            anchor_open=o, anchor_close=c, anchor_high=a["h"] / PTS, anchor_low=a["l"] / PTS,
            anchor_body=body, anchor_range=(a["h"] - a["l"]) / PTS,
            anchor_dir="BEAR" if bear else "BULL", body_high=bhi, body_low=blo,
            sig_hm=cd["hm_start"], sig_open=cd["o"] / PTS, sig_close=cc,
            t_sig_close=cd["t_close"], kind="FLIP_LONG" if long_ else "A_SHORT", long=long_,
            t_entry=int(E.NY[k0]), entry_bid=bid, entry_ask=ask, entry_spread=spread,
            entry=entry, nearest25=round(entry / p["grid"]) * p["grid"], dist25=dq,
            k0=k0, kend=kend, fav=fav,
            rmax=np.maximum.accumulate(fav), rmin=np.minimum.accumulate(fav),
            tms=E.NY[k0:kend]))
    out.sort(key=lambda r: r["t_entry"])
    return out


def apply(trades, sl, tp, time_stop_min=None):
    """Resolve cached paths at (sl, tp). -> DataFrame, one row per trade."""
    rows = []
    sl_i, tp_i = int(round(sl * PTS)), int(round(tp * PTS))
    for t in trades:
        rmax, rmin, fav, tms = t["rmax"], t["rmin"], t["fav"], t["tms"]
        n = len(fav)
        if time_stop_min:
            n = int(np.searchsorted(tms, tms[0] + time_stop_min * 60_000, "right"))
            if n <= 0:
                continue
            rmax, rmin, fav = rmax[:n], rmin[:n], fav[:n]
        i_tp = int(np.searchsorted(rmax, tp_i, "left"));  i_tp = i_tp if i_tp < n else 10**9
        i_sl = int(np.searchsorted(-rmin, sl_i, "left")); i_sl = i_sl if i_sl < n else 10**9
        j = min(i_tp, i_sl)
        if j >= 10**9:
            pnl, why, ji = int(fav[-1]), ("TIME" if time_stop_min else "EOD"), n - 1
        else:
            pnl, why, ji = int(fav[j]), ("TP" if j == i_tp else "SL"), j
        rows.append(dict(
            date=t["date"], kind=t["kind"], long=t["long"],
            anchor_open=t["anchor_open"], anchor_close=t["anchor_close"],
            anchor_body=t["anchor_body"], anchor_range=t["anchor_range"],
            anchor_dir=t["anchor_dir"], body_high=t["body_high"], body_low=t["body_low"],
            sig_hm=t["sig_hm"], sig_open=t["sig_open"], sig_close=t["sig_close"],
            entry_bid=t["entry_bid"], entry_ask=t["entry_ask"], entry_spread=t["entry_spread"],
            entry=t["entry"], nearest25=t["nearest25"], dist25=t["dist25"],
            t_entry=pd.Timestamp(t["t_entry"], unit="ms"),
            t_exit=pd.Timestamp(int(tms[ji]), unit="ms"),
            stop_price=t["entry"] - sl if t["long"] else t["entry"] + sl,
            target_price=t["entry"] + tp if t["long"] else t["entry"] - tp,
            exit_price=t["entry"] + (pnl / PTS if t["long"] else -pnl / PTS),
            exit_reason=why, mfe=int(t["rmax"][-1]) / PTS, mae=int(t["rmin"][-1]) / PTS,
            pnl=pnl / PTS, hold_min=(int(tms[ji]) - t["t_entry"]) / 60000.0))
    return pd.DataFrame(rows)


def summarise(df):
    return E.stats(df["pnl"].tolist()) if len(df) else E.stats([])
