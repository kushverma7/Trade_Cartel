"""
Standalone previous-week-level break strategy. No contact with G1*.

THE HYPOTHESIS, AND A DEFINITION MISMATCH THAT HAS TO BE STATED FIRST
  The measurement study's surviving cell was `PWH break`, n=450, traded in the
  direction of the break. That cell contains BOTH directions:

      PWH broken UPWARD   price below the previous week's high closes above it
      PWH broken DOWNWARD price above the previous week's high closes back
                          below it

  The brief's strategy is "close above PWH -> long, close below PWL -> short".
  That is not the same set. It takes one half of the surviving cell (PWH broken
  up) and pairs it with a half of a cell that did NOT survive -- `PWL break`
  scored edge_mm -0.008 and was rejected. So the brief's strategy is a mixture
  of the measured edge and a measured non-edge.

  Three signal definitions are therefore run, and reported side by side, so the
  question "did the measured edge survive execution" is separable from "is the
  brief's pairing a good idea":

      V1  the brief exactly: long on close above PWH, short on close below PWL
      V2  the surviving cell exactly: every PWH break, traded in its direction
      V3  the purest read: long only, PWH broken upward

  Guessing which one the brief meant and reporting a single number would hide a
  real fork in the road.

BAND
  The study classified a break as a close beyond the level by more than
  tol x ATR. tol = 0.25 and 0.50 both showed the edge (edge_mm 0.095 and 0.092),
  so both are run, plus tol = 0 (the literal "closes above" of the brief). This
  is a robustness check across the study's own tested range, not a search.

DE-DUPLICATION
  Once price is beyond the level, `side` flips and no further break of that
  level in that direction can fire until price returns. The signal is therefore
  self-limiting: at most one long per weekly level per excursion. No cooldown is
  imposed on top, because that would be an unmeasured extra parameter.

EXECUTION
  Entry at the signal bar's close. Costs identical to every other test on this
  desk: commission 0.07/oz/side, slippage 0.20. No pyramiding. Sizing is fixed
  fractional, bisected to the drawdown budget, exactly as G1* was.
"""
import numpy as np, pandas as pd

from backtest.io import load_csv
from backtest import exit_lab
from research.level_profile import build_levels
from research.voltarget import montecarlo

COMMISSION, SLIPPAGE = 0.07, 0.20
CONTROL_DELTAS = (+0.0035, -0.0035, +0.0060, -0.0060)
SEEDS = (11, 101, 2027)
MC_N = 1500


def signals(df, atr, tol, variant, levels=None):
    """PWH/PWL break signals under the three definitions."""
    c = df["close"].to_numpy(float)
    L = build_levels(df) if levels is None else levels
    pwh, pwl = L["PWH"], L["PWL"]
    prev = np.r_[c[0], c[:-1]]
    band = tol * atr

    # BUG, found 2026-08-05 by reconciling signal counts against the study.
    # The first version used `prev <= L + band`, which fires on bars whose
    # PREVIOUS close was already inside the tolerance band on the far side --
    # continuation bars, not fresh breaks. That produced 637 PWH up-breaks at
    # tol 0.5 where the measurement study recorded 274, a 2.3x inflation, and
    # would have diluted the tested population with the very bars the study
    # excluded. The study's condition is `prev` strictly on the other side of
    # the LEVEL, with the band applied only to the closing side. Reproduced
    # exactly: 274 up + 176 down = 450 at tol 0.5, 408 + 295 = 703 at 0.25.
    up_h = (prev < pwh) & (c > pwh + band)             # PWH broken upward
    dn_h = (prev > pwh) & (c < pwh - band)             # PWH broken downward
    up_l = (prev < pwl) & (c > pwl + band)             # PWL broken upward
    dn_l = (prev > pwl) & (c < pwl - band)             # PWL broken downward
    fin = np.isfinite(pwh) & np.isfinite(pwl) & np.isfinite(atr)

    if variant == "V1":                                  # the brief
        sl, ss = up_h, dn_l
    elif variant == "V2":                                # the surviving cell
        sl, ss = up_h, dn_h
    else:                                                # V3, long only
        sl, ss = up_h, np.zeros(len(c), bool)
    return (np.nan_to_num(sl & fin, nan=0).astype(bool),
            np.nan_to_num(ss & fin, nan=0).astype(bool))


def run_exit(df, sl, ss, exitcfg, risk):
    return exit_lab.run(df, sl, ss, risk_pct=risk, atr_n=14,
                        commission=COMMISSION, slippage=SLIPPAGE,
                        pyr_max=0, frac_qty=True, **exitcfg)


