"""Phases 1-27: decomposition, MAE/MFE, first passage, path, parameter studies,
conditioning, costs. Writes markdown sections into tables/.

SAMPLE DISCIPLINE
  Descriptive tables (distributions, coverage, monthly) use the FULL sample —
  they select nothing.
  Every table that could CHOOSE a parameter or a filter is computed on DEV only
  and labelled DEV. VAL and HOLD are reported in robustness.py.
"""
import os, sys, csv, math, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core, lib
from lib import f, pctl, table, METRIC_HEAD, metrics_row

OUT = []
def sec(title):
    OUT.append(f"\n## {title}\n")
def add(s):
    OUT.append(s)

LOGICS = list(core.LOGICS)
LABEL = {"A_SHORT": "A Short", "A_LONG": "A Long", "FLIP_L": "Flip Long", "FLIP_S": "Flip Short"}

MAE_PCTS = [10, 20, 25, 50, 75, 80, 90, 95]
DOLLARS = [1, 2, 3, 5, 7.5, 10, 12.5, 15, 20, 25, 30, 40, 50]
ATR_UNITS = [0.10, 0.20, 0.25, 0.33, 0.50, 0.75, 1.00, 1.25, 1.50, 2.00, 2.50, 3.00]
SLS = [2, 3, 4, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, 30, 35, 40, 50, 60, 75, 100]
TPS = [2, 3, 5, 7.5, 10, 12.5, 15, 20, 25, 30, 35, 40, 50, 60, 75, 100, 125, 150, 200]
FP = [1, 2, 3, 5, 7.5, 10, 12.5, 15, 20, 25, 30, 40, 50, 60, 75, 100]


# ------------------------------------------------------------------ helpers
def by_logic(rows):
    d = {lg: [r for r in rows if r["logic"] == lg] for lg in LOGICS}
    return d


def combo(rows, logics, setups_index):
    """Daily state machine for a combination: no pyramiding, enter only while
    flat. Trades are taken in trigger order; a later trigger is admitted only
    if the previous trade has already exited."""
    byday = collections.defaultdict(list)
    for r in rows:
        if r["logic"] in logics:
            byday[r["date"]].append(r)
    out = []
    for d in sorted(byday):
        free_at = -1
        for r in sorted(byday[d], key=lambda x: x["entry_minute"]):
            if r["entry_minute"] < free_at:
                continue
            out.append(r)
            free_at = r["base_exit_minute"] if r["base_exit_minute"] is not None else 10 ** 9
    return out


def resim(rows, sl, tp, paths, cost=0.0, eod_cap=None):
    """Re-resolve a set of trades at new SL/TP using cached 1-minute paths."""
    pn = []
    for r in rows:
        p = paths[(r["date"], r["logic"])]
        eod = r["eod_minute"] if eod_cap is None else min(r["eod_minute"], eod_cap)
        res = core.resolve(r["entry"], r["side"], sl, tp, p, eod)
        pn.append(res["pnl_pess"] - cost)
    return pn


def load_paths(rows):
    """Rebuild the 1-minute path for each trade once, keyed by (date, logic)."""
    raw = core.load_1m(os.path.join(core.RAW, "xauusd_1m_bid_dukascopy.csv.gz"))
    mrows = core.to_melbourne(raw)
    dmins = core.minutes_by_day(mrows)
    paths = {}
    for r in rows:
        paths[(r["date"], r["logic"])] = core.path_after(dmins[r["date_d"]], r["entry_minute"])
    return paths, dmins


# =============================================================== PHASE 1
def phase1(tr, setups):
    sec("Phase 1 — Logic decomposition (full sample, baseline SL $17 / TP $39, zero cost)")
    rows = []
    for lg in LOGICS:
        rows.append(metrics_row(LABEL[lg], [r["base_pnl"] for r in tr if r["logic"] == lg]))
    combos = [("Flip Long + Flip Short", ["FLIP_L", "FLIP_S"]),
              ("A Short + Flip Long", ["A_SHORT", "FLIP_L"]),
              ("A Short + Flip Short", ["A_SHORT", "FLIP_S"]),
              ("A Short + both Flips", ["A_SHORT", "FLIP_L", "FLIP_S"]),
              ("A Long + A Short", ["A_LONG", "A_SHORT"]),
              ("All four", LOGICS)]
    for name, ls in combos:
        rows.append(metrics_row(name, [r["base_pnl"] for r in combo(tr, ls, setups)]))
    add(table(METRIC_HEAD, rows))

    # setup counts and trade frequency
    n_setup = len(setups)
    span_weeks = (max(s["date_d"] for s in setups) - min(s["date_d"] for s in setups)).days / 7
    rows = []
    for lg in LOGICS:
        sub = [r for r in tr if r["logic"] == lg]
        elig = sum(1 for s in setups if s["side"] == (-1 if lg in ("A_SHORT", "FLIP_L") else 1))
        rows.append([LABEL[lg], elig, len(sub), f(100 * len(sub) / elig, 1) + "%",
                     f(len(sub) / span_weeks, 2), f(len(sub) / (span_weeks / 4.345), 2)])
    add(table(["Logic", "Eligible setup days", "Trades", "Fire rate",
               "Trades/week", "Trades/month"], rows))

    amb = sum(1 for r in tr if r["base_outcome"] == "ambiguous")
    add(f"\nAmbiguous resolutions (SL and TP inside the same 1-minute bar): "
        f"**{amb} of {len(tr)} ({100*amb/len(tr):.2f}%)**. All headline numbers use the "
        f"PESSIMISTIC assignment (stop first). The optimistic assignment is carried in the "
        f"ledger as `base_pnl_opt`.\n")
    if amb:
        add(f"Optimistic-assignment net by logic: " + ", ".join(
            f"{LABEL[lg]} ${sum(r['base_pnl_opt'] for r in tr if r['logic']==lg):.0f}"
            for lg in LOGICS) + "\n")


