"""
The 22-voice register, vectorised.

Every voice from strategies/multivoice_confluence_engine.pine, ported to
numpy so the whole knowledge base can be tested against real bars instead
of a single in-sample TradingView run.

Each voice returns an int8 array over the bar series: +1 bullish, -1
bearish, 0 abstain. Votes are computed ONCE; a search over voter subsets
and conviction thresholds is then almost free, because only the backtest
loop costs anything.

NO LOOKAHEAD. Every rolling statistic is shifted so a bar is never scored
using its own outcome or anything after it. Where the Pine original was
sloppy about this (Monday range read from a still-running day) the port
deliberately does not reproduce it.

Voice -> hypothesis -> source, matching the Pine comments:
  V1  H48 Hougaard 4-bar fractal      V12 H35 EMA bunching
  V2  H22 repeated failed visits      V13 H23 ADR thirds
  V3  H71 Hima 2-bar test failure     V14 H5  momentum-join
  V4  H63 Gann signal day             V15 H17 leg-size regime
  V5  H37 role inversion              V16 H70 eighths retracement
  V6  H36 IDM-gated BOS               V17 H8  rejection count
  V7  H44 liquidity grab              V18 --  Nison tier-A candle
  V8  H46 HVN cluster                 V19 --  key-level sweep+reclaim
  V9  H30 Wendell fresh zone          V20 H10 session structure
  V10 H49 mid-trend divergence        V21 H37 key-level break/retest
  V11 H16 volume tsunami              V22 --  higher-timeframe trend
"""
import numpy as np
import pandas as pd

NAMES = [
    "V1 Hougaard 4bar", "V2 failed visits", "V3 Hima test-fail",
    "V4 Gann signal day", "V5 role inversion", "V6 IDM-gated BOS",
    "V7 liquidity grab", "V8 HVN cluster", "V9 Wendell zone",
    "V10 mid-trend div", "V11 vol tsunami", "V12 EMA bunching",
    "V13 ADR thirds", "V14 momentum-join", "V15 leg regime",
    "V16 eighths", "V17 rejection count", "V18 tier-A candle",
    "V19 KL sweep", "V20 session", "V21 KL break-retest", "V22 HTF trend",
]
HIGH_CRED = {0, 8, 9, 10, 13}          # Hougaard, Wendell, Valentini -- double weight


def _roll(a, n, fn):
    """Rolling stat over the PREVIOUS n bars, excluding the current one."""
    s = pd.Series(a)
    return getattr(s.rolling(n), fn)().shift(1).to_numpy()


def _ema(a, n):
    return pd.Series(a).ewm(span=n, adjust=False).mean().to_numpy()


