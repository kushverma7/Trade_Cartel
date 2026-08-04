"""
Target-before-stop probabilities across an ATR grid.

METHOD. For each signal the forward path is walked ONCE, recording for every
bar the running favourable excursion and running adverse excursion in ATR.
A (target, stop) pair is then resolved by comparing the first bar at which each
threshold is crossed. This gives identical answers to walking the path per
combination, at 1/63rd of the cost.

AMBIGUITY. If both thresholds are first crossed on the SAME bar the true order
is unknowable at 30m resolution. Those are counted as LOSSES (stop-first, the
conservative branch) and reported separately, because on wide targets they are
frequent enough to change the conclusion.
"""
import numpy as np, pandas as pd
from backtest import exit_lab

TGTS  = [0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 2.00, 2.50, 3.00]
STOPS = [0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 2.00]


def paths(df, sL, sS, horizon=200, atr_n=14):
    """Per signal: bar index at which each ATR threshold is first crossed."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    A = exit_lab._atr(h, l, c, atr_n)
    n = len(c)
    out = []
    for i in np.where(sL | sS)[0]:
        j = i + 1
        if j + horizon >= n:
            continue
        d = 1 if sL[i] else -1
        a = A[i]
        if not np.isfinite(a) or a <= 0:
            continue
        entry = o[j]
        hh, ll = h[j:j + horizon], l[j:j + horizon]
        fav = ((hh - entry) if d > 0 else (entry - ll)) / a
        adv = ((entry - ll) if d > 0 else (hh - entry)) / a
        out.append((d, np.maximum.accumulate(fav), np.maximum.accumulate(adv)))
    return out


def _first(run, thr):
    w = np.argmax(run >= thr)
    return w if run[w] >= thr else 10 ** 9


def grid(P, tgts=TGTS, stops=STOPS, sel=None):
    rows = []
    for t in tgts:
        for s in stops:
            win = loss = neither = ambig = 0
            for d, fav, adv in P:
                if sel is not None and d != sel:
                    continue
                ft, fs = _first(fav, t), _first(adv, s)
                if ft == 10 ** 9 and fs == 10 ** 9:
                    neither += 1
                elif ft < fs:
                    win += 1
                elif fs < ft:
                    loss += 1
                else:
                    ambig += 1; loss += 1          # same bar -> conservative
            tot = win + loss + neither
            res = win + loss
            p = win / res if res else np.nan
            be = s / (s + t)                        # break-even hit rate
            rows.append({"target": t, "stop": s, "n": tot, "resolved": res,
                         "hit%": 100 * p, "breakeven%": 100 * be,
                         "edge": p * t - (1 - p) * s if res else np.nan,
                         "ambig%": 100 * ambig / res if res else np.nan,
                         "unresolved%": 100 * neither / tot if tot else np.nan})
    return pd.DataFrame(rows)
