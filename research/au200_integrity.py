"""
AU200 measurement-engine integrity gate. No strategy search in this file.

WHY THIS EXISTS
  Two AU200 "edges" in succession were execution artifacts:
    - AU200-BASE: a 0.5-point trail whose fills were an artifact of 15m bar
      resolution. 78% of its profit vanished when the path was walked on 5m.
    - EMA 5/20: a 15m state forward-filled onto the three 5m bars INSIDE the
      still-forming 15m bar, i.e. up to 10 minutes of lookahead on every
      signal. PF 1.889 -> 0.696 once corrected.
  Both looked robust by every downstream check -- plateaus, 7/7 profitable
  years, out-of-sample improvement. Downstream robustness cannot detect an
  upstream timing defect, because the defect applies uniformly. The only
  defence is to test the ENGINE directly.

THE TEST THIS ADDS BEYOND THE BRIEF
  A synthetic random-walk null. The engine is run on a price series built by
  shuffling the real 5m log returns: same bar structure, same volatility, same
  session pattern, but no exploitable structure by construction. A correct
  engine must return PF ~ 1.0 at zero cost and PF < 1.0 after costs on such a
  series. Anything above that is edge the engine INVENTED, and it localises the
  defect without needing to guess which rule exposed it. The deliberately
  broken (unshifted) engine is run on the same synthetic data as a positive
  control, so the test is shown to have the power to detect what it claims to.
"""
import numpy as np, pandas as pd

from research.au200_lab import load
from research.au200_ma import cross_state, run, stat, atr

SLIP_FLOOR = 1.0
SEEDS = (11, 101, 2027, 55555, 987654)


# --------------------------------------------------------------------- A1
def a1_alignment(d15, d5):
    """Prove the stamp convention from the data rather than assuming it."""
    print("=" * 112)
    print("A1 — TIMESTAMP AND BAR ALIGNMENT")
    print("=" * 112)
    rows = []
    for t in d15.index[:3]:
        sub = d5[(d5.index >= t) & (d5.index < t + pd.Timedelta("15min"))]
        rows.append((t, d15.loc[t, "open"], d15.loc[t, "close"],
                     [str(x)[11:16] for x in sub.index],
                     sub.open.iloc[0], sub.close.iloc[-1]))
    for t, o, c, span, so, sc in rows:
        print(f"  15m {t}  open={o:.1f} close={c:.1f}")
        print(f"      spans 5m {span}  -> first open {so:.1f}, last close {sc:.1f}")
    ok_open = all(abs(o - so) < 1e-6 for _, o, _, _, so, _ in rows)
    ok_close = all(abs(c - sc) < 1e-6 for _, _, c, _, _, sc in rows)
    print(f"\n  15m open  == first spanned 5m open : {ok_open}")
    print(f"  15m close == last  spanned 5m close: {ok_close}")
    print("  CONVENTION: the index stamp is the bar's OPEN time. A 15m bar")
    print("  stamped T covers [T, T+15) and its CLOSE is only knowable at T+15.")
    print("  ASSERTION: no signal derived from a bar's close may be acted on")
    print("  before T+15. The engine enforces this by shifting the state index")
    print("  forward one full bar before reindexing onto the finer series.")
    return ok_open and ok_close


