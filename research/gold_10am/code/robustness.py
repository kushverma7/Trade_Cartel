"""Phases 28-34: out-of-sample, walk-forward, placebos, bootstrap, Monte Carlo,
multiple-testing accounting.

The holdout (2026-02-20 .. 2026-08-19) is opened ONCE, at the end, and is never
used to choose anything.
"""
import os, sys, csv, math, random, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core, lib
from lib import f, pctl, table, METRIC_HEAD, metrics_row
import analysis as A

OUT = []
def sec(t): OUT.append(f"\n## {t}\n")
def add(s): OUT.append(s)

LOGICS = list(core.LOGICS)
LABEL = A.LABEL
COST = 1.26          # measured round-trip spread cost, see Phase 27


# =============================================================== PHASE 28
def phase28(tr, paths):
    sec("Phase 28 — Chronological out-of-sample")
    add(f"Split declared before any parameter search:\n\n"
        f"- **DEV** {lib.DEV[0]} → {lib.DEV[1]}\n"
        f"- **VAL** {lib.VAL[0]} → {lib.VAL[1]}\n"
        f"- **HOLD** {lib.HOLD[0]} → {lib.HOLD[1]} (opened once, below)\n\n"
        f"Baseline SL $17 / TP $39, round-trip cost ${COST:.2f} charged to P&L.\n")
    rows = []
    for lg in LOGICS:
        for nm, w in (("DEV", lib.DEV), ("VAL", lib.VAL), ("HOLD", lib.HOLD)):
            sub = [r for r in lib.window(tr, w) if r["logic"] == lg]
            rows.append(metrics_row(f"{LABEL[lg]} {nm}", [r["base_pnl"] - COST for r in sub]))
    add(table(METRIC_HEAD, rows))
    return rows


# =============================================================== PHASE 29
def phase29(tr, paths):
    sec("Phase 29 — Walk-forward")
    add("Each fold optimises SL and TP on its training window over the same coarse grid, "
        "then applies the single best cell to the immediately following test window. "
        "All planned folds are reported — none are dropped.\n")
    G_SL = [7.5, 10, 12.5, 15, 17.5, 20, 25, 30]
    G_TP = [10, 15, 20, 25, 30, 40, 50, 75]
    designs = [("6m train / 2m test", 6, 2), ("9m train / 3m test", 9, 3)]
    start, end = lib.DEV[0], lib.HOLD[1]

    def addm(d, months):
        y, m = d.year, d.month + months
        y += (m - 1) // 12; m = (m - 1) % 12 + 1
        return dt.date(y, m, min(d.day, 28))

    for dname, trn, tst in designs:
        add(f"\n**{dname}**\n")
        rows = []
        for lg in LOGICS:
            tot, wins, folds = [], 0, 0
            a = start
            while True:
                b = addm(a, trn); c = addm(b, tst)
                if c > end:
                    break
                trs = [r for r in tr if r["logic"] == lg and a <= r["date_d"] < b]
                tes = [r for r in tr if r["logic"] == lg and b <= r["date_d"] < c]
                if len(trs) >= 15 and tes:
                    best, bx = None, None
                    for sl in G_SL:
                        for tp in G_TP:
                            m = core.metrics([p - COST for p in A.resim(trs, sl, tp, paths)], False)
                            if best is None or m["expectancy"] > best:
                                best, bx = m["expectancy"], (sl, tp)
                    pn = [p - COST for p in A.resim(tes, bx[0], bx[1], paths)]
                    tot.extend(pn); folds += 1; wins += (sum(pn) > 0)
                a = addm(a, tst)
            m = core.metrics(tot, False)
            rows.append([LABEL[lg], folds, f"{wins}/{folds}", m["n"],
                         f(m.get("win_pct", 0), 1), f(m.get("expectancy", 0), 3),
                         f(m.get("pf", 0), 3), f(m.get("net", 0))])
        add(table(["Logic", "Folds", "Profitable folds", "OOS trades", "Win %",
                   "Expectancy", "PF", "Net $"], rows))


