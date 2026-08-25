"""The LOCKED entry universe. Built once, never modified by any exit search.

Rule, exactly as specified and not one filter more:
  1. the 10:00 Melbourne candle must be BULLISH (close > open)
  2. after it completes, watch BOTH first breaks on completed 5-minute closes
       A_LONG      close > 10AM body high
       FLIP_SHORT  close < 10AM body low
  3. whichever fires FIRST wins
  4. at most ONE trade per day; later signals that day are ignored
  5. entry window and an entry-spread cap are applied as stated

Because the anchor candle is bullish, body high IS its close and body low IS its
open, so A_LONG is a break above the 10AM close and FLIP_SHORT a break below the
10AM open. No other condition exists here. Candle size, wicks, ATR, indicators,
news and session context are deliberately absent -- that half is someone else's.

SPREAD REJECTION IS A SKIP, NOT A SUBSTITUTION. If the first break's entry
spread exceeds the cap the day produces no trade; the code does not walk forward
to the next signal, because that would silently become a different entry rule.
"""
import sys, pickle, numpy as np, pandas as pd
PTS = 1000.0
BASE = "/home/user/Trade_Cartel/research/gold_10am_flip"
prep = pickle.load(open(f"{BASE}/data/prep10.pkl", "rb"))

class TK:
    t = np.load(f"{BASE}/data/tk_t.npy")
    bid = np.load(f"{BASE}/data/tk_bid.npy")
    ask = np.load(f"{BASE}/data/tk_ask.npy")


def build(window_end_hhmm=1100, max_spread=2.0):
    """-> list of trade dicts, one per qualifying day, with the tick path cached."""
    out = []
    for day in prep:
        if day["side"] != 1:                       # BULLISH 10AM candle only
            continue
        c, bhi, blo = day["c"], day["bhi"], day["blo"]
        tclose = day["t_close"]
        # bar clock time in HHMM, from the naive Melbourne wall clock
        mins = ((tclose - 5 * 60 * 1000) % 86_400_000) // 60_000
        hhmm = (mins // 60) * 100 + (mins % 60)
        up, dn = c > bhi, c < blo
        iu = int(np.argmax(up)) if up.any() else 10**9
        idn = int(np.argmax(dn)) if dn.any() else 10**9
        if min(iu, idn) >= 10**9:
            continue
        i = min(iu, idn)                           # FIRST break of either kind wins
        long_ = iu <= idn
        if hhmm[i] > window_end_hhmm:              # outside the entry window
            continue
        ask_i, bid_i = int(day["ask_c"][i]), int(day["bid_c"][i])
        spread = (ask_i - bid_i) / PTS
        if max_spread is not None and spread > max_spread:
            continue                               # SKIP the day; do not substitute
        e = ask_i if long_ else bid_i
        k0 = day["i0"] + int(np.searchsorted(TK.t[day["i0"]:day["j0"]], int(tclose[i]), side="right"))
        if k0 >= day["j0"]:
            continue
        ex = TK.bid[k0:day["j0"]] if long_ else TK.ask[k0:day["j0"]]
        tt = TK.t[k0:day["j0"]]
        fav = (ex.astype(np.int64) - e) if long_ else (e - ex.astype(np.int64))
        out.append(dict(date=pd.Timestamp(day["date"]), kind="A_LONG" if long_ else "FLIP_SHORT",
                        long=long_, bar=i, hhmm=int(hhmm[i]), t_signal=int(tclose[i] - 5*60*1000),
                        t_entry=int(tclose[i]), entry=e / PTS, spread=spread,
                        fav=fav, tms=tt,
                        rmax=np.maximum.accumulate(fav), rmin=np.minimum.accumulate(fav)))
    out.sort(key=lambda r: r["date"])
    return out


def splits(trades, dev=0.60, val=0.20):
    """Chronological DEV / VAL / HOLD by DATE across the qualifying days."""
    ds = sorted({t["date"] for t in trades})
    d1, d2 = ds[int(len(ds) * dev)], ds[int(len(ds) * (dev + val))]
    return d1, d2


def label(trades, d1, d2):
    for t in trades:
        t["split"] = "DEV" if t["date"] <= d1 else ("VAL" if t["date"] <= d2 else "HOLD")
    return trades