# --------------------------------------------------------------------- A2/A3
def run_unshifted(state15, d5, slip, stop_atr=0.0, a5=None):
    """The OLD, BROKEN path, kept solely as a positive control for the battery.

    Identical to research.au200_ma.run except the state is NOT shifted and the
    fill is at the 5m close. This is the code that produced PF 1.889.
    """
    o, h, l, c = (d5[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    tgt = state15.reindex(d5.index, method="ffill").fillna(0).to_numpy().astype(np.int8)
    day = d5.index.normalize().to_numpy()
    tr = []; pos = None
    for i in range(1, len(c)):
        if pos is not None:
            d, e = pos["d"], pos["e"]
            if np.isfinite(pos["stop"]) and ((l[i] <= pos["stop"]) if d > 0
                                             else (h[i] >= pos["stop"])):
                px = pos["stop"] - d * slip
                tr.append(dict(pnl=d * (px - e) - 2.0, day=pos["day"])); pos = None
            elif tgt[i] != d:
                px = c[i] - d * slip
                tr.append(dict(pnl=d * (px - e) - 2.0, day=pos["day"])); pos = None
        if pos is None and tgt[i] != 0:
            d = int(tgt[i])
            st = c[i] - d * stop_atr * a5[i] if (stop_atr > 0 and a5 is not None) else np.nan
            pos = dict(d=d, e=c[i] + d * slip, pk=c[i], stop=st, day=day[i])
    return pd.DataFrame(tr)


# --------------------------------------------------------------------- synth
def synthetic(d5, seed):
    """Return-shuffled twin of the real 5m series.

    Log returns are permuted, so the marginal distribution, the volatility and
    the bar/session structure are preserved exactly while every temporal
    relationship -- trend, autocorrelation, time-of-day effect -- is destroyed.
    Intrabar shape (high/low/open relative to close) travels with its own bar so
    bar ranges stay realistic. Volume is carried unchanged.
    """
    rng = np.random.default_rng(seed)
    c = d5["close"].to_numpy(float)
    r = np.diff(np.log(c), prepend=np.log(c[0]))
    hr = np.log(d5["high"].to_numpy(float) / c)
    lr = np.log(d5["low"].to_numpy(float) / c)
    orr = np.log(d5["open"].to_numpy(float) / c)
    p = rng.permutation(len(r))
    nc = np.exp(np.log(c[0]) + np.cumsum(r[p]))
    out = pd.DataFrame({"open": nc * np.exp(orr[p]), "high": nc * np.exp(hr[p]),
                        "low": nc * np.exp(lr[p]), "close": nc},
                       index=d5.index)
    out["volume"] = d5["volume"].to_numpy()[p]
    out["high"] = out[["high", "open", "close"]].max(axis=1)
    out["low"] = out[["low", "open", "close"]].min(axis=1)
    return out


def to15(d5):
    return d5.resample("15min").agg({"open": "first", "high": "max", "low": "min",
                                     "close": "last", "volume": "sum"}).dropna()


# --------------------------------------------------------------------- B
def baseline_state(d5, kind, seed=11, n_target=2400, win=(10, 16)):
    """Naive baselines as a per-5m-bar target-direction series."""
    hh = d5.index.hour.to_numpy()
    n = len(d5)
    if kind == "B1":                       # always long in the cash session
        return pd.Series(np.where((hh >= win[0]) & (hh < win[1]), 1, 0).astype(np.int8),
                         index=d5.index)
    if kind == "B2":                       # always long, all day
        return pd.Series(np.ones(n, np.int8), index=d5.index)
    if kind in ("B3", "B4"):               # random entries, matched frequency
        rng = np.random.default_rng(seed)
        ok = ((hh >= win[0]) & (hh < win[1])) if kind == "B3" else np.ones(n, bool)
        idx = np.flatnonzero(ok)
        pick = rng.choice(idx, size=min(n_target, len(idx)), replace=False)
        s = np.zeros(n, np.int8); s[np.sort(pick)] = 1
        # hold until the exit rule fires: represent as a one-bar impulse the
        # engine turns into a position, so entry frequency is what is matched
        return pd.Series(s, index=d5.index)
    raise ValueError(kind)


def hold_engine(sig5, d5, slip, stop_atr=3.0, a5=None, flat_hour=16):
    """Baseline engine: enter on the impulse, exit on 3xATR stop or session close.

    Deliberately simple and path-robust -- no trail, no flip, no sub-point logic.
    Fills at the bar OPEN, matching the corrected strategy engine.
    """
    o, h, l, c = (d5[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    s = sig5.to_numpy()
    hh = d5.index.hour.to_numpy(); day = d5.index.normalize().to_numpy()
    tr = []; pos = None
    for i in range(1, len(c)):
        if pos is not None:
            d, e = pos["d"], pos["e"]
            if (l[i] <= pos["stop"]) if d > 0 else (h[i] >= pos["stop"]):
                fill = min(pos["stop"], o[i]) if d > 0 else max(pos["stop"], o[i])
                px = fill - d * slip
                tr.append(dict(pnl=d * (px - e) - 2.0, day=pos["day"])); pos = None
            elif hh[i] >= flat_hour or day[i] != pos["day"]:
                px = o[i] - d * slip
                tr.append(dict(pnl=d * (px - e) - 2.0, day=pos["day"])); pos = None
        if pos is None and s[i] != 0:
            d = int(s[i])
            pos = dict(d=d, e=o[i] + d * slip, stop=o[i] - d * stop_atr * a5[i],
                       day=day[i])
    return pd.DataFrame(tr)
