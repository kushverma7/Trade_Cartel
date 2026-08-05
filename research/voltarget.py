"""
Volatility targeting on the locked Gold Trend system, as a pure SIZING lever.

WHAT IS AND IS NOT BEING CHANGED
  Unchanged: entry (Donchian + EMA regime + dual SMA, shorts also need falling
  EMA slope), exit (single ratcheting chandelier 4.24 ATR tightening to 2.0
  after +15 ATR), no targets, no time stops, no breakeven, adds 4 x 1.5 ATR
  sized on entry-time ATR, cooldown 30, closed-bar only.
  Changed: how many contracts the entry buys. Nothing else.

THE ARITHMETIC, STATED SO THE IMPLEMENTATION CAN BE CHECKED
  Current sizing is constant-fractional-risk:
      qty = equity * risk% / 100 / (4.24 * ATR)
  Volatility targeting instead holds the position's expected DAILY volatility
  contribution constant:
      qty = equity * volTarget% / 100 / (sigma_daily * price)
  exit_lab sizes through `eff / stop_dist`, so the second is reached from the
  first by a per-bar multiplier

      m_i = (4.24 * ATR_i) / (sigma_daily_i * price_i)

  passed as `risk_series`. Substituting: qty = eq*risk*m/100/sdist
  = eq*risk/(100*sigma_d*px), and the position's daily vol contribution
  qty*px*sigma_d = eq*risk/100 -- constant, which is the definition. Any
  constant factor in m is absorbed by the bisection that solves for the
  drawdown budget, so only the SHAPE of m matters and the estimators can be
  left in their natural units.

  m is normalised to median 1 and clipped to [0.25, 4.0]. The clip is not
  cosmetic: sigma_daily can approach zero in a dead holiday session and an
  unclipped multiplier would then size a position of essentially unbounded
  leverage. It is reported how often the clip binds.

WHY ADDS NEEDED AN ENGINE CHANGE
  `risk_series` applied only to the opening unit -- which is correct for G1,
  whose multiplier is deliberately opening-only. Under volatility targeting an
  add sized at base risk would break the target the moment it filled. The new
  `risk_series_adds` flag applies the ENTRY-TIME multiplier to adds as well,
  which preserves the locked spec's "adds sized on the ATR at entry" character
  rather than re-reading volatility mid-trade. Default False, so G1 and every
  ledger row are untouched; verified by regression before this file was run.

VARIANT C, AND WHY IT IS A GATE RATHER THAN A REBALANCE
  The brief asks for a soft ceiling on open volatility. Prior work established
  that hard-capping open risk destroyed most of the return, so `open_vol_cap`
  never reduces an existing position -- it only declines to make the stack
  larger once its expected daily vol contribution reaches the cap. This is the
  softest intervention that still addresses portfolio heat, and it cannot
  amputate a winner, only stop feeding it.
"""
import numpy as np, pandas as pd

from backtest.io import load_csv
from backtest import champion as ch, exit_lab

BPD = 48                     # 30-minute bars in a 24h gold day
MC_N = 2000
CLIP = (0.25, 4.0)


# --------------------------------------------------------------- estimators
def estimators(df):
    """sigma_daily for each estimator, all in the same units (fraction of price)."""
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    r = pd.Series(np.r_[np.nan, np.diff(np.log(c))])
    out = {}
    for n in (14, 20, 50):
        out[f"ATR{n}"] = exit_lab._atr(h, l, c, n) / c * np.sqrt(BPD)
    # EWMA of |returns|, lambda = 0.94, scaled to a daily sigma
    ew = r.abs().ewm(alpha=1 - 0.94, adjust=False).mean().to_numpy()
    out["EWMA094"] = ew * np.sqrt(BPD) * np.sqrt(np.pi / 2)
    for d in (20, 40):
        out[f"SD{d}d"] = r.rolling(d * BPD).std(ddof=0).to_numpy() * np.sqrt(BPD)
    return out


