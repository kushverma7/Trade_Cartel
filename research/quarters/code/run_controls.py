"""CONTROLS — isolate each component of the result.

1. entry-at-level    enter AT Q with the stop 0.30*S the wrong side, so the
                     risk matches the baseline exactly. This is the fair test
                     of whether waiting for the 0.30*S penetration earns
                     anything. (An earlier version put the stop at Q as well,
                     making risk ~= the spread; that was degenerate, not a
                     result, and is discarded.)
2. zero-cost         the baseline filled on MID instead of bid/ask. If the
                     system is profitable on mid and unprofitable on real
                     quotes, the loss IS the spread -- the same verdict the
                     all-day QT sweep reached in Phase 9.
3. inverted          take the opposite side of every baseline signal. If the
                     rule carried real information, inverting it should make
                     money (minus twice the spread). If inverting also loses,
                     there is no directional information to invert.
"""
import sys, time, numpy as np, pandas as pd
sys.path.insert(0, "research/quarters/code"); sys.path.insert(0, "research/goldmap/code")
from system import Book, prep, run, stats, PTS
from grid import DATA

SCALES = [25.0, 50.0, 100.0, 250.0]
rows = []
for year, d in DATA.items():
    b = Book(d, year)
    print(f"\n{'#'*104}\n{year}\n{'#'*104}", flush=True)
    print(f"  {'S':>8}  {'control':<16}{'n':>7}{'PF':>8}{'exp R':>9}{'net R':>10}"
          f"{'net $':>11}{'WR':>7}{'spread/risk':>13}")
    for S in SCALES:
        g = prep(b, S, 0.0)
        base = run(b, S, 0.0, grids=g)
        variants = {
            "yotov (baseline)": base,
            "entry-at-level":   run(b, S, 0.0, grids=g, decisive=False, stop_at=0.30),
        }
        # zero-cost: rerun with bid=ask=mid so no spread is paid anywhere
        mb = type("B", (), {})()
        mb.ny, mb.mid, mb.bid, mb.ask = b.ny, b.mid, b.mid, b.mid
        variants["zero-cost (mid fills)"] = run(mb, S, 0.0)
        for name, tr in variants.items():
            s = stats(tr)
            if s is None:
                continue
            spr = np.nan
            if name == "yotov (baseline)" and tr:
                spr = 0.67 / (0.30 * S)     # measured round-trip spread / nominal risk
            rows.append(dict(year=year, S=S, control=name, **s))
            print(f"  {S:8.2f}  {name:<16}{s['n']:>7}{s['pf']:>8.3f}{s['exp']:>+9.4f}"
                  f"{s['net_R']:>+10.1f}{s['net_usd']:>+11.1f}{s['wr']:>6.1f}%"
                  f"{(f'{spr:.1%}' if spr == spr else ''):>13}", flush=True)
        # keep the baseline trade list so direction / monthly splits are possible
        if base:
            pd.DataFrame(base, columns=["t_ms", "dir", "entry", "pnl_usd",
                                        "pnl_R", "tag", "hold_min"]).assign(
                year=year, S=S).to_csv(
                f"research/quarters/results/trades_{year}_{int(S)}.csv", index=False)
            for dd, lbl in ((1, "long"), (-1, "short")):
                sub = [t for t in base if t[1] == dd]
                if not sub:
                    continue
                rr = np.array([t[4] for t in sub])
                gpp, gll = rr[rr > 0].sum(), -rr[rr < 0].sum()
                print(f"  {S:8.2f}  {'  -> ' + lbl:<16}{len(rr):>7}"
                      f"{(gpp/gll if gll>0 else np.inf):>8.3f}{rr.mean():>+9.4f}"
                      f"{rr.sum():>+10.1f}{'':>11}{100*(rr>0).mean():>6.1f}%", flush=True)

        # inverted: same trade list, opposite sign, so it needs no new pass
        r = np.array([t[4] for t in base], float)
        inv = -r
        gp, gl = inv[inv > 0].sum(), -inv[inv < 0].sum()
        print(f"  {S:8.2f}  {'inverted':<16}{len(inv):>7}"
              f"{(gp/gl if gl>0 else np.inf):>8.3f}{inv.mean():>+9.4f}{inv.sum():>+10.1f}"
              f"{'':>11}{100*(inv>0).mean():>6.1f}%", flush=True)
        rows.append(dict(year=year, S=S, control="inverted", n=len(inv),
                         pf=(gp/gl if gl > 0 else np.inf), exp=float(inv.mean()),
                         net_R=float(inv.sum()), net_usd=np.nan,
                         wr=100*float((inv > 0).mean()), dd=np.nan,
                         tp=0, sl=0, time=0, hold=np.nan))
        del g
    del b
pd.DataFrame(rows).to_csv("research/quarters/results/controls.csv", index=False)
print("\nwritten -> research/quarters/results/controls.csv")
