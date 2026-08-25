"""Adversarial battery, part 1: A time, B body, C quarter, D grid placebo,
E spread, F window, G direction. Exits fixed at SL 15.50 / TP 25.50 throughout
so that only the entry rule varies."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/microq3/code")
import microq3 as M

SL, TP = 15.5, 25.5
pd.set_option("display.width", 250)


def run(**kw):
    tr = M.signals(**kw)
    d = M.apply(tr, SL, TP)
    s = M.summarise(d)
    s["long_n"] = int(d["long"].sum()) if len(d) else 0
    return s, d


def line(tag, s, extra=""):
    if s["n"] == 0:
        return f"{tag:<34}{'0':>5}{'--':>9}{'--':>9}{'--':>9}{'--':>8}{'--':>8}  {extra}"
    return (f"{tag:<34}{s['n']:>5}{s['pf']:>9.2f}{s['exp']:>9.2f}{s['net']:>9.1f}"
            f"{s['wr']:>7.0f}%{s['mdd']:>8.1f}  {extra}")


HDR = f"{'':<34}{'n':>5}{'PF':>9}{'exp':>9}{'net':>9}{'WR':>8}{'maxDD':>8}"

print("=" * 100)
print("A. TIME ROBUSTNESS — anchor start shifted, everything else fixed")
print("=" * 100)
print(HDR)
rowsA = []
for st in range(17 * 60 + 45, 20 * 60 + 15, 5):
    s, _ = run(anchor_start=st, win_from=st + 15, win_to=st + 45)
    tag = f"  {st//60:02d}:{st%60:02d}-{(st+15)//60:02d}:{(st+15)%60:02d}"
    mark = "   <-- CLAIMED" if st == 18 * 60 + 45 else ""
    print(line(tag, s, mark))
    rowsA.append(dict(anchor_start=st, **{k: s[k] for k in ("n", "pf", "exp", "net", "wr", "mdd")}))
pd.DataFrame(rowsA).to_csv("research/microq3/results/A_time.csv", index=False)
prof = [r for r in rowsA if r["n"] >= 10 and r["pf"] > 1]
print(f"\nanchors with n>=10 and PF>1: {len(prof)} of {sum(1 for r in rowsA if r['n']>=10)} "
      f"with a usable sample")

print("\n" + "=" * 100)
print("D. PRICE-GRID PLACEBO — same $25 spacing, grid shifted off round numbers")
print("=" * 100)
print(HDR)
rowsD = []
for ph in [0.0, 2.5, 5.0, 7.5, 10.0, 12.5, 15.0, 17.5, 20.0, 22.5]:
    s, _ = run(grid_phase=ph)
    mark = "   <-- TRUE $25 GRID" if ph == 0 else ""
    print(line(f"  25n + {ph:g}", s, mark))
    rowsD.append(dict(phase=ph, **{k: s[k] for k in ("n", "pf", "exp", "net", "wr", "mdd")}))
D = pd.DataFrame(rowsD); D.to_csv("research/microq3/results/D_grid_placebo.csv", index=False)
true = D[D.phase == 0].iloc[0]; plac = D[D.phase != 0]
print(f"\ntrue grid PF {true.pf:.2f}, exp {true.exp:+.2f}")
print(f"placebo grids PF {plac.pf.mean():.2f} +- {plac.pf.std():.2f}  (range {plac.pf.min():.2f}..{plac.pf.max():.2f})")
print(f"placebos with PF >= the true grid: {int((plac.pf >= true.pf).sum())} of {len(plac)}")
print(f"placebos with exp >= the true grid: {int((plac.exp >= true.exp).sum())} of {len(plac)}")
print(f"percentile rank of the true grid among all 10: "
      f"{100.0*(D.pf < true.pf).sum()/len(D):.0f}th on PF")

print("\n" + "=" * 100)
print("C. QUARTER-DISTANCE ROBUSTNESS")
print("=" * 100)
print(HDR)
rowsC = []
for q in [1, 2, 3, 4, 5, 6, 6.25, 7, 7.5, 8, 10, 12.5, None]:
    s, _ = run(qdist=q)
    mark = "   <-- CLAIMED" if q == 6.25 else ("   (filter off)" if q is None else "")
    print(line(f"  <= ${q}" if q else "  no quarter filter", s, mark))
    rowsC.append(dict(qdist=(q if q else 99), **{k: s[k] for k in ("n", "pf", "exp", "net", "wr", "mdd")}))
pd.DataFrame(rowsC).to_csv("research/microq3/results/C_quarter.csv", index=False)

print("\n" + "=" * 100)
print("E. SPREAD FILTER ROBUSTNESS")
print("=" * 100)
print(HDR)
rowsE = []
for sp in [None, 3.0, 2.5, 2.0, 1.75, 1.6, 1.5, 1.4, 1.25, 1.0]:
    s, _ = run(spread_max=sp)
    mark = "   <-- CLAIMED" if sp == 1.5 else ""
    print(line("  no spread filter" if sp is None else f"  <= ${sp}", s, mark))
    rowsE.append(dict(spread_max=(sp if sp else 99), **{k: s[k] for k in ("n", "pf", "exp", "net", "wr", "mdd")}))
pd.DataFrame(rowsE).to_csv("research/microq3/results/E_spread.csv", index=False)

print("\n" + "=" * 100)
print("F. SIGNAL-WINDOW ROBUSTNESS — minutes after the anchor completes")
print("=" * 100)
print(HDR)
rowsF = []
for w in [10, 15, 20, 25, 30, 35, 45, 60, 90]:
    s, _ = run(win_to=19 * 60 + w)
    mark = "   <-- CLAIMED" if w == 30 else ""
    print(line(f"  19:00 + {w}m", s, mark))
    rowsF.append(dict(win_min=w, **{k: s[k] for k in ("n", "pf", "exp", "net", "wr", "mdd")}))
pd.DataFrame(rowsF).to_csv("research/microq3/results/F_window.csv", index=False)

print("\n" + "=" * 100)
print("G. DIRECTION DECOMPOSITION  (Wilson 95% CI on win rate)")
print("=" * 100)
print(HDR)
for tag, kw in (("  A SHORT only", dict(allow_long=False)),
                ("  FLIP LONG only", dict(allow_short=False)),
                ("  combined", {})):
    s, d = run(**kw)
    if s["n"]:
        w, n = int((d.pnl > 0).sum()), s["n"]
        z = 1.96; ph = w / n
        den = 1 + z * z / n
        c = (ph + z * z / (2 * n)) / den
        hw = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
        print(line(tag, s, f"wins {w}/{n}  WR 95% CI [{100*(c-hw):.0f}%, {100*(c+hw):.0f}%]"))
    else:
        print(line(tag, s))
print("\nNOTE: allow_short/allow_long filter AFTER the first-break rule, so a day whose")
print("first break is the excluded direction is dropped, never replaced by a later break.")

print("\n" + "=" * 100)
print("Q. BODY-DIRECTION PLACEBO — does 'bearish anchor' matter?")
print("=" * 100)
print(HDR)
for tag, kw in (("  bearish anchors (claimed)", dict(need_bearish=True)),
                ("  bullish anchors", dict(need_bearish=False)),
                ("  ignore direction", dict(need_bearish=None))):
    s, _ = run(**kw)
    print(line(tag, s))