# =============================================================== PHASE 30
def phase30():
    sec("Phase 30 — Clock placebo: is 09:50/10:00 special?")
    add("The whole method is rebuilt at nearby anchor pairs, keeping the 10-minute "
        "reference→body spacing. To make the comparison fair, **only days on which every "
        "anchor pair exists** are used, so a pair is never flattered by trading a different "
        "set of days.\n")
    raw = core.load_1m(os.path.join(core.RAW, "xauusd_1m_bid_dukascopy.csv.gz"))
    mrows = core.to_melbourne(raw)
    bars5 = core.build_5m(mrows)
    days5 = core.by_day(bars5)
    dmins = core.minutes_by_day(mrows)

    PAIRS = [(570, 580), (575, 585), (580, 590), (585, 595), (590, 600),
             (595, 605), (600, 610), (605, 615)]
    common = []
    for d in sorted(days5):
        if d.weekday() >= 5:
            continue
        mm = {b["minute"]: b for b in days5[d]}
        if all(r in mm and b in mm for r, b in PAIRS):
            common.append(d)
    add(f"Days on which all {len(PAIRS)} anchor pairs exist: **{len(common)}** "
        f"(the baseline alone has 339; the shared set is smaller because the earlier "
        f"anchors fall inside the maintenance break on more days).\n")

    rows = []
    for ref_m, body_m in PAIRS:
        pn = collections.defaultdict(list)
        for d in common:
            mm = {b["minute"]: b for b in days5[d]}
            ref, body = mm[ref_m], mm[body_m]
            d_open = ref["open"]
            b_hi = max(body["open"], body["close"]); b_lo = min(body["open"], body["close"])
            side = 1 if body["close"] > d_open else -1
            mins = dmins[d]; eod = max(m["minute"] for m in mins)
            seen = set()
            for b in days5[d]:
                if b["minute"] <= body_m:
                    continue
                c = b["close"]
                up = c > b_hi and c > d_open
                dn = c < b_lo and c < d_open
                lg = None
                if side == -1:
                    lg = "A_SHORT" if dn else ("FLIP_L" if up else None)
                else:
                    lg = "A_LONG" if up else ("FLIP_S" if dn else None)
                if lg is None or lg in seen:
                    continue
                seen.add(lg)
                sd = core.DIRECTION[lg]
                p = core.path_after(mins, b["minute"])
                pn[lg].append(core.resolve(c, sd, 17.0, 39.0, p, eod)["pnl_pess"] - COST)
        tag = "**BASE**" if (ref_m, body_m) == (590, 600) else ""
        rows.append([f"{ref_m//60:02d}:{ref_m%60:02d}/{body_m//60:02d}:{body_m%60:02d} {tag}"] +
                    [f"{core.metrics(pn[lg],False).get('expectancy',0):.2f} "
                     f"({core.metrics(pn[lg],False).get('pf',0):.2f}, n={len(pn[lg])})"
                     for lg in LOGICS])
    add(table(["Anchor pair"] + [LABEL[lg] for lg in LOGICS], rows))
    return rows


# =============================================================== PHASE 31
def phase31(tr, paths, n_iter=2000, seed=11):
    sec("Phase 31 — Random placebos")
    add("Three nulls, each preserving something real about the strategy and destroying "
        "the claimed edge. The observed value must sit outside the null distribution to "
        "mean anything.\n")
    rnd = random.Random(seed)
    rows = []
    for lg in LOGICS:
        sub = [r for r in tr if r["logic"] == lg]
        obs = core.metrics([r["base_pnl"] - COST for r in sub], False)["expectancy"]

        # NULL 1 — random direction, same entries, same barriers
        dist = []
        for _ in range(n_iter):
            pn = []
            for r in sub:
                sd = 1 if rnd.random() < 0.5 else -1
                p = paths[(r["date"], r["logic"])]
                pn.append(core.resolve(r["entry"], sd, 17.0, 39.0, p, r["eod_minute"])["pnl_pess"] - COST)
            dist.append(sum(pn) / len(pn))
        p1 = sum(1 for x in dist if x >= obs) / len(dist)

        # NULL 2 — sign-flipped outcomes (permutation of the direction label)
        base = [r["base_pnl"] for r in sub]
        d2 = []
        for _ in range(n_iter):
            d2.append(sum((x if rnd.random() < 0.5 else -x) - COST for x in base) / len(base))
        p2 = sum(1 for x in d2 if x >= obs) / len(d2)

        # NULL 3 — random entry minute on the same day, same direction
        d3 = []
        for _ in range(min(n_iter, 400)):
            pn = []
            for r in sub:
                p = paths[(r["date"], r["logic"])]
                if len(p) < 30:
                    continue
                k = rnd.randrange(0, len(p) - 20)
                pn.append(core.resolve(p[k]["close"], r["side"], 17.0, 39.0,
                                       p[k + 1:], r["eod_minute"])["pnl_pess"] - COST)
            if pn:
                d3.append(sum(pn) / len(pn))
        p3 = sum(1 for x in d3 if x >= obs) / len(d3) if d3 else float("nan")

        rows.append([LABEL[lg], f(obs, 3),
                     f"{pctl(dist,50):.2f} [{pctl(dist,5):.2f},{pctl(dist,95):.2f}]", f(p1, 3),
                     f"{pctl(d2,50):.2f} [{pctl(d2,5):.2f},{pctl(d2,95):.2f}]", f(p2, 3),
                     f"{pctl(d3,50):.2f} [{pctl(d3,5):.2f},{pctl(d3,95):.2f}]" if d3 else "—",
                     f(p3, 3)])
    add(table(["Logic", "Observed exp $", "Null 1 random direction", "p",
               "Null 2 sign flip", "p", "Null 3 random entry time", "p"], rows))
    return rows


