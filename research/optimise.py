"""
Staged parameter search with a strictly chronological 60/20/20 split.

DISCIPLINE THIS FILE ENFORCES
  * TRAIN (first 60%) is the ONLY window the search may read.
  * VALIDATION (next 20%) is read once per stage, to choose between finalists.
  * TEST (final 20%) is not touched until `--stage test` is run, which happens
    after the parameter set is frozen and written to frozen.json.
  * Every combination actually executed is written to CSV. The reported count is
    len(that file), never an estimate.

SCORING
  Ranking is NOT by net profit. A combination is scored on out-of-sample-like
  qualities: profit factor, return per unit of drawdown, and consistency, with
  hard rejection filters applied first.
"""
import argparse, itertools, json, time
import numpy as np, pandas as pd
from backtest.io import load_csv
from backtest import champion as ch, exit_lab

SPLIT = (0.60, 0.80)


def windows(df):
    n = len(df)
    a, b = int(n * SPLIT[0]), int(n * SPLIT[1])
    return df.iloc[:a], df.iloc[a:b], df.iloc[b:]


def metrics(tr, df, label=""):
    """Everything the brief asks be stored per combination."""
    if len(tr) < 5:
        return None
    s = exit_lab.stats(tr)
    d = pd.DataFrame(tr)
    d["date"] = [df.index[b] for b in d["bar"]]
    p = d.pnl.values
    w, l = p[p > 0], p[p <= 0]
    yrs = (df.index[-1] - df.index[0]).days / 365.25
    eq = 10000 + np.cumsum(p)
    rel = p / (10000 + np.concatenate([[0], np.cumsum(p)]))[:-1]
    # streaks
    run = mx = 0
    for x in (p > 0):
        if not x:
            run += 1; mx = max(mx, run)
        else:
            run = 0
    # consistency
    mon = d.groupby(d.date.dt.to_period("M")).pnl.sum()
    yr = d.groupby(d.date.dt.year).pnl.sum()
    top_month = mon.max() / p.sum() if p.sum() > 0 else np.nan
    sharpe = rel.mean() / rel.std() * np.sqrt(len(rel) / yrs) if rel.std() > 0 else np.nan
    dn = rel[rel < 0]
    sortino = rel.mean() / dn.std() * np.sqrt(len(rel) / yrs) if len(dn) > 1 and dn.std() > 0 else np.nan
    return dict(
        label=label, n=s["n"], n_long=int((d.dir > 0).sum()), n_short=int((d.dir < 0).sum()),
        wr=s["wr"], pf=s["pf"], net_pct=s["net_pct"], maxdd=s["maxdd_pct"],
        rdd=s["rdd"], avg_win=w.mean() if len(w) else 0, avg_loss=l.mean() if len(l) else 0,
        med_win=np.median(w) if len(w) else 0, med_loss=np.median(l) if len(l) else 0,
        expectancy_r=p.mean() / abs(np.median(l)) if len(l) else np.nan,
        sharpe=sharpe, sortino=sortino,
        med_mfe_pts=np.nan, longest_loss_streak=mx,
        months_pos=100 * (mon > 0).mean(), years_pos=100 * (yr > 0).mean(),
        top_month_share=100 * top_month,
        bars_held=s["avg_bars"],
    )


def reject(m):
    """Hard filters, applied BEFORE any ranking. Returns a reason or None."""
    if m is None:                       return "no trades"
    if m["n"] < 120:                    return "too few signals"
    if m["maxdd"] > 55:                 return "drawdown > 55%"
    if m["pf"] < 1.15:                  return "profit factor < 1.15"
    if m["top_month_share"] > 40:       return "one month is >40% of profit"
    if m["months_pos"] < 40:            return "fewer than 40% of months positive"
    return None


def score(m):
    """Rank on robustness-flavoured qualities, deliberately NOT on net profit."""
    return (m["pf"] * 2.0
            + min(m["rdd"], 60) / 30.0
            + m["months_pos"] / 50.0
            + m["years_pos"] / 100.0
            - max(0, m["maxdd"] - 35) / 20.0
            - max(0, m["top_month_share"] - 25) / 20.0)


def run_cfg(df, c):
    tr, _ = ch.run(df,
                   lb_over=dict(entry=c["entry"], ema=c["ema"], sma=c["sma"],
                                sma2=c["sma2"], slope=c["slope"]),
                   trail_atr=c["trail"], cooldown=c["cooldown"],
                   pyr=dict(pyr_atr=1.5, pyr_max=4, pyr_mode="vol_entry"),
                   tighten_after=20, tighten_to=2.0, frac_qty=True)
    return tr


def search(df, grid, tag):
    keys = list(grid)
    rows, t0 = [], time.time()
    for i, vals in enumerate(itertools.product(*[grid[k] for k in keys])):
        c = dict(zip(keys, vals))
        m = metrics(run_cfg(df, c), df)
        r = {**c}
        why = reject(m)
        r["rejected"] = why or ""
        if m:
            r.update({k: v for k, v in m.items() if k != "label"})
            r["score"] = score(m) if not why else np.nan
        rows.append(r)
        if (i + 1) % 200 == 0:
            print(f"    {tag}: {i+1} combos, {time.time()-t0:.0f}s", flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(f"research/opt_{tag}.csv", index=False)
    print(f"  {tag}: EXECUTED {len(out)} combinations in {time.time()-t0:.0f}s "
          f"({(out.rejected=='').sum()} passed the rejection filters)", flush=True)
    return out