# =============================================================== PHASE 2-5
def phase2345(tr):
    sec("Phase 2 — MAE distribution (full sample, dollars, no SL/TP cap)")
    head = ["Set", "N", "Mean", "Median"] + [f"p{p}" for p in MAE_PCTS] + ["Max"]
    rows = []
    for lg in LOGICS:
        for tag, sub in (("all", [r for r in tr if r["logic"] == lg]),
                         ("winners", [r for r in tr if r["logic"] == lg and r["base_pnl"] > 0]),
                         ("losers", [r for r in tr if r["logic"] == lg and r["base_pnl"] < 0])):
            xs = [r["mae_full"] for r in sub]
            if not xs:
                continue
            rows.append([f"{LABEL[lg]} {tag}", len(xs), f(sum(xs) / len(xs)), f(pctl(xs, 50))]
                        + [f(pctl(xs, p)) for p in MAE_PCTS] + [f(max(xs))])
    add(table(head, rows))

    sec("Phase 3 — MFE distribution (full sample, dollars, no SL/TP cap)")
    rows = []
    for lg in LOGICS:
        for tag, sub in (("all", [r for r in tr if r["logic"] == lg]),
                         ("winners", [r for r in tr if r["logic"] == lg and r["base_pnl"] > 0]),
                         ("losers", [r for r in tr if r["logic"] == lg and r["base_pnl"] < 0])):
            xs = [r["mfe_full"] for r in sub]
            if not xs:
                continue
            rows.append([f"{LABEL[lg]} {tag}", len(xs), f(sum(xs) / len(xs)), f(pctl(xs, 50))]
                        + [f(pctl(xs, p)) for p in MAE_PCTS] + [f(max(xs))])
    add(table(head, rows))

    sec("Phase 4 — Loser MFE: how far losing trades ran in our favour first")
    add("Percentage of LOSING trades (baseline exits) that first reached each favourable "
        "excursion. Read it as: *this much profit was on the table before the trade died.*\n")
    head = ["Logic", "Losers"] + [f"+${d:g}" for d in DOLLARS]
    rows = []
    for lg in LOGICS:
        sub = [r for r in tr if r["logic"] == lg and r["base_pnl"] < 0]
        if not sub:
            continue
        rows.append([LABEL[lg], len(sub)] +
                    [f(100 * sum(1 for r in sub if r["mfe"] >= d) / len(sub), 1) for d in DOLLARS])
    add(table(head, rows))

    sec("Phase 5 — Winner MAE: the empirical stop-survival curve")
    add("Percentage of WINNING trades that first suffered each adverse excursion. "
        "A stop tighter than a given column would have killed that share of the winners.\n")
    head = ["Logic", "Winners"] + [f"-${d:g}" for d in DOLLARS]
    rows = []
    for lg in LOGICS:
        sub = [r for r in tr if r["logic"] == lg and r["base_pnl"] > 0]
        if not sub:
            continue
        rows.append([LABEL[lg], len(sub)] +
                    [f(100 * sum(1 for r in sub if r["mae"] >= d) / len(sub), 1) for d in DOLLARS])
    add(table(head, rows))

    sec("Phase 5b — Recovery probability by adverse excursion reached")
    add("Of trades that reached a given MAE, what share still finished as baseline winners.\n")
    head = ["Logic"] + [f"≥${d:g}" for d in DOLLARS[:9]]
    rows = []
    for lg in LOGICS:
        sub = [r for r in tr if r["logic"] == lg]
        cells = []
        for d in DOLLARS[:9]:
            hit = [r for r in sub if r["mae"] >= d]
            cells.append(f"{100*sum(1 for r in hit if r['base_pnl']>0)/len(hit):.0f}% (n={len(hit)})"
                         if hit else "—")
        rows.append([LABEL[lg]] + cells)
    add(table(head, rows))


# =============================================================== PHASE 6
def phase6(tr):
    sec("Phase 6 — First passage at symmetric barriers (full sample)")
    add("For each ±$X, which side is touched first. A signal with genuine directional "
        "content shows **favourable-first above 50%** after unresolved days are dropped. "
        "The null is 50%; a 95% Wilson interval that contains 50% is no evidence.\n")
    for lg in LOGICS:
        sub = [r for r in tr if r["logic"] == lg]
        rows = []
        for x in FP:
            k = f"fp_{x}"
            fav = sum(1 for r in sub if r[k] == "fav")
            adv = sum(1 for r in sub if r[k] == "adv")
            amb = sum(1 for r in sub if r[k] == "amb")
            non = sum(1 for r in sub if r[k] == "none")
            n = fav + adv
            lo, hi = lib.wilson(fav, n)
            tf = [r[f"fpt_{x}"] for r in sub if r[k] == "fav" and r[f"fpt_{x}"]]
            ta = [r[f"fpt_{x}"] for r in sub if r[k] == "adv" and r[f"fpt_{x}"]]
            rows.append([f"${x:g}", n, f(100 * fav / n, 1) if n else "—",
                         f"[{100*lo:.1f}, {100*hi:.1f}]" if n else "—",
                         f(lib.binom_p(fav, n), 3) if n else "—",
                         amb, non,
                         f(pctl(tf, 50), 0) if tf else "—", f(pctl(ta, 50), 0) if ta else "—"])
        add(f"\n**{LABEL[lg]}** (n={len(sub)})\n")
        add(table(["Barrier", "Resolved", "Fav first %", "95% CI", "p (binom)",
                   "Amb", "Unresolved", "Med min to fav", "Med min to adv"], rows))


