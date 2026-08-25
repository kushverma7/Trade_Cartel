"""Part 1/2/17 — the 24-hour Gold activity map, built independently per year.

Aggregates the raw tick stream into one row per (year, NY date, 5-minute bucket)
carrying every activity measure separately. They are kept separate on purpose:
tick count, quoted volume, range, realized volatility and spread are different
things and the study is about which of them agree.

DUKASCOPY VOLUME IS NOT GLOBAL GOLD VOLUME. It is the quoted size of one
liquidity provider's stream. It is reported here as one activity proxy among
several and is never described as market volume.
"""
import os, sys, lzma, struct, datetime as dt, numpy as np, pandas as pd
import pyarrow.parquet as pq

OUT = "research/goldmap/results"
os.makedirs(OUT, exist_ok=True)
Y2_PARQUET = ("research/gold_tick_data/dukascopy/processed/"
              "GOLD_XAUUSD_DUKASCOPY_TICKS_2025-08-21_to_2026-08-20.parquet")
Y1_RAW = "research/gold_holdout_tick_data/dukascopy/raw"


def chunks_y2(size=6_000_000):
    f = pq.ParquetFile(Y2_PARQUET)
    for b in f.iter_batches(batch_size=size,
                            columns=["timestamp_utc", "bid", "ask", "bid_volume", "ask_volume"]):
        ts = b.column("timestamp_utc").to_numpy(zero_copy_only=False)
        yield (ts.astype("datetime64[ms]").astype(np.int64),
               b.column("bid").to_numpy(zero_copy_only=False),
               b.column("ask").to_numpy(zero_copy_only=False),
               b.column("bid_volume").to_numpy(zero_copy_only=False),
               b.column("ask_volume").to_numpy(zero_copy_only=False))


def chunks_y1(size=6_000_000):
    files = sorted(os.path.join(r, f) for r, _, fs in os.walk(Y1_RAW) for f in fs if f.endswith(".bi5"))
    T, B, A, BV, AV = [], [], [], [], []
    tot = 0
    for path in files:
        p = path.split(os.sep)
        base = int(dt.datetime(int(p[-4]), int(p[-3]), int(p[-2]), int(p[-1][:2]),
                               tzinfo=dt.timezone.utc).timestamp() * 1000)
        blob = open(path, "rb").read()
        if not blob:
            continue
        raw = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE).decompress(blob)
        n = len(raw) // 20
        if n == 0:
            continue
        a = np.frombuffer(raw[:n * 20], dtype=">u4,>u4,>u4,>f4,>f4")
        T.append(base + a["f0"].astype(np.int64))
        A.append(a["f1"].astype(np.float64) / 1000.0)     # ask precedes bid in the record
        B.append(a["f2"].astype(np.float64) / 1000.0)
        AV.append(a["f3"].astype(np.float64)); BV.append(a["f4"].astype(np.float64))
        tot += n
        if tot >= size:
            yield (np.concatenate(T), np.concatenate(B), np.concatenate(A),
                   np.concatenate(BV), np.concatenate(AV))
            T, B, A, BV, AV = [], [], [], [], []; tot = 0
    if T:
        yield (np.concatenate(T), np.concatenate(B), np.concatenate(A),
               np.concatenate(BV), np.concatenate(AV))


def build(year, gen):
    acc = {}
    for utc, bid, ask, bv, av in gen:
        o = np.argsort(utc, kind="stable")
        utc, bid, ask, bv, av = utc[o], bid[o], ask[o], bv[o], av[o]
        ny = (pd.DatetimeIndex(utc.astype("datetime64[ms]")).tz_localize("UTC")
              .tz_convert("America/New_York").tz_localize(None)
              .values.astype("datetime64[ms]").astype(np.int64))
        mid = (bid + ask) / 2.0
        spr = ask - bid
        key = ny // 300_000                       # 5-minute bucket id
        # group by runs of equal key (ticks are time-ordered inside a chunk)
        nr = np.empty(len(key), bool); nr[0] = True
        np.not_equal(key[1:], key[:-1], out=nr[1:])
        st = np.flatnonzero(nr); en = np.append(st[1:], len(key))
        for i0, i1, k in zip(st, en, key[st]):
            m = mid[i0:i1]; s = spr[i0:i1]
            r = acc.setdefault(int(k), dict(n=0, bv=0.0, av=0.0, sp=[], hi=-1e18, lo=1e18,
                                            first=m[0], last=m[-1], sq=0.0))
            r["n"] += i1 - i0
            r["bv"] += float(bv[i0:i1].sum()); r["av"] += float(av[i0:i1].sum())
            r["sp"].append(s)
            r["hi"] = max(r["hi"], float(m.max())); r["lo"] = min(r["lo"], float(m.min()))
            r["last"] = float(m[-1])
            if len(m) > 1:
                d = np.diff(m); r["sq"] += float((d * d).sum())
    rows = []
    for k, r in acc.items():
        sp = np.concatenate(r["sp"])
        t = pd.Timestamp(k * 300_000, unit="ms")
        rows.append(dict(year=year, bucket=k, date=t.date(),
                         hm=t.hour * 60 + t.minute, dow=t.dayofweek,
                         ticks=r["n"], bid_vol=r["bv"], ask_vol=r["av"],
                         spread_med=float(np.median(sp)), spread_mean=float(sp.mean()),
                         spread_p90=float(np.percentile(sp, 90)),
                         rng=r["hi"] - r["lo"], ret=r["last"] - r["first"],
                         rv=float(np.sqrt(r["sq"]))))
    return pd.DataFrame(rows).sort_values("bucket").reset_index(drop=True)


if __name__ == "__main__":
    import time
    out = []
    for year, gen in (("2024-25", chunks_y1()), ("2025-26", chunks_y2())):
        t0 = time.time()
        d = build(year, gen)
        print(f"{year}: {len(d):,} five-minute buckets, {d.ticks.sum():,} ticks "
              f"({time.time()-t0:.0f}s)", flush=True)
        out.append(d)
    D = pd.concat(out, ignore_index=True)
    D["tot_vol"] = D.bid_vol + D.ask_vol
    D["abs_ret"] = D.ret.abs()
    for x in (10, 15, 20, 25):
        D[f"ge{x}"] = (D.rng >= x).astype(int)
    D["mv_per_spread"] = D.rng / D.spread_med.clip(lower=1e-6)
    D["mv_per_cost"] = D.rng / (2 * D.spread_med).clip(lower=1e-6)   # round-trip cost proxy
    D.to_parquet(f"{OUT}/activity_5m.parquet", index=False)
    print(f"\nwrote {OUT}/activity_5m.parquet  rows={len(D):,}")
    print(D.groupby("year").agg(days=("date", "nunique"), buckets=("bucket", "size"),
                                ticks=("ticks", "sum")).to_string())
