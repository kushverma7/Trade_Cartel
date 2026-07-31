#!/usr/bin/env python3
"""
Stress-test a selected configuration before it is allowed to count.

A positive out-of-sample number is where this project has historically gone
wrong: PF 3.656 and PF 1.783 both looked like results and both were
artifacts. So no configuration enters RESULTS_LEDGER as validated until it
survives all three checks here.

  1. RANDOM NULL AT THE MATCHED SAMPLE SIZE
     Profit-factor error scales with 1/sqrt(n), so a null built from
     800-trade samples says nothing about a 60-trade result. The null is
     rebuilt at the same n before any comparison is made.

  2. DEFLATED SHARPE FOR THE SELECTION
     Greedy selection plus the parameter grid tries several hundred
     configurations. DSR asks how surprising the winner is GIVEN that many
     attempts. Reported across trial counts because the honest count is
     never obvious.

  3. BUY AND HOLD OVER THE SAME WINDOW
     A strategy that underperforms simply owning the asset has not earned
     the complexity, whatever its profit factor.

  python3 -m backtest.stress_test --run backtest/xau15_run.json \\
      --csv data/xauusd_15m.csv.gz
"""
import argparse, json
import numpy as np
from backtest import engine, levels as L, io as bio
from backtest.optimize import session_mask
from backtest.overfit import deflated_sharpe_ratio, sharpe_from_pnl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--split", type=float, default=0.60)
    ap.add_argument("--trials", type=int, default=400)
    a = ap.parse_args()

    r = json.load(open(a.run))
    df = bio.load_csv(a.csv); lv = L.build(df); sess = session_mask(df.index)
    cut = int(len(df) * a.split)
    te, lvte, ste = df.iloc[cut:], lv.iloc[cut:], sess[cut:]

    cfg = engine.Config(levels=r["levels"], **r["params"])
    tr, st = engine.run(te, lvte, cfg, ste)
    print(f"config : {r['levels']}  {r['params']}")
    print(f"OOS    : n={st['n']}  WR {st['wr']:.2f}%  PF {st['pf']:.3f}  "
          f"net {st['net_pct']:+.2f}%  maxDD {st['maxdd_pct']:.2f}%\n")

    # 1 ---- random null, matched n
    rate = st["n"] / len(te)
    pfs, srs = [], []
    for s in range(a.trials):
        c2 = engine.Config(levels=r["levels"], random_p=rate * 3,
                           random_seed=s, **r["params"])
        t2, s2 = engine.run(te, lvte, c2, ste)
        if 30 <= s2["n"] <= max(200, st["n"] * 3) and np.isfinite(s2["pf"]):
            pfs.append(s2["pf"])
            srs.append(sharpe_from_pnl([x["pnl"] for x in t2])["sr"])
    pfs = np.array(pfs)
    print(f"1. RANDOM NULL matched to n~{st['n']}  ({len(pfs)} trials)")
    for q in (50, 75, 90, 95, 99):
        print(f"     {q:>2}th pct  PF {np.percentile(pfs, q):.3f}")
    pct = (pfs < st["pf"]).mean() * 100
    print(f"     our PF {st['pf']:.3f} sits at the {pct:.1f}th percentile of random")
    print(f"     {'PASS' if pct >= 95 else 'FAIL'} — needs >= 95th to beat a coin flip\n")

    # 2 ---- deflated Sharpe
    m = sharpe_from_pnl([t["pnl"] for t in tr])
    v = float(np.var(srs, ddof=1)) if len(srs) > 1 else 0.0
    print(f"2. DEFLATED SHARPE   SR/trade {m['sr']:+.4f} on n={m['n']}")
    for k in (1, 100, 370):
        d = deflated_sharpe_ratio(m["sr"], m["n"], n_trials=k, variance_trials=v,
                                  skewness=m["skew"], kurtosis=m["kurt"])
        print(f"     trials={k:>4}  E[max SR]={d['expected_max_sharpe']:.4f}  "
              f"DSR={d['dsr']:.3f}  {'PASS' if d['dsr'] >= 0.95 else 'FAIL'}")
    print()

    # 3 ---- buy and hold
    bh = (te["close"].iloc[-1] / te["close"].iloc[0] - 1) * 100
    print(f"3. BUY AND HOLD  {bh:+.2f}%   vs strategy {st['net_pct']:+.2f}%")
    print(f"     {'PASS' if st['net_pct'] > bh else 'FAIL'} — "
          "underperforming the asset does not justify the complexity")


if __name__ == "__main__":
    main()
