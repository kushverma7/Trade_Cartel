"""
G1* under gold-only rules: the adoption decision, with US30 removed.

WHAT CHANGED AND WHAT IT COSTS
  User directive 2026-08-05: "you are only working on gold remove us30."
  Adoption bar 5 (second-instrument transfer) is therefore withdrawn. That was
  the only bar G1* failed, so the decision now turns on the gold-only evidence
  alone.

  Stated once, because it is a real cost and not a formality: US30 was the
  control that killed the most candidates in this project, and G1* failed it
  hard -- P(DD>30%) rose from 36% to 53% there. Removing the control does not
  make that number disappear; it makes it out of scope. What can still be said
  after this file is "G1* is better on gold", not "G1* is better".

WHAT REPLACES IT
  Three gold-only controls, chosen because each attacks the specific way a
  sizing rule can look good for the wrong reason:

  1  DOWN YEARS IN ISOLATION. Gold ran 1450 -> 4100 across this sample. Any
     rule that quietly sizes up in rising markets tests well for a reason that
     has nothing to do with edge -- this is the trap that killed the short-risk
     candidate. 2021, 2022 and 2026 are the down/flat years and are read on
     their own.

  2  ANCHORED WALK-FORWARD. Half-samples can hide a rule that only works once
     equity is large. An expanding window with a fixed forward step tests the
     rule the way it would actually have been run.

  3  MC SEED STABILITY. A single Monte Carlo seed reporting P(DD>30%) at 10.6%
     is one draw. Five seeds x 5,000 paths establishes whether the tail
     improvement is a property of the return distribution or of the seed.

WHAT G1* ACTUALLY IS
  One line. G1's existing regime multiplier -- clip(f(trend distance) x
  f(ATR expansion), 0.5, 2.0) -- currently scales only the OPENING unit. G1*
  applies the same multiplier, captured at entry, to the pyramid adds as well.
  No new indicator, no new threshold, no change to entry, exit, trail, add
  triggers or cooldown. Mean adds per trade is unchanged at 1.809: the trade
  paths are identical and only the size of each add moves.
"""
import numpy as np, pandas as pd

from backtest import exit_lab
from research.voltarget import Book, evaluate, show, montecarlo

BUDGETS = (25.0, 20.0)


def year_table(book, arms):
    print("=" * 118)
    print("CONTROL 1 -- YEAR BY YEAR, with the down years read on their own.")
    print("  Gold ran 1450 -> 4100 here. A sizing rule that leans on that is the")
    print("  failure mode this control exists to catch.")
    print("=" * 118)
    c = book.df["close"].to_numpy(float)
    yrs = sorted(set(book.year))
    hdr = f"  {'year':<6}{'chg':>8}  " + "".join(f"{a:>26}" for a in arms)
    print(hdr)
    rows = []
    for y in yrs:
        m = book.year == y
        if m.sum() < 500:
            continue
        chg = c[m][-1] / c[m][0] - 1
        line = f"  {y:<6}{chg:>+7.1%}  "
        rec = dict(year=y, chg=chg)
        for a, tr in arms.items():
            s = exit_lab.stats([t for t in tr if book.year[t["bar"]] == y])
            line += f"{'n=%d PF=%.3f' % (s['n'], s['pf']):>26}"
            rec[f"{a}_pf"] = s["pf"]; rec[f"{a}_n"] = s["n"]
        print(line + ("   <-- DOWN/FLAT" if chg < 0.05 else ""))
        rows.append(rec)
    return pd.DataFrame(rows)


