"""
VWAP and volume-weighted sigma bands for AU200, tested against the EMA 5/20
champion under the identical protocol.

SESSION ANCHOR, DERIVED NOT ASSUMED
  The cash session is 10:00-16:00 Australia/Sydney: hours 10-15 carry ~6,050
  bars each against ~720 for every extended-hours hour, and 1,337 of the 2,468
  intraday gaps end at hour 10. Session VWAP therefore resets at the first bar
  at or after 10:00 local each day. Anchoring at midnight would cut the session
  in half and is not used.

SIGMA FORMULA, STATED EXACTLY
  Price basis is the TYPICAL price p = (high + low + close) / 3, used for both
  the VWAP and the deviation, so the two are on the same basis.

      VWAP_t  = sum(v_i * p_i, i<=t) / sum(v_i, i<=t)
      var_t   = sum(v_i * (p_i - VWAP_t)^2, i<=t) / sum(v_i, i<=t)
      sigma_t = sqrt(var_t)
      Upper_k = VWAP_t + k * sigma_t      Lower_k = VWAP_t - k * sigma_t

  var is computed with the running-moments identity
  E[p^2] - (E[p])^2 on volume weights, which is exact here and avoids a second
  pass. Both accumulators run through bar t inclusive, so every value uses only
  information available at that bar's close. No lookahead.

  A one-bar session has variance 0 by construction, so sigma is undefined-ish
  at the open; bands are marked NaN until at least MIN_BARS bars have
  accumulated and no signal may reference them before then.
"""
import numpy as np, pandas as pd

MIN_BARS = 4          # bars of accumulation before sigma bands are usable


def _typical(df):
    return ((df["high"] + df["low"] + df["close"]) / 3.0).to_numpy(float)


def session_id(df, anchor_hour=10):
    """Trading-day id that rolls over at `anchor_hour` local time."""
    idx = df.index
    d = pd.Series(idx.normalize(), index=idx)
    roll = idx.hour < anchor_hour          # before the open belongs to the prior day
    return (d - pd.to_timedelta(roll.astype(int), unit="D")).dt.date.to_numpy()


def session_vwap(df, anchor_hour=10):
    """Session VWAP and volume-weighted sigma, reset at the session anchor."""
    p, v = _typical(df), df["volume"].to_numpy(float)
    sid = session_id(df, anchor_hour)
    new = np.r_[True, sid[1:] != sid[:-1]]
    n = len(p)
    vw = np.empty(n); sg = np.full(n, np.nan)
    cv = cpv = cpv2 = 0.0; cnt = 0
    for i in range(n):
        if new[i]:
            cv = cpv = cpv2 = 0.0; cnt = 0
        cv += v[i]; cpv += v[i] * p[i]; cpv2 += v[i] * p[i] * p[i]; cnt += 1
        m = cpv / cv if cv > 0 else p[i]
        vw[i] = m
        if cnt >= MIN_BARS and cv > 0:
            var = max(cpv2 / cv - m * m, 0.0)
            sg[i] = np.sqrt(var)
    return vw, sg


def rolling_vwap(df, n=24):
    """Rolling VWAP and volume-weighted sigma over the last n bars."""
    p, v = _typical(df), df["volume"].to_numpy(float)
    S = pd.Series
    sv = S(v).rolling(n).sum()
    m = (S(v * p).rolling(n).sum() / sv).to_numpy()
    m2 = (S(v * p * p).rolling(n).sum() / sv).to_numpy()
    return m, np.sqrt(np.maximum(m2 - m * m, 0.0))


def bands(vw, sg, k):
    return vw + k * sg, vw - k * sg
