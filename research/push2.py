"""DD-budget-matched candidate evaluation with Monte Carlo and regime splits."""
import numpy as np, pandas as pd
from backtest.io import load_csv
from backtest import champion as ch, exit_lab

GD = load_csv("data/xauusd_15m.csv.gz", rule="30min")
YRS = (GD.index[-1] - GD.index[0]).days / 365.25
_h, _l, _c = (GD[k].to_numpy(float) for k in ("high", "low", "close"))
_A = exit_lab._atr(_h, _l, _c, 14)
ATRP = pd.Series(_A / _c, index=GD.index)
VOLR = ATRP.rolling(2000).rank(pct=True).to_numpy()          # volatility percentile
FAST = pd.Series(_A, index=GD.index).rolling(20).mean()
SLOW = pd.Series(_A, index=GD.index).rolling(200).mean()
VEXP = (FAST / SLOW).to_numpy()                              # expansion ratio
EMA = pd.Series(_c, index=GD.index).ewm(span=1008, adjust=False).mean()
TSTR = (np.abs(_c - EMA.to_numpy()) / np.maximum(_A, 1e-9))  # trend strength in ATR
YEAR = np.array([t.year for t in GD.index])
BASE = dict(pyr_atr=1.5, pyr_max=4, pyr_mode="vol_entry")


def run(risk, W=None, **kw):
    W = GD if W is None else W
    pyr = {**BASE}
    for k in list(kw):
        if k.startswith("pyr_"):
            pyr[k] = kw.pop(k)
    return ch.run(W, pyr=pyr, cooldown=kw.pop("cooldown", 30),
                  lb_over=dict(sma2=630),
                  tighten_after=kw.pop("tighten_after", 15),
                  tighten_to=kw.pop("tighten_to", 2.0),
                  frac_qty=True, risk_pct=risk, **kw)[0]


def solve(target=25.0, **kw):
    lo, hi = 0.03, 3.0
    for _ in range(12):
        m = (lo + hi) / 2
        s = exit_lab.stats(run(m, **kw))
        if s["n"] < 60:
            return None
        if s["maxdd_pct"] > target:
            hi = m
        else:
            lo = m
    return lo, run(lo, **kw)


def mc(tr, n=2000):
    d = pd.DataFrame(tr)
    eq = 10000 + np.concatenate([[0], np.cumsum(d.pnl.values)])
    rel = d.pnl.values / eq[:-1]
    rng = np.random.default_rng(11)
    o = []
    for _ in range(n):
        x = rng.permutation(rel)
        e = np.cumprod(1 + x)
        pk = np.maximum.accumulate(e)
        o.append((1 - e / pk).max() * 100)
    return np.array(o)


def evaluate(label, target=25.0, **kw):
    r = solve(target, **kw)
    if r is None:
        return None
    risk, tr = r
    s = exit_lab.stats(tr)
    if s["n"] < 150:
        return None
    m = mc(tr)
    d = pd.DataFrame(tr)
    d["yr"] = [GD.index[b].year for b in d.bar]
    mid = len(tr) // 2
    # regime robustness: drop the 2025-2026 trend entirely
    pre = d[d.yr <= 2024]
    pw = pre[pre.pnl > 0].pnl.sum(); pl = -pre[pre.pnl <= 0].pnl.sum()
    cagr = ((1 + s["net_pct"] / 100) ** (1 / YRS) - 1) * 100
    return dict(label=label, risk=risk, n=s["n"], wr=s["wr"], pf=s["pf"],
                net=s["net_pct"], dd=s["maxdd_pct"], mar=cagr / s["maxdd_pct"],
                mc_med=np.median(m), mc_p95=np.percentile(m, 95),
                p30=100 * (m > 30).mean(),
                h1=exit_lab.stats(tr[:mid])["pf"], h2=exit_lab.stats(tr[mid:])["pf"],
                pf_pre2025=pw / max(pl, 1e-9),
                yrs_pos=sum(1 for _, g in d.groupby("yr") if g.pnl.sum() > 0),
                yrs=d.yr.nunique())