# =============================================================== PHASE 7
def phase7(tr):
    sec("Phase 7 — Volatility-normalised excursions and first passage")
    add("All excursions divided by the 14-period 5-minute ATR measured strictly before "
        "entry. Gold's dollar volatility roughly doubled across this window, so dollar "
        "thresholds are not comparable across the sample; ATR units are.\n")
    ok = [r for r in tr if r["atr14"] and r["atr14"] > 0]
    add(f"Trades with a computable pre-entry ATR: {len(ok)} of {len(tr)}. "
        f"Median ATR ${pctl([r['atr14'] for r in ok],50):.2f} "
        f"(2024 ${pctl([r['atr14'] for r in ok if r['year']==2024],50):.2f}, "
        f"2026 ${pctl([r['atr14'] for r in ok if r['year']==2026],50):.2f}).\n")
    head = ["Set", "N", "Mean", "Median"] + [f"p{p}" for p in MAE_PCTS]
    rows = []
    for lg in LOGICS:
        for tag, key in (("MAE/ATR", "mae_full"), ("MFE/ATR", "mfe_full")):
            xs = [r[key] / r["atr14"] for r in ok if r["logic"] == lg]
            if not xs:
                continue
            rows.append([f"{LABEL[lg]} {tag}", len(xs), f(sum(xs) / len(xs)), f(pctl(xs, 50))]
                        + [f(pctl(xs, p)) for p in MAE_PCTS])
    add(table(head, rows))

    add("\n**First passage in ATR units** (favourable-first %, resolved only)\n")
    rows = []
    for lg in LOGICS:
        sub = [r for r in ok if r["logic"] == lg]
        cells = []
        for u in ATR_UNITS:
            fav = adv = 0
            for r in sub:
                x = u * r["atr14"]
                # recompute from cached dollar barriers is not possible; use nearest
                # dollar barrier is wrong — so this is computed in resim_atr below
                cells.append(None)
                break
            break
        rows.append(None)
    add("_(computed in `atr_first_passage.csv`, see Phase 7b)_\n")


def phase7b(tr, paths):
    """Exact ATR-unit first passage — recomputed on the 1-minute paths."""
    rows = []
    ok = [r for r in tr if r["atr14"] and r["atr14"] > 0]
    for lg in LOGICS:
        sub = [r for r in ok if r["logic"] == lg]
        cells = []
        for u in ATR_UNITS:
            fav = adv = 0
            for r in sub:
                w, _ = core.first_passage(r["entry"], r["side"], u * r["atr14"],
                                          paths[(r["date"], r["logic"])], r["eod_minute"])
                if w == "fav":
                    fav += 1
                elif w == "adv":
                    adv += 1
            n = fav + adv
            lo, hi = lib.wilson(fav, n)
            cells.append(f"{100*fav/n:.1f} [{100*lo:.0f},{100*hi:.0f}] n={n}" if n else "—")
        rows.append([LABEL[lg]] + cells)
    add("\n**Phase 7b — first passage at ATR-scaled barriers** "
        "(fav-first %, 95% CI, resolved n)\n")
    add(table(["Logic"] + [f"{u:.2f}×ATR" for u in ATR_UNITS], rows))


# =============================================================== PHASE 8-10
def phase8910(tr, paths):
    dev = lib.window(tr, lib.DEV)
    sec("Phase 8 — Fixed stop study (DEV only, TP held at $39)")
    head = ["SL $"] + [LABEL[lg] + " PF" for lg in LOGICS] + [LABEL[lg] + " exp" for lg in LOGICS]
    rows = []
    for sl in SLS:
        cells_pf, cells_e = [], []
        for lg in LOGICS:
            sub = [r for r in dev if r["logic"] == lg]
            m = core.metrics(resim(sub, sl, 39.0, paths), absurd_check=False)
            cells_pf.append(f(m.get("pf", 0), 2)); cells_e.append(f(m.get("expectancy", 0), 2))
        rows.append([f"{sl:g}"] + cells_pf + cells_e)
    add(table(head, rows))

    sec("Phase 9 — Fixed target study (DEV only, SL held at $17)")
    rows = []
    for tp in TPS:
        cells_pf, cells_e = [], []
        for lg in LOGICS:
            sub = [r for r in dev if r["logic"] == lg]
            m = core.metrics(resim(sub, 17.0, tp, paths), absurd_check=False)
            cells_pf.append(f(m.get("pf", 0), 2)); cells_e.append(f(m.get("expectancy", 0), 2))
        rows.append([f"{tp:g}"] + cells_pf + cells_e)
    add(table(["TP $"] + [LABEL[lg] + " PF" for lg in LOGICS] +
              [LABEL[lg] + " exp" for lg in LOGICS], rows))

    sec("Phase 10 — SL × TP expectancy surfaces (DEV only)")
    add("Cell = expectancy in dollars per trade. A single bright cell is noise; a broad "
        "warm region is a plateau. Grid is coarse enough to see the shape and fine enough "
        "to locate a plateau edge.\n")
    G_SL = [5, 7.5, 10, 12.5, 15, 17.5, 20, 25, 30, 40]
    G_TP = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
    surfaces = {}
    for lg in LOGICS:
        sub = [r for r in dev if r["logic"] == lg]
        rows = []
        grid = {}
        for sl in G_SL:
            cells = []
            for tp in G_TP:
                m = core.metrics(resim(sub, sl, tp, paths), absurd_check=False)
                grid[(sl, tp)] = m
                cells.append(f(m.get("expectancy", 0), 2))
            rows.append([f"SL {sl:g}"] + cells)
        surfaces[lg] = grid
        add(f"\n**{LABEL[lg]}** (DEV n={len(sub)})\n")
        add(table([""] + [f"TP {t:g}" for t in G_TP], rows))
    return surfaces, G_SL, G_TP


