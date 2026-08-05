"""
The Bollinger squeeze gate, put through every control that has killed a
candidate in this project.

THE RESULT THAT NEEDS EXPLAINING
  Gating the champion's entries to bars where Bollinger bandwidth sits in the
  bottom 40% took net/DD from 27.26 to 46.53 at a matched 25% drawdown, and the
  complement (no squeeze) collapsed to 4.49. Nothing else in seventeen families
  of tested ideas has done that. Which is exactly why it gets audited harder
  than anything that merely looked promising.

THE CONTROLS, AND WHAT EACH ONE WOULD KILL
  1  HALVES        an effect present in one half only is a fitting artifact.
  2  DOWN YEARS    gold went 1450 -> 4100. Any filter that quietly reduces
                   exposure in falling markets tests well for a reason that has
                   nothing to do with edge (B-0xx). 2021 and 2026 are the two
                   down years and are checked in isolation.
  3  US30          the second instrument. Six previous candidates improved gold
                   and degraded US30; that is the signature of gold-specific
                   fitting and it is the control that has killed the most.
  4  THRESHOLD     a cliff means the 40th percentile was chosen by the search.
                   A plateau across 20-60% means the effect is the variable,
                   not the number.
  5  IS IT BOLLINGER, OR IS IT JUST LOW VOLATILITY?
                   Bandwidth is rolling sigma over price. If gating on plain
                   ATR-rank -- a different measure of the same underlying thing
                   -- reproduces the result, then the finding is "enter
                   breakouts out of quiet markets" and Bollinger contributed
                   nothing but a name. This is the control that decides what
                   the finding actually IS.
  6  DOES IT SURVIVE ITS OWN SELECTION?
                   The squeeze arm trades 458 times against the baseline's 789.
                   Fewer trades at higher risk% is a leverage story unless the
                   per-trade quality genuinely improved, so average R and the
                   payoff ratio are reported alongside.
"""
import numpy as np, pandas as pd

from backtest.io import load_csv
from backtest import champion, exit_lab
from research.scalp_checklist import bollinger, solve_risk_kw, report


def atr_rank(df, n=14, win=480):
    from research.source_battery import atr
    a = atr(df, n)
    s = pd.Series(a)
    return s.rolling(win).rank(pct=True).to_numpy()


def slice_stats(tr, lo, hi):
    return exit_lab.stats([t for t in tr if lo <= t["bar"] < hi])


def main():
    df = load_csv("data/xauusd_15m.csv.gz", rule="30min")
    _ma, bw = bollinger(df)
    thr40 = np.nanquantile(bw, 0.40)
    sq = np.nan_to_num(bw < thr40, nan=0).astype(bool)
    out = []

    print("=" * 104)
    print("CONTROL 0 -- restate the claim at matched 25% drawdown")
    print("=" * 104)
    r0, s0, tr0 = solve_risk_kw(df)
    report("baseline champion", r0, s0, out)
    rq, sq_s, trq = solve_risk_kw(df, mask=sq)
    report("squeeze gate (bw < 40th pct)", rq, sq_s, out)

    print("\n" + "=" * 104)
    print("CONTROL 1 -- halves. Both must hold; one-half effects are fitting.")
    print("=" * 104)
    half = len(df) // 2
    for nm, tr in (("baseline", tr0), ("squeeze", trq)):
        h1, h2 = slice_stats(tr, 0, half), slice_stats(tr, half, len(df))
        print(f"  {nm:<12} h1: n={h1['n']:<4} PF={h1['pf']:.3f}   "
              f"h2: n={h2['n']:<4} PF={h2['pf']:.3f}")

    print("\n" + "=" * 104)
    print("CONTROL 2 -- the two DOWN years in isolation (2021, 2026).")
    print("  A filter that helps only in rising years is a bull-market artifact.")
    print("=" * 104)
    yr = pd.Series(df.index.year, index=df.index).to_numpy()
    for y in (2020, 2021, 2022, 2023, 2024, 2025, 2026):
        m = yr == y
        if m.sum() < 500:
            continue
        chg = df["close"].to_numpy()[m][-1] / df["close"].to_numpy()[m][0] - 1
        b = exit_lab.stats([t for t in tr0 if yr[t["bar"]] == y])
        q = exit_lab.stats([t for t in trq if yr[t["bar"]] == y])
        tag = "DOWN" if chg < 0 else "up  "
        print(f"  {y} ({tag} {chg:+6.1%})  baseline n={b['n']:<4} PF={b['pf']:6.3f}   "
              f"squeeze n={q['n']:<4} PF={q['pf']:6.3f}")

    print("\n" + "=" * 104)
    print("CONTROL 3 -- US30, the second instrument. Six prior candidates died here.")
    print("=" * 104)
    try:
        us = load_csv("data/us30_15m.csv.gz", rule="30min")
        _m2, bw2 = bollinger(us)
        sq2 = np.nan_to_num(bw2 < np.nanquantile(bw2, 0.40), nan=0).astype(bool)
        for nm, m in (("US30 baseline", None), ("US30 squeeze gate", sq2)):
            r, s, _ = solve_risk_kw(us, mask=m, dd_target=25.0)
            report(nm, r, s, out)
    except Exception as e:
        print(f"  US30 unavailable: {e}")

    print("\n" + "=" * 104)
    print("CONTROL 4 -- threshold sensitivity. A cliff means the number was fitted.")
    print("=" * 104)
    for p in (0.20, 0.30, 0.40, 0.50, 0.60, 0.70):
        m = np.nan_to_num(bw < np.nanquantile(bw, p), nan=0).astype(bool)
        r, s, _ = solve_risk_kw(df, mask=m)
        report(f"bw < {int(p*100)}th pct", r, s, out)

    print("\n" + "=" * 104)
    print("CONTROL 5 -- is this Bollinger, or is it just low volatility?")
    print("  ATR-rank is a different measure of the same underlying quantity. If it")
    print("  reproduces the result, the finding is 'breakouts out of quiet markets'")
    print("  and the Bollinger construction adds nothing.")
    print("=" * 104)
    ar = atr_rank(df)
    for p in (0.30, 0.40, 0.50):
        m = np.nan_to_num(ar < p, nan=0).astype(bool)
        r, s, _ = solve_risk_kw(df, mask=m)
        report(f"ATR rank < {int(p*100)}th pct", r, s, out)
    ok = np.isfinite(bw) & np.isfinite(ar)
    print(f"\n  corr(bandwidth rank, ATR rank) = "
          f"{np.corrcoef(pd.Series(bw[ok]).rank(pct=True), ar[ok])[0,1]:+.4f}")

    print("\n" + "=" * 104)
    print("CONTROL 6 -- per-trade quality, not leverage. Is each trade better?")
    print("=" * 104)
    for nm, tr in (("baseline", tr0), ("squeeze", trq)):
        p = np.array([t["points"] for t in tr], float)
        w, l = p[p > 0], -p[p < 0]
        print(f"  {nm:<10} n={len(tr):<4} WR={100*len(w)/len(p):4.1f}%  "
              f"avg win={w.mean():7.2f} pts  avg loss={l.mean():6.2f} pts  "
              f"payoff={w.mean()/l.mean():5.2f}:1  "
              f"expectancy={p.mean():+6.2f} pts")

    pd.DataFrame(out).to_csv("research/squeeze_controls.csv", index=False)


if __name__ == "__main__":
    main()
