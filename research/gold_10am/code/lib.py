"""Shared helpers: ledger loading, sample windows, table formatting, stats."""
import os, sys, csv, math, random, statistics as st, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

PROC = core.PROC
TAB = os.path.join(core.HERE, "..", "tables")
RES = os.path.join(core.HERE, "..", "results")

# Pre-registered chronological split. Declared BEFORE any parameter search.
DEV = (dt.date(2024, 8, 20), dt.date(2025, 8, 19))
VAL = (dt.date(2025, 8, 20), dt.date(2026, 2, 19))
HOLD = (dt.date(2026, 2, 20), dt.date(2026, 8, 19))

NUM = ("d_open b_hi b_lo entry dist_beyond sig_body sig_range atr14 mae mfe "
       "mae_full mfe_full base_pnl base_pnl_opt eod_pnl body_size body_range "
       "upper_wick lower_wick body_ratio close_vs_dopen open_vs_dopen "
       "bhi_vs_dopen blo_vs_dopen ref_range atr14 "
       "body_open body_close body_high body_low").split()
INT = ("entry_minute bars_to_entry path_len eod_minute base_bars base_exit_minute year "
       "t_mae t_mfe t_mae_full t_mfe_full side setup_side").split()


def load(name):
    rows = []
    with open(os.path.join(PROC, name)) as f:
        for r in csv.DictReader(f):
            r["date_d"] = dt.date.fromisoformat(r["date"])
            for k in list(r):
                if k in NUM or k.startswith(("fwd_",)):
                    r[k] = float(r[k]) if r[k] not in ("", None) else None
                elif k in INT or k.startswith("fpt_"):
                    r[k] = int(float(r[k])) if r[k] not in ("", None) else None
            for k in ("body_straddle", "full_straddle"):
                if k in r:
                    r[k] = r[k] == "True"
            rows.append(r)
    return rows


def window(rows, w):
    return [r for r in rows if w[0] <= r["date_d"] <= w[1]]


def sample_of(d):
    if DEV[0] <= d <= DEV[1]:
        return "DEV"
    if VAL[0] <= d <= VAL[1]:
        return "VAL"
    return "HOLD"


def pctl(xs, p):
    if not xs:
        return float("nan")
    xs = sorted(xs)
    k = (len(xs) - 1) * p / 100.0
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    return xs[lo] if lo == hi else xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def table(headers, rows, align=None):
    align = align or ["---"] * len(headers)
    out = ["| " + " | ".join(str(h) for h in headers) + " |",
           "| " + " | ".join(align) + " |"]
    for r in rows:
        out.append("| " + " | ".join("" if c is None else str(c) for c in r) + " |")
    return "\n".join(out) + "\n"


def f(x, n=2):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "inf" if isinstance(x, float) and math.isinf(x) and x > 0 else "—"
    return f"{x:.{n}f}"


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    s = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - s) / d, (c + s) / d)


def binom_p(k, n, p0=0.5):
    """two-sided exact binomial p-value"""
    if n == 0:
        return 1.0
    from math import comb
    def pmf(i):
        return comb(n, i) * p0 ** i * (1 - p0) ** (n - i)
    obs = pmf(k)
    return min(1.0, sum(pmf(i) for i in range(n + 1) if pmf(i) <= obs * (1 + 1e-12)))


def block_bootstrap(pnls, n_iter=5000, block=10, seed=7):
    rnd = random.Random(seed)
    n = len(pnls)
    if n == 0:
        return {}
    nb = max(1, n // block)
    out_net, out_pf, out_exp, out_dd = [], [], [], []
    for _ in range(n_iter):
        s = []
        while len(s) < n:
            i = rnd.randrange(0, max(1, n - block + 1))
            s.extend(pnls[i:i + block])
        s = s[:n]
        m = core.metrics(s, absurd_check=False)
        out_net.append(m["net"]); out_exp.append(m["expectancy"])
        out_pf.append(m["pf"] if m["pf"] != float("inf") else 99.0)
        out_dd.append(m["max_dd"])
    q = lambda a, p: pctl(a, p)
    return dict(net=(q(out_net, 5), q(out_net, 50), q(out_net, 95)),
                exp=(q(out_exp, 5), q(out_exp, 50), q(out_exp, 95)),
                pf=(q(out_pf, 5), q(out_pf, 50), q(out_pf, 95)),
                dd=(q(out_dd, 5), q(out_dd, 50), q(out_dd, 95)),
                p_positive=sum(1 for x in out_net if x > 0) / len(out_net))


def mannwhitney(a, b):
    """U test -> (U, z, p). No scipy dependency."""
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        return (0, 0.0, 1.0)
    allv = sorted([(v, 0) for v in a] + [(v, 1) for v in b])
    ranks = [0.0] * len(allv)
    i = 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]:
            j += 1
        rk = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[k] = rk
        i = j + 1
    r1 = sum(ranks[k] for k in range(len(allv)) if allv[k][1] == 0)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    mu = n1 * n2 / 2.0
    sd = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    z = (u1 - mu) / sd if sd > 0 else 0.0
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return (u1, z, p)


def metrics_row(label, pnls, extra=None):
    m = core.metrics(pnls)
    if m["n"] == 0:
        return [label] + ["—"] * 10
    return [label, m["n"], f(m["win_pct"], 1), f(m["avg_win"]), f(m["avg_loss"]),
            f(m["expectancy"], 3), f(m["pf"], 3), f(m["net"]), f(m["max_dd"]),
            f(m["payoff"], 2), f(m["recovery"], 2)]


METRIC_HEAD = ["Set", "N", "Win %", "Avg win", "Avg loss", "Expectancy",
               "PF", "Net $", "Max DD", "Payoff", "Recovery"]
