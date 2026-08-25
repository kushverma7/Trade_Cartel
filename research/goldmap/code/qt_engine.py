"""Parts 5, 6, 13 — Quarterly Theory labelling and an ALL-DAY event universe.

QUARTER STRUCTURE (America/New_York, DST from the tz database, never a fixed
offset). The daily cycle opens 18:00 NY:
    daily quarters   Q1 18:00, Q2 00:00, Q3 06:00, Q4 12:00      (6 hours each)
    90-minute        four inside each daily quarter               (16 per day)
    micro 22.5-min   four inside each 90-minute quarter           (64 per day)

THE GENERALISED EVENT. The anchor is a QT boundary, not a clock time chosen by
search. For every one of the 16 ninety-minute quarters in a day:

    anchor  = that quarter's own MQ1, the first 22.5 minutes
    signal  = first completed 5-minute close beyond the anchor's body,
              searched through MQ2 and MQ3 (22.5 to 67.5 minutes in)
    side    = CONTINUATION if the break follows the anchor's own body
              direction, FLIP if it opposes it

Every event is generated ALL DAY. No activity, compression, spread or price
filter is applied here -- they are recorded as FEATURES so the baseline can be
measured before anything is restricted.
"""
import os, numpy as np, pandas as pd

PTS = 1000.0
DAY_Q = {0: "Q2", 6: "Q3", 12: "Q4", 18: "Q1"}


class Book:
    """One year's tick stream, indexed for millisecond-precision candles."""

    def __init__(self, data_dir, year):
        self.year = year
        self.ny = np.load(f"{data_dir}/ny_ms.npy")
        self.bid = np.load(f"{data_dir}/bid_i.npy")
        self.ask = np.load(f"{data_dir}/ask_i.npy")
        self.mid = (self.bid.astype(np.int64) + self.ask.astype(np.int64)) // 2
        self.day = self.ny // 86_400_000
        d = np.unique(self.day)
        lo = np.searchsorted(self.day, d, "left"); hi = np.searchsorted(self.day, d, "right")
        self.slice = {int(x): (int(a), int(b)) for x, a, b in zip(d, lo, hi)}
        self.days = [int(x) for x in d]

    def candle(self, day, s0, s1, min_ticks=15):
        """OHLC of MID between s0 and s1 seconds past NY midnight."""
        r = self.slice.get(day)
        if r is None:
            return None
        lo, hi = r
        t0 = day * 86_400_000 + int(s0 * 1000)
        t1 = day * 86_400_000 + int(s1 * 1000)
        i = lo + int(np.searchsorted(self.ny[lo:hi], t0, "left"))
        j = lo + int(np.searchsorted(self.ny[lo:hi], t1, "left"))
        if j - i < min_ticks:
            return None
        seg = self.mid[i:j]
        return dict(o=int(seg[0]), c=int(seg[-1]), h=int(seg.max()), l=int(seg.min()),
                    i0=i, i1=j, t_close=int(self.ny[j - 1]), n=j - i)

    def spread_at(self, k):
        return (int(self.ask[k]) - int(self.bid[k])) / PTS

    def first_after(self, t_ms):
        return int(np.searchsorted(self.ny, t_ms, "right"))

    def horizon(self, day, hours=8):
        """Tick index `hours` after the day's start of that bar, capped at data end."""
        return None


def q90_starts():
    """The 16 ninety-minute quarter opens of a NY trading day, in seconds."""
    out = []
    for dq_h in (18, 0, 6, 12):
        for k in range(4):
            out.append(((dq_h * 3600) + k * 5400) % 86400)
    return out


def qt_labels(sec):
    """-> (daily quarter, 90m index within it, micro index) for a second-of-day."""
    h = sec // 3600
    dq_h = 18 if h >= 18 else (12 if h >= 12 else (6 if h >= 6 else 0))
    dq = DAY_Q[dq_h]
    off = (sec - dq_h * 3600) % 86400
    q90 = int(off // 5400) + 1
    mq = int((off % 5400) // 1350) + 1
    return dq, q90, mq


ANCHOR_S = 1350          # 22.5 minutes
STEP_S = 300             # 5-minute signal candles
SEARCH_S = 2700          # search MQ2 and MQ3


def events(book, max_days=None):
    rows = []
    for day in (book.days if max_days is None else book.days[:max_days]):
        for s0 in q90_starts():
            a = book.candle(day, s0, s0 + ANCHOR_S)
            if a is None:
                continue
            o, c = a["o"] / PTS, a["c"] / PTS
            hi, lo = a["h"] / PTS, a["l"] / PTS
            body = abs(c - o); rng = hi - lo
            up_anchor = c > o
            bhi, blo = max(o, c), min(o, c)
            hit = None
            for s in range(s0 + ANCHOR_S, s0 + ANCHOR_S + SEARCH_S, STEP_S):
                cd = book.candle(day, s, s + STEP_S)
                if cd is None:
                    continue
                cc = cd["c"] / PTS
                if cc > bhi:
                    hit = (cd, True, s); break
                if cc < blo:
                    hit = (cd, False, s); break
            if hit is None:
                continue
            cd, long_, s_sig = hit
            k0 = book.first_after(cd["t_close"])
            if k0 >= len(book.ny):
                continue
            bid, ask = int(book.bid[k0]) / PTS, int(book.ask[k0]) / PTS
            entry = ask if long_ else bid
            dq, q90, _ = qt_labels(s0)
            rows.append(dict(
                year=book.year, day=day,
                date=pd.Timestamp(day * 86400000, unit="ms").date(),
                q_open_s=s0, q_open=f"{s0//3600:02d}:{(s0%3600)//60:02d}",
                daily_q=dq, q90_idx=q90,
                anchor_o=o, anchor_c=c, anchor_h=hi, anchor_l=lo,
                anchor_body=body, anchor_rng=rng, anchor_ticks=a["n"],
                anchor_up=up_anchor, body_hi=bhi, body_lo=blo,
                anchor_eff=(abs(c - o) / rng if rng > 0 else np.nan),
                sig_s=s_sig, sig_min_in=(s_sig - s0) / 60.0,
                sig_mq=int(((s_sig - s0) % 5400) // 1350) + 1,
                long=long_, cont=(long_ == up_anchor),
                entry=entry, spread=ask - bid, k0=k0,
                t_entry=int(book.ny[k0])))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import time, sys
    out = []
    for dd, yr in (("research/microq3/data_holdout", "2024-25"),
                   ("research/microq3/data", "2025-26")):
        t0 = time.time()
        b = Book(dd, yr)
        e = events(b)
        print(f"{yr}: {len(e):,} events over {e.date.nunique()} days "
              f"({len(e)/max(e.date.nunique(),1):.1f}/day, {time.time()-t0:.0f}s)", flush=True)
        out.append(e)
    E = pd.concat(out, ignore_index=True)
    E.to_parquet("research/goldmap/results/events_allday.parquet", index=False)
    print(f"\nwrote events_allday.parquet  rows={len(E):,}")
    print("\nby daily quarter:")
    print(E.groupby(["year", "daily_q"]).size().unstack(fill_value=0).to_string())
    print(f"\ncontinuation {100*E.cont.mean():.1f}%   flip {100*(~E.cont).mean():.1f}%")
    print(f"long {100*E.long.mean():.1f}%")
