#!/usr/bin/env python3
"""
Greedy level selection + parameter grid, with a LOCKED train/test split.

THE POINT OF THIS FILE is not to find a high number. It is to find a
configuration on the training half and then discover what that
configuration does on data it has never touched. The out-of-sample block
is evaluated ONCE, at the end. If it is run repeatedly and the config
adjusted in between, the split is destroyed and the result becomes
in-sample again -- which is how every previous result in this repo was
produced.

Why greedy rather than exhaustive: 18 levels is 262,144 subsets. Greedy
forward selection reaches a good subset in ~150 runs and, more importantly,
each step is interpretable -- you can see WHICH level was added and what it
bought. A subset picked by brute force over one window is fitted by
construction.

  python3 -m backtest.optimize --csv XAUUSD_15.csv
  python3 -m backtest.optimize --synthetic          # plumbing check only
"""
import argparse, datetime as dt, itertools, json, sys
import numpy as np, pandas as pd
from backtest import engine, levels as L, io as bio, synth

MIN_N = 30          # below this a result is not read, whatever the PF


def session_mask(idx, london=("08:00", "12:00"), ny=("13:30", "16:30")):
    t = idx.time
    def win(a, b):
        a, b = dt.time(*map(int, a.split(":"))), dt.time(*map(int, b.split(":")))
        return np.array([(x >= a) and (x < b) for x in t])
    return win(*london) | win(*ny)


def score(df, lv, sess, cfg):
    _, s = engine.run(df, lv, cfg, sess)
    return s


def greedy_levels(df, lv, sess, base, verbose=True):
    chosen, best_pf, log = [], -1.0, []
    pool = list(L.LEVEL_NAMES)
    while pool:
        cand_best, cand_stat, cand_name = None, None, None
        for name in pool:
            cfg = engine.Config(levels=chosen + [name], **base)
            s = score(df, lv, sess, cfg)
            if s["n"] < MIN_N or not np.isfinite(s["pf"]):
                continue
            if cand_best is None or s["pf"] > cand_best:
                cand_best, cand_stat, cand_name = s["pf"], s, name
        if cand_name is None or cand_best <= best_pf + 1e-9:
            break
        chosen.append(cand_name); pool.remove(cand_name)
        best_pf = cand_best
        log.append((cand_name, cand_stat))
        if verbose:
            print(f"  + {cand_name:5s} -> train PF {cand_best:.3f}  "
                  f"n={cand_stat['n']}  WR {cand_stat['wr']:.1f}%")
    return chosen, best_pf, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv"); ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--split", type=float, default=0.60)
    ap.add_argument("--out", default="backtest/last_run.json")
    a = ap.parse_args()

    if a.synthetic:
        df = synth.make(bars=20000)
        print("SYNTHETIC DATA — plumbing check only. Results are noise.\n")
    elif a.csv:
        df = bio.load_csv(a.csv)
    else:
        sys.exit("need --csv <file> or --synthetic")

    lv = L.build(df)
    sess = session_mask(df.index)
    cut = int(len(df) * a.split)
    tr, te = df.iloc[:cut], df.iloc[cut:]
    lvtr, lvte = lv.iloc[:cut], lv.iloc[cut:]
    str_, ste = sess[:cut], sess[cut:]
    print(f"bars {len(df)}  {df.index[0]:%Y-%m-%d} -> {df.index[-1]:%Y-%m-%d}")
    print(f"TRAIN {len(tr)} bars to {tr.index[-1]:%Y-%m-%d} | "
          f"TEST {len(te)} bars from {te.index[0]:%Y-%m-%d}\n")

    # Staged search. Re-running greedy selection inside a full parameter
    # grid is 72 x ~150 = ~10,800 backtests (~25 min); staging it is ~370
    # (~50s) and loses nothing that matters, because the level set and the
    # parameters are close to independent here.
    grid = {"mode": ["sweep", "retest", "both"],
            "tp_mode": ["levels", "fixed"],
            "min_sl": [0.6, 1.0], "max_sl": [2.0, 3.0],
            "tol_atr": [0.15, 0.25, 0.40]}
    keys = list(grid)
    defaults = {"mode": "both", "tp_mode": "levels", "min_sl": 1.0,
                "max_sl": 2.5, "tol_atr": 0.25}

    print("STAGE 1 — greedy level selection on TRAIN, default parameters")
    chosen, pf1, _ = greedy_levels(tr, lvtr, str_, defaults)
    if not chosen:
        print("\nNo level reached the minimum sample on TRAIN."); return

    print("\nSTAGE 2 — parameter grid on TRAIN, level set held fixed")
    best = (pf1, dict(defaults), list(chosen),
            score(tr, lvtr, str_, engine.Config(levels=chosen, **defaults)))
    for combo in itertools.product(*(grid[k] for k in keys)):
        base = dict(zip(keys, combo))
        s = score(tr, lvtr, str_, engine.Config(levels=chosen, **base))
        if s["n"] < MIN_N or not np.isfinite(s["pf"]):
            continue
        if s["pf"] > best[0]:
            best = (s["pf"], base, list(chosen), s)
            print(f"  train PF {s['pf']:.3f}  n={s['n']:<4} {base}")

    print("\nSTAGE 3 — re-select levels under the winning parameters")
    chosen2, pf3, _ = greedy_levels(tr, lvtr, str_, best[1])
    if chosen2:
        s3 = score(tr, lvtr, str_, engine.Config(levels=chosen2, **best[1]))
        if s3["n"] >= MIN_N and np.isfinite(s3["pf"]) and s3["pf"] > best[0]:
            best = (s3["pf"], best[1], chosen2, s3)

    if best is None:
        print("\nNo configuration reached the minimum sample on TRAIN.")
        return

    pf_tr, base, chosen, s_tr = best
    cfg = engine.Config(levels=chosen, **base)

    print("\n" + "=" * 66)
    print("SELECTED ON TRAIN")
    print("=" * 66)
    print(f"levels : {chosen}")
    print(f"params : {base}")
    print(f"train  : n={s_tr['n']}  WR {s_tr['wr']:.2f}%  PF {s_tr['pf']:.3f}  "
          f"net {s_tr['net_pct']:+.2f}%  maxDD {s_tr['maxdd_pct']:.2f}%")

    s_te = score(te, lvte, ste, cfg)                 # <-- the only OOS run
    print("\n" + "=" * 66)
    print("OUT OF SAMPLE — evaluated once, nothing tuned against it")
    print("=" * 66)
    if s_te["n"] < MIN_N:
        print(f"  n={s_te['n']} — BELOW THE READABLE MINIMUM ({MIN_N}). "
              "No conclusion either way.")
    else:
        print(f"  n={s_te['n']}  WR {s_te['wr']:.2f}%  PF {s_te['pf']:.3f}  "
              f"net {s_te['net_pct']:+.2f}%  maxDD {s_te['maxdd_pct']:.2f}%")
        drop = pf_tr - s_te["pf"]
        print(f"\n  train PF {pf_tr:.3f} -> test PF {s_te['pf']:.3f}   "
              f"decay {drop:+.3f}")
        if s_te["pf"] >= 1.0 and drop < 0.30:
            print("  VERDICT: survived. Worth a forward test.")
        elif s_te["pf"] >= 1.0:
            print("  VERDICT: positive but decayed hard — partly fitted.")
        else:
            print("  VERDICT: did not survive. The train result was fitting.")

    json.dump({"levels": chosen, "params": base, "train": s_tr, "test": s_te},
              open(a.out, "w"), indent=2, default=float)
    print(f"\nwritten to {a.out}")


if __name__ == "__main__":
    main()
