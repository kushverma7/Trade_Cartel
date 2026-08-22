"""Battery part 2: B body surface, H exit surface, J MFE/MAE, K chronology and
walk-forward, L leave-one-month-out, M tail dependence."""
import sys, numpy as np, pandas as pd, itertools
sys.path.insert(0, "research/microq3/code")
import microq3 as M
import engine as E

SL, TP = 15.5, 25.5
pd.set_option("display.width", 260)
BASE = M.signals()
BD = M.apply(BASE, SL, TP)
print(f"base: n={len(BD)}  PF={M.summarise(BD)['pf']:.2f}\n")

# ---------------- B. BODY FILTER SURFACE ----------------
print("=" * 108)
print("B. BODY FILTER SURFACE — cell shows  PF / n   (SL 15.5 / TP 25.5). '--' = fewer than 8 trades")
print("=" * 108)
mins = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
maxs = [4, 5, 6, 6.25, 7, 8, 10, 12, 15, None]
hdr = "min\\max".ljust(9) + "".join(f"{(str(x) if x else 'none'):>13}" for x in maxs)
print(hdr)
rowsB = []
for bmin in mins:
    line = f"{bmin:<9g}"
    for bmax in maxs:
        if bmax is not None and bmax <= bmin:
            line += f"{'.':>13}"; continue
        s = M.summarise(M.apply(M.signals(body_min=bmin, body_max=bmax), SL, TP))
        rowsB.append(dict(body_min=bmin, body_max=(bmax if bmax else 99), **{k: s[k] for k in ("n","pf","exp","net","mdd")}))
        cell = (f"{s['pf']:.2f}/{s['n']}" if s['n'] >= 8 else f"--/{s['n']}")
        line += f"{cell:>13}"
    print(line)
B = pd.DataFrame(rowsB); B.to_csv("research/microq3/results/B_body.csv", index=False)
ok = B[(B.n >= 8)]
print(f"\ncells with n>=8: {len(ok)}   PF>=4: {int((ok.pf>=4).sum())}   PF>=2: {int((ok.pf>=2).sum())}   PF<1: {int((ok.pf<1).sum())}")
cl = B[(B.body_min==1.0)&(B.body_max==6.25)].iloc[0]
print(f"claimed cell (1.00, 6.25): PF {cl.pf:.2f} n {int(cl.n)}   rank {int((ok.pf>cl.pf).sum())+1} of {len(ok)}")

# ---------------- H. EXIT SURFACE ----------------
print("\n" + "=" * 108)
print("H. EXIT SURFACE — PF, entry universe fixed at the claimed rule (n=25)")
print("=" * 108)
SLS = [5,7.5,10,12.5,15,15.5,17.5,20,25,30,40]
TPS = [3,5,10,15,20,25,25.5,30,35,50,75,100]
print("SL\\TP".ljust(8) + "".join(f"{t:>8g}" for t in TPS))
rowsH = []
for sl in SLS:
    line = f"{sl:<8g}"
    for tp in TPS:
        s = M.summarise(M.apply(BASE, sl, tp))
        rowsH.append(dict(sl=sl, tp=tp, **{k: s[k] for k in ("n","pf","exp","net","mdd","wr")}))
        line += f"{s['pf']:>8.2f}"
    print(line)
H = pd.DataFrame(rowsH); H.to_csv("research/microq3/results/H_exit_surface.csv", index=False)
print(f"\ncells: {len(H)}   PF>=2: {int((H.pf>=2).sum())} ({100*(H.pf>=2).mean():.0f}%)   "
      f"PF>=1: {int((H.pf>=1).sum())} ({100*(H.pf>=1).mean():.0f}%)   PF<1: {int((H.pf<1).sum())}")
z = H[(H.sl.between(10,20)) & (H.tp.between(20,35))]
print(f"zoom SL 10-20 x TP 20-35: {len(z)} cells, PF {z.pf.min():.2f}..{z.pf.max():.2f}, "
      f"all >= 1? {bool((z.pf>=1).all())}, median {z.pf.median():.2f}")

# ---------------- I. NO-OPTIMISATION EXITS ----------------
print("\n" + "=" * 108)
print("I. SIMPLE, UNOPTIMISED EXITS — does the ENTRY carry the edge?")
print("=" * 108)
print(f"{'exit':<26}{'n':>5}{'PF':>9}{'exp':>9}{'net':>9}{'WR':>8}{'maxDD':>9}")
for tag, kw in (("SL10/TP10", dict(sl=10,tp=10)), ("SL15/TP15", dict(sl=15,tp=15)),
                ("SL20/TP20", dict(sl=20,tp=20)), ("SL25/TP25", dict(sl=25,tp=25)),
                ("SL15/TP25", dict(sl=15,tp=25)), ("SL25/TP15", dict(sl=25,tp=15)),
                ("SL15.5/TP25.5 CLAIMED", dict(sl=15.5,tp=25.5))):
    s = M.summarise(M.apply(BASE, **kw))
    print(f"{tag:<26}{s['n']:>5}{s['pf']:>9.2f}{s['exp']:>9.2f}{s['net']:>9.1f}{s['wr']:>7.0f}%{s['mdd']:>9.1f}")