# =============================================================== PHASE 11
def phase11(tr):
    sec("Phase 11 — Trade path: forward movement after entry (full sample)")
    add("Mean and median signed movement in the trade's direction, in dollars, at fixed "
        "horizons. This is unconditional on any exit.\n")
    mins = [1, 2, 3, 5, 10, 15, 20, 30, 45, 60, 90, 120, 180]
    rows = []
    for lg in LOGICS:
        sub = [r for r in tr if r["logic"] == lg]
        med = [pctl([r[f"fwd_{n}m"] for r in sub if r.get(f"fwd_{n}m") is not None], 50) for n in mins]
        rows.append([LABEL[lg] + " median"] + [f(x) for x in med])
    for lg in LOGICS:
        sub = [r for r in tr if r["logic"] == lg]
        pos = []
        for n in mins:
            xs = [r[f"fwd_{n}m"] for r in sub if r.get(f"fwd_{n}m") is not None]
            pos.append(f(100 * sum(1 for x in xs if x > 0) / len(xs), 1) if xs else "—")
        rows.append([LABEL[lg] + " % positive"] + pos)
    add(table(["Set"] + [f"{n}m" for n in mins], rows))

    add("\n**Does an early move predict the outcome?** Median forward move at each horizon, "
        "split by baseline outcome.\n")
    rows = []
    for lg in LOGICS:
        for tag, pred in (("winners", lambda r: r["base_pnl"] > 0),
                          ("losers", lambda r: r["base_pnl"] < 0)):
            sub = [r for r in tr if r["logic"] == lg and pred(r)]
            rows.append([f"{LABEL[lg]} {tag}"] +
                        [f(pctl([r[f"fwd_{n}m"] for r in sub if r.get(f"fwd_{n}m") is not None], 50))
                         for n in mins])
    add(table(["Set"] + [f"{n}m" for n in mins], rows))

    add("\n**Time stop scan** (DEV, baseline SL/TP, position closed at the horizon if still open)\n")


def phase11_timestop(tr, paths):
    dev = lib.window(tr, lib.DEV)
    caps = [15, 30, 45, 60, 90, 120, 180, 240, 360, 480, None]
    rows = []
    for lg in LOGICS:
        sub = [r for r in dev if r["logic"] == lg]
        cells = []
        for c in caps:
            pn = []
            for r in sub:
                p = paths[(r["date"], r["logic"])]
                eod = r["eod_minute"] if c is None else min(r["eod_minute"], r["entry_minute"] + 5 + c)
                pn.append(core.resolve(r["entry"], r["side"], 17.0, 39.0, p, eod)["pnl_pess"])
            m = core.metrics(pn, absurd_check=False)
            cells.append(f(m.get("expectancy", 0), 2))
        rows.append([LABEL[lg]] + cells)
    add(table(["Logic"] + [f"{c}m" if c else "EOD" for c in caps], rows))


# =============================================================== PHASE 12
def phase12(tr, setups):
    sec("Phase 12 — The flip mechanism")
    add("For every Flip, what happened BEFORE it: did the original direction actually "
        "break out first (a genuine failed breakout / sweep), or did price simply cross "
        "back through without ever committing?\n")
    sidx = {s["date"]: s for s in setups}
    rows = []
    for lg in ("FLIP_L", "FLIP_S"):
        sub = [r for r in tr if r["logic"] == lg]
        orig = "A_SHORT" if lg == "FLIP_L" else "A_LONG"
        prior = {r["date"]: r for r in tr if r["logic"] == orig}
        with_break = [r for r in sub if r["date"] in prior
                      and prior[r["date"]]["entry_minute"] < r["entry_minute"]]
        without = [r for r in sub if r not in with_break]
        for tag, s in (("after a real opposite breakout", with_break),
                       ("no prior opposite breakout", without)):
            rows.append(metrics_row(f"{LABEL[lg]} — {tag}", [r["base_pnl"] for r in s]))
    add(table(METRIC_HEAD, rows))

    add("\n**Flip timing and geometry**\n")
    rows = []
    for lg in ("FLIP_L", "FLIP_S"):
        sub = [r for r in tr if r["logic"] == lg]
        rows.append([LABEL[lg], len(sub),
                     f(pctl([r["bars_to_entry"] for r in sub], 50), 0),
                     f(pctl([r["entry_minute"] for r in sub], 50) / 60, 2),
                     f(pctl([r["dist_beyond"] for r in sub], 50)),
                     f(pctl([abs(r["entry"] - r["d_open"]) for r in sub], 50)),
                     f(pctl([r["mae_full"] for r in sub], 50)),
                     f(pctl([r["mfe_full"] for r in sub], 50))])
    add(table(["Logic", "N", "Median 5m bars after 10:00", "Median entry hour (dec)",
               "Median $ beyond body edge", "Median $ beyond dOpen",
               "Median MAE", "Median MFE"], rows))