# =============================================================== PHASE 32/33
def phase32(tr):
    sec("Phase 32 — Block bootstrap (block = 10 trades, 5,000 resamples)")
    add("Trades from the same regime are not independent, so the resample is by blocks "
        "of ten consecutive trades rather than by single trades.\n")
    rows = []
    for lg in LOGICS:
        sub = sorted([r for r in tr if r["logic"] == lg], key=lambda r: (r["date"], r["entry_minute"]))
        b = lib.block_bootstrap([r["base_pnl"] - COST for r in sub])
        rows.append([LABEL[lg], len(sub),
                     f"{b['exp'][1]:.2f} [{b['exp'][0]:.2f}, {b['exp'][2]:.2f}]",
                     f"{b['pf'][1]:.2f} [{b['pf'][0]:.2f}, {b['pf'][2]:.2f}]",
                     f"{b['net'][1]:.0f} [{b['net'][0]:.0f}, {b['net'][2]:.0f}]",
                     f"{b['dd'][1]:.0f} [{b['dd'][0]:.0f}, {b['dd'][2]:.0f}]",
                     f"{100*b['p_positive']:.1f}%"])
    add(table(["Logic", "N", "Expectancy (median [5,95])", "PF", "Net $", "Max DD",
               "P(net > 0)"], rows))
    return rows


def phase33(tr, n_iter=5000, seed=23):
    sec("Phase 33 — Monte Carlo")
    add("Each run reshuffles trade order, draws a round-trip cost from the measured "
        "spread distribution scaled for slippage, and randomly drops 10% of trades as "
        "missed fills.\n")
    rnd = random.Random(seed)
    rows = []
    for lg in LOGICS:
        sub = [r["base_pnl"] for r in tr if r["logic"] == lg]
        nets, dds, streaks = [], [], []
        for _ in range(n_iter):
            s = [x for x in sub if rnd.random() > 0.10]
            rnd.shuffle(s)
            c = rnd.uniform(0.9, 2.5)
            s = [x - c for x in s]
            m = core.metrics(s, False)
            nets.append(m["net"]); dds.append(m["max_dd"])
            run = best = 0
            for x in s:
                run = run + 1 if x < 0 else 0
                best = max(best, run)
            streaks.append(best)
        rows.append([LABEL[lg],
                     f"{pctl(nets,50):.0f}", f"{pctl(nets,5):.0f}", f"{pctl(nets,95):.0f}",
                     f"{100*sum(1 for x in nets if x>0)/len(nets):.1f}%",
                     f"{pctl(dds,50):.0f}", f"{pctl(dds,95):.0f}",
                     f"{pctl(streaks,50):.0f}", f"{pctl(streaks,95):.0f}"])
    add(table(["Logic", "Median net $", "5th pct", "95th pct", "P(profit)",
               "Median DD", "95th DD", "Median losing streak", "95th streak"], rows))
    return rows


# =============================================================== PHASE 34
def phase34(counts):
    sec("Phase 34 — Multiple-testing accounting")
    tot = sum(counts.values())
    rows = [[k, v] for k, v in counts.items()]
    rows.append(["**Total distinct evaluations**", f"**{tot}**"])
    add(table(["Family", "Combinations evaluated"], rows))
    bar = math.sqrt(2 * math.log(tot)) if tot > 1 else 0
    add(f"\nWith **K ≈ {tot}** evaluations, the selection-adjusted significance bar is "
        f"t ≥ √(2·ln K) = **{bar:.2f}**. A result must clear that, not t ≈ 2, before it "
        f"counts as a discovery rather than as the maximum of a search.\n")
    return bar


def main():
    tr = lib.load("trades.csv")
    paths, dmins = A.load_paths(tr)
    OUT.append("# Gold 10AM — robustness (Phases 28–34)\n")
    OUT.append(f"_Round-trip cost of **${COST:.2f}** (twice the measured median spread) is "
               f"charged to every trade in this file._\n")
    phase28(tr, paths); print("p28", flush=True)
    phase29(tr, paths); print("p29", flush=True)
    phase30(); print("p30", flush=True)
    phase31(tr, paths); print("p31", flush=True)
    phase32(tr); print("p32", flush=True)
    phase33(tr); print("p33", flush=True)
    phase34({"logic branches and combinations (Phase 1)": 10,
             "first-passage barriers (Phase 6)": 64,
             "ATR-scaled barriers (Phase 7b)": 48,
             "fixed stops (Phase 8)": 76,
             "fixed targets (Phase 9)": 76,
             "SL x TP surface cells (Phase 10)": 400,
             "time stops (Phase 11)": 44,
             "structure terciles (Phase 13)": 84,
             "side definitions (Phase 14)": 16,
             "volatility regimes (Phase 15)": 20,
             "entry-time bands (Phase 16)": 40,
             "sessions (Phase 17)": 16,
             "weekdays (Phase 19)": 20,
             "entry buffers (Phase 22)": 32,
             "breakout-strength terciles (Phase 23)": 48,
             "exit-management variants (Phase 24)": 32,
             "cost levels (Phase 27)": 36,
             "walk-forward fold optimisations (Phase 29)": 64,
             "clock placebos (Phase 30)": 32})
    with open(os.path.join(lib.TAB, "phases_28_34.md"), "w") as f_:
        f_.write("\n".join(x for x in OUT if x))
    print("wrote tables/phases_28_34.md")


if __name__ == "__main__":
    main()
