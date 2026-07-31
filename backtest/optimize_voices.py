#!/usr/bin/env python3
"""
Search the 22-voice register against real bars, under the three gates.

This is the test the Multi-Voice engine has always deserved and never had:
the full voice register, on 6.7 years, with a locked train/test split, a
random null rebuilt at the matched sample size, and deflated Sharpe over
the real trial count.

Two things are searched:
  minScore  -- the conviction threshold (how many voices must agree)
  subset    -- which voices are allowed to vote, chosen greedily

Votes are precomputed once, so each configuration costs only a backtest.

  python3 -m backtest.optimize_voices --csv data/xauusd_15m.csv.gz
"""
import argparse, json
import numpy as np
from backtest import engine, levels as L, io as bio, voices
from backtest.optimize import session_mask

MIN_N = 30
LEVELS = ["DO", "PDH", "PDL", "WO", "PWH", "PWL", "MONH", "MONL"]


def signals(V, subset, minScore, weight_high=True):
    w = np.ones(22)
    if weight_high:
        for i in voices.HIGH_CRED:
            w[i] = 2.0
    mask = np.zeros(22, bool); mask[list(subset)] = True
    score = (V * (w * mask)).sum(1)
    return score >= minScore, score <= -minScore


def run_cfg(df, lv, sess, V, subset, minScore, base):
    sl, ss = signals(V, subset, minScore)
    cfg = engine.Config(levels=LEVELS, **base)
    return engine.run(df, lv, cfg, sess, sl, ss)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--split", type=float, default=0.60)
    ap.add_argument("--out", default="backtest/voices_run.json")
    a = ap.parse_args()

    df = bio.load_csv(a.csv); lv = L.build(df); sess = session_mask(df.index)
    atr = engine.atr(df["high"].to_numpy(float), df["low"].to_numpy(float),
                     df["close"].to_numpy(float))
    V = voices.compute(df, lv, atr, sess)
    cut = int(len(df) * a.split)
    tr, lvtr, str_, Vtr = df.iloc[:cut], lv.iloc[:cut], sess[:cut], V[:cut]
    te, lvte, ste, Vte = df.iloc[cut:], lv.iloc[cut:], sess[cut:], V[cut:]
    print(f"bars {len(df):,}   TRAIN to {tr.index[-1]:%Y-%m-%d} | "
          f"TEST from {te.index[0]:%Y-%m-%d}\n")

    base = dict(tp_mode="fixed", tp1_r=1.0, tp2_r=2.0, tp1_pct=50,
                min_sl=0.5, max_sl=2.5, cooldown=12, time_stop=48, max_day=4)

    # ---- stage 1: conviction threshold with every voice enabled ----
    print("STAGE 1 — conviction threshold, all 22 voices")
    allv = list(range(22)); best = None
    for ms in range(4, 19):
        t, s = run_cfg(tr, lvtr, str_, Vtr, allv, ms, base)
        if s["n"] < MIN_N:
            print(f"  minScore {ms:>2}: n={s['n']} — too few"); continue
        print(f"  minScore {ms:>2}: n={s['n']:>5}  WR {s['wr']:5.2f}%  PF {s['pf']:.3f}")
        if best is None or s["pf"] > best[0]:
            best = (s["pf"], ms, s)
    if best is None:
        print("no threshold produced a usable sample"); return
    pf0, ms0, s0 = best
    print(f"  -> best minScore {ms0} at train PF {pf0:.3f}\n")

    # ---- stage 2: greedy voice selection at that threshold ----
    print("STAGE 2 — greedy voice selection")
    chosen, bestpf = [], -1.0
    pool = list(range(22))
    while pool:
        cand = None
        for i in pool:
            t, s = run_cfg(tr, lvtr, str_, Vtr, chosen + [i], ms0, base)
            if s["n"] < MIN_N or not np.isfinite(s["pf"]):
                continue
            if cand is None or s["pf"] > cand[0]:
                cand = (s["pf"], i, s)
        if cand is None or cand[0] <= bestpf + 1e-9:
            break
        bestpf, i, s = cand
        chosen.append(i); pool.remove(i)
        print(f"  + {voices.NAMES[i]:22s} train PF {bestpf:.3f}  n={s['n']}")
    if not chosen:
        chosen, bestpf = allv, pf0

    # ---- stage 3: re-tune the threshold for the chosen subset ----
    print("\nSTAGE 3 — re-tune threshold for the selected voices")
    for ms in range(2, 15):
        t, s = run_cfg(tr, lvtr, str_, Vtr, chosen, ms, base)
        if s["n"] >= MIN_N and np.isfinite(s["pf"]) and s["pf"] > bestpf:
            bestpf, ms0 = s["pf"], ms
            print(f"  minScore {ms:>2}: train PF {s['pf']:.3f}  n={s['n']}  <- new best")

    t_tr, s_tr = run_cfg(tr, lvtr, str_, Vtr, chosen, ms0, base)
    print("\n" + "=" * 66)
    print("SELECTED ON TRAIN")
    print("=" * 66)
    print(f"voices    : {[voices.NAMES[i] for i in chosen]}")
    print(f"minScore  : {ms0}")
    print(f"train     : n={s_tr['n']}  WR {s_tr['wr']:.2f}%  PF {s_tr['pf']:.3f}  "
          f"net {s_tr['net_pct']:+.2f}%  maxDD {s_tr['maxdd_pct']:.2f}%")

    t_te, s_te = run_cfg(te, lvte, ste, Vte, chosen, ms0, base)
    print("\n" + "=" * 66)
    print("OUT OF SAMPLE — evaluated once")
    print("=" * 66)
    print(f"  n={s_te['n']}  WR {s_te['wr']:.2f}%  PF {s_te['pf']:.3f}  "
          f"net {s_te['net_pct']:+.2f}%  maxDD {s_te['maxdd_pct']:.2f}%")
    bh = (te["close"].iloc[-1] / te["close"].iloc[0] - 1) * 100
    print(f"  buy & hold same window: {bh:+.2f}%")

    json.dump({"voices": chosen, "voice_names": [voices.NAMES[i] for i in chosen],
               "minScore": ms0, "base": base, "train": s_tr, "test": s_te,
               "buy_hold_pct": bh}, open(a.out, "w"), indent=2, default=float)
    print(f"\nwritten to {a.out}")


if __name__ == "__main__":
    main()
