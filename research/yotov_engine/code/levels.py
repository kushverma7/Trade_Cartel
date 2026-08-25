"""LAYER 2 — Spaceman structural levels, per Gold session, from 1-minute bars.

Gold's session runs 18:00 NY to 17:00 NY the next calendar day, so a session is
labelled by the calendar day it CLOSES on: bars at hm >= 18:00 belong to the
NEXT day's session. Every level is therefore known before the session it is
used in, which is what makes it usable as a location filter rather than a
look-ahead.

    DO      session open (first mid at/after 18:00 NY)
    PDH/PDL previous session's high / low
    ASIAH/L high / low of 18:00 -> 03:00 NY inside the session
    WO      week open (session open of the week's first session)
    PWH/PWL previous week's high / low
    MONH/L  Monday session's high / low (available from Tuesday on)

`levels_for(day)` returns only levels that were COMPLETE before that session
opened. Asia H/L is the one exception: it completes at 03:00 inside the session,
so it carries `ready_hm = 180` and callers must not use it earlier.
"""
import numpy as np, pandas as pd

PTS = 1000.0
SESSION_OPEN_HM = 18 * 60
ASIA_END_HM = 3 * 60


def build(bars_path):
    b = pd.read_parquet(bars_path, columns=["minute", "i0", "i1", "mid_o",
                                            "mid_h", "mid_l", "mid_c"])
    b["day"] = b.minute // 1440
    b["hm"] = b.minute % 1440
    # session label: the calendar day the session CLOSES on
    b["sess"] = b.day + (b.hm >= SESSION_OPEN_HM).astype(np.int64)

    g = b.groupby("sess")
    s = pd.DataFrame({
        "open": g.mid_o.first(), "high": g.mid_h.max(), "low": g.mid_l.min(),
        "close": g.mid_c.last(), "i0": g.i0.first(), "i1": g.i1.last(),
        "start_min": g.minute.first(), "nbars": g.size(),
    })
    # Asia = 18:00 -> 03:00 NY, i.e. hm >= 18:00 on the prior day OR hm < 03:00
    a = b[(b.hm >= SESSION_OPEN_HM) | (b.hm < ASIA_END_HM)].groupby("sess")
    s["asia_h"], s["asia_l"] = a.mid_h.max(), a.mid_l.min()

    s = s[s.nbars >= 300].copy()            # drop stub sessions (holidays)
    s["pdh"], s["pdl"] = s.high.shift(1), s.low.shift(1)

    # calendar week of the session's start, ISO
    ts = pd.to_datetime(s.start_min * 60_000, unit="ms")
    s["dow"], s["week"] = ts.dt.dayofweek, ts.dt.strftime("%G-%V")
    w = s.groupby("week")
    s["wo"] = s.week.map(w.open.first())
    wk = pd.DataFrame({"h": w.high.max(), "l": w.low.min()})
    prev = {k: v for k, v in zip(wk.index[1:], wk.index[:-1])}
    s["pwh"] = s.week.map(lambda k: wk.h.get(prev.get(k), np.nan))
    s["pwl"] = s.week.map(lambda k: wk.l.get(prev.get(k), np.nan))
    # Monday session = the week's first session; usable from the SECOND session on
    s["mon_h"] = s.week.map(w.high.first())
    s["mon_l"] = s.week.map(w.low.first())
    first_of_week = ~s.week.duplicated()
    s.loc[first_of_week, ["mon_h", "mon_l"]] = np.nan
    return s


# level name -> (column, minute inside the session from which it is valid)
SPEC = [("DO", "open", 0), ("PDH", "pdh", 0), ("PDL", "pdl", 0),
        ("WO", "wo", 0), ("PWH", "pwh", 0), ("PWL", "pwl", 0),
        ("MONH", "mon_h", 0), ("MONL", "mon_l", 0),
        ("ASIAH", "asia_h", ASIA_END_HM), ("ASIAL", "asia_l", ASIA_END_HM)]


def levels_for(row):
    """-> list of (name, price_int, ready_hm) for one session, NaNs dropped."""
    out = []
    for name, col, ready in SPEC:
        v = row[col]
        if v == v and v is not None:
            out.append((name, int(v), ready))
    return out


if __name__ == "__main__":
    import sys
    for tag, p in (("2025-26", "research/microq3/data/bars_1m_ny.parquet"),
                   ("2024-25", "research/microq3/data_holdout/bars_1m_ny.parquet")):
        s = build(p)
        print(f"\n{tag}: {len(s)} sessions, "
              f"{pd.to_datetime(s.start_min.iloc[0]*60000, unit='ms'):%Y-%m-%d} .. "
              f"{pd.to_datetime(s.start_min.iloc[-1]*60000, unit='ms'):%Y-%m-%d}")
        n = {k: int(s[c].notna().sum()) for k, c, _ in SPEC}
        print("  levels available per session:", n)
        r = s.iloc[120]
        print(f"  sample session {pd.to_datetime(r.start_min*60000, unit='ms'):%Y-%m-%d %a}  "
              f"O={r.open/PTS:.2f} H={r.high/PTS:.2f} L={r.low/PTS:.2f}")
        for nm, px, rd in levels_for(r):
            print(f"    {nm:>6} {px/PTS:>9.2f}   ready hm {rd}")