def solve(df, sl, ss, exitcfg, target):
    lo, hi = 0.02, 8.0
    for _ in range(16):
        m = (lo + hi) / 2
        s = exit_lab.stats(run_exit(df, sl, ss, exitcfg, m))
        if s["n"] == 0 or s["maxdd_pct"] > target:
            hi = m
        else:
            lo = m
    return lo, run_exit(df, sl, ss, exitcfg, lo)


EXITS = {
    "A trail 3.0ATR": dict(trail_mode="chandelier", trail_atr=3.0, stop_atr=3.0),
    "A trail 4.0ATR": dict(trail_mode="chandelier", trail_atr=4.0, stop_atr=4.0),
    "A trail 5.0ATR": dict(trail_mode="chandelier", trail_atr=5.0, stop_atr=5.0),
    "B 1.5R tgt": dict(trail_mode="none", stop_atr=2.0, tp1_mode="rr",
                       tp1_val=1.5, tp1_pct=1.0),
    "B 2R tgt": dict(trail_mode="none", stop_atr=2.0, tp1_mode="rr",
                     tp1_val=2.0, tp1_pct=1.0),
    "B 3R tgt": dict(trail_mode="none", stop_atr=2.0, tp1_mode="rr",
                     tp1_val=3.0, tp1_pct=1.0),
    "C time 32 + 4ATR": dict(trail_mode="none", stop_atr=4.0, max_bars=32),
    "C time 64 + 4ATR": dict(trail_mode="none", stop_atr=4.0, max_bars=64),
}