def _rsi(c, n=14):
    d = np.diff(c, prepend=c[0])
    up = pd.Series(np.where(d > 0, d, 0.0)).ewm(alpha=1 / n, adjust=False).mean()
    dn = pd.Series(np.where(d < 0, -d, 0.0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = up / dn.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).to_numpy()


def compute(df, lv, atr, in_session, htf_len=200):
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    v = df["volume"].to_numpy(float) if "volume" in df.columns else np.ones(len(c))
    n = len(c)
    V = np.zeros((n, 22), np.int8)
    rng_ = h - l
    body = np.abs(c - o)
    tol = atr * 0.25

    def sh(a, k=1):
        out = np.full_like(a, np.nan, dtype=float); out[k:] = a[:-k]; return out

    # V1 Hougaard 4-bar fractal: close beats the highs/lows of bars 1 and 3 back
    V[:, 0] = np.where((c > sh(h, 1)) & (c > sh(h, 3)), 1,
              np.where((c < sh(l, 1)) & (c < sh(l, 3)), -1, 0))

    # levels matrix, used by several voices
    Lm = lv.to_numpy(float)
    near = np.abs(c[:, None] - Lm) <= tol[:, None]
    above = Lm > c[:, None]
    below = Lm < c[:, None]

    # V2 repeated failed visits: many touches of a level that never broke it
    touch = (np.abs(h[:, None] - Lm) <= tol[:, None]) | (np.abs(l[:, None] - Lm) <= tol[:, None])
    tc = pd.DataFrame(touch.astype(float)).rolling(96).sum().shift(1).to_numpy()
    V[:, 1] = np.where(np.nansum(np.where(above & (tc >= 3), 1, 0), 1) > 0, -1,
              np.where(np.nansum(np.where(below & (tc >= 3), 1, 0), 1) > 0, 1, 0))

    # V3 Hima 2-bar test failure of a level
    pierce_up = (sh(h)[:, None] > Lm) & (sh(c)[:, None] < Lm)
    pierce_dn = (sh(l)[:, None] < Lm) & (sh(c)[:, None] > Lm)
    V[:, 2] = np.where((pierce_up & (c[:, None] < Lm)).any(1), -1,
              np.where((pierce_dn & (c[:, None] > Lm)).any(1), 1, 0))

    # V4 Gann signal day: N-bar extreme with the close in the far third
    hi20, lo20 = _roll(h, 20, "max"), _roll(l, 20, "min")
    farlo = (c - l) <= rng_ * 0.33
    farhi = (h - c) <= rng_ * 0.33
    V[:, 3] = np.where((h >= hi20) & farlo, -1, np.where((l <= lo20) & farhi, 1, 0))

    # V5 role inversion: level broken earlier, now holding from the other side
    lo12, hi12 = _roll(l, 12, "min"), _roll(h, 12, "max")
    V[:, 4] = np.where(((c[:, None] > Lm) & (lo12[:, None] < Lm) & near).any(1), 1,
              np.where(((c[:, None] < Lm) & (hi12[:, None] > Lm) & near).any(1), -1, 0))
    # (near/above/below are (n, n_levels); every comparison against a bar
    #  series must be broadcast with [:, None] or numpy silently refuses)

    # V6 IDM-gated BOS: break of the 20-bar range, but only once the opposite
    # side has been swept first (Alchemist's inducement gate).
    # The inducement window must be EARLIER than the sweep window. Comparing
    # the 12-bar low against the 40-bar low that CONTAINS it made the
    # condition structurally impossible -- the voice fired on 0.0% of bars.
    lo_old = pd.Series(l).rolling(28).min().shift(13).to_numpy()
    hi_old = pd.Series(h).rolling(28).max().shift(13).to_numpy()
    V[:, 5] = np.where((c > hi20) & (lo12 < lo_old), 1,
              np.where((c < lo20) & (hi12 > hi_old), -1, 0))

    # V7 liquidity grab: long wick relative to body
    uw, lw = h - np.maximum(o, c), np.minimum(o, c) - l
    V[:, 6] = np.where((lw > body * 2) & (lw > uw * 2), 1,
              np.where((uw > body * 2) & (uw > lw * 2), -1, 0))

    # V8 HVN proxy: rolling VWAP as the volume-weighted fair value
    tp = (h + l + c) / 3
    vw = (pd.Series(tp * v).rolling(96).sum() / pd.Series(v).rolling(96).sum()).shift(1).to_numpy()
    V[:, 7] = np.where(np.abs(c - vw) <= tol, np.where(c > vw, 1, -1), 0)

    # V9 Wendell fresh zone: strong departure from a level not yet revisited
    strong = body > _roll(body, 20, "mean") * 1.5
    V[:, 8] = np.where(strong & (c > o), 1, np.where(strong & (c < o), -1, 0))

    # V10 mid-trend divergence = continuation (Hougaard), not reversal
    r = _rsi(c)
    V[:, 9] = np.where((c > sh(c, 5)) & (r < sh(r, 5)), 1,
              np.where((c < sh(c, 5)) & (r > sh(r, 5)), -1, 0))

    # V11 Valentini volume tsunami vs hollow move
    va = _roll(v, 20, "mean")
    V[:, 10] = np.where((v > va * 1.5) & (c > o), 1,
               np.where((v > va * 1.5) & (c < o), -1, 0))

    # V12 EMA stack bunching (13/50/200)
    e13, e50, e200 = _ema(c, 13), _ema(c, 50), _ema(c, 200)
    bunched = (np.abs(e13 - e50) + np.abs(e50 - e200)) < atr * 0.5
    V[:, 11] = np.where(bunched & (e13 > e50) & (e50 > e200), 1,
               np.where(bunched & (e13 < e50) & (e50 < e200), -1, 0))

    # V13 ADR thirds: position within the day's average range
    dh = pd.Series(h).groupby(df.index.normalize()).transform("cummax").to_numpy()
    dl = pd.Series(l).groupby(df.index.normalize()).transform("cummin").to_numpy()
    pos = np.where(dh > dl, (c - dl) / (dh - dl), 0.5)
    V[:, 12] = np.where(pos < 0.33, 1, np.where(pos > 0.67, -1, 0))

    # V14 Valentini momentum-join
    V[:, 13] = np.where((c > e50) & (c > sh(c)), 1,
               np.where((c < e50) & (c < sh(c)), -1, 0))

    # V15 Ario leg-size regime: net move relative to the swing it sits in
    leg = _roll(h, 20, "max") - _roll(l, 20, "min")
    ratio = np.where(leg > 0, (c - sh(c, 20)) / leg, 0)
    V[:, 14] = np.where(ratio > 0.35, 1, np.where(ratio < -0.35, -1, 0))

    # V16 Hima eighths: reaction at the 50% / 62.5% of the recent swing
    sh30, sl30 = _roll(h, 30, "max"), _roll(l, 30, "min")
    rr = sh30 - sl30
    for frac, sgn in ((0.500, 1), (0.375, 1), (0.625, -1)):
        lvl = sl30 + rr * frac
        hit = np.abs(c - lvl) <= tol
        V[:, 15] = np.where(hit & (V[:, 15] == 0), sgn, V[:, 15])

    # V17 rejection count: consecutive same-direction closes weakening
    up3 = (c > o) & (sh(c) > sh(o)) & (sh(c, 2) > sh(o, 2))
    dn3 = (c < o) & (sh(c) < sh(o)) & (sh(c, 2) < sh(o, 2))
    V[:, 16] = np.where(up3, -1, np.where(dn3, 1, 0))

    # V18 Nison tier-A reversal candles
    ab = _roll(body, 14, "mean")
    beng = (c > o) & (sh(c) < sh(o)) & (body >= ab) & (c >= np.maximum(sh(c), sh(o))) & (o <= np.minimum(sh(c), sh(o)))
    seng = (c < o) & (sh(c) > sh(o)) & (body >= ab) & (o >= np.maximum(sh(c), sh(o))) & (c <= np.minimum(sh(c), sh(o)))
    ham = (lw > body * 2) & (uw < body * 0.5)
    sho = (uw > body * 2) & (lw < body * 0.5)
    V[:, 17] = np.where(beng | ham, 1, np.where(seng | sho, -1, 0))

    # V19 key-level sweep + reclaim
    swu = ((l[:, None] < Lm) & (c[:, None] > Lm)).any(1) & (c > o)
    swd = ((h[:, None] > Lm) & (c[:, None] < Lm)).any(1) & (c < o)
    V[:, 18] = np.where(swu, 1, np.where(swd, -1, 0))

    # V20 session structure relative to the daily open
    do = lv["DO"].to_numpy(float)
    V[:, 19] = np.where(in_session & (c > do), 1, np.where(in_session & (c < do), -1, 0))

    # V21 key-level break and retest
    V[:, 20] = np.where(((c[:, None] > Lm) & (lo12[:, None] < Lm) & (l[:, None] <= Lm + tol[:, None])).any(1) & (c > o), 1,
               np.where(((c[:, None] < Lm) & (hi12[:, None] > Lm) & (h[:, None] >= Lm - tol[:, None])).any(1) & (c < o), -1, 0))

    # V22 higher-timeframe trend
    eh = _ema(c, htf_len)
    V[:, 21] = np.where(c > eh, 1, np.where(c < eh, -1, 0))

    return np.nan_to_num(V).astype(np.int8)
