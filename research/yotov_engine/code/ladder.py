"""YOTOV GOLD QUARTER ENGINE — step 1: does the level ladder carry information?

The spec's price map, as fractions of the $25 Large Quarter (LQP):

    LQP  0.00 | overshoot end 0.10 | HZ end 0.30 | half 0.50
    whole 0.80 | completion 0.90 | target LQP 1.00

An ATTEMPT is a crossing of an LQP in some direction. It ends when price either
reaches the target LQP one quarter away (success) or loses the originating LQP
(failure). Along the way we record which ladder rungs it touched.

The conditional progressions the spec quotes -- "Whole -> Completion ~89.66%",
"Completion -> LQP ~84.76%" -- are exactly this, and both have a closed form.
From rung at fraction x, with absorbing barriers at the next rung y (up) and the
origin 0 (down), a driftless walk reaches y first with probability x/y (H99,
gambler's ruin). So:

    whole -> completion    0.80 / 0.90 = 0.8889
    completion -> target   0.90 / 1.00 = 0.9000

A measurement matching those numbers is measuring geometry, not gold. The
PHASE CONTROL settles it: the same ladder on a grid shifted off the round
numbers must score the same if roundness is doing nothing.

Fine grid is S/100 = $0.25, so every rung lands on an exact fine line.
Comparison asymmetry (BUG from an earlier build):
    price >= line W  <=>  cell >= W        price <= line W  <=>  cell <= W-1
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/quarters/code"); sys.path.insert(0, "research/goldmap/code")
from system import fine, SUB
from qt_engine import Book, PTS

DATA = {"2025-26": "research/microq3/data", "2024-25": "research/microq3/data_holdout"}
RUNGS = [("overshoot", 10), ("hz", 30), ("half", 50), ("whole", 80),
         ("completion", 90), ("target", 100)]


def attempts(idx, cells, ny):
    """Walk every LQP crossing to its resolution. Returns one row per attempt:
    direction, which rungs were touched, resolution, duration, attempt number."""
    n = len(cells)
    out = []
    seen = {}                                  # (lqp_cell, dir) -> attempt count
    j = 1
    while j < n:
        c, prev = int(cells[j]), int(cells[j - 1])
        up = c > prev
        # first LQP line crossed in the direction of travel
        if up:
            q = -(-(prev + 1) // SUB) * SUB    # ceil to the next multiple of SUB
            if q > c:
                j += 1; continue
        else:
            q = (prev // SUB) * SUB
            if q < c + 1:
                j += 1; continue
        # walk forward to resolution
        hi, lo = (q + SUB, q - 1) if up else (q + 1, q - SUB)
        reach = 0                              # deepest rung index touched
        res, kx = "OPEN", idx[j]
        for m in range(j, n):
            v = int(cells[m])
            prog = (v - q) if up else (q - v)
            # a rung at offset r is touched when progress >= r going up, and
            # when progress >= r going down too (prog is already signed by dir)
            while reach < len(RUNGS) and prog >= RUNGS[reach][1]:
                reach += 1
            if (up and v >= hi) or ((not up) and v <= lo):
                res, kx = "TARGET", idx[m]; break
            if (up and v <= lo) or ((not up) and v >= hi):
                res, kx = "LOST", idx[m]; break
        else:
            m = n - 1
        key = (q, 1 if up else -1)
        seen[key] = seen.get(key, 0) + 1
        out.append(dict(k0=int(idx[j]), kx=int(kx), q=q, up=up, reach=reach,
                        res=res, attempt=seen[key],
                        mins=(int(ny[kx]) - int(ny[idx[j]])) / 60000.0))
        # next attempt starts after this one resolved
        while j < n and idx[j] <= kx:
            j += 1
    return pd.DataFrame(out)


def ladder_table(df):
    """Conditional progression at every rung, with the H99 closed form."""
    rows = []
    for i, (name, off) in enumerate(RUNGS):
        base = df[df.reach >= i] if i else df
        hit = df[df.reach >= i + 1]
        prev_off = RUNGS[i - 1][1] if i else 0
        pred = prev_off / off                  # x / y, H99
        rows.append(dict(step=f"{'LQP' if i==0 else RUNGS[i-1][0]} -> {name}",
                         n=len(base), hit=len(hit),
                         obs=(len(hit) / len(base) if len(base) else np.nan),
                         h99=pred))
    return pd.DataFrame(rows)


PHASES = list(range(12))                       # k/12 of $25 = $2.083 steps
S_i = int(25.0 * PTS)

allrows = []
for year, d in DATA.items():
    b = Book(d, year)
    print(f"\n{'='*104}\n{year}\n{'='*104}", flush=True)
    for k in PHASES:
        ph = int(round(k / 12 * S_i))
        idx, cells, f = fine(b.mid, S_i, ph)
        df = attempts(idx, cells, b.ny)
        t = ladder_table(df)
        t["year"], t["phase"] = year, k
        allrows.append(t)
        if k == 0:
            print(f"\n  ROUND $25 grid — {len(df)} attempts, "
                  f"{(df.res=='TARGET').mean():.1%} complete the quarter")
            print(f"  {'step':>26}{'n':>8}{'hit':>8}{'observed':>11}"
                  f"{'H99 x/y':>10}{'diff':>9}")
            for _, r in t.iterrows():
                print(f"  {r.step:>26}{r.n:>8}{r.hit:>8}{r.obs:>10.2%}"
                      f"{r.h99:>10.2%}{r.obs-r.h99:>+9.2%}")
        del idx, cells, df
    del b

R = pd.concat(allrows, ignore_index=True)
R.to_csv("research/yotov_engine/results/ladder.csv", index=False)

print(f"\n{'='*104}\nPHASE CONTROL — is the ladder about ROUNDNESS or about geometry?\n{'='*104}")
for year in DATA:
    print(f"\n  {year}")
    print(f"  {'step':>26}{'ROUND':>9}{'shifted min':>13}{'shifted max':>13}"
          f"{'shifted mean':>14}{'round rank':>12}")
    y = R[R.year == year]
    for step in y.step.unique():
        s = y[y.step == step]
        rd = float(s[s.phase == 0].obs.iloc[0])
        sh = s[s.phase != 0].obs.values
        rank = int((sh > rd).sum()) + 1
        print(f"  {step:>26}{rd:>8.2%}{sh.min():>13.2%}{sh.max():>13.2%}"
              f"{sh.mean():>14.2%}{f'{rank}/12':>12}")
print("\nwritten -> research/yotov_engine/results/ladder.csv")