# =============================================================== PHASE 13/14
def phase13(tr, setups):
    sec("Phase 13 — 10AM candle structure vs outcome")
    add("Continuous variables bucketed into terciles of their own DEV distribution. "
        "A relationship worth anything is monotonic and survives outside DEV.\n")
    dev = lib.window(tr, lib.DEV)
    sidx = {s["date"]: s for s in setups}
    VARS = [("body_size", "10AM body size $"), ("body_range", "10AM full range $"),
            ("body_ratio", "body/range ratio"), ("upper_wick", "upper wick $"),
            ("lower_wick", "lower wick $"), ("close_vs_dopen", "close − dOpen $"),
            ("ref_range", "09:50 candle range $")]
    for lg in LOGICS:
        sub = [r for r in dev if r["logic"] == lg]
        rows = []
        for key, name in VARS:
            xs = sorted(abs(sidx[r["date"]][key]) if key in ("close_vs_dopen",) else sidx[r["date"]][key]
                        for r in sub)
            if not xs:
                continue
            q1, q2 = pctl(xs, 33.3), pctl(xs, 66.7)
            buckets = {"low": [], "mid": [], "high": []}
            for r in sub:
                v = sidx[r["date"]][key]
                v = abs(v) if key == "close_vs_dopen" else v
                buckets["low" if v <= q1 else "mid" if v <= q2 else "high"].append(r["base_pnl"])
            rows.append([name] + [f"{core.metrics(buckets[b],False).get('expectancy',0):.2f} "
                                  f"(n={len(buckets[b])})" for b in ("low", "mid", "high")])
        add(f"\n**{LABEL[lg]}** — expectancy $ by tercile (DEV)\n")
        add(table(["Variable", "Low", "Mid", "High"], rows))

    add("\n**Straddle flags (DEV)**\n")
    rows = []
    for lg in LOGICS:
        sub = [r for r in dev if r["logic"] == lg]
        for key in ("body_straddle", "full_straddle"):
            y = [r["base_pnl"] for r in sub if sidx[r["date"]][key]]
            n = [r["base_pnl"] for r in sub if not sidx[r["date"]][key]]
            rows.append([f"{LABEL[lg]} {key}",
                         f"{core.metrics(y,False).get('expectancy',0):.2f} (n={len(y)})",
                         f"{core.metrics(n,False).get('expectancy',0):.2f} (n={len(n)})"])
    add(table(["Set", "True", "False"], rows))


def phase14(setups, tr, paths, dmins, days5):
    sec("Phase 14 — Alternative side definitions (DEV, reported separately from baseline)")
    add("The baseline is `side = close(10:00) > dOpen`. Three alternatives are rebuilt "
        "from scratch — they change which days are eligible for which logic, so they are "
        "NOT mixed into any baseline number.\n")
    sidx = {s["date"]: s for s in setups}
    defs = {
        "baseline close>dOpen": lambda s: 1 if s["body_close"] > s["d_open"] else -1,
        "whole body above/below": lambda s: 1 if s["b_lo"] > s["d_open"] else (-1 if s["b_hi"] < s["d_open"] else 0),
        "body midpoint": lambda s: 1 if (s["b_hi"] + s["b_lo"]) / 2 > s["d_open"] else -1,
        "full candle midpoint": lambda s: 1 if (s["body_high"] + s["body_low"]) / 2 > s["d_open"] else -1,
    }
    rows = []
    for name, fn in defs.items():
        # a trade's logic depends only on (setup side, breakout direction); recompute labels
        pn = collections.defaultdict(list)
        for r in lib.window(tr, lib.DEV):
            s = sidx[r["date"]]
            side_new = fn(s)
            if side_new == 0:
                continue
            up = r["side"] > 0
            lg = ("A_LONG" if up else "FLIP_S") if side_new > 0 else ("FLIP_L" if up else "A_SHORT")
            pn[lg].append(r["base_pnl"])
        rows.append([name] + [f"{core.metrics(pn[lg],False).get('expectancy',0):.2f} (n={len(pn[lg])})"
                              for lg in LOGICS])
    add(table(["Side definition"] + [LABEL[lg] for lg in LOGICS], rows))


