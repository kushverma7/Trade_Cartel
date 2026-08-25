"""Decode the holdout year's raw BI5 straight into the engine's NY arrays.

Same decoder as the audited year: LZMA1 'alone', 20-byte big-endian records
'>IIIff' = (ms offset from the hour, ASK, BID, ask volume, bid volume), XAUUSD
divisor 1000. Ask precedes bid; reversing them yields a permanently negative
spread, which the audit below would catch.
"""
import os, sys, lzma, struct, numpy as np, pandas as pd, datetime as dt

RAW = "research/gold_holdout_tick_data/dukascopy/raw"
OUT = "research/microq3/data_holdout"
os.makedirs(OUT, exist_ok=True)
REC = struct.Struct(">IIIff")

files = []
for root, _, fs in os.walk(RAW):
    for f in sorted(fs):
        if f.endswith(".bi5"):
            files.append(os.path.join(root, f))
files.sort()
print(f"raw hourly files: {len(files):,}")

ts, bids, asks = [], [], []
bad = 0
for path in files:
    parts = path.split(os.sep)
    y, m, d = int(parts[-4]), int(parts[-3]), int(parts[-2])
    h = int(parts[-1][:2])
    base = int(dt.datetime(y, m, d, h, tzinfo=dt.timezone.utc).timestamp() * 1000)
    blob = open(path, "rb").read()
    if not blob:
        continue
    try:
        raw = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE).decompress(blob)
    except Exception:
        bad += 1; continue
    n = len(raw) // 20
    if n == 0:
        continue
    arr = np.frombuffer(raw[:n * 20], dtype=">u4,>u4,>u4,>f4,>f4")
    ts.append(base + arr["f0"].astype(np.int64))
    asks.append(arr["f1"].astype(np.int64))
    bids.append(arr["f2"].astype(np.int64))
print(f"undecodable files: {bad}")

utc = np.concatenate(ts); bid = np.concatenate(bids); ask = np.concatenate(asks)
o = np.argsort(utc, kind="stable")
utc, bid, ask = utc[o], bid[o], ask[o]
print(f"ticks: {len(utc):,}")
print(f"UTC span: {pd.Timestamp(utc[0],unit='ms')} -> {pd.Timestamp(utc[-1],unit='ms')}")

# ---- audit, same checks the audited year passed ----
sp = ask - bid
print("\nDATA AUDIT")
print(f"  bid > ask          : {int((sp<0).sum())}")
print(f"  zero spread        : {int((sp==0).sum())}")
print(f"  non-positive price : {int((bid<=0).sum()+(ask<=0).sum())}")
print(f"  out-of-order       : {int((np.diff(utc)<0).sum())}")
dup = int((np.diff(utc)==0).sum())
print(f"  identical timestamps: {dup:,} (normal — several prints share a millisecond)")
print(f"  median spread      : ${np.median(sp[::97])/1000:.3f}")
print(f"  price range        : ${bid.min()/1000:,.2f} .. ${ask.max()/1000:,.2f}")

# ---- to New York wall clock, tz-aware, never a fixed offset ----
ny = np.empty(len(utc), np.int64)
CH = 4_000_000
for i in range(0, len(utc), CH):
    idx = pd.DatetimeIndex(utc[i:i+CH].astype("datetime64[ms]")).tz_localize("UTC")\
            .tz_convert("America/New_York").tz_localize(None)
    ny[i:i+CH] = idx.values.astype("datetime64[ms]").astype(np.int64)
print(f"\nNY wall clock: {pd.Timestamp(ny[0],unit='ms')} -> {pd.Timestamp(ny[-1],unit='ms')}")

np.save(f"{OUT}/ny_ms.npy", ny)
np.save(f"{OUT}/bid_i.npy", bid.astype(np.int32))
np.save(f"{OUT}/ask_i.npy", ask.astype(np.int32))

minute = ny // 60_000
nr = np.empty(len(minute), bool); nr[0] = True
np.not_equal(minute[1:], minute[:-1], out=nr[1:])
st = np.flatnonzero(nr); en = np.append(st[1:], len(minute))
mid = (bid + ask) // 2
bars = {"minute": minute[st], "i0": st, "i1": en, "n": en - st}
for nm, a in (("mid", mid), ("bid", bid), ("ask", ask)):
    bars[f"{nm}_o"] = a[st]; bars[f"{nm}_c"] = a[en-1]
    bars[f"{nm}_h"] = np.maximum.reduceat(a, st); bars[f"{nm}_l"] = np.minimum.reduceat(a, st)
pd.DataFrame(bars).to_parquet(f"{OUT}/bars_1m_ny.parquet", index=False)
print(f"1-minute NY bars: {len(st):,}")
hm = (bars['minute'] % 1440)
print(f"bars inside 18:45-19:00 NY: {int(((hm>=18*60+45)&(hm<19*60)).sum())}")
