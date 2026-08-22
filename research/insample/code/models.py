"""ONE-YEAR IN-SAMPLE OPTIMISED — the ten model categories, surfaces, top 100.

EVERY NUMBER HERE IS IN-SAMPLE, SELECTED FROM 246,807 GRID CELLS ON ONE YEAR.
None of it is a forecast.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/insample/code")
pd.set_option("display.width", 260)

C = pd.read_parquet("research/insample/results/cycles_resolved.parquet")
C["pnl_R"] = pd.to_numeric(C.pnl_R_q3q4, errors="coerce")
C["why"] = C.why_q3q4
C = C.dropna(subset=["pnl_R"]).reset_index(drop=True)
P = C.pnl_R.to_numpy(float)
MON = pd.to_datetime(C.date).dt.to_period("M").astype(str).to_numpy()
S = pd.read_parquet("research/insample/results/search_all.parquet")
# parquet returns the activity band as an array, not a tuple; normalise it
S["act"] = S.act.map(lambda a: (float(a[0]), float(a[1])))
S["act0"] = S.act.map(lambda a: a[0])
S["act1"] = S.act.map(lambda a: a[1])
F = {k: np.nan_to_num(C[k].to_numpy(float), nan=(9.9 if k == "q2_eff" else -1.0))
     for k in ("q2_eff", "dfr_over_q1", "q1_eff", "rr", "sweep_depth", "act_pct")}
CYC, SWP = C.cycle.to_numpy(), C.sweep.to_numpy()
CYCM = {"ALL": np.ones(len(C), bool), "D123": CYC != "D4",
        **{d: CYC == d for d in ("D1", "D2", "D3", "D4")}}
SWPM = {"any": np.ones(len(C), bool), "single": SWP != "both", "both": SWP == "both"}


def mask_of(r):
    m = CYCM[r.cyc] & SWPM[r.swp]
    m &= (F["q2_eff"] <= r.q2_eff_max) & (F["dfr_over_q1"] <= r.dfr_max)
    m &= (F["q1_eff"] >= r.q1_eff_min) & (F["rr"] <= r.rr_max)
    m &= F["sweep_depth"] <= r.sweep_max
    a0, a1 = r.act
    if (a0, a1) != (0.0, 1.0):
        m &= (F["act_pct"] >= a0) & (F["act_pct"] <= a1)
    return m


def full(m):
    p = P[m]
    eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
    dd = pk - eq
    b = k = 0
    for v in p:
        b = b + 1 if v <= 0 else 0; k = max(k, b)
    mo = pd.Series(p).groupby(MON[m]).sum()
    w = C.why.to_numpy()[m]; gl = -p[p < 0].sum()
    return dict(n=len(p), pf=(p[p > 0].sum() / gl if gl > 0 else np.inf), exp=p.mean(),
                net=p.sum(), wr=100 * (p > 0).mean(), mdd=float(dd.max()),
                ulcer=float(np.sqrt((dd ** 2).mean())),
                r2=float(np.corrcoef(np.arange(len(eq)), eq)[0, 1] ** 2) if len(eq) > 2 else np.nan,
                streak=k, mo_pos=int((mo > 0).sum()), mo=len(mo),
                tp=int((w == "TP").sum()), sl=int((w == "SL").sum()), time=int((w == "TIME").sum()),
                time_R=float(p[w == "TIME"].sum()))


# smoothness composite: reward R2 and monthly consistency, punish DD/Ulcer/streak
def shortlist(sub, minn=20, k=1500):
    """Full statistics are expensive, so rank cheaply first and evaluate the top k."""
    d = sub[(sub.n >= minn) & (sub.exp > 0)].copy()
    d["_s"] = d.pf.replace(np.inf, 999).rank(pct=True) + d.wr.rank(pct=True) + d.net.rank(pct=True)
    return d.sort_values("_s", ascending=False).head(k)


def smooth_rank(sub, minn=20):
    out = []
    for _, r in shortlist(sub, minn).iterrows():
        s = full(mask_of(r))
        if s["exp"] <= 0:
            continue
        sc = (s["r2"] + s["mo_pos"] / max(s["mo"], 1)) - (s["mdd"] / 5 + s["ulcer"] / 3 + s["streak"] / 10)
        out.append((sc, r, s))
    out.sort(key=lambda x: -x[0])
    return out


print("=" * 126)
print("TEN MODEL CATEGORIES   ***ONE-YEAR IN-SAMPLE OPTIMISED, 2025-08-21 to 2026-08-20***")
print("Selected as the maximum over 246,807 grid cells on a base universe of PF 0.581 / -0.288R.")
print("=" * 126)
hdr = (f"  {'':<6}{'n':>5}{'PF':>8}{'exp R':>8}{'net R':>8}{'WR':>7}{'DD':>7}{'Ulcer':>7}"
       f"{'R2':>7}{'strk':>5}{'mo+':>7}{'TP/SL/TIME':>13}")
finalists = {}


def emit(tag, r, s, note=""):
    finalists[tag] = (r, s)
    print(f"\n{tag}   {note}")
    print(f"  rule: cyc={r.cyc} sweep={r.swp} Q2eff<={r.q2_eff_max:g} DFR<={r.dfr_max:g} "
          f"Q1eff>={r.q1_eff_min:g} RR<={r.rr_max:g} sweep<={r.sweep_max:g} act={r.act}")
    print(hdr)
    print(f"  {'':<6}{s['n']:>5}{s['pf']:>8.2f}{s['exp']:>+8.3f}{s['net']:>+8.2f}{s['wr']:>6.1f}%"
          f"{s['mdd']:>7.2f}{s['ulcer']:>7.2f}{s['r2']:>7.3f}{s['streak']:>5}"
          f"{s['mo_pos']:>4}/{s['mo']:<2}{f'{s[chr(116)+chr(112)]}/{s[chr(115)+chr(108)]}/{s[chr(116)+chr(105)+chr(109)+chr(101)]}':>13}")
    if s["time"]:
        print(f"  unresolved time exits contribute {s['time_R']:+.2f}R of {s['net']:+.2f}R "
              f"({100*s['time_R']/s['net']:.0f}%)")


fin = S[np.isfinite(S.pf)]
for tag, sub, by, asc in (
        ("MODEL 1  ABSOLUTE HIGHEST PF", S, "pf", False),
        ("MODEL 2  HIGHEST PF, n>=20", S[S.n >= 20], "pf", False),
        ("MODEL 3  HIGHEST PF, n>=30", S[S.n >= 30], "pf", False),
        ("MODEL 4  HIGHEST NET R", S, "net", False),
        ("MODEL 5  HIGHEST EXPECTANCY", S[S.n >= 15], "exp", False)):
    r = sub.sort_values(by, ascending=asc).iloc[0]
    emit(tag, r, full(mask_of(r)))

sm = smooth_rank(S, 20)
emit("MODEL 6  SMOOTHEST EQUITY", sm[0][1], sm[0][2], "(composite of R2, monthly consistency, DD, Ulcer, streak)")
lo = []
for _, r in shortlist(S, 20).iterrows():
    st = full(mask_of(r)); lo.append((st["mdd"], -st["net"], r, st))
lo.sort(key=lambda x: (x[0], x[1]))
emit("MODEL 7  LOWEST DRAWDOWN, n>=20", lo[0][2], lo[0][3])
act = S[(S.n >= 20) & ~((S.act0 == 0.0) & (S.act1 == 1.0))]
r = act.sort_values("pf", ascending=False).iloc[0]
emit("MODEL 8  BEST ACTIVITY-GATED", r, full(mask_of(r)))
pure = S[(S.n >= 20) & (S.act0 == 0.0) & (S.act1 == 1.0) & (S.cyc == "ALL") & (S.q2_eff_max >= 9)]
if len(pure):
    r = pure.sort_values("pf", ascending=False).iloc[0]
    emit("MODEL 9  BEST PURE QT (sweep/DFR structure only)", r, full(mask_of(r)))
allday = S[(S.n >= 25) & (S.cyc == "ALL")]
r = allday.sort_values("pf", ascending=False).iloc[0]
emit("MODEL 10  BEST ALL-DAY", r, full(mask_of(r)))

S.assign(_pf=S.pf.replace(np.inf, 999)).sort_values("_pf", ascending=False).head(100)\
 .drop(columns=["_pf"]).to_csv("research/insample/results/top100.csv", index=False)
print("\n  top 100 candidates written to results/top100.csv")

print("\n" + "=" * 126)
print("PARAMETER SURFACES — is the edge a plateau or one cell?   [IN-SAMPLE]")
print("=" * 126)
base = dict(cyc="ALL", swp="any", dfr_max=0.75, q1_eff_min=0.2, rr_max=2.0,
            sweep_max=9.0, act=(0.3, 0.8))
print("\n  Q2 EFFICIENCY THRESHOLD  (the reported cliff near 0.45)")
print(f"  {'Q2eff <=':<10}{'n':>5}{'PF':>8}{'exp R':>9}{'net R':>9}{'WR':>7}   new trades admitted")
prev = None
for t in (0.30, 0.325, 0.35, 0.375, 0.40, 0.425, 0.4375, 0.45, 0.475, 0.50, 0.55, 0.60, 9.0):
    r = pd.Series({**base, "q2_eff_max": t})
    m = mask_of(r); s = full(m)
    add = ""
    if prev is not None:
        new = m & ~prev
        if new.sum():
            add = "  ".join(f"{v:+.2f}R" for v in P[new])
    print(f"  {t:<10g}{s['n']:>5}{s['pf']:>8.2f}{s['exp']:>+9.3f}{s['net']:>+9.2f}{s['wr']:>6.1f}%   {add}")
    prev = m

print("\n  DFR / Q1 THRESHOLD")
print(f"  {'DFR <=':<10}{'n':>5}{'PF':>8}{'exp R':>9}{'net R':>9}{'WR':>7}")
for t in (0.50, 0.60, 0.70, 0.75, 0.775, 0.80, 0.825, 0.85, 0.90, 9.0):
    s = full(mask_of(pd.Series({**base, "q2_eff_max": 0.40, "dfr_max": t})))
    print(f"  {t:<10g}{s['n']:>5}{s['pf']:>8.2f}{s['exp']:>+9.3f}{s['net']:>+9.2f}{s['wr']:>6.1f}%")

print("\n  SWEEP DEPTH THRESHOLD  (shallow liquidity grabs hypothesis)")
print(f"  {'sweep <=':<10}{'n':>5}{'PF':>8}{'exp R':>9}{'net R':>9}{'WR':>7}")
for t in (0.05, 0.075, 0.10, 0.125, 0.15, 0.175, 0.20, 0.225, 0.25, 0.30, 0.40, 0.50, 9.0):
    s = full(mask_of(pd.Series({**base, "q2_eff_max": 9.0, "dfr_max": 0.80,
                                "q1_eff_min": 0.0, "rr_max": 99.0, "act": (0.0, 1.0),
                                "sweep_max": t})))
    print(f"  {t:<10g}{s['n']:>5}{s['pf']:>8.2f}{s['exp']:>+9.3f}{s['net']:>+9.2f}{s['wr']:>6.1f}%")

print("\n  ACTIVITY PERCENTILE DECILES  (is the relationship hump-shaped?)")
print(f"  {'activity':<14}{'n':>5}{'PF':>8}{'exp R':>9}{'net R':>9}{'WR':>7}")
A = C.act_pct.to_numpy()
for lo_, hi_ in [(i / 10, (i + 1) / 10) for i in range(10)]:
    m = (A >= lo_) & (A < hi_ + (1e-9 if hi_ == 1.0 else 0))
    if m.sum() < 10:
        print(f"  {f'{lo_:.0%}-{hi_:.0%}':<14}{int(m.sum()):>5}   (too few)"); continue
    s = full(m)
    print(f"  {f'{lo_:.0%}-{hi_:.0%}':<14}{s['n']:>5}{s['pf']:>8.2f}{s['exp']:>+9.3f}"
          f"{s['net']:>+9.2f}{s['wr']:>6.1f}%")
