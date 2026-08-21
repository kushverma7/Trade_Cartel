"""Is the prior-day-high edge real, or the best of eight coin flips?

pivot_study.py tested eight levels and exactly one came out ahead of its sham
control (PDH, +9.7pp on n=122). That is precisely the shape of result this
session has already had to throw away twice, so it gets three separate attacks
before it is allowed to mean anything:

  1. SHAM DISTRIBUTION. Redraw the random-day pairing many times to get a null
     distribution per level, then ask where the real number sits -- both on its
     own (per-level p) and after paying for having looked at eight levels
     (family-wise p on the largest edge).
  2. DISPLACEMENT. Keep the day, keep the level, move the LINE by a few points.
     A real level is local: PDH should beat PDH+-delta. If the displaced lines
     work just as well, the edge is "a line roughly there", not "the prior high".
  3. STABILITY. Split the year in half and sweep the reaction horizon. One cell
     that works is a cell; a plateau is an effect.
"""
import numpy as np, pandas as pd

b = pd.read_parquet("/home/user/Trade_Cartel/research/gold_10am_flip/data/bars_5m_melbourne.parquet")
b["ts"] = pd.to_datetime(b["ts_mel"]); b = b.sort_values("ts")
b["d"] = b["ts"].dt.date
days = b.groupby("d").agg(o=("o", "first"), h=("h", "max"), l=("l", "min"),
                          c=("c", "last"), n=("c", "size")).reset_index()
days = days[days.n >= 100].reset_index(drop=True)

# pre-slice each day's bars once
BARS = {}
for d, g in b.groupby("d"):
    if len(g) >= 50:
        BARS[d] = (g["h"].to_numpy(), g["l"].to_numpy(), g["c"].to_numpy())

KEYS = ["PDH", "PDL", "PDC", "PP", "R1", "S1", "R2", "S2"]


def levels_from(prev):
    H, L, C = prev.h, prev.l, prev.c
    P = (H + L + C) / 3.0
    return {"PDH": H, "PDL": L, "PDC": C, "PP": P,
            "R1": 2 * P - L, "S1": 2 * P - H,
            "R2": P + (H - L), "S2": P - (H - L)}


def reaction(hi, lo, cl, lvl, hor):
    t = np.flatnonzero((hi >= lvl) & (lo <= lvl))
    if len(t) == 0:
        return None
    k = int(t[0])
    if k == 0:
        return None
    approach_up = cl[k - 1] < lvl
    seg = cl[k + 1:k + 1 + hor]
    if len(seg) < 3:
        return None
    end = seg[-1]
    return 1 if ((end < lvl) if approach_up else (end > lvl)) else 0


IDX = [i for i in range(1, len(days)) if days.iloc[i].d in BARS]
PREV = {i: levels_from(days.iloc[i - 1]) for i in IDX}
OPEN = {i: float(days.iloc[i].o) for i in IDX}
# levels of every day expressed as offset from that day's own open
OFF = {i: {k: v - OPEN[i] for k, v in PREV[i].items()} for i in IDX}


def run(offsets_for_day, hor=12, keys=KEYS):
    """offsets_for_day(i) -> dict level->offset-from-open. Returns hits/n per level."""
    acc = {k: [0, 0] for k in keys}
    for i in IDX:
        hi, lo, cl = BARS[days.iloc[i].d]
        off = offsets_for_day(i)
        for k in keys:
            r = reaction(hi, lo, cl, OPEN[i] + off[k], hor)
            if r is not None:
                acc[k][0] += r; acc[k][1] += 1
    return acc


def rate(acc, k):
    h, n = acc[k]
    return (h / n if n else np.nan), n


print(f"days used: {len(IDX)}")
real = run(lambda i: OFF[i])
print(f"\n{'-'*78}\n1. SHAM DISTRIBUTION  (400 redraws of the random-day pairing)\n{'-'*78}")

