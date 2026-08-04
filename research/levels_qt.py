"""
Level types, Quarterly Theory cycles and the $25 quarter grid — definitions.

NO-LOOKAHEAD DISCIPLINE
  Every level is built from information available STRICTLY BEFORE the bar it is
  attached to. Previous-day/week/month extremes use a shift; session extremes
  are RUNNING (only the part of the session already elapsed); True Opens are the
  open of a period that has already begun. Nothing here reads a bar's own high
  or low to decide anything about that bar.

QUARTERLY THEORY (ICT / Daye), time-based
  Each cycle is split into four equal time quarters:
    Weekly  : Mon / Tue / Wed / Thu  (Fri excluded - the classic definition)
    Daily   : 18-00, 00-06, 06-12, 12-18 UTC  (approximating the NY-anchored day)
    Session : each 6h block split into four 90-minute quarters
  True Open = the OPEN of Q2 for that cycle. Premium = above it, discount below.
  Phases: Q1 accumulation, Q2 manipulation (Judas), Q3 distribution, Q4
  continuation/reversal.

  DST CAVEAT, stated: the data is UTC and these boundaries are fixed UTC hours.
  ICT's definitions are New-York-anchored, so the blocks drift one hour against
  the intended session twice a year. Not corrected; a known limitation.
"""
import numpy as np, pandas as pd


# ---------------------------------------------------------------- price levels
def price_levels(df):
    """Previous day/week/month extremes and true opens. All shifted."""
    out = pd.DataFrame(index=df.index)
    idx = df.index
    for name, rule in (("D", idx.date), ("W", idx.to_period("W")), ("M", idx.to_period("M"))):
        k = pd.Series(rule, index=idx)
        g = df.groupby(k)
        hi, lo = g["high"].max(), g["low"].min()
        op = g["open"].first()
        out[f"P{name}H"] = k.map(hi.shift(1)).values
        out[f"P{name}L"] = k.map(lo.shift(1)).values
        out[f"{name}O"] = k.map(op).values          # true open of the CURRENT period
    return out


def session_running(df, blocks=(("ASIA", 0, 7), ("LDN", 7, 12), ("NY", 12, 21))):
    """Running high/low of each session SO FAR, plus the previous day's final."""
    out = pd.DataFrame(index=df.index)
    hh = df.index.hour
    day = pd.Series(df.index.date, index=df.index)
    for nm, a, b in blocks:
        m = (hh >= a) & (hh < b)
        h = df["high"].where(m); l = df["low"].where(m)
        # running extreme within the session, shifted so the current bar is excluded
        out[f"{nm}H"] = h.groupby(day).cummax().shift(1)
        out[f"{nm}L"] = l.groupby(day).cummin().shift(1)
        # previous day's completed session extreme
        fin_h = h.groupby(day).max(); fin_l = l.groupby(day).min()
        out[f"P{nm}H"] = day.map(fin_h.shift(1)).values
        out[f"P{nm}L"] = day.map(fin_l.shift(1)).values
    return out


def quarter_grid(px, step):
    """Nearest grid level at or below, and above, for a $step grid."""
    lo = np.floor(px / step) * step
    return lo, lo + step


# ------------------------------------------------------------ quarterly theory
def qt_daily(idx):
    """Daily cycle quarters, NY-anchored 18:00 UTC start."""
    h = idx.hour
    q = np.select([(h >= 18) | (h < 0), (h >= 0) & (h < 6),
                   (h >= 6) & (h < 12), (h >= 12) & (h < 18)],
                  [1, 2, 3, 4], default=0)
    # cycle id: the "trading day" starting at 18:00
    cyc = pd.Series(idx.date, index=idx)
    cyc = np.where(h >= 18, pd.Series(idx.date, index=idx) + pd.Timedelta(days=1),
                   pd.Series(idx.date, index=idx))
    return q, pd.Series(cyc, index=idx).astype(str).values


def qt_weekly(idx):
    """Weekly cycle: Mon=Q1, Tue=Q2, Wed=Q3, Thu=Q4. Friday excluded."""
    d = idx.dayofweek
    q = np.where(d <= 3, d + 1, 0)
    cyc = pd.Series(idx.to_period("W").astype(str), index=idx).values
    return q, cyc


def qt_session(idx):
    """Session cycle: each 6h block split into four 90-minute quarters."""
    mins = idx.hour * 60 + idx.minute
    blk = (mins // 360)
    within = mins - blk * 360
    q = (within // 90) + 1
    cyc = (pd.Series(idx.date, index=idx).astype(str) + "_" + pd.Series(blk, index=idx).astype(str)).values
    return q.astype(int), cyc


def true_open(df, q, cyc):
    """Open of Q2 for each cycle, broadcast forward. NaN before Q2 begins."""
    s = pd.DataFrame({"q": q, "cyc": cyc, "open": df["open"].values}, index=df.index)
    q2 = s[s.q == 2].groupby("cyc")["open"].first()
    to = s["cyc"].map(q2)
    # a cycle's true open is only KNOWN from the moment Q2 starts
    known = s.groupby("cyc").cumcount() >= 0
    to = to.where(s.q >= 2)
    return to.values
