"""AU200 final diagnostic — pre-entry characteristics vs the FROZEN +-20 outcome.

Every variable uses ONLY information available at the entry candle's close.
Outcome frozen in advance: does the trade touch +20 before -20 (1-minute
resolved). No target search. No new indicators.
"""
import sys, math, statistics as st
sys.path.insert(0, "research/au200")
import phase1 as P1, phase2 as P2


def features(days, m1):
    """One row per Logic A trade, all pre-entry."""
    rows = []
    for d in sorted(days):
        D = days[d]
        s = P1.setup(D)
        if s is None or P1.SESS_EXIT not in D:
            continue
        do, bh, bl, side = s
        a = P1.logic_a(D, s)
        if not a:
            continue
        sd, em, entry = a
        o10, h10, l10, c10 = D[P1.BODY]
        o95, h95, l95, c95 = D[P1.REF]
        bo, bhi, blo, bc = D[em]                 # the breakout candle itself
        body = bh - bl
        rng = h10 - l10
        brng = bhi - blo
        bbody = abs(bc - bo)
        dist = (bl - do) if side == "ABOVE" else (do - bh)
        rows.append(dict(
            date=d, side=sd, entry=entry, entry_m=em,
            body_size=body,
            range_1000=rng,
            body_range_ratio=(body / rng) if rng > 0 else 0.0,
            dist_from_open=dist,
            dist_norm=(dist / rng) if rng > 0 else 0.0,
            beyond=(entry - bh) if sd > 0 else (bl - entry),
            brk_body=bbody,
            brk_range=brng,
            brk_ratio=(bbody / brng) if brng > 0 else 0.0,
            bars_to_entry=(em - P1.BODY) // 5,
            chg_0950=c95 - o95,
            rng_0950=h95 - l95,
        ))
    return rows


VARS = ["body_size", "range_1000", "body_range_ratio", "dist_from_open", "dist_norm",
        "beyond", "brk_body", "brk_range", "brk_ratio", "bars_to_entry",
        "chg_0950", "rng_0950"]


def mannwhitney(a, b):
    """U test with normal approximation and tie correction. Returns (z, p)."""
    n1, n2 = len(a), len(b)
    if n1 < 5 or n2 < 5:
        return float("nan"), float("nan")
    comb = sorted([(v, 0) for v in a] + [(v, 1) for v in b])
    ranks = [0.0] * len(comb)
    i = 0
    ties = 0
    while i < len(comb):
        j = i
        while j + 1 < len(comb) and comb[j + 1][0] == comb[i][0]:
            j += 1
        r = (i + j) / 2 + 1
        t = j - i + 1
        ties += t ** 3 - t
        for k in range(i, j + 1):
            ranks[k] = r
        i = j + 1
    R1 = sum(ranks[k] for k in range(len(comb)) if comb[k][1] == 0)
    U1 = R1 - n1 * (n1 + 1) / 2
    mu = n1 * n2 / 2
    N = n1 + n2
    sd = math.sqrt(max(1e-12, (n1 * n2 / 12) * ((N + 1) - ties / (N * (N - 1)))))
    z = (U1 - mu) / sd
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return z, p


def cohen_d(a, b):
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    s1, s2 = st.pstdev(a), st.pstdev(b)
    n1, n2 = len(a), len(b)
    sp = math.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / max(1, n1 + n2 - 2))
    return (st.mean(a) - st.mean(b)) / sp if sp > 0 else float("nan")


def rpb_ci(x, y):
    """point-biserial r between continuous x and binary y, with 95% CI."""
    n = len(x)
    mx, my = st.mean(x), st.mean(y)
    sx, sy = st.pstdev(x), st.pstdev(y)
    if sx == 0 or sy == 0:
        return float("nan"), float("nan"), float("nan")
    r = sum((a - mx) * (b - my) for a, b in zip(x, y)) / (n * sx * sy)
    r = max(-0.999999, min(0.999999, r))
    z = 0.5 * math.log((1 + r) / (1 - r))
    se = 1 / math.sqrt(n - 3)
    lo = math.tanh(z - 1.96 * se)
    hi = math.tanh(z + 1.96 * se)
    return r, lo, hi
