"""
Relaxation ladder for the LIQUIDITY_SWEEP v2.0 rule set.

WHY A LADDER. Run literally, the spec produces 1-4 trades in 6.7 years on
every instrument tested -- an untestable population. The funnel and the
risk-distribution measurement (see RESULTS_LEDGER) show why: the spec's own
sweep-depth rule (5.3.1, 0.25-0.55 ATR_D beyond the level) mechanically
produces a stop that its own validity gate (1.2, risk <= 0.32-0.35 ATR_D)
then rejects. The two rules fight each other.

So the question "does the sweep entry carry edge" cannot be answered at the
spec's own settings. The ladder relaxes the binding constraints one at a
time, in the order the diagnosis implies, and asks at each rung:

    (a) is the population large enough to say anything at all?
    (b) does it beat a MATCHED RANDOM ENTRY through the identical exit
        engine?  (spec 7.2 Control 1 -- the decisive test)

Rung (b) is the whole point. This repo has run that control seven times on
seven entry families and the entry has never won it.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

from research.sweep_lab import (INSTRUMENTS, Cfg, prepare, run, stats,
                               null_control, split)

LADDER = [
    ("L0  spec as written (sweep basis ATR_D)", dict()),
    ("L1  sweep basis ATR_X", dict(sweep_basis="X")),
    ("L2  L1 + risk cap 1.00 ATR_D  [the measured inconsistency]",
     dict(sweep_basis="X", risk_cap=1.00)),
    ("L3  L2 + speed window x2", dict(sweep_basis="X", risk_cap=1.00, speed_mult=2.0)),
    ("L4  L3 + volume criterion OFF (5.1.4)",
     dict(sweep_basis="X", risk_cap=1.00, speed_mult=2.0, require_vol=False)),
    ("L5  L4 + FVG requirement OFF (5.2 ablation)",
     dict(sweep_basis="X", risk_cap=1.00, speed_mult=2.0, require_vol=False,
          require_fvg=False)),
    ("L6  L5 + retest/arm windows x2",
     dict(sweep_basis="X", risk_cap=1.00, speed_mult=2.0, require_vol=False,
          require_fvg=False, retest_bars=30, arm_bars=48)),
    ("L7  L6 + session gate OFF (B1 ablation)",
     dict(sweep_basis="X", risk_cap=1.00, speed_mult=2.0, require_vol=False,
          require_fvg=False, retest_bars=30, arm_bars=48, session_gate=False)),
    ("L8  L7 + min_r 1.5, sweep 0.15-1.00 ATR_X, tested<=4",
     dict(sweep_basis="X", risk_cap=1.00, speed_mult=2.0, require_vol=False,
          require_fvg=False, retest_bars=30, arm_bars=48, session_gate=False,
          min_r=1.5, sweep_min=0.15, sweep_max=1.00, max_tested=4)),
]

NULL_SEEDS = 5


def fmt(s):
    if s.get("n", 0) == 0:
        return "n=0"
    return (f"n={s['n']:<5d} PF={s['pf']:<6.3f} WR={s['wr']:<6.2f} "
            f"expR={s['exp_r']:<8.4f} net={s['net']:<10.1f} "
            f"DD={s['maxdd']:<9.1f} bars={s['avg_bars']:.0f}")


def main():
    out = []
    for key in ("gold", "us30", "au200"):
        inst = INSTRUMENTS[key]
        A = prepare(inst, Cfg())
        print(f"\n{'='*100}")
        print(f"{inst.name}   bars={A['n']}   "
              f"{A['idx'][0].date()} -> {A['idx'][-1].date()}   "
              f"medATR_D={np.nanmedian(A['atr_d']):.2f} "
              f"medATR_X={np.nanmedian(A['atr_x']):.2f}")
        print('='*100)
        for label, kw in LADDER:
            cfg = Cfg(**kw)
            tr = run(A, inst, cfg)
            s = stats(tr, label)
            line = f"  {label:<62s} {fmt(s)}"
            rec = {"inst": key, "rung": label, **s}

            if s.get("n", 0) >= 30:
                # ---- CONTROL 1: matched random entry, identical exit engine
                nulls = [stats(null_control(A, inst, cfg, tr, seed=sd))
                         for sd in range(NULL_SEEDS)]
                npf = np.mean([x["pf"] for x in nulls if x.get("n")])
                nex = np.mean([x["exp_r"] for x in nulls if x.get("n")])
                nsd = np.std([x["exp_r"] for x in nulls if x.get("n")])
                z = (s["exp_r"] - nex) / nsd if nsd > 0 else float("nan")
                line += f"\n      NULL: PF={npf:.3f} expR={nex:+.4f}+/-{nsd:.4f}" \
                        f"  -> edge over null: {s['exp_r']-nex:+.4f} R  (z={z:+.2f})"
                rec.update(null_pf=round(float(npf), 3),
                           null_exp_r=round(float(nex), 4),
                           edge_over_null=round(float(s["exp_r"] - nex), 4),
                           z=round(float(z), 2))

                # ---- IS/OOS
                a, b = split(tr, A["idx"])
                sa, sb = stats(a, "IS"), stats(b, "OOS")
                line += (f"\n      IS  n={sa.get('n',0)} PF={sa.get('pf','-')}"
                         f"   OOS n={sb.get('n',0)} PF={sb.get('pf','-')}")
                rec.update(is_n=sa.get("n"), is_pf=sa.get("pf"),
                           oos_n=sb.get("n"), oos_pf=sb.get("pf"))

                # ---- type separation (spec 5.8)
                for t in ("R", "C"):
                    st_ = stats([x for x in tr if x["type"] == t], t)
                    if st_.get("n"):
                        line += (f"\n      Type {t}: n={st_['n']} PF={st_['pf']} "
                                 f"WR={st_['wr']} expR={st_['exp_r']:+.4f}")
                        rec[f"type{t}_n"] = st_["n"]
                        rec[f"type{t}_pf"] = st_["pf"]
            print(line)
            out.append(rec)

    pd.DataFrame(out).to_csv("research/sweep_ladder.csv", index=False)
    print("\nwrote research/sweep_ladder.csv")


if __name__ == "__main__":
    main()
