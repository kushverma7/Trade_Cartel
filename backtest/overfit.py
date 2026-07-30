"""
Overfitting diagnostics: Deflated Sharpe Ratio and Probability of Backtest
Overfitting.

Ported from stefan-jansen/machine-learning-for-trading
(16_strategy_simulation/12_dsr_validation.py) and Bailey & Lopez de Prado,
"The Deflated Sharpe Ratio" (2014) / "The Probability of Backtest
Overfitting" (2015).

WHY THIS MATTERS HERE. This repo has tried ~17 configurations and reports
the best one. That is a selection process, and a selection process applied
to noise produces good-looking winners on its own. The synthetic-data run
in backtest/README.md made the point concretely: greedy search over
random-walk bars produced train PF 1.730.

DSR answers the question directly: given that N attempts were made and the
Sharpe ratios of those attempts varied by this much, how surprising is the
best one? A DSR near 0.5 means the winner is exactly what chance would have
produced anyway. Only a DSR above ~0.95 is evidence of skill.
"""
import numpy as np
from scipy import stats
from itertools import combinations

EULER = 0.5772156649015329


def deflated_sharpe_ratio(observed_sharpe, n_samples, n_trials=1,
                          variance_trials=0.0, skewness=0.0, kurtosis=3.0):
    """Probability the true Sharpe exceeds zero, after deflating for the
    number of trials that were run. Inputs in per-observation units."""
    if n_trials <= 1 or variance_trials <= 0:
        expected_max = 0.0
    else:
        z1 = stats.norm.ppf(1.0 - 1.0 / n_trials)
        z2 = stats.norm.ppf(1.0 - np.exp(-1.0) / n_trials)
        expected_max = np.sqrt(variance_trials) * ((1 - EULER) * z1 + EULER * z2)
    denom = np.sqrt(max(1.0 - skewness * observed_sharpe
                        + ((kurtosis - 1.0) / 4.0) * observed_sharpe ** 2, 1e-12))
    z = ((observed_sharpe - expected_max) * np.sqrt(max(n_samples - 1, 1))) / denom
    return {"dsr": float(stats.norm.cdf(z)),
            "expected_max_sharpe": float(expected_max),
            "adjusted_sharpe": float(observed_sharpe - expected_max),
            "z": float(z)}


def sharpe_from_pnl(pnl):
    """Per-trade Sharpe and its higher moments from a P&L series."""
    p = np.asarray(pnl, float)
    if len(p) < 2 or p.std(ddof=1) == 0:
        return dict(sr=np.nan, n=len(p), skew=0.0, kurt=3.0)
    return dict(sr=float(p.mean() / p.std(ddof=1)), n=len(p),
                skew=float(stats.skew(p)), kurt=float(stats.kurtosis(p, fisher=False)))


def sr_from_pf_wr(pf, wr, n):
    """Reconstruct a per-trade Sharpe from the only three numbers most of
    this repo's historical results recorded.

    ASSUMPTION, stated because it matters: every win is the same size and
    every loss is the same size. Real trade distributions are fatter-tailed
    than that, which makes the reconstructed Sharpe OPTIMISTIC. Treat the
    output as an upper bound, not a measurement.
    """
    wr = wr / 100.0 if wr > 1 else wr
    if not (0 < wr < 1) or pf <= 0:
        return np.nan
    ratio = pf * (1 - wr) / wr           # avg win / avg loss
    mu = wr * ratio - (1 - wr)
    var = wr * (ratio - mu) ** 2 + (1 - wr) * (-1 - mu) ** 2
    return float(mu / np.sqrt(var)) if var > 0 else np.nan


def pbo_cscv(returns_matrix, n_blocks=10):
    """Probability of Backtest Overfitting via combinatorially symmetric CV.

    returns_matrix: (T observations x N configurations).
    Splits the timeline into n_blocks, takes every way of choosing half the
    blocks as in-sample, picks the config that wins in-sample, and records
    where it ranks out-of-sample. PBO is the share of splits where the
    in-sample winner lands in the BOTTOM half out of sample.

    PBO > 0.5 means the selection procedure is worse than picking at random.
    """
    M = np.asarray(returns_matrix, float)
    T, N = M.shape
    if N < 2:
        return dict(pbo=np.nan, n_splits=0, note="needs >= 2 configurations")
    n_blocks -= n_blocks % 2
    blocks = np.array_split(np.arange(T), n_blocks)
    lam = []
    for combo in combinations(range(n_blocks), n_blocks // 2):
        tr = np.concatenate([blocks[b] for b in combo])
        te = np.concatenate([blocks[b] for b in range(n_blocks) if b not in combo])
        def sr(idx):
            sub = M[idx]
            sd = sub.std(axis=0, ddof=1)
            return np.where(sd > 0, sub.mean(axis=0) / np.where(sd > 0, sd, 1), -np.inf)
        best = int(np.argmax(sr(tr)))
        oos = sr(te)
        rank = float(stats.rankdata(oos)[best] / N)      # 1.0 = best OOS
        lam.append(np.log(rank / (1 - rank)) if 0 < rank < 1 else 0.0)
    lam = np.array(lam)
    return dict(pbo=float((lam <= 0).mean()), n_splits=len(lam),
                median_logit=float(np.median(lam)))
