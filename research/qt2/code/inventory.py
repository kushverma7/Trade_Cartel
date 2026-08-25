"""Step 1 — inventory every XAUUSD tick part, verify coverage and continuity.

Reports gaps rather than filling them. A gap that falls inside a known market
closure is attributed; anything else is listed so it can be judged.
"""
import numpy as np, pandas as pd, os, glob

PTS = 1000.0
PARTS = {"2024-25": "research/microq3/data_holdout", "2025-26": "research/microq3/data"}

print("=" * 104)
print("XAUUSD TICK INVENTORY")
print("=" * 104)
tot = 0
for tag, d in PARTS.items():
    ny = np.load(f"{d}/ny_ms.npy", mmap_mode="r")
    bid = np.load(f"{d}/bid_i.npy", mmap_mode="r")
    ask = np.load(f"{d}/ask_i.npy", mmap_mode="r")
    n = len(ny); tot += n
    t0, t1 = pd.Timestamp(int(ny[0]), unit="ms"), pd.Timestamp(int(ny[-1]), unit="ms")
    sz = sum(os.path.getsize(f) for f in glob.glob(f"{d}/*.npy")) / 2**20
    print(f"\n  {tag}   {d}")
    print(f"    ticks      {n:>14,}      on-disk {sz:>8.0f} MiB")
    print(f"    NY span    {t0:%Y-%m-%d %H:%M} -> {t1:%Y-%m-%d %H:%M}  "
          f"({(t1-t0).days} days)")
    # continuity
    s = np.asarray(ny, np.int64)
    dif = np.diff(s)
    print(f"    monotonic  {'YES' if (dif >= 0).all() else 'NO -- ' + str((dif<0).sum()) + ' inversions'}")
    print(f"    duplicates {int((dif == 0).sum()):,} identical-ms ticks "
          f"({100*(dif==0).mean():.2f}%)")
    # price sanity on a thinned sample (full arrays are ~700MB each as int64)
    st = max(1, n // 4_000_000)
    b, a = np.asarray(bid[::st], np.int64), np.asarray(ask[::st], np.int64)
    sp = a - b
    print(f"    bid>ask    {int((sp < 0).sum()):,}   zero spread {int((sp == 0).sum()):,}"
          f"   (sampled 1 in {st})")
    print(f"    spread     median ${np.median(sp)/PTS:.3f}  mean ${sp.mean()/PTS:.3f}"
          f"  p95 ${np.percentile(sp,95)/PTS:.3f}  max ${sp.max()/PTS:.2f}")
    print(f"    price      ${b.min()/PTS:,.2f} .. ${a.max()/PTS:,.2f}")
    # gaps
    g = np.flatnonzero(dif > 60_000)           # > 1 minute
    if len(g):
        mins = dif[g] / 60000.0
        big = g[np.argsort(mins)[-5:]][::-1]
        print(f"    gaps >1min {len(g):,}   total {mins.sum()/60:.1f} h"
              f"   median {np.median(mins):.1f} min")
        print(f"    5 largest:")
        for i in big:
            a0 = pd.Timestamp(int(s[i]), unit="ms"); a1 = pd.Timestamp(int(s[i+1]), unit="ms")
            print(f"      {a0:%Y-%m-%d %a %H:%M} -> {a1:%Y-%m-%d %a %H:%M}"
                  f"   {(int(s[i+1])-int(s[i]))/3600000:>6.1f} h")
        # weekend attribution: NY Fri 17:00 -> Sun 18:00
        hm = (s[g] // 60000) % 1440
        dow = pd.to_datetime(s[g], unit="ms").dayofweek
        # The gap STARTS at the last tick before the close, which is 16:59 on a
        # normal Friday and 12:58 on an early close -- so the test must be
        # "Friday afternoon", not "at or after 17:00", or every weekend is missed.
        wk = ((dow == 4) & (hm >= 12 * 60)) | (dow == 5) | ((dow == 6) & (hm < 18 * 60))
        # the daily settlement break: 17:00-18:00 NY on a trading day
        brk = (~wk) & (hm >= 16 * 60) & (hm < 18 * 60) & (mins <= 75)
        print(f"    weekend closes          {int(wk.sum()):>5,}"
              f"  ({mins[wk].sum()/60:>7.1f} h)")
        print(f"    daily settlement breaks {int(brk.sum()):>5,}"
              f"  ({mins[brk].sum()/60:>7.1f} h)")
        print(f"    UNATTRIBUTED            {int((~wk & ~brk).sum()):>5,}"
              f"  ({mins[~wk & ~brk].sum()/60:>7.1f} h)")
        nw = mins[~wk & ~brk]
        if len(nw):
            print(f"      unattributed: median {np.median(nw):.1f} min,"
                  f" max {nw.max()/60:.2f} h, "
                  f"{int((nw > 120).sum())} over 2h")
    del ny, bid, ask, s, dif

print(f"\n  TOTAL {tot:,} ticks across {len(PARTS)} parts")
print("\n" + "=" * 104)
print("CHRONOLOGICAL SPLIT for this study (train on the EARLIEST data)")
print("=" * 104)
for lab, a, b in (("TRAIN", "2024-08-20", "2025-08-20"),
                  ("VALIDATION", "2025-08-20", "2026-02-20"),
                  ("HOLDOUT  (frozen)", "2026-02-20", "2026-08-21")):
    print(f"  {lab:<20} {a} -> {b}")
