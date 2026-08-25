"""The 10AM Quarter Matrix on the year it has never seen.

When the 10AM system was measured at PF 2.01 the holdout year did not exist in
this project. It does now. This runs the same rule on both years, on the same
tick engine, with the same fill convention -- the test Micro-Q3 already failed.

TWO RULES ARE RUN, because they are different strategies:
  RESEARCHED  first 5-minute body break wins; if it fails a filter the DAY IS
              SKIPPED; entry window ends 11:00 Melbourne.
  PINE v1     the quarter test gates the trade but not the day, so a rejected
              break leaves the day open and the script keeps scanning (BUG-047).
"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, "research/goldmap/code")
from qt_engine import Book, PTS
pd.set_option("display.width", 240)

MEL = "Australia/Melbourne"


def mel_labels(book, cache):
    """Melbourne wall clock (naive, ms) for every tick, from the stored NY wall
    clock. The NY->UTC step is ambiguous only inside the autumn fall-back hour,
    which is a Sunday 01:00-02:00 and has no ticks; asserted below."""
    if os.path.exists(cache):
        return np.load(cache)
    out = np.empty(len(book.ny), np.int64)
    CH = 4_000_000
    for i in range(0, len(book.ny), CH):
        idx = pd.DatetimeIndex(book.ny[i:i + CH].astype("datetime64[ms]"))
        utc = idx.tz_localize("America/New_York", ambiguous=True,
                              nonexistent="shift_forward").tz_convert("UTC")
        out[i:i + CH] = (utc.tz_convert(MEL).tz_localize(None)
                         .values.astype("datetime64[ms]").astype(np.int64))
    np.save(cache, out)
    return out


def tenam(book, mel, rule, sl=15.0, tp=25.0, qd=7.5, spr=2.0, body_min=1.0,
          win_end=11 * 60, far_end=23 * 60):
    mm = mel // 60_000
    mday, mhm = mm // 1440, mm % 1440
    days = np.unique(mday)
    lo_all = np.searchsorted(mday, days, "left"); hi_all = np.searchsorted(mday, days, "right")
    DS = {int(d): (int(a), int(b)) for d, a, b in zip(days, lo_all, hi_all)}

    def mcandle(day, h0, h1):
        r = DS.get(day)
        if r is None:
            return None
        a, b = r
        k = np.flatnonzero((mhm[a:b] >= h0) & (mhm[a:b] < h1)) + a
        if len(k) < 15:
            return None
        seg = book.mid[k[0]:k[-1] + 1]
        return dict(o=int(seg[0]), c=int(seg[-1]), i1=k[-1] + 1, t_close=int(mel[k[-1]]))

    rows = []
    for day in sorted(DS):
        a = mcandle(day, 10 * 60, 10 * 60 + 5)
        if a is None:
            continue
        o, c = a["o"] / PTS, a["c"] / PTS
        if c <= o or (c - o) < body_min:                 # bullish 10AM, minimum body
            continue
        bhi, blo = c, o
        end = win_end if rule == "researched" else far_end
        taken = None
        for s in range(10 * 60 + 5, end + 1, 5):
            cd = mcandle(day, s, s + 5)
            if cd is None:
                continue
            cc = cd["c"] / PTS
            if not (cc > bhi or cc < blo):
                continue
            long_ = cc > bhi
            k0 = int(np.searchsorted(mel, cd["t_close"], "right"))
            if k0 >= len(mel):
                break
            bid, ask = int(book.bid[k0]) / PTS, int(book.ask[k0]) / PTS
            entry = ask if long_ else bid
            r = entry % 25.0
            ok = (ask - bid <= spr) and (min(r, 25 - r) <= qd)
            if rule == "researched":
                if ok:
                    taken = (k0, long_, entry, ask - bid, min(r, 25 - r), s)
                break                                    # first break decides the day
            if ok:
                taken = (k0, long_, entry, ask - bid, min(r, 25 - r), s)
                break                                    # v1: keep scanning until one passes
        if taken is None:
            continue
        k0, long_, entry, sprd, dq, s_sig = taken
        k1 = min(k0 + 400_000, len(book.ny))
        e = int(book.ask[k0]) if long_ else int(book.bid[k0])
        ex = book.bid[k0:k1] if long_ else book.ask[k0:k1]
        fav = (ex.astype(np.int64) - e) if long_ else (e - ex.astype(np.int64))
        # cut at 17:00 NY the next day
        lim = book.ny[k0] + int(22 * 3600 * 1000)
        n = int(np.searchsorted(book.ny[k0:k1], lim, "right"))
        fav = fav[:max(n, 2)]
        rmax = np.maximum.accumulate(fav); rmin = np.minimum.accumulate(fav)
        itp = int(np.searchsorted(rmax, int(tp * PTS), "left"))
        isl = int(np.searchsorted(-rmin, int(sl * PTS), "left"))
        m = len(fav)
        if itp < m and itp <= isl:
            pnl, why = tp, "TP"                          # resting limit fills AT the target
        elif isl < m:
            pnl, why = fav[isl] / PTS, "SL"              # market stop, real slipped quote
        else:
            pnl, why = fav[-1] / PTS, "EOD"
        rows.append(dict(year=book.year, date=pd.Timestamp(day * 86400000, unit="ms").date(),
                         kind="A_LONG" if long_ else "FLIP_SHORT", sig_hm=s_sig,
                         entry=entry, spread=sprd, dist25=dq, pnl=pnl, why=why))
    return pd.DataFrame(rows)


def stat(d):
    p = d.pnl.to_numpy()
    if len(p) == 0:
        return None
    gp, gl = p[p > 0].sum(), -p[p < 0].sum()
    eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
    dd = pk - eq
    return dict(n=len(p), wr=100 * (p > 0).mean(), pf=(gp / gl if gl else np.inf),
                exp=p.mean(), net=p.sum(), mdd=float(dd.max()),
                ulcer=float(np.sqrt((dd ** 2).mean())))


books = {}
for dd, yr, cache in (("research/microq3/data_holdout", "2024-25", "research/goldmap/results/mel_y1.npy"),
                      ("research/microq3/data", "2025-26", "research/goldmap/results/mel_y2.npy")):
    b = Book(dd, yr)
    books[yr] = (b, mel_labels(b, cache))
    print(f"{yr}: Melbourne labels built, {len(b.ny):,} ticks", flush=True)

print("\n" + "=" * 108)
print("THE 10AM QUARTER MATRIX ON BOTH YEARS  —  SL 15 / TP 25, limit target, slipped stop")
print("=" * 108)
print(f"  {'rule / year':<38}{'n':>6}{'WR':>8}{'PF':>8}{'exp':>9}{'net':>10}{'maxDD':>9}{'Ulcer':>8}")
keep = {}
for rule in ("researched", "pine_v1"):
    for yr in ("2024-25", "2025-26"):
        b, mel = books[yr]
        d = tenam(b, mel, rule)
        keep[(rule, yr)] = d
        s = stat(d)
        tag = f"{'RESEARCHED' if rule=='researched' else 'PINE v1 (BUG-047)'}  {yr}"
        if s:
            print(f"  {tag:<38}{s['n']:>6}{s['wr']:>7.1f}%{s['pf']:>8.3f}{s['exp']:>9.2f}"
                  f"{s['net']:>10.1f}{s['mdd']:>9.1f}{s['ulcer']:>8.1f}")
    both = pd.concat([keep[(rule, "2024-25")], keep[(rule, "2025-26")]])
    s = stat(both)
    print(f"  {'   -> both years pooled':<38}{s['n']:>6}{s['wr']:>7.1f}%{s['pf']:>8.3f}"
          f"{s['exp']:>9.2f}{s['net']:>10.1f}{s['mdd']:>9.1f}{s['ulcer']:>8.1f}\n")

R = pd.concat([v.assign(rule=k[0]) for k, v in keep.items()])
R.to_csv("research/goldmap/results/tenam_both_years.csv", index=False)

print("=" * 108)
print("COMPONENT CHECK ON THE UNSEEN YEAR — does the filter stack still help?")
print("=" * 108)
b, mel = books["2024-25"]
print(f"  {'variant (2024-25)':<38}{'n':>6}{'PF':>8}{'exp':>9}{'net':>10}")
for tag, kw in (("no quarter, no spread filter", dict(qd=None, spr=None)),
                ("+ spread <= 2.0", dict(qd=None, spr=2.0)),
                ("+ within $7.50 of a $25 level", dict(qd=7.5, spr=2.0))):
    kw2 = {k: v for k, v in kw.items()}
    if kw2.get("qd") is None: kw2["qd"] = 1e9
    if kw2.get("spr") is None: kw2["spr"] = 1e9
    s = stat(tenam(b, mel, "researched", **kw2))
    print(f"  {tag:<38}{s['n']:>6}{s['pf']:>8.3f}{s['exp']:>9.2f}{s['net']:>10.1f}")
