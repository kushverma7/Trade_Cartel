"""
Reads research/level_profile.csv and produces the ranked tables.

WHY THE PHASE-SHIFTED CONTROL IS THE BASELINE, NOT THE UNCONDITIONAL DRIFT
  The unconditional forward move is direction-blind: gold drifted up over this
  sample, so a set of events that happens to lean long beats it automatically.
  The phase-shifted control does not have that problem. It contains the same
  families, the same tolerances, the same event mix and -- because the level is
  only displaced, not replaced -- very nearly the same long/short balance. The
  quantity reported everywhere below as EDGE is

      edge = real(metric) - random(metric)

  matched on family, event, tolerance and horizon. The unconditional drift is
  printed once, for context, and is not used to score anything.
"""
import numpy as np, pandas as pd

MINN = 100
pd.set_option("display.width", 250)


def load():
    t = pd.read_csv("research/level_profile.csv")
    real = t[(t.src == "real") & (t.cut == "all")]
    k = ["family", "event", "tol", "horizon"]
    # average the four parallel-displaced control replicates
    rc = t[t.src.str.startswith("random") & (t.cut == "all")]
    rand = (rc.groupby(k)[["n", "mean_ret", "mfe", "mae", "mfe_mae", "winrate"]]
              .mean().reset_index())
    m = real.merge(rand, on=k, suffixes=("", "_r"))
    m["edge_ret"] = m.mean_ret - m.mean_ret_r
    m["edge_mm"] = m.mfe_mae - m.mfe_mae_r
    m["edge_wr"] = m.winrate - m.winrate_r
    return t, m


def fmt(d, cols):
    return d[cols].to_string(index=False, float_format=lambda v: f"{v:8.3f}")


