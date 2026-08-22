"""Rebuild the 10AM Quarter Matrix on the SAME tick engine, same EOD rule.

The two strategies must not be compared across different execution paths, so
the 10AM rule is re-run here on the full 91.6M-tick NY engine rather than on the
Melbourne arrays used earlier (which are truncated to 09:00-23:59 Melbourne).
"""
import sys, os, numpy as np, pandas as pd, pyarrow.parquet as pq
sys.path.insert(0, "research/microq3/code")
import engine as E
import microq3 as M
from engine import PTS

MELF = "research/microq3/data/mel_ms.npy"
if not os.path.exists(MELF):
    src = "research/gold_tick_data/dukascopy/processed/GOLD_XAUUSD_DUKASCOPY_TICKS_2025-08-21_to_2026-08-20.parquet"
    f = pq.ParquetFile(src)
    mel = np.empty(f.metadata.num_rows, np.int64); pos = 0
    for b in f.iter_batches(batch_size=4_000_000, columns=["timestamp_melbourne"]):
        v = b.column("timestamp_melbourne").to_numpy(zero_copy_only=False).astype("datetime64[ms]").astype(np.int64)
        mel[pos:pos + len(v)] = v; pos += len(v)
    np.save(MELF, mel); print("melbourne labels built")
MEL = np.load(MELF)
assert len(MEL) == len(E.NY)

# 1-minute Melbourne bars, run-based like the NY set
mm = MEL // 60_000
nr = np.empty(len(mm), bool); nr[0] = True
np.not_equal(mm[1:], mm[:-1], out=nr[1:])
st = np.flatnonzero(nr); en = np.append(st[1:], len(mm))
lab = mm[st]
MIDI = (E.BID.astype(np.int64) + E.ASK.astype(np.int64)) // 2
mo, mc = MIDI[st], MIDI[en - 1]
mday, mhm = lab // 1440, lab % 1440
DS = {}
for d in np.unique(mday):
    a = np.searchsorted(mday, d, "left"); b = np.searchsorted(mday, d, "right")
    DS[int(d)] = (int(a), int(b))


def mcandle(day, hm0, hm1):
    a, b = DS.get(day, (0, 0))
    if b <= a: return None
    h = mhm[a:b]; k = np.flatnonzero((h >= hm0) & (h < hm1)) + a
    if not len(k): return None
    return dict(o=int(mo[k[0]]), c=int(mc[k[-1]]), i1=int(en[k[-1]]),
                t_close=int(MEL[int(en[k[-1]]) - 1]), n=len(k))


def tenam(sl=15.0, tp=25.0, qd=7.5, spr=2.0, body_min=1.0, win_end=11 * 60):
    pl, rows = [], []
    for day in sorted(DS):
        a = mcandle(day, 10 * 60, 10 * 60 + 5)
        if a is None or a["n"] < 3: continue
        o, c = a["o"] / PTS, a["c"] / PTS
        if c <= o: continue                                  # bullish 10AM only
        if (c - o) < body_min: continue
        bhi, blo = c, o
        hit = None
        for s in range(10 * 60 + 5, win_end + 1, 5):
            cd = mcandle(day, s, s + 5)
            if cd is None: continue
            cc = cd["c"] / PTS
            if cc > bhi: hit = (cd, True); break
            if cc < blo: hit = (cd, False); break
        if hit is None: continue
        cd, long_ = hit
        k0 = int(np.searchsorted(MEL, cd["t_close"], "right"))
        # same EOD convention as Micro-Q3: 17:00 NY on the following NY day
        nyday = int(E.NY[k0] // 86_400_000)
        kend = E.session_end_index(nyday, 17 * 60)
        if kend is None or k0 >= kend: continue
        bid, ask = int(E.BID[k0]) / PTS, int(E.ASK[k0]) / PTS
        if spr is not None and ask - bid > spr: continue
        entry = ask if long_ else bid
        r = entry % 25.0
        if qd is not None and min(r, 25 - r) > qd: continue
        rr = E.resolve(k0, kend, long_, sl, tp)
        if rr:
            pl.append(rr["pnl"])
            rows.append(dict(date=pd.Timestamp(day * 86400000, unit="ms").date(), pnl=rr["pnl"]))
    return E.stats(pl), pd.DataFrame(rows)


def ulcer(p):
    eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
    dd = pk - eq
    return float(np.sqrt(np.mean(dd ** 2)))


def r2(p):
    eq = np.cumsum(p); x = np.arange(len(eq))
    if len(eq) < 3: return np.nan
    return float(np.corrcoef(x, eq)[0, 1] ** 2)


def streak(p):
    b = m = 0
    for v in p:
        b = b + 1 if v <= 0 else 0; m = max(m, b)
    return m


print(f"{'strategy':<34}{'n':>5}{'PF':>8}{'exp':>8}{'net':>9}{'maxDD':>8}{'Ulcer':>8}{'MAR':>7}{'R2':>7}{'streak':>8}")
res = {}
for tag, (s, d) in (("10AM Quarter Matrix (q<=7.5)", tenam()),
                    ("10AM, no quarter filter", tenam(qd=None))):
    p = d.pnl.to_numpy()
    res[tag] = p
    print(f"{tag:<34}{s['n']:>5}{s['pf']:>8.2f}{s['exp']:>8.2f}{s['net']:>9.1f}{s['mdd']:>8.1f}"
          f"{ulcer(p):>8.1f}{s['net']/max(s['mdd'],1e-9):>7.2f}{r2(p):>7.3f}{streak(p):>8}")

for tag, kw in (("Micro-Q3 base (no filters)", dict(body_min=0, body_max=None, qdist=None, spread_max=None)),
                ("Micro-Q3 Compression (claimed)", {})):
    d = M.apply(M.signals(**kw), 15.5, 25.5)
    p = d.pnl.to_numpy(); s = E.stats(p.tolist()); res[tag] = p
    print(f"{tag:<34}{s['n']:>5}{s['pf']:>8.2f}{s['exp']:>8.2f}{s['net']:>9.1f}{s['mdd']:>8.1f}"
          f"{ulcer(p):>8.1f}{s['net']/max(s['mdd'],1e-9):>7.2f}{r2(p):>7.3f}{streak(p):>8}")
L = max(len(v) for v in res.values())
np.save("research/microq3/results/equity_curves.npy",
        np.array([np.pad(np.cumsum(v), (0, L - len(v)), constant_values=np.nan) for v in res.values()]))
pd.Series(list(res.keys())).to_csv("research/microq3/results/equity_labels.csv", index=False, header=False)
