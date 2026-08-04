"""
Per-signal MFE / MAE analysis for the champion's ENTRY SIGNAL.

WHAT IS BEING MEASURED, AND WHAT IS NOT
  This measures the raw entry signal in isolation -- entry at the OPEN of the
  bar AFTER the signal bar closes, then excursion tracked forward. It says
  nothing about the shipped strategy's P&L, which uses a trailing exit and
  pyramiding. The point is to characterise what the signal alone is worth, so
  that exit design can be argued from evidence rather than preference.

ENTRY ASSUMPTION (stated, not buried)
  Signal confirms on the CLOSE of bar N. Entry is the OPEN of bar N+1.
  No use of bar N's intrabar path. No use of any bar beyond the measurement
  window. Longs and shorts kept separate throughout.

SAME-BAR AMBIGUITY
  On a 30m bar a stop and a target can both sit inside the range. Without
  lower-timeframe data the true order is unknowable. This module resolves such
  bars as STOP-FIRST (the conservative branch) and reports how often it happens
  so the reader can judge how much the answer rests on that choice.
"""
import numpy as np, pandas as pd
from backtest.io import load_csv
from backtest import champion as ch, exit_lab

HOLDS = [3, 5, 10, 15, 20, 30, 50]


def build(rule="30min"):
    df = load_csv("data/xauusd_15m.csv.gz", rule=rule)
    lb = ch.lookbacks(df, "bars", 30.0 if rule == "30min" else 15.0)
    lb["sma2"] = 630
    sL, sS = ch.signals(df, lb)
    return df, sL, sS, lb


def excursions(df, sL, sS, atr_n=14):
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    A = exit_lab._atr(h, l, c, atr_n)
    idx = df.index
    n = len(c)
    maxh = max(HOLDS)
    rows = []
    for i in np.where(sL | sS)[0]:
        j = i + 1                                  # entry bar = signal bar + 1
        if j + maxh >= n:
            continue
        d = 1 if sL[i] else -1
        entry = o[j]                               # OPEN of the next bar
        a = A[i]                                   # ATR as known at signal close
        if not np.isfinite(a) or a <= 0:
            continue
        r = {"i": i, "entry_bar": j, "time": idx[j], "dir": d,
             "entry": entry, "atr": a,
             "hour": idx[j].hour, "dow": idx[j].dayofweek}
        for H in HOLDS:
            w = slice(j, j + H)                    # window never exceeds H bars
            hi, lo = h[w].max(), l[w].min()
            mfe = (hi - entry) if d > 0 else (entry - lo)
            mae = (entry - lo) if d > 0 else (hi - entry)
            r[f"mfe_{H}"] = mfe
            r[f"mae_{H}"] = mae
            r[f"mfe_atr_{H}"] = mfe / a
            r[f"mae_atr_{H}"] = mae / a
            # bars until the extreme, measured inside the same window only
            r[f"bars_mfe_{H}"] = int(np.argmax(h[w]) if d > 0 else np.argmin(l[w]))
            r[f"bars_mae_{H}"] = int(np.argmin(l[w]) if d > 0 else np.argmax(h[w]))
            cl = c[w]
            r[f"maxfclose_{H}"] = (cl.max() - entry) if d > 0 else (entry - cl.min())
            r[f"maxaclose_{H}"] = (entry - cl.min()) if d > 0 else (cl.max() - entry)
            r[f"ret_{H}"] = d * (c[j + H - 1] - entry)
        rows.append(r)
    return pd.DataFrame(rows)


def first_passage(df, sig, tgt_atr, stop_atr, horizon=200, atr_n=14):
    """Target-before-stop, bar by bar. Ambiguous bars resolve to the STOP."""
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    A = exit_lab._atr(h, l, c, atr_n)
    n = len(c)
    win = loss = neither = ambig = 0
    for i in np.where(sig != 0)[0]:
        j = i + 1
        if j + horizon >= n:
            continue
        d = sig[i]
        a = A[i]
        if not np.isfinite(a) or a <= 0:
            continue
        entry = o[j]
        tp = entry + d * tgt_atr * a
        sl = entry - d * stop_atr * a
        done = False
        for k in range(j, j + horizon):
            hit_t = (h[k] >= tp) if d > 0 else (l[k] <= tp)
            hit_s = (l[k] <= sl) if d > 0 else (h[k] >= sl)
            if hit_t and hit_s:
                ambig += 1; loss += 1; done = True; break
            if hit_t:
                win += 1; done = True; break
            if hit_s:
                loss += 1; done = True; break
        if not done:
            neither += 1
    return win, loss, neither, ambig