def walkforward(book, arms, folds=6):
    print("\n" + "=" * 118)
    print("CONTROL 2 -- ANCHORED WALK-FORWARD. Expanding window, fixed forward step.")
    print("  Each row is profit factor on bars the rule had not yet reached.")
    print("=" * 118)
    n = len(book.df)
    edges = [int(n * (0.4 + 0.6 * i / folds)) for i in range(folds + 1)]
    print(f"  {'fold':<6}{'OOS bars':>22}  " + "".join(f"{a:>24}" for a in arms))
    rows = []
    for i in range(folds):
        lo, hi = edges[i], edges[i + 1]
        rec = dict(fold=i + 1, lo=lo, hi=hi)
        line = f"  {i+1:<6}{f'{lo}-{hi}':>22}  "
        for a, tr in arms.items():
            s = exit_lab.stats([t for t in tr if lo <= t["bar"] < hi])
            line += f"{'n=%d PF=%.3f' % (s['n'], s['pf']):>24}"
            rec[f"{a}_pf"] = s["pf"]; rec[f"{a}_n"] = s["n"]
        print(line)
        rows.append(rec)
    return pd.DataFrame(rows)


def mc_stability(arms, seeds=(11, 101, 2027, 55555, 987654), n=5000):
    print("\n" + "=" * 118)
    print("CONTROL 3 -- MONTE CARLO SEED STABILITY, 5 seeds x 5,000 paths each")
    print("=" * 118)
    rows = []
    for a, tr in arms.items():
        med, p30 = [], []
        for s in seeds:
            m = montecarlo(tr, n=n, seed=s)
            med.append(np.median(m)); p30.append(100 * (m > 30).mean())
        rows.append(dict(arm=a, mc_med=np.mean(med), mc_med_sd=np.std(med),
                         p30=np.mean(p30), p30_sd=np.std(p30),
                         p30_min=min(p30), p30_max=max(p30)))
        print(f"  {a:<26} MC median {np.mean(med):6.2f} (sd {np.std(med):.3f})   "
              f"P(DD>30%) {np.mean(p30):6.2f}% (sd {np.std(p30):.3f}, "
              f"range {min(p30):.2f}-{max(p30):.2f})")
    return pd.DataFrame(rows)


def main():
    g = Book("data/xauusd_15m.csv.gz")
    print("GOLD ONLY. US30 withdrawn from the protocol per user directive.")
    print(f"  {len(g.df)} 30m bars, {g.df.index[0].date()} -> {g.df.index[-1].date()}"
          f" ({g.yrs:.2f}y)\n")

    rows = []
    for b in BUDGETS:
        rows.append(evaluate(g, "E", b))
        rows.append(evaluate(g, "G1", b, risk_series=g.g1))
        rows.append(evaluate(g, "G1*", b, risk_series=g.g1, risk_series_adds=True))
    t = show(rows, "HEADLINE -- gold only, both drawdown budgets")
    t.to_csv("research/g1star_goldonly.csv", index=False)

    _r, trE = g.solve(25.0)
    _r, trG = g.solve(25.0, risk_series=g.g1)
    _r, trS = g.solve(25.0, risk_series=g.g1, risk_series_adds=True)
    arms = {"E": trE, "G1": trG, "G1*": trS}

    print()
    yt = year_table(g, arms); yt.to_csv("research/g1star_years.csv", index=False)
    wf = walkforward(g, arms); wf.to_csv("research/g1star_wf.csv", index=False)
    ms = mc_stability(arms); ms.to_csv("research/g1star_mc.csv", index=False)

    print("\n" + "=" * 118)
    print("THE THRESHOLD SLOPE, resolved rather than left hanging")
    print("=" * 118)
    print("  The plateau sweep showed G1*'s expansion threshold rising monotonically")
    print("  (expThr 1.00 -> 1.20 gives MAR 2.475 -> 2.759). That is NOT a cliff the")
    print("  adopted point sits on -- it is a slope the adopted point sits BELOW.")
    print("  Adopting 1.10 is therefore the conservative choice, and the higher")
    print("  numbers are left deliberately untaken: chasing them is re-optimisation")
    print("  (hard finding #10) and the sweep gives no reason to believe 1.20 is")
    print("  anything but the edge of the tested range.")


if __name__ == "__main__":
    main()