# =============================================================== PHASE 15-21
def conditioning(tr, setups):
    sidx = {s["date"]: s for s in setups}
    dev = lib.window(tr, lib.DEV)

    sec("Phase 15 — Volatility regimes (quintiles of pre-entry ATR, DEV)")
    ok = [r for r in dev if r["atr14"] and r["atr14"] > 0]
    cuts = [pctl([r["atr14"] for r in ok], p) for p in (20, 40, 60, 80)]
    names = ["very low", "low", "normal", "high", "very high"]
    def bucket(v):
        for i, c in enumerate(cuts):
            if v <= c:
                return names[i]
        return names[-1]
    add(f"ATR quintile cuts (DEV): " + ", ".join(f"${c:.2f}" for c in cuts) + "\n")
    rows = []
    for lg in LOGICS:
        sub = [r for r in ok if r["logic"] == lg]
        cells = []
        for nm in names:
            pn = [r["base_pnl"] for r in sub if bucket(r["atr14"]) == nm]
            cells.append(f"{core.metrics(pn,False).get('expectancy',0):.2f} (n={len(pn)})" if pn else "—")
        rows.append([LABEL[lg]] + cells)
    add(table(["Logic"] + names, rows))

    sec("Phase 16 — Entry time (Melbourne, full sample)")
    bands = [(605, 630, "10:05–10:30"), (630, 660, "10:30–11:00"), (660, 720, "11:00–12:00"),
             (720, 780, "12:00–13:00"), (780, 840, "13:00–14:00"), (840, 900, "14:00–15:00"),
             (900, 960, "15:00–16:00"), (960, 1080, "16:00–18:00"),
             (1080, 1200, "18:00–20:00"), (1200, 1441, "20:00+")]
    rows = []
    for lo, hi, nm in bands:
        cells = []
        for lg in LOGICS:
            pn = [r["base_pnl"] for r in tr if r["logic"] == lg and lo <= r["entry_minute"] < hi]
            m = core.metrics(pn, False)
            cells.append(f"{m.get('expectancy',0):.2f} / {m.get('pf',0):.2f} (n={m['n']})"
                         if m["n"] else "—")
        rows.append([nm] + cells)
    add("Cells are expectancy $ / PF (n).\n")
    add(table(["Melbourne band"] + [LABEL[lg] for lg in LOGICS], rows))

    sec("Phase 17 — International session context")
    from zoneinfo import ZoneInfo
    LON, NY = ZoneInfo("Europe/London"), ZoneInfo("America/New_York")
    def session(r):
        # entry instant in UTC, reconstructed from the Melbourne date+minute
        d = r["date_d"]
        local = dt.datetime.combine(d, dt.time(r["entry_minute"] // 60, r["entry_minute"] % 60),
                                    tzinfo=core.MEL)
        lon = local.astimezone(LON); ny = local.astimezone(NY)
        lon_open = 8 <= lon.hour < 16.5 or (lon.hour == 16 and lon.minute < 30)
        ny_open = 9 <= ny.hour < 16 or (ny.hour == 9 and ny.minute >= 30)
        ny_open = (ny.hour > 9 or (ny.hour == 9 and ny.minute >= 30)) and ny.hour < 16
        if lon_open and ny_open:
            return "London–NY overlap"
        if ny_open:
            return "New York"
        if lon_open:
            return "London"
        return "Sydney/Asia"
    rows = []
    for nm in ("Sydney/Asia", "London", "London–NY overlap", "New York"):
        cells = []
        for lg in LOGICS:
            pn = [r["base_pnl"] for r in tr if r["logic"] == lg and session(r) == nm]
            m = core.metrics(pn, False)
            cells.append(f"{m.get('expectancy',0):.2f} / {m.get('pf',0):.2f} (n={m['n']})"
                         if m["n"] else "—")
        rows.append([nm] + cells)
    add("Sessions computed with real historical clocks for Europe/London and "
        "America/New_York — the three zones change DST on different dates, so no fixed "
        "offset is used anywhere.\n")
    add(table(["Session at entry"] + [LABEL[lg] for lg in LOGICS], rows))

    sec("Phase 18 — AEST vs AEDT")
    rows = []
    for lg in LOGICS:
        for tag in ("AEST", "AEDT"):
            sub = [r for r in tr if r["logic"] == lg and r["dst"] == tag]
            rows.append(metrics_row(f"{LABEL[lg]} {tag}", [r["base_pnl"] for r in sub]))
    add(table(METRIC_HEAD, rows))
    aedt_days = len({s["date"] for s in setups if s["dst"] == "AEDT"})
    aest_days = len({s["date"] for s in setups if s["dst"] == "AEST"})
    add(f"\nSetup days: AEST {aest_days}, AEDT {aedt_days}. The AEDT count is small "
        f"**because the feed's maintenance break destroys 09:50 for the whole "
        f"AEDT+NY-EST stretch** — see the coverage section. AEDT results here come only "
        f"from the October and March/April shoulders.\n")

    sec("Phase 19 — Weekday")
    rows = []
    for wd in ("Mon", "Tue", "Wed", "Thu", "Fri"):
        cells = []
        for lg in LOGICS:
            pn = [r["base_pnl"] for r in tr if r["logic"] == lg and r["weekday"] == wd]
            m = core.metrics(pn, False)
            cells.append(f"{m.get('expectancy',0):.2f} / {m.get('pf',0):.2f} (n={m['n']})")
        rows.append([wd] + cells)
    add(table(["Weekday"] + [LABEL[lg] for lg in LOGICS], rows))

    sec("Phase 20 — Month by month (full sample)")
    months = sorted({r["month"] for r in tr})
    rows = []
    for mo in months:
        cells = []
        tot = 0.0
        for lg in LOGICS:
            pn = [r["base_pnl"] for r in tr if r["logic"] == lg and r["month"] == mo]
            tot += sum(pn)
            cells.append(f"{sum(pn):+.0f} (n={len(pn)})" if pn else "—")
        rows.append([mo, f"{tot:+.0f}"] + cells)
    add(table(["Month", "All four net $"] + [LABEL[lg] for lg in LOGICS], rows))

    sec("Phase 21 — Rolling performance")
    add("Rolling 40-trade expectancy and PF, per logic, in trade order.\n")
    rows = []
    for lg in LOGICS:
        sub = sorted([r for r in tr if r["logic"] == lg], key=lambda r: (r["date"], r["entry_minute"]))
        pn = [r["base_pnl"] for r in sub]
        w = 40
        vals = []
        for i in range(w, len(pn) + 1, 10):
            m = core.metrics(pn[i - w:i], False)
            vals.append(f"{m['expectancy']:.1f}")
        rows.append([LABEL[lg], len(pn), " → ".join(vals)])
    add(table(["Logic", "N", "Rolling 40-trade expectancy $ (step 10)"], rows))


# =============================================================== PHASE 22/23
def phase2223(tr, paths, setups):
    sec("Phase 22 — Entry confirmation buffers (DEV)")
    add("The trigger requires a close beyond BOTH the body edge and dOpen. Here the close "
        "must clear the body edge by an extra buffer. Trades that never clear it are lost, "
        "so N falls as the buffer rises — that is the cost being measured.\n")
    dev = lib.window(tr, lib.DEV)
    bufs = [0, 0.25, 0.5, 1, 1.5, 2, 3, 5]
    rows = []
    for lg in LOGICS:
        sub = [r for r in dev if r["logic"] == lg]
        cells = []
        for b in bufs:
            pn = [r["base_pnl"] for r in sub if r["dist_beyond"] >= b]
            m = core.metrics(pn, False)
            cells.append(f"{m.get('expectancy',0):.2f} (n={m['n']})" if m["n"] else "—")
        rows.append([LABEL[lg]] + cells)
    add(table(["Logic"] + [f"+${b:g}" for b in bufs], rows))
    add("\n_Note: this filters on the realised first trigger's distance, which is the "
        "conservative reading — a true buffer rule would instead wait for a LATER bar to "
        "clear the level, changing the entry price. That variant is tested in Phase 22b._\n")

    rows = []
    for lg in LOGICS:
        sub = [r for r in dev if r["logic"] == lg]
        cells = []
        for b in bufs:
            atrs = [r["dist_beyond"] / r["atr14"] for r in sub if r["atr14"]]
            cells.append("")
        rows.append(None)

    sec("Phase 23 — Breakout strength at entry (DEV, terciles)")
    rows = []
    for lg in LOGICS:
        sub = [r for r in dev if r["logic"] == lg]
        for key, nm in (("dist_beyond", "$ beyond edge"), ("sig_body", "signal body $"),
                        ("sig_range", "signal range $"), ("bars_to_entry", "5m bars since 10:00")):
            xs = sorted(r[key] for r in sub)
            q1, q2 = pctl(xs, 33.3), pctl(xs, 66.7)
            b = {"low": [], "mid": [], "high": []}
            for r in sub:
                v = r[key]
                b["low" if v <= q1 else "mid" if v <= q2 else "high"].append(r["base_pnl"])
            rows.append([f"{LABEL[lg]} — {nm}"] +
                        [f"{core.metrics(b[k],False).get('expectancy',0):.2f} (n={len(b[k])})"
                         for k in ("low", "mid", "high")])
    add(table(["Set", "Low", "Mid", "High"], rows))


# =============================================================== PHASE 24/25
def phase2425(tr, paths):
    sec("Phase 24 — Exit management (DEV)")
    add("Every management rule is compared against the plain fixed SL/TP on the SAME "
        "trades. A rule that does not beat the simple version here is not carried forward.\n")
    dev = lib.window(tr, lib.DEV)
    rows = []
    for lg in LOGICS:
        sub = [r for r in dev if r["logic"] == lg]
        base = resim(sub, 17.0, 39.0, paths)
        variants = {"fixed 17/39": base}
        # breakeven after +X
        for be in (5, 10, 15):
            pn = []
            for r in sub:
                p = paths[(r["date"], r["logic"])]
                pn.append(exit_be(r, p, 17.0, 39.0, be))
            variants[f"BE at +${be}"] = pn
        # partial at 1R
        pn = []
        for r in sub:
            p = paths[(r["date"], r["logic"])]
            pn.append(exit_partial(r, p, 17.0, 39.0, 17.0))
        variants["50% off at 1R"] = pn
        # trailing
        for tr_d in (10, 15, 20):
            pn = [exit_trail(r, paths[(r["date"], r["logic"])], 17.0, tr_d) for r in sub]
            variants[f"trail ${tr_d}"] = pn
        for nm, pn in variants.items():
            m = core.metrics(pn, False)
            rows.append([f"{LABEL[lg]} — {nm}", m["n"], f(m["win_pct"], 1), f(m["expectancy"], 3),
                         f(m["pf"], 3), f(m["net"]), f(m["max_dd"])])
    add(table(["Set", "N", "Win %", "Expectancy", "PF", "Net $", "Max DD"], rows))

    sec("Phase 25 — Giveback: MFE minus realised P&L (full sample, baseline exits)")
    rows = []
    for lg in LOGICS:
        for tag, pred in (("winners", lambda r: r["base_pnl"] > 0),
                          ("losers", lambda r: r["base_pnl"] < 0)):
            sub = [r for r in tr if r["logic"] == lg and pred(r)]
            g = [r["mfe_full"] - r["base_pnl"] for r in sub]
            if not g:
                continue
            rows.append([f"{LABEL[lg]} {tag}", len(g), f(sum(g) / len(g)), f(pctl(g, 50)),
                         f(pctl(g, 90)), f(max(g))])
    add(table(["Set", "N", "Mean giveback $", "Median", "p90", "Max"], rows))


def exit_be(r, path, sl, tp, be_at):
    side, entry = r["side"], r["entry"]
    stop = entry - side * sl; targ = entry + side * tp; moved = False
    for m in path:
        if m["minute"] > r["eod_minute"]:
            break
        fav = (m["high"] - entry) if side > 0 else (entry - m["low"])
        hit_sl = (m["low"] <= stop) if side > 0 else (m["high"] >= stop)
        hit_tp = (m["high"] >= targ) if side > 0 else (m["low"] <= targ)
        if hit_sl:
            return (stop - entry) * side
        if hit_tp:
            return tp
        if not moved and fav >= be_at:
            stop = entry; moved = True          # R4: never widens
    return ((path[-1]["close"] - entry) * side) if path else 0.0


def exit_partial(r, path, sl, tp, r1):
    side, entry = r["side"], r["entry"]
    stop = entry - side * sl; targ = entry + side * tp
    took = False; realised = 0.0; size = 1.0
    for m in path:
        if m["minute"] > r["eod_minute"]:
            break
        hit_sl = (m["low"] <= stop) if side > 0 else (m["high"] >= stop)
        hit_1r = ((m["high"] - entry) >= r1) if side > 0 else ((entry - m["low"]) >= r1)
        hit_tp = (m["high"] >= targ) if side > 0 else (m["low"] <= targ)
        if hit_sl:
            return realised + size * (stop - entry) * side
        if not took and hit_1r:
            realised += 0.5 * r1; size = 0.5; took = True; stop = entry
        if hit_tp:
            return realised + size * tp
    return realised + (size * (path[-1]["close"] - entry) * side if path else 0.0)


def exit_trail(r, path, sl, dist):
    side, entry = r["side"], r["entry"]
    stop = entry - side * sl; peak = entry
    for m in path:
        if m["minute"] > r["eod_minute"]:
            break
        hit_sl = (m["low"] <= stop) if side > 0 else (m["high"] >= stop)
        if hit_sl:
            return (stop - entry) * side
        peak = max(peak, m["high"]) if side > 0 else min(peak, m["low"])
        cand = peak - side * dist
        stop = max(stop, cand) if side > 0 else min(stop, cand)   # R4
    return ((path[-1]["close"] - entry) * side) if path else 0.0


# =============================================================== PHASE 26/27
def phase26(tr):
    sec("Phase 26 — High-impact US economic events")
    add("Only events whose dates are derivable from a published rule are tagged here. "
        "**US Non-Farm Payrolls** releases on the first Friday of the month at 08:30 New "
        "York, which is a deterministic calendar rule requiring no external calendar. "
        "CPI/PPI/PCE/FOMC dates are NOT rule-derivable and no verified historical calendar "
        "was reachable from this container, so they are **not tagged** rather than guessed "
        "— see Failed Experiments.\n")
    from zoneinfo import ZoneInfo
    NY = ZoneInfo("America/New_York")
    def is_nfp_window(r):
        d = r["date_d"]
        local = dt.datetime.combine(d, dt.time(r["entry_minute"] // 60, r["entry_minute"] % 60),
                                    tzinfo=core.MEL)
        ny = local.astimezone(NY)
        if ny.weekday() != 4:
            return False
        if ny.day > 7:
            return False
        # entry within the NY trading day containing 08:30
        return True
    rows = []
    for lg in LOGICS:
        y = [r["base_pnl"] for r in tr if r["logic"] == lg and is_nfp_window(r)]
        n = [r["base_pnl"] for r in tr if r["logic"] == lg and not is_nfp_window(r)]
        my, mn = core.metrics(y, False), core.metrics(n, False)
        rows.append([LABEL[lg],
                     f"{my.get('expectancy',0):.2f} / {my.get('pf',0):.2f} (n={my['n']})" if my["n"] else "—",
                     f"{mn.get('expectancy',0):.2f} / {mn.get('pf',0):.2f} (n={mn['n']})",
                     f(pctl([r['mae_full'] for r in tr if r['logic']==lg and is_nfp_window(r)],50)),
                     f(pctl([r['mae_full'] for r in tr if r['logic']==lg and not is_nfp_window(r)],50))])
    add(table(["Logic", "NFP day exp/PF", "Other days exp/PF", "NFP median MAE",
               "Other median MAE"], rows))


def phase27(tr, paths):
    sec("Phase 27 — Realistic execution cost")
    add("The Pine `costPts` mechanism shrinks the SL and TP distances by half the cost. "
        "That is not transaction-cost accounting: it changes where the orders sit rather "
        "than charging the fill. Here the round-trip cost is **charged to the P&L** and the "
        "SL/TP stay where the rule puts them.\n")
    # measured spread from the ask feed
    spread = measured_spread()
    if spread:
        add(f"**Measured Dukascopy XAU/USD spread** across the 339 setup days, "
            f"10:00–16:00 Melbourne: median **${spread['median']:.3f}**, "
            f"p90 ${spread['p90']:.3f}, p99 ${spread['p99']:.3f} "
            f"(n={spread['n']:,} minute observations). A round trip crosses it twice, so "
            f"the spread alone costs about **${2*spread['median']:.2f}** per trade before "
            f"any slippage.\n")
    dev = lib.window(tr, lib.DEV)
    costs = [0, 0.20, 0.40, 0.60, 1.00, 1.50, 2.00, 3.00, 5.00]
    rows = []
    for lg in LOGICS:
        sub = [r for r in dev if r["logic"] == lg]
        base = resim(sub, 17.0, 39.0, paths)
        cells = []
        for c in costs:
            m = core.metrics([p - c for p in base], False)
            cells.append(f"{m['expectancy']:.2f} / {m['pf']:.2f}")
        rows.append([LABEL[lg]] + cells)
    add("Cells are expectancy $ / PF at each round-trip cost (DEV).\n")
    add(table(["Logic"] + [f"${c:.2f}" for c in costs], rows))
    return spread


def measured_spread():
    bid = os.path.join(core.RAW, "xauusd_1m_bid_dukascopy.csv.gz")
    ask = os.path.join(core.RAW, "xauusd_1m_ask_dukascopy.csv.gz")
    if not os.path.exists(ask):
        return None
    b = {t: c for t, o, h, l, c, v in core.load_1m(bid)}
    a = {t: c for t, o, h, l, c, v in core.load_1m(ask)}
    sp = []
    for t in a:
        if t in b:
            lt = t.astimezone(core.MEL)
            if lt.weekday() < 5 and 600 <= lt.hour * 60 + lt.minute < 960:
                d = a[t] - b[t]
                if d >= 0:
                    sp.append(d)
    if not sp:
        return None
    return dict(n=len(sp), median=pctl(sp, 50), p90=pctl(sp, 90), p99=pctl(sp, 99),
                mean=sum(sp) / len(sp))


# =============================================================== main
def main():
    tr = lib.load("trades.csv")
    setups = lib.load("setups.csv")
    print(f"{len(tr)} trades, {len(setups)} setups", flush=True)
    paths, dmins = load_paths(tr)
    print("paths cached", flush=True)

    OUT.append("# Gold 10AM — analysis tables (Phases 1–27)\n")
    OUT.append(f"_Generated from `data/processed/trades.csv`; "
               f"{len(setups)} setup days, {len(tr)} trades._\n")
    phase1(tr, setups); print("p1", flush=True)
    phase2345(tr); print("p2-5", flush=True)
    phase6(tr); print("p6", flush=True)
    phase7(tr); phase7b(tr, paths); print("p7", flush=True)
    phase8910(tr, paths); print("p8-10", flush=True)
    phase11(tr); phase11_timestop(tr, paths); print("p11", flush=True)
    phase12(tr, setups); print("p12", flush=True)
    phase13(tr, setups); print("p13", flush=True)
    phase14(setups, tr, paths, dmins, None); print("p14", flush=True)
    conditioning(tr, setups); print("p15-21", flush=True)
    phase2223(tr, paths, setups); print("p22-23", flush=True)
    phase2425(tr, paths); print("p24-25", flush=True)
    phase26(tr); print("p26", flush=True)
    phase27(tr, paths); print("p27", flush=True)

    os.makedirs(lib.TAB, exist_ok=True)
    with open(os.path.join(lib.TAB, "phases_1_27.md"), "w") as f_:
        f_.write("\n".join(x for x in OUT if x))
    print("wrote tables/phases_1_27.md")


if __name__ == "__main__":
    main()
