"""
The one survivor of the corrected Quarterly Theory test, put through controls.

The corrected weekly cycle (Q1=Tue ... Q4=Fri) produced exactly one arm that
beat the ungated champion: weekly Q4, PF 1.825 vs 1.626, and it held in both
halves. Weekly Q4 is FRIDAY. Before that becomes a belief it has to survive
three things the raw number does not address:

  1  MULTIPLE COMPARISONS. Twelve quarter-arms were scanned. The best of twelve
     noisy arms is high by construction. The honest control is the full
     day-of-week sweep: if Friday is genuinely special it should stand clear of
     the other four weekdays, not merely be the top of a scattered five.

  2  IS IT "QUARTERLY THEORY" AT ALL? If plain day-of-week reproduces the
     result, the theory contributed nothing -- the finding is "Friday", and it
     needs no cycle framework to state. Quarterly Theory would only earn credit
     if the Tue-anchored cycle beat the calendar days it is built from.

  3  DRAWDOWN-MATCHED COMPARISON. The gate trades 28% as often, so it earns 333%
     against the champion's 1512%. Comparing PF across different trade counts
     and different drawdowns is the mistake this desk has made before. Both are
     re-run dialled to the SAME max drawdown; the one that returns more at equal
     risk wins, and nothing else does.
"""
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo

from backtest.io import load_csv
from backtest import champion, exit_lab
from research.qt_corrected import to_local, weekly_quarters

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def solve_risk(df, mask, dd_target=25.0, lo=0.05, hi=12.0, iters=22):
    """Binary-search risk% so the arm lands on `dd_target` max drawdown.

    Drawdown is monotone in risk% under fractional sizing, so bisection is
    sound. This is what makes two configs with different natural leverage
    comparable: fix the risk taken, then compare the return.
    """
    best = None
    for _ in range(iters):
        mid = (lo + hi) / 2
        tr, _ = champion.run(df, mask=mask, risk_pct=mid)
        s = exit_lab.stats(tr)
        best = (mid, s)
        if s["n"] == 0:
            hi = mid; continue
        if s["maxdd_pct"] > dd_target:
            hi = mid
        else:
            lo = mid
    return best


def main():
    df = load_csv("data/xauusd_15m.csv.gz", rule="30min")
    loc = to_local(df.index, "ny")
    dow = loc.dayofweek.to_numpy()
    half = len(df) // 2

    print("=" * 92)
    print("CONTROL 1 -- full day-of-week sweep (is Friday special, or is one of five always top?)")
    print("=" * 92)
    rows = []
    for d in range(7):
        m = dow == d
        if m.sum() < 200:
            continue
        tr, _ = champion.run(df, mask=m)
        s = exit_lab.stats(tr)
        if s["n"] < 30:
            continue
        h1 = exit_lab.stats([t for t in tr if t["bar"] < half])
        h2 = exit_lab.stats([t for t in tr if t["bar"] >= half])
        rows.append(dict(day=DAYS[d], n=s["n"], wr=s["wr"], pf=s["pf"],
                         net=s["net_pct"], dd=s["maxdd_pct"],
                         pf_h1=h1["pf"], pf_h2=h2["pf"]))
    t = pd.DataFrame(rows)
    print(t.to_string(index=False, float_format=lambda v: f"{v:8.3f}"))

    print("\n" + "=" * 92)
    print("CONTROL 2 -- does the Tue-anchored weekly cycle add anything over the bare weekday?")
    print("=" * 92)
    q, _ = weekly_quarters(loc)
    for k in (1, 2, 3, 4):
        m = q == k
        tr, _ = champion.run(df, mask=m)
        s = exit_lab.stats(tr)
        print(f"  weeklyQ{k} == {DAYS[k]:<4} n={s['n']:<4} PF={s['pf']:.3f}   "
              f"(identical to the weekday row above by construction)")
    print("  The corrected weekly cycle is a relabelling of Tue/Wed/Thu/Fri. It")
    print("  cannot differ from the weekday sweep, so it adds no information of")
    print("  its own -- whatever is there is a day-of-week effect.")

    print("\n" + "=" * 92)
    print("CONTROL 3 -- drawdown-matched: champion vs Friday-only, both dialled to 25% DD")
    print("=" * 92)
    for label, m in (("champion (all days)", None), ("Friday only", dow == 4),
                     ("drop Friday", dow != 4)):
        r, s = solve_risk(df, m, 25.0)
        if s["n"] == 0:
            print(f"  {label:<22} no trades"); continue
        mar = s["net_pct"] / s["maxdd_pct"] if s["maxdd_pct"] else np.nan
        print(f"  {label:<22} risk={r:5.2f}%  n={s['n']:<4} PF={s['pf']:.3f}  "
              f"net={s['net_pct']:>+9.1f}%  DD={s['maxdd_pct']:5.2f}%  net/DD={mar:6.2f}")
    print("\n  Read the net/DD column, not PF. At equal risk the question is only")
    print("  which arm compounds more.")


if __name__ == "__main__":
    main()