def vt_series(df, sigma, stop_atr=4.24, atr_n=14):
    """The risk multiplier that converts fixed-fractional into vol targeting."""
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    a = exit_lab._atr(h, l, c, atr_n)
    denom = sigma * c
    m = np.where(denom > 0, (stop_atr * a) / np.where(denom > 0, denom, 1), np.nan)
    med = np.nanmedian(m)
    m = m / med
    clipped = np.isfinite(m) & ((m < CLIP[0]) | (m > CLIP[1]))
    return np.clip(np.nan_to_num(m, nan=1.0), *CLIP), float(clipped.mean())


def g1_series(df):
    """Config G1's regime multiplier, exactly as specified: trend distance from
    the EMA in ATR, times ATR expansion, product clipped to [0.5, 2.0]."""
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    a = exit_lab._atr(h, l, c, 14)
    ema = pd.Series(c).ewm(span=1008, adjust=False).mean().to_numpy()
    trend = np.abs(c - ema) / np.maximum(a, 1e-9)
    fast = pd.Series(a).rolling(20).mean().to_numpy()
    slow = pd.Series(a).rolling(200).mean().to_numpy()
    vexp = np.where(slow > 0, fast / slow, 1.0)
    f1 = np.where(trend > 6.0, 1.30, 0.85)
    f2 = np.where(vexp > 1.10, 1.30, 0.85)
    return np.clip(np.nan_to_num(f1 * f2, nan=1.0), 0.5, 2.0)


# ------------------------------------------------------------------ harness
class Book:
    """One instrument, its estimators, and the locked run configuration."""

    def __init__(self, path, tf="30min"):
        self.df = load_csv(path, rule=tf)
        self.yrs = (self.df.index[-1] - self.df.index[0]).days / 365.25
        self.year = np.array([t.year for t in self.df.index])
        self.est = estimators(self.df)
        self.g1 = g1_series(self.df)

    def run(self, risk, **kw):
        """The LOCKED configuration. Only `risk_series`/caps vary."""
        pyr = dict(pyr_atr=1.5, pyr_max=4, pyr_mode="vol_entry")
        return ch.run(self.df, pyr=pyr, cooldown=30, lb_over=dict(sma2=630),
                      tighten_after=15, tighten_to=2.0, frac_qty=True,
                      risk_pct=risk, **kw)[0]

    def solve(self, target, **kw):
        """Bisection on risk% to land on the drawdown budget."""
        lo, hi = 0.02, 4.0
        for _ in range(16):
            m = (lo + hi) / 2
            s = exit_lab.stats(self.run(m, **kw))
            if s["n"] == 0 or s["maxdd_pct"] > target:
                hi = m
            else:
                lo = m
        return lo, self.run(lo, **kw)


def montecarlo(tr, n=MC_N, seed=11):
    """Shuffle EQUITY-RELATIVE returns, not raw dollars -- under compounding the
    dollar series is path-dependent and reshuffling it is meaningless."""
    d = pd.DataFrame(tr)
    eq = 10000 + np.concatenate([[0], np.cumsum(d.pnl.values)])
    rel = d.pnl.values / eq[:-1]
    rng = np.random.default_rng(seed)
    o = np.empty(n)
    for i in range(n):
        e = np.cumprod(1 + rng.permutation(rel))
        o[i] = (1 - e / np.maximum.accumulate(e)).max() * 100
    return o


def tail(tr):
    """Right-tail diagnosis: is the candidate amputating the big winners?"""
    p = np.sort(np.array([t["pnl"] for t in tr], float))[::-1]
    tot = p[p > 0].sum()
    return dict(top10_share=100 * p[:10].sum() / max(tot, 1e-9),
                biggest_win=float(p[0]),
                n_over_10R=int((np.array([t["points"] / max(t["atr0"] * 4.24, 1e-9)
                                          for t in tr]) > 10).sum()))