R = 400
rng = np.random.default_rng(11)
null = {k: [] for k in KEYS}
pool = list(IDX)
for r_i in range(R):
    perm = rng.permutation(pool)
    m = {a: b_ for a, b_ in zip(pool, perm)}
    acc = run(lambda i: OFF[m[i]])
    for k in KEYS:
        null[k].append(rate(acc, k)[0])

print(f"{'level':<6}{'real':>8}{'n':>6}   {'sham mean':>10}{'sham sd':>9}   {'edge':>8}{'p(1-sided)':>12}")
edges, ps = {}, {}
for k in KEYS:
    rr, n = rate(real, k)
    arr = np.array([x for x in null[k] if np.isfinite(x)])
    e = rr - arr.mean()
    p = (np.sum(arr >= rr) + 1) / (len(arr) + 1)
    edges[k], ps[k] = e, p
    print(f"{k:<6}{100*rr:>7.1f}%{n:>6}   {100*arr.mean():>9.1f}%{100*arr.std():>8.1f}%   {100*e:>+7.1f}pp{p:>12.3f}")

# family-wise: how often does the BEST of eight sham levels beat +9.7pp?
cent = {k: np.array([x for x in null[k] if np.isfinite(x)]) for k in KEYS}
mu = {k: cent[k].mean() for k in KEYS}
maxnull = np.max(np.vstack([cent[k] - mu[k] for k in KEYS]), axis=0)
obs_max = max(edges.values())
p_fw = (np.sum(maxnull >= obs_max) + 1) / (len(maxnull) + 1)
print(f"\nbest observed edge = {100*obs_max:+.1f}pp ({max(edges, key=edges.get)})")
print(f"how often the best of EIGHT sham levels beats that by chance: p = {p_fw:.3f}")

print(f"\n{'-'*78}\n2. DISPLACEMENT  (same day, same level type, line moved)\n{'-'*78}")
print(f"{'shift':<8}{'PDH rej':>9}{'n':>6}   {'PDL rej':>9}{'n':>6}   {'PP rej':>9}{'n':>6}")
for sh in [-8, -5, -3, -1.5, 0, 1.5, 3, 5, 8]:
    acc = run(lambda i: {k: v + sh for k, v in OFF[i].items()})
    row = f"{sh:<8.1f}"
    for k in ["PDH", "PDL", "PP"]:
        rr, n = rate(acc, k)
        row += f"{100*rr:>8.1f}%{n:>6}   "
    print(row)

print(f"\n{'-'*78}\n3. STABILITY  (horizon sweep, and each half of the year)\n{'-'*78}")
half = len(IDX) // 2
H1, H2 = IDX[:half], IDX[half:]
print(f"{'hor':<6}{'PDH all':>10}{'n':>6}{'PDH H1':>10}{'n':>6}{'PDH H2':>10}{'n':>6}{'sham all':>10}")
for hor in [3, 6, 12, 24, 36, 48]:
    saveIDX = IDX
    acc = run(lambda i: OFF[i], hor=hor, keys=["PDH"])
    rr, n = rate(acc, "PDH")
    parts = []
    for sub in (H1, H2):
        globals()["IDX"] = sub
        a2 = run(lambda i: OFF[i], hor=hor, keys=["PDH"])
        parts.append(rate(a2, "PDH"))
        globals()["IDX"] = saveIDX
    # one sham draw at this horizon for reference
    perm = rng.permutation(pool); m = {a: b_ for a, b_ in zip(pool, perm)}
    sh = run(lambda i: OFF[m[i]], hor=hor, keys=["PDH"])
    sr, _ = rate(sh, "PDH")
    print(f"{hor:<6}{100*rr:>9.1f}%{n:>6}{100*parts[0][0]:>9.1f}%{parts[0][1]:>6}"
          f"{100*parts[1][0]:>9.1f}%{parts[1][1]:>6}{100*sr:>9.1f}%")
