"""ONE-YEAR IN-SAMPLE STUDY — QT cycle event engine. 2025-08-21 to 2026-08-20 ONLY.

STRUCTURAL DEFINITIONS (documented because the reproduction depends on them):

  cycle       one 6-hour daily quarter of the New York QT day
              D1 = 18:00 NY   D2 = 00:00   D3 = 06:00   D4 = 12:00
  Q1..Q4      the four 90-minute quarters inside that cycle
  Q1 eff      |Q1 close - Q1 open| / Q1 range
  Q2 eff      |Q2 close - Q2 open| / Q2 range
  DFR         Defining Range: drop the first third of Q1, take the high and low
              of its final 60 minutes.  DFR/Q1 = DFR width / Q1 range
  sweep       Q2 high > Q1 high  -> high swept;  Q2 low < Q1 low -> low swept
  sweep depth (Q2 high - Q1 high)/Q1 range, or (Q1 low - Q2 low)/Q1 range
  direction   OPPOSITE the swept side. Low swept = bearish manipulation = LONG.
              A double sweep takes the opposite of the DEEPER side.
  entry       first executable tick at or after the Q3 open
  stop        the Q2 extreme on the swept side (the manipulation wick)
  target      the opposite Q1 extreme (the liquidity the theory says gets taken)
  R           one unit of risk = |entry - stop|; all P&L is reported in R
  RR          |target - entry| / |entry - stop|

Signal construction uses MID. Execution uses real bid/ask, always.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/goldmap/code")
from qt_engine import Book, PTS

DATA, YEAR = "research/microq3/data", "2025-26"
CYCLES = {"D1": 18 * 3600, "D2": 0, "D3": 6 * 3600, "D4": 12 * 3600}
Q = 5400          # 90 minutes


def quarter(book, day, s0, span=Q, min_ticks=60):
    c = book.candle(day, s0, s0 + span, min_ticks=min_ticks)
    if c is None:
        return None
    lo, hi = c["i0"], c["i1"]
    return dict(o=c["o"] / PTS, c=c["c"] / PTS, h=c["h"] / PTS, l=c["l"] / PTS,
                ticks=c["n"], i0=lo, i1=hi, t_close=c["t_close"])


def build():
    b = Book(DATA, YEAR)
    rows = []
    for day in b.days:
        for dname, dh in CYCLES.items():
            qs = [(dh + k * Q) % 86400 for k in range(4)]
            q1, q2, q3, q4 = [quarter(b, day, s) for s in qs]
            if q1 is None or q2 is None or q3 is None:
                continue
            r1 = q1["h"] - q1["l"]
            if r1 <= 0:
                continue

            # --- Defining Range: final two-thirds of Q1 ---
            # final two-thirds of Q1 ONLY: 60 minutes, never reaching into Q2
            dfr = quarter(b, day, (qs[0] + Q // 3) % 86400, span=Q - Q // 3, min_ticks=30)
            if dfr is None:
                continue
            dfr_w = dfr["h"] - dfr["l"]

            # --- Q2 sweep of Q1 liquidity ---
            up_d = (q2["h"] - q1["h"]) / r1 if q2["h"] > q1["h"] else 0.0
            dn_d = (q1["l"] - q2["l"]) / r1 if q2["l"] < q1["l"] else 0.0
            if up_d == 0 and dn_d == 0:
                sweep, depth, long_ = "none", 0.0, None
            elif up_d > 0 and dn_d > 0:
                sweep = "both"; depth = max(up_d, dn_d); long_ = up_d < dn_d
            elif up_d > 0:
                sweep, depth, long_ = "high only", up_d, False
            else:
                sweep, depth, long_ = "low only", dn_d, True
            if long_ is None:
                continue

            # --- the structural trade, taken at the Q3 open ---
            k0 = int(np.searchsorted(b.ny, q2["t_close"], "right"))
            if k0 >= q3["i1"]:
                continue
            bid, ask = int(b.bid[k0]) / PTS, int(b.ask[k0]) / PTS
            entry = ask if long_ else bid
            stop = q2["l"] if long_ else q2["h"]
            target = q1["h"] if long_ else q1["l"]
            risk = abs(entry - stop)
            reward = abs(target - entry)
            if risk <= 0.01:
                continue

            rows.append(dict(
                year=YEAR, day=day, date=pd.Timestamp(day * 86400000, unit="ms").date(),
                cycle=dname, cycle_open_s=dh,
                q1_o=q1["o"], q1_c=q1["c"], q1_h=q1["h"], q1_l=q1["l"], q1_rng=r1,
                q1_eff=abs(q1["c"] - q1["o"]) / r1, q1_ticks=q1["ticks"],
                q2_o=q2["o"], q2_c=q2["c"], q2_h=q2["h"], q2_l=q2["l"],
                q2_rng=q2["h"] - q2["l"],
                q2_eff=(abs(q2["c"] - q2["o"]) / (q2["h"] - q2["l"])) if q2["h"] > q2["l"] else np.nan,
                q2_ticks=q2["ticks"], q2_over_q1=(q2["h"] - q2["l"]) / r1,
                q2_dir_ret=((q2["c"] - q2["o"]) * (1 if long_ else -1)) / r1,
                q3_o=q3["o"], q3_c=q3["c"], q3_h=q3["h"], q3_l=q3["l"], q3_ticks=q3["ticks"],
                dfr_h=dfr["h"], dfr_l=dfr["l"], dfr_w=dfr_w, dfr_over_q1=dfr_w / r1,
                dfr_mid=(dfr["h"] + dfr["l"]) / 2,
                sweep=sweep, sweep_depth=depth, sweep_up=up_d, sweep_dn=dn_d,
                back_inside=(q1["l"] <= q2["c"] <= q1["h"]),
                long=long_, k0=k0, k_end=q3["i1"], t_entry=int(b.ny[k0]),
                entry=entry, spread=ask - bid, stop=stop, target=target,
                risk=risk, reward=reward, rr=reward / risk,
                q1_min=Q / 60.0, q2_min=Q / 60.0))
    return pd.DataFrame(rows), b


if __name__ == "__main__":
    import time
    t0 = time.time()
    C, b = build()
    # rolling, PAST-ONLY activity percentile from real Dukascopy tick rates
    C = C.sort_values(["day", "cycle_open_s"]).reset_index(drop=True)
    C["q1_rate"] = C.q1_ticks / C.q1_min
    C["q2_rate"] = C.q2_ticks / C.q2_min
    C["pre_q3_rate"] = (C.q1_rate + C.q2_rate) / 2.0
    for col, out in (("pre_q3_rate", "act_pct"), ("q1_rng", "comp_pct")):
        C[out] = np.nan
        for cyc, idx in C.groupby("cycle").groups.items():
            idx = np.array(sorted(idx)); v = C.loc[idx, col].to_numpy()
            for i in range(len(v)):
                pr = v[max(0, i - 40):i]
                if len(pr) >= 15:
                    C.loc[idx[i], out] = (pr < v[i]).mean()
    C.to_parquet("research/insample/results/cycles.parquet", index=False)
    print(f"ONE-YEAR IN-SAMPLE. cycles with a Q2 sweep and a tradeable Q3: {len(C):,} "
          f"({time.time()-t0:.0f}s)")
    print(C.groupby("cycle").size().to_string())
    print(f"\nsweep types: {C.sweep.value_counts().to_dict()}")
    print(f"direction: long {int(C.long.sum())}  short {int((~C.long).sum())}")
    print(f"\nRR: median {C.rr.median():.2f}  p25 {C.rr.quantile(.25):.2f}  p75 {C.rr.quantile(.75):.2f}")
    print(f"DFR/Q1: median {C.dfr_over_q1.median():.2f}")
    print(f"Q2 eff: median {C.q2_eff.median():.2f}   Q1 eff: median {C.q1_eff.median():.2f}")
    print(f"sweep depth: median {C.sweep_depth.median():.3f}")