def evaluate(book, label, target, **kw):
    risk, tr = book.solve(target, **kw)
    s = exit_lab.stats(tr)
    if s["n"] < 60:
        return None
    d = pd.DataFrame(tr)
    d["yr"] = book.year[d.bar.values]
    pre = d[d.yr <= 2024]
    pf_pre = pre[pre.pnl > 0].pnl.sum() / max(-pre[pre.pnl <= 0].pnl.sum(), 1e-9)
    mc = montecarlo(tr)
    cagr = ((1 + s["net_pct"] / 100) ** (1 / book.yrs) - 1) * 100
    n = len(tr); a, b = n // 3, 2 * n // 3
    losses = -d.pnl[d.pnl < 0]
    r_unit = float(losses.median()) if len(losses) else np.nan
    longs = d[d.dir > 0]
    return dict(
        arm=label, budget=target, risk=risk, n=s["n"], wr=s["wr"], pf=s["pf"],
        net=s["net_pct"], cagr=cagr, dd=s["maxdd_pct"], mar=cagr / s["maxdd_pct"],
        mc_med=float(np.median(mc)), p30=100 * float((mc > 30).mean()),
        pf_pre2025=pf_pre, avg_r=float(d.pnl.mean() / r_unit) if r_unit else np.nan,
        avg_bars=s["avg_bars"], long_share=100 * len(longs) / n,
        pf_tr=exit_lab.stats(tr[:a])["pf"], pf_va=exit_lab.stats(tr[a:b])["pf"],
        pf_te=exit_lab.stats(tr[b:])["pf"], **tail(tr))


COLS = ["arm", "budget", "risk", "n", "wr", "pf", "cagr", "dd", "mar", "mc_med",
        "p30", "pf_pre2025", "avg_r", "avg_bars", "long_share",
        "pf_tr", "pf_va", "pf_te", "top10_share", "n_over_10R"]


def show(rows, title):
    t = pd.DataFrame([r for r in rows if r])[COLS]
    print(f"\n{'=' * 150}\n{title}\n{'=' * 150}")
    print(t.to_string(index=False, float_format=lambda v: f"{v:8.3f}"))
    return t


def main():
    gold = Book("data/xauusd_15m.csv.gz")
    print("LOADED  locked spec: Donchian 12h + EMA regime + dual SMA, shorts need")
    print("        falling slope | chandelier 4.24 ATR -> 2.0 after +15 ATR | no")
    print("        targets, no time stop, no BE | 4 adds x 1.5 ATR on entry ATR |")
    print("        cooldown 30 | sma2 630 | closed-bar only")
    print(f"        gold: {len(gold.df)} 30m bars, {gold.df.index[0].date()} -> "
          f"{gold.df.index[-1].date()} ({gold.yrs:.2f}y)")

    rows = []
    for budget in (25.0, 20.0):
        rows.append(evaluate(gold, "E  (baseline)", budget))
        rows.append(evaluate(gold, "G1 (baseline)", budget,
                             risk_series=gold.g1))
        for nm, sig in gold.est.items():
            m, clip = vt_series(gold.df, sig)
            rows.append(evaluate(gold, f"A: VT {nm}", budget,
                                 risk_series=m, risk_series_adds=True))
            if nm in ("ATR20", "SD20d"):
                rows.append(evaluate(gold, f"B: VT {nm} x G1", budget,
                                     risk_series=m * gold.g1,
                                     risk_series_adds=True))
        for cap in (2.0, 3.0, 4.0):
            rows.append(evaluate(gold, f"C: G1 + open-vol cap {cap:.0f}%", budget,
                                 risk_series=gold.g1,
                                 vol_daily=gold.est["ATR20"], open_vol_cap=cap))

    t = show(rows, "GOLD -- Config E vs G1 vs volatility-targeting variants, "
                   "both drawdown budgets")
    t.to_csv("research/voltarget_gold.csv", index=False)

    print("\nCLIP DIAGNOSTIC -- how often the [0.25, 4.0] multiplier clamp binds:")
    for nm, sig in gold.est.items():
        _m, frac = vt_series(gold.df, sig)
        print(f"  {nm:<10} {100*frac:5.2f}% of bars")


if __name__ == "__main__":
    main()
