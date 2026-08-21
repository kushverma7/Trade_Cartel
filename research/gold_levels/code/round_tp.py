"""Does snapping the exit to a round number beat a plain fixed distance?

This is the only version of the level question that can actually change what
the strategy does. The exit work settled on a broad plateau centred near
SL 15 / TP 27. If round numbers are magnets, then a TP parked at the next
25/10/5 boundary beyond that distance should fill more often than the plain
fixed TP, and a TP parked just SHORT of the boundary (queue ahead of the wall)
should fill more often still.

Every variant below is resolved on the same cached tick paths as every other
experiment in this repo, against the same locked entry universe, and is scored
the same way: MINIMUM profit factor across the chronological DEV/VAL/HOLD
splits, never full-sample PF.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Trade_Cartel/research/gold_exit_eng/code")
from entry_universe import build, splits, label
from exits import resolve, stats

SL, TP_MIN = 15.0, 27.0

tr = build(1100, 2.0); d1, d2 = splits(tr); label(tr, d1, d2)
print(f"locked entry universe: n={len(tr)}  "
      f"({sum(t['kind']=='A_LONG' for t in tr)} A_LONG / {sum(t['kind']=='FLIP_SHORT' for t in tr)} FLIP_SHORT)")


def snapped_tp(t, S, buf):
    """TP distance for this trade when the target is pulled to the grid.

    buf > 0 places the order that many points on the NEAR side of the level
    (queue ahead of the wall); buf = 0 sits exactly on it.
    """
    e = t["entry"]
    if t["kind"] == "A_LONG":
        lvl = np.ceil((e + TP_MIN) / S) * S
        return (lvl - buf) - e
    lvl = np.floor((e - TP_MIN) / S) * S
    return e - (lvl + buf)


def score(tp_fn, name):
    recs = [(t["split"], resolve(t, sl=SL, tp=max(tp_fn(t), 1.0))[0]) for t in tr]
    d = {s: [v for sp, v in recs if sp == s] for s in ("DEV", "VAL", "HOLD")}
    A = stats([v for _, v in recs]); S_ = {s: stats(d[s]) for s in d}
    dist = [tp_fn(t) for t in tr]
    return dict(variant=name, n=A["n"], tp_mean=float(np.mean(dist)), pf=A["pf"], exp=A["exp"],
                net=A["net"], wr=A["wr"], mdd=A["mdd"],
                pf_dev=S_["DEV"]["pf"], pf_val=S_["VAL"]["pf"], pf_hold=S_["HOLD"]["pf"],
                minPF=min(S_[s]["pf"] for s in S_))


rows = [score(lambda t: TP_MIN, f"FIXED {TP_MIN:g}")]
for S in (5, 10, 25, 50):
    for buf in (0.0, 0.5, 1.0):
        tag = "on level" if buf == 0 else f"{buf:g} short of it"
        rows.append(score(lambda t, S=S, b=buf: snapped_tp(t, S, b), f"snap {S:>2}  {tag}"))

# control: the same snapping geometry against a grid that is NOT round.
# If the snapped variants win only because they change the average TP distance,
# a shifted grid of identical spacing wins by the same amount.
for S in (10, 25):
    rows.append(score(lambda t, S=S: snapped_tp(t, S, 0.0) + S / 3.0, f"snap {S:>2}  SHIFTED control"))

out = pd.DataFrame(rows)
out.to_csv("/home/user/Trade_Cartel/research/gold_levels/results/round_tp.csv", index=False)
pd.set_option("display.width", 220)
print(f"\n{'='*104}")
print(f"EXIT SNAPPED TO A ROUND NUMBER vs A PLAIN FIXED DISTANCE   (SL {SL:g} fixed, entry universe locked)")
print(f"{'='*104}")
print(out[["variant", "n", "tp_mean", "wr", "pf", "exp", "net", "mdd", "pf_dev", "pf_val", "pf_hold", "minPF"]]
      .to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
