"""Melbourne-aligned 5-minute bars + a compact session tick array, from the
91.6M-tick Dukascopy XAUUSD file.

WHY BOTH. Signals are defined on 5-minute closes, so bars drive the logic. But
exits are stops and targets, and resolving those on bars forces a guess about
the intrabar path -- the single assumption this repo has seen turn five separate
"champions" into execution artefacts. The tick array removes the guess: once a
position is open, the exit is found by walking actual quotes in the order they
arrived. Nothing is assumed about which of stop or target was touched first.

BARS are built on MID (bid+ask)/2, an unambiguous construction that matches what
a chart shows without committing to either side of the book. FILLS are not: the
bar also carries the last bid and last ask inside it, so a long pays the ask and
a short pays the bid, measured rather than modelled as a fixed cost.
"""
import os, numpy as np, pandas as pd, pyarrow.parquet as pa_pq

SRC = "/home/user/Trade_Cartel/research/gold_tick_data/dukascopy/processed/GOLD_XAUUSD_DUKASCOPY_TICKS_2025-08-21_to_2026-08-20.parquet"
OUT = "/home/user/Trade_Cartel/research/gold_10am_flip/data"
BAR_MS = 5 * 60 * 1000
PTS = 1000.0                      # price -> integer points, exact for 3dp


def main():
    pf = pa_pq.ParquetFile(SRC)
    parts, ticks = [], []
    n = 0
    for bi, batch in enumerate(pf.iter_batches(batch_size=4_000_000,
                                               columns=["timestamp_melbourne", "bid", "ask"])):
        mel = batch.column(0).cast("int64").to_numpy()          # epoch ms of LOCAL wall clock
        bid = batch.column(1).to_numpy(zero_copy_only=False)
        ask = batch.column(2).to_numpy(zero_copy_only=False)
        mid = (bid + ask) / 2.0
        n += len(mel)

        bucket = mel // BAR_MS
        df = pd.DataFrame({"b": bucket, "mid": mid, "bid": bid, "ask": ask})
        g = df.groupby("b", sort=True)
        agg = g.agg(o=("mid", "first"), h=("mid", "max"), l=("mid", "min"),
                    c=("mid", "last"), bid_c=("bid", "last"), ask_c=("ask", "last"),
                    ticks=("mid", "size"))
        agg["batch"] = bi
        parts.append(agg.reset_index())

        # Session ticks: 09:00-23:59 Melbourne is all the strategy can ever need
        # (09:50 line, 10:00 body, entries to 23:00, exits after). Storing the
        # whole year of ticks would be 1.4 GB for no gain.
        mins = (mel % 86_400_000) // 60_000
        keep = (mins >= 9 * 60) & (mins <= 23 * 60 + 59)
        if keep.any():
            ticks.append(np.stack([mel[keep].astype(np.int64),
                                   np.rint(bid[keep] * PTS).astype(np.int64),
                                   np.rint(ask[keep] * PTS).astype(np.int64)], axis=1))
        if (bi + 1) % 5 == 0:
            print(f"  batch {bi+1}, {n:,} ticks", flush=True)

    raw = pd.concat(parts, ignore_index=True).sort_values(["b", "batch"])
    # Merge partial buckets that straddled a batch boundary: first-of-first,
    # max, min, last-of-last, in batch order.
    bars = raw.groupby("b", sort=True).agg(
        o=("o", "first"), h=("h", "max"), l=("l", "min"), c=("c", "last"),
        bid_c=("bid_c", "last"), ask_c=("ask_c", "last"), ticks=("ticks", "sum")
    ).reset_index()

    ts = (bars["b"] * BAR_MS).astype("int64")
    dt = pd.to_datetime(ts, unit="ms")                # naive Melbourne wall clock
    bars["ts_mel"] = dt
    bars["date"] = dt.dt.date
    bars["hhmm"] = dt.dt.hour * 100 + dt.dt.minute
    bars = bars.drop(columns=["b"])
    bars.to_parquet(os.path.join(OUT, "bars_5m_melbourne.parquet"), index=False)

    T = np.concatenate(ticks, axis=0)
    T = T[np.argsort(T[:, 0], kind="stable")]
    np.save(os.path.join(OUT, "session_ticks.npy"), T)

    print(f"\nticks read      : {n:,}")
    print(f"5m bars         : {len(bars):,}")
    print(f"session ticks   : {len(T):,}  ({T.nbytes/1e6:.0f} MB)")
    print(f"bar span        : {bars['ts_mel'].min()}  ->  {bars['ts_mel'].max()}")


if __name__ == "__main__":
    main()