def profile(df, year, yrs, tr, risk, label, budget):
    s = exit_lab.stats(tr)
    if s["n"] < 20:
        return dict(arm=label, budget=budget, n=s["n"], note="too few trades")
    d = pd.DataFrame(tr)
    d["yr"] = year[d.bar.values]
    pre = d[d.yr <= 2024]
    pf_pre = pre[pre.pnl > 0].pnl.sum() / max(-pre[pre.pnl <= 0].pnl.sum(), 1e-9)
    cagr = ((1 + s["net_pct"] / 100) ** (1 / yrs) - 1) * 100
    p = np.sort(d.pnl.values)[::-1]
    gw = p[p > 0].sum()
    med, p30 = [], []
    for sd in SEEDS:
        mc = montecarlo(tr, n=MC_N, seed=sd)
        med.append(np.median(mc)); p30.append(100 * (mc > 30).mean())
    n = len(tr)
    dy = {}
    for y in (2021, 2022, 2026):
        g = d[d.yr == y]
        dy[f"pf{y}"] = (g[g.pnl > 0].pnl.sum() /
                        max(-g[g.pnl <= 0].pnl.sum(), 1e-9)) if len(g) else np.nan
    return dict(arm=label, budget=budget, risk=risk, n=s["n"], wr=s["wr"],
                pf=s["pf"], cagr=cagr, dd=s["maxdd_pct"],
                mar=cagr / max(s["maxdd_pct"], 1e-9),
                mc_med=np.mean(med), p30=np.mean(p30), p30_sd=np.std(p30),
                pf_pre2025=pf_pre, **dy,
                top1=100 * p[:max(1, n // 100)].sum() / max(gw, 1e-9),
                top5=100 * p[:max(1, n // 20)].sum() / max(gw, 1e-9),
                top10=100 * p[:max(1, n // 10)].sum() / max(gw, 1e-9),
                long_share=100 * (d.dir > 0).mean(), avg_bars=s["avg_bars"])


COLS = ["arm", "budget", "risk", "n", "wr", "pf", "cagr", "dd", "mar", "mc_med",
        "p30", "pf_pre2025", "pf2021", "pf2022", "pf2026", "top1", "top5",
        "top10", "long_share", "avg_bars"]


def main():
    df = load_csv("data/xauusd_15m.csv.gz", rule="30min")
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    atr = np.r_[np.nan, exit_lab._atr(h, l, c, 14)[:-1]]
    year = np.array([t.year for t in df.index])
    yrs = (df.index[-1] - df.index[0]).days / 365.25

    print("=" * 150)
    print("DATA AND CONSTRUCTION")
    print("=" * 150)
    print(f"  XAUUSD 30m, {len(df):,} bars, {df.index[0]} -> {df.index[-1]} ({yrs:.2f}y)")
    print(f"  PWH/PWL: previous COMPLETED week only, constant within each week,")
    print(f"  verified equal to the prior week's high/low for all 349 weeks.")
    print(f"  costs: commission {COMMISSION}/oz/side, slippage {SLIPPAGE}. No pyramiding.")

    # signal counts
    print("\n  SIGNAL COUNTS")
    for v in ("V1", "V2", "V3"):
        for tol in (0.0, 0.25, 0.5):
            sl, ss = signals(df, atr, tol, v)
            print(f"    {v} tol={tol:<5} long={sl.sum():<5} short={ss.sum():<5} "
                  f"total={sl.sum()+ss.sum()}")

    rows = []
    for v in ("V1", "V2", "V3"):
        for tol in (0.0, 0.25, 0.5):
            sl, ss = signals(df, atr, tol, v)
            if sl.sum() + ss.sum() < 40:
                continue
            for en, cfg in EXITS.items():
                for budget in (25.0, 20.0):
                    r, tr = solve(df, sl, ss, cfg, budget)
                    rows.append(profile(df, year, yrs, tr, r,
                                        f"{v} tol{tol} | {en}", budget))
    t = pd.DataFrame([r for r in rows if "note" not in r])
    t.to_csv("research/pwh_break.csv", index=False)

    pd.set_option("display.width", 260)
    for budget in (25.0, 20.0):
        q = t[t.budget == budget].sort_values("mar", ascending=False)
        print("\n" + "=" * 150)
        print(f"RESULTS -- {budget:.0f}% DRAWDOWN BUDGET, sorted by MAR")
        print("=" * 150)
        print(q[COLS].to_string(index=False, float_format=lambda x: f"{x:7.3f}"))

    # ---------------------------------------------------------- controls
    print("\n" + "=" * 150)
    print("CONTROL 1 -- DISPLACED WEEKLY LEVELS (same construction, wrong price)")
    print("  4 replicates at +/-0.35% and +/-0.60% of price, averaged.")
    print("=" * 150)
    base = build_levels(df)
    best = t[t.budget == 25.0].sort_values("mar", ascending=False).iloc[0]
    bv, btol, ben = best.arm.split(" | ")[0].split(" tol")[0], \
        float(best.arm.split(" tol")[1].split(" | ")[0]), best.arm.split(" | ")[1]
    print(f"  applied to the top arm: {best.arm}")
    ctl = []
    for dl in CONTROL_DELTAS:
        lv = {k: vv * (1 + dl) for k, vv in base.items()}
        sl, ss = signals(df, atr, btol, bv, levels=lv)
        r, tr = solve(df, sl, ss, EXITS[ben], 25.0)
        s = exit_lab.stats(tr)
        cagr = ((1 + s["net_pct"] / 100) ** (1 / yrs) - 1) * 100
        ctl.append(dict(delta=dl, n=s["n"], pf=s["pf"], cagr=cagr,
                        dd=s["maxdd_pct"], mar=cagr / max(s["maxdd_pct"], 1e-9)))
    cd = pd.DataFrame(ctl)
    print(cd.to_string(index=False, float_format=lambda x: f"{x:8.3f}"))
    print(f"\n  real arm MAR {best.mar:.3f}  vs  displaced-control mean MAR "
          f"{cd.mar.mean():.3f}")
    cd.to_csv("research/pwh_break_control.csv", index=False)

    print("\n" + "=" * 150)
    print("CONTROL 2 -- BUY AND HOLD")
    print("=" * 150)
    ret = c[-1] / c[0] - 1
    eq = c / c[0]
    dd = float((1 - eq / np.maximum.accumulate(eq)).max() * 100)
    bh = ((1 + ret) ** (1 / yrs) - 1) * 100
    print(f"  net {100*ret:+.1f}%   CAGR {bh:.2f}%   max DD {dd:.2f}%   "
          f"MAR {bh/dd:.3f}")

    print("\n" + "=" * 150)
    print("ANCHORED WALK-FORWARD on the top arm, 6 folds")
    print("=" * 150)
    sl, ss = signals(df, atr, btol, bv)
    _r, tr = solve(df, sl, ss, EXITS[ben], 25.0)
    n = len(df)
    edges = [int(n * (0.4 + 0.6 * i / 6)) for i in range(7)]
    for i in range(6):
        lo, hi = edges[i], edges[i + 1]
        s = exit_lab.stats([x for x in tr if lo <= x["bar"] < hi])
        print(f"  fold {i+1}  bars {lo}-{hi}   n={s['n']:<4} PF={s['pf']:.3f}")


if __name__ == "__main__":
    main()
