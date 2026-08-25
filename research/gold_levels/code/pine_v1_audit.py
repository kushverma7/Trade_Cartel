"""What does the Pine actually trade, versus the rule it documents?

Two structural deviations are visible by reading it. Both are measurable, so
they get measured rather than asserted.

  A. THE RESEARCHED RULE. First body break after the 10:00 candle wins. If that
     break fails the quarter test, the DAY IS SKIPPED. Entry window ends 11:00.

  B. THE PINE AS WRITTEN. `tradePermission` includes `quarterOK`, and
     `tradedToday` is only set when a trade actually fires. So a first break
     that fails the quarter test does not end the day -- the script keeps
     scanning and takes the next break that happens to be near a quarter,
     any time up to 23:00. That is a SUBSTITUTION, and it is also free to
     switch direction: a rejected downside break can be replaced hours later
     by an upside one.

Same tick data, same fills, same exits. Only the selection rule differs.
"""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Trade_Cartel/research/gold_exit_eng/code")
from exits import resolve, stats
PTS = 1000.0
BASE = "/home/user/Trade_Cartel/research/gold_10am_flip"
prep = pickle.load(open(f"{BASE}/data/prep10.pkl", "rb"))
TKt = np.load(f"{BASE}/data/tk_t.npy")
TKb = np.load(f"{BASE}/data/tk_bid.npy")
TKa = np.load(f"{BASE}/data/tk_ask.npy")

SL, TP = 15.0, 25.0
GRID, TOL = 25.0, 7.5
MINBODY = 1.0


def qdist(px):
    r = px % GRID
    return min(r, GRID - r)


def make(day, i, long_):
    ask_i, bid_i = int(day["ask_c"][i]), int(day["bid_c"][i])
    e = ask_i if long_ else bid_i
    k0 = day["i0"] + int(np.searchsorted(TKt[day["i0"]:day["j0"]], int(day["t_close"][i]), side="right"))
    if k0 >= day["j0"]:
        return None
    ex = TKb[k0:day["j0"]] if long_ else TKa[k0:day["j0"]]
    fav = (ex.astype(np.int64) - e) if long_ else (e - ex.astype(np.int64))
    return dict(date=pd.Timestamp(day["date"]), kind="A_LONG" if long_ else "FLIP_SHORT",
                entry=e / PTS, spread=(ask_i - bid_i) / PTS, hhmm=None,
                fav=fav, tms=TKt[k0:day["j0"]],
                rmax=np.maximum.accumulate(fav), rmin=np.minimum.accumulate(fav))


def build(mode, window_end=1100, spread_cap=2.0):
    out = []
    for day in prep:
        if day["side"] != 1:
            continue
        if (day["bhi"] - day["blo"]) < MINBODY:
            continue
        c, bhi, blo, tclose = day["c"], day["bhi"], day["blo"], day["t_close"]
        mins = ((tclose - 5 * 60 * 1000) % 86_400_000) // 60_000
        hhmm = (mins // 60) * 100 + (mins % 60)
        up, dn = c > bhi, c < blo
        iu = int(np.argmax(up)) if up.any() else 10**9
        idn = int(np.argmax(dn)) if dn.any() else 10**9
        if mode == "researched":
            i = min(iu, idn)
            if i >= 10**9 or hhmm[i] > window_end:
                continue
            if qdist(c[i]) > TOL:               # SKIP the day
                continue
            long_ = iu <= idn
            t = make(day, i, long_)
            if t is None: continue
            if spread_cap is not None and t["spread"] > spread_cap: continue
            t["hhmm"] = int(hhmm[i]); out.append(t)
        else:                                   # "pine": keep scanning
            hit = None
            for i in range(len(c)):
                if hhmm[i] >= 2300:
                    break
                if not (up[i] or dn[i]):
                    continue
                if qdist(c[i]) > TOL:           # SUBSTITUTE: try the next one
                    continue
                hit = (i, bool(up[i])); break
            if hit is None:
                continue
            i, long_ = hit
            t = make(day, i, long_)
            if t is None: continue
            if spread_cap is not None and t["spread"] > spread_cap: continue
            t["hhmm"] = int(hhmm[i]); out.append(t)
    out.sort(key=lambda r: r["date"])
    return out


def splits3(tr):
    ds = sorted({t["date"] for t in tr}); n = len(ds)
    d1, d2 = ds[int(n * .6)], ds[int(n * .8)]
    for t in tr:
        t["split"] = "DEV" if t["date"] < d1 else ("VAL" if t["date"] < d2 else "HOLD")


def report(name, tr):
    splits3(tr)
    recs = [(t["split"], resolve(t, sl=SL, tp=TP)[0]) for t in tr]
    A = stats([v for _, v in recs])
    S = {s: stats([v for sp, v in recs if sp == s]) for s in ("DEV", "VAL", "HOLD")}
    mp = min(S[s]["pf"] for s in S)
    nl = sum(1 for t in tr if t["kind"] == "A_LONG")
    late = sum(1 for t in tr if t["hhmm"] > 1100)
    print(f"{name:<42}{A['n']:>5}{A['pf']:>8.3f}{A['exp']:>8.2f}{A['net']:>9.1f}"
          f"{A['wr']:>7.1f}%{A['mdd']:>8.1f}{mp:>8.2f}   {nl}L/{A['n']-nl}S   {late} after 11:00")
    return tr


print(f"{'selection rule':<42}{'n':>5}{'PF':>8}{'exp':>8}{'net':>9}{'WR':>8}{'DD':>8}{'minPF':>8}   mix        late")
a = report("A  researched: first break, else SKIP", build("researched"))
b = report("B  Pine as written: keep scanning", build("pine"))
c = report("B' Pine, no spread cap (as it runs)", build("pine", spread_cap=None))

da, db = {t["date"] for t in a}, {t["date"] for t in b}
print(f"\ndays in both: {len(da & db)}    only in researched: {len(da - db)}    only in Pine: {len(db - da)}")
same_dir = sum(1 for t in a for u in b if t["date"] == u["date"] and t["kind"] == u["kind"])
print(f"of the {len(da & db)} shared days, same direction on {same_dir}; "
      f"DIRECTION FLIPPED on {len(da & db) - same_dir}")