for tsm in (240, 480):
    s = M.summarise(M.apply(BASE, 10_000, 10_000, time_stop_min=tsm))
    print(f"{f'pure {tsm}m time exit':<26}{s['n']:>5}{s['pf']:>9.2f}{s['exp']:>9.2f}{s['net']:>9.1f}{s['wr']:>7.0f}%{s['mdd']:>9.1f}")
s = M.summarise(M.apply(BASE, 10_000, 10_000))
print(f"{'pure EOD exit (no SL/TP)':<26}{s['n']:>5}{s['pf']:>9.2f}{s['exp']:>9.2f}{s['net']:>9.1f}{s['wr']:>7.0f}%{s['mdd']:>9.1f}")

# ---------------- J. MFE / MAE ----------------
print("\n" + "=" * 108)
print("J. MFE / MAE — unrestricted, no SL or TP applied, measured to session end")
print("=" * 108)
raw = M.apply(BASE, 10_000, 10_000)
print(f"{'group':<14}{'n':>4}" + "".join(f"{q:>9}" for q in ("mean","p25","p50","p75","p90","p95","max")))
for grp in ("A_SHORT", "FLIP_LONG", "ALL"):
    sub = raw if grp == "ALL" else raw[raw.kind == grp]
    for col, nm in (("mfe", "MFE"), ("mae", "MAE")):
        v = sub[col].abs()
        print(f"{grp+' '+nm:<14}{len(sub):>4}" + "".join(f"{x:>9.1f}" for x in
              (v.mean(), v.quantile(.25), v.quantile(.5), v.quantile(.75), v.quantile(.9), v.quantile(.95), v.max())))
raw.to_csv("research/microq3/results/J_mfe_mae.csv", index=False)

# ---------------- K. CHRONOLOGY ----------------
print("\n" + "=" * 108)
print("K. CHRONOLOGICAL SPLITS")
print("=" * 108)
BD2 = BD.sort_values("t_entry").reset_index(drop=True)
def chunk(df, k, nm):
    print(f"\n  {nm}:")
    print(f"    {'segment':<26}{'n':>5}{'PF':>9}{'exp':>9}{'net':>9}{'WR':>8}")
    b = np.array_split(np.arange(len(df)), k)
    for i, ix in enumerate(b):
        s = E.stats(df.iloc[ix]["pnl"].tolist())
        d0, d1 = df.iloc[ix[0]]["date"], df.iloc[ix[-1]]["date"]
        print(f"    {str(d0)+' .. '+str(d1):<26}{s['n']:>5}{s['pf']:>9.2f}{s['exp']:>9.2f}{s['net']:>9.1f}{s['wr']:>7.0f}%")
for k, nm in ((2, "halves"), (3, "thirds"), (4, "quarters")):
    chunk(BD2, k, nm)
BD2["ym"] = pd.to_datetime(BD2.t_entry).dt.to_period("M").astype(str)
print("\n  by calendar month:")
print(f"    {'month':<10}{'n':>5}{'PF':>9}{'net':>9}")
for ym, g in BD2.groupby("ym"):
    s = E.stats(g.pnl.tolist())
    print(f"    {ym:<10}{s['n']:>5}{s['pf']:>9.2f}{s['net']:>9.1f}")

# ---------------- L. LEAVE ONE MONTH OUT ----------------
print("\n" + "=" * 108)
print("L. LEAVE-ONE-MONTH-OUT")
print("=" * 108)
print(f"    {'removed':<10}{'n':>5}{'PF':>9}{'exp':>9}{'net':>9}")
worst = []
for ym in sorted(BD2.ym.unique()):
    g = BD2[BD2.ym != ym]
    s = E.stats(g.pnl.tolist())
    worst.append((s["pf"], s["exp"], ym, s["n"]))
    print(f"    {ym:<10}{s['n']:>5}{s['pf']:>9.2f}{s['exp']:>9.2f}{s['net']:>9.1f}")
worst.sort()
print(f"\n    worst LOMO PF {worst[0][0]:.2f} (removing {worst[0][2]}, leaves n={worst[0][3]})")

# ---------------- M. TAIL DEPENDENCE ----------------
print("\n" + "=" * 108)
print("M. TAIL DEPENDENCE")
print("=" * 108)
p = np.sort(BD2.pnl.to_numpy())[::-1]
print(f"    {'variant':<28}{'n':>5}{'PF':>9}{'exp':>9}{'net':>9}")
for k in (0, 1, 3, 5):
    q = p[k:]
    s = E.stats(q.tolist())
    print(f"    {('drop best '+str(k) if k else 'all trades'):<28}{s['n']:>5}{s['pf']:>9.2f}{s['exp']:>9.2f}{s['net']:>9.1f}")
k10 = max(1, int(round(0.10 * len(p))))
s = E.stats(p[k10:].tolist())
print(f"    {'drop best 10% ('+str(k10)+')':<28}{s['n']:>5}{s['pf']:>9.2f}{s['exp']:>9.2f}{s['net']:>9.1f}")
w = np.clip(BD2.pnl.to_numpy(), None, np.percentile(BD2.pnl, 90))
s = E.stats(w.tolist())
print(f"    {'winsorise winners at p90':<28}{s['n']:>5}{s['pf']:>9.2f}{s['exp']:>9.2f}{s['net']:>9.1f}")
BD2.to_csv("research/microq3/results/trade_ledger.csv", index=False)
print(f"\nledger written: research/microq3/results/trade_ledger.csv ({len(BD2)} rows)")
