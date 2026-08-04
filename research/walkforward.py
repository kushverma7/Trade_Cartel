"""Rolling walk-forward: optimise on 12 months, trade the next 3, step 3."""
import numpy as np, pandas as pd
from backtest import exit_lab
from research.optimise import run_cfg, metrics, reject, score


def walk(df, grid_list, train_m=12, test_m=3, step_m=3):
    out, chosen = [], []
    start = df.index[0]
    while True:
        tr_a = start
        tr_b = tr_a + pd.DateOffset(months=train_m)
        te_b = tr_b + pd.DateOffset(months=test_m)
        if te_b > df.index[-1]:
            break
        TR = df[(df.index >= tr_a) & (df.index < tr_b)]
        TE = df[(df.index >= tr_b) & (df.index < te_b)]
        best, bs = None, -1e9
        for c in grid_list:                       # optimise on TRAIN only
            m = metrics(run_cfg(TR, c), TR)
            if m is None or m["n"] < 25 or m["pf"] < 1.0:
                continue
            s = m["pf"] + min(m["rdd"], 40) / 40.0
            if s > bs:
                bs, best = s, c
        if best is None:
            start = start + pd.DateOffset(months=step_m); continue
        mt = metrics(run_cfg(TE, best), TE)       # trade it forward, untouched
        chosen.append(best)
        out.append(dict(train_start=tr_a.date(), test_start=tr_b.date(), test_end=te_b.date(),
                        **{f"p_{k}": v for k, v in best.items()},
                        n=mt["n"] if mt else 0, pf=mt["pf"] if mt else np.nan,
                        net=mt["net_pct"] if mt else 0.0,
                        dd=mt["maxdd"] if mt else np.nan))
        start = start + pd.DateOffset(months=step_m)
    return pd.DataFrame(out), chosen