def main():
    t, m = load()
    base = pd.read_csv("research/level_baseline.csv")
    freq = pd.read_csv("research/level_frequency.csv")
    dep = pd.read_csv("research/level_sweep_depth.csv")

    print("=" * 140)
    print("UNCONDITIONAL DRIFT (context only -- not used for scoring)")
    print("=" * 140)
    print(fmt(base, list(base.columns)))

    print("\n" + "=" * 140)
    print("EVENT FREQUENCY, tolerance 0.5 ATR")
    print("=" * 140)
    f = freq[freq.tol == 0.5].pivot_table(index="family", columns="event",
                                          values="n", fill_value=0).astype(int)
    f["TOTAL"] = f.sum(axis=1)
    f["% of bars"] = (100 * f.TOTAL / 78695).round(2)
    print(f.sort_values("TOTAL", ascending=False).to_string())

    print("\n" + "=" * 140)
    print("TABLE 1 -- LEVEL FAMILY RANKING vs its own phase-shifted twin")
    print("  horizon 16 bars, tolerance 0.5 ATR. edge_mm = MFE/MAE above control.")
    print("=" * 140)
    q = m[(m.horizon == 16) & (m.tol == 0.5)].copy()
    q = q.sort_values("edge_mm", ascending=False)
    print(fmt(q, ["family", "event", "n", "mean_ret", "mfe", "mae", "mfe_mae",
                  "mfe_mae_r", "edge_mm", "winrate", "edge_wr", "low_conf"]))

    print("\n" + "=" * 140)
    print("TABLE 2 -- SWEEP vs CLEAN BREAK, all tolerances, horizon 16")
    print("=" * 140)
    q2 = m[(m.horizon == 16) & (m.event.isin(["sweep", "break"]))]
    p = q2.pivot_table(index=["family", "tol"], columns="event",
                       values=["n", "mfe_mae", "edge_mm", "winrate"])
    print(p.round(3).to_string())

    print("\n" + "=" * 140)
    print("TABLE 3 -- CONFLUENCE: single vs dual vs triple+, round numbers only")
    print("  tolerance 0.5 ATR. Cells under n=100 are flagged.")
    print("=" * 140)
    cc = t[(t.src == "real") & (t.cut.isin(["single", "dual", "triple+"]))
           & (t.tol == 0.5) & (t.horizon == 16)]
    print(fmt(cc.sort_values(["family", "event", "cut"]),
              ["family", "event", "cut", "n", "mean_ret", "mfe_mae",
               "winrate", "low_conf"]))

    print("\n" + "=" * 140)
    print("TABLE 4 -- TOUCH NUMBER: first vs second vs third+, tolerance 0.5, horizon 16")
    print("=" * 140)
    tt = t[(t.src == "real") & (t.cut.str.startswith("touch")) & (t.tol == 0.5)
           & (t.horizon == 16)]
    p4 = tt.pivot_table(index=["family", "event"], columns="cut",
                        values=["n", "mfe_mae", "mean_ret"])
    print(p4.round(3).to_string())

    print("\n" + "=" * 140)
    print("TABLE 5 -- REGIME SPLIT, tolerance 0.5 ATR, horizon 16")
    print("=" * 140)
    rr = t[(t.src == "real") & (t.cut.isin(["above_ema", "below_ema"]))
           & (t.tol == 0.5) & (t.horizon == 16)]
    p5 = rr.pivot_table(index=["family", "event"], columns="cut",
                        values=["n", "mean_ret", "mfe_mae", "winrate"])
    print(p5.round(3).to_string())

    print("\n" + "=" * 140)
    print("TABLE 6 -- SWEEP DEPTH beyond the tolerance band, in ATR")
    print("=" * 140)
    print(fmt(dep.sort_values(["tol", "family"]),
              ["family", "tol", "mean_depth_atr", "med_depth_atr"]))

    print("\n" + "=" * 140)
    print("TABLE 7 -- SWEEP: continuation vs reversal at 8 and 16 bars")
    print("  'reversal' = the fade direction paid (ret > 0); tolerance 0.5 ATR")
    print("=" * 140)
    sw = m[(m.event == "sweep") & (m.tol == 0.5) & (m.horizon.isin([8, 16]))]
    print(fmt(sw.sort_values(["family", "horizon"]),
              ["family", "horizon", "n", "winrate", "winrate_r", "edge_wr",
               "mean_ret", "edge_ret"]))

    print("\n" + "=" * 140)
    print("TABLE 8 -- TOLERANCE SENSITIVITY of the top families (horizon 16)")
    print("=" * 140)
    top = q.head(5).family.unique()
    ts = m[(m.horizon == 16) & (m.family.isin(top))]
    print(ts.pivot_table(index=["family", "event"], columns="tol",
                         values=["n", "edge_mm"]).round(3).to_string())

    # ---------------------------------------------------------- survivors
    print("\n" + "=" * 140)
    print("SURVIVORS -- cells beating their phase-shifted twin on BOTH MFE/MAE and")
    print("  win rate, at n >= 100, in the SAME direction at 8, 16 and 32 bars")
    print("=" * 140)
    ok = m[(m.n >= MINN) & (m.edge_mm > 0) & (m.edge_wr > 0)]
    g = (ok[ok.horizon.isin([8, 16, 32])]
         .groupby(["family", "event", "tol"])
         .agg(horizons=("horizon", "count"), n=("n", "min"),
              edge_mm=("edge_mm", "mean"), edge_wr=("edge_wr", "mean"),
              edge_ret=("edge_ret", "mean")).reset_index())
    g = g[g.horizons == 3].sort_values("edge_mm", ascending=False)
    if len(g):
        print(fmt(g, ["family", "event", "tol", "n", "edge_mm", "edge_wr", "edge_ret"]))
    else:
        print("  NONE.")
    g.to_csv("research/level_survivors.csv", index=False)
    print(f"\n  {len(g)} of {len(m[m.horizon.isin([8,16,32])].groupby(['family','event','tol']))}"
          f" family x event x tolerance combinations survive all three horizons.")


if __name__ == "__main__":
    main()
