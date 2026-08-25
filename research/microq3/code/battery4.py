"""Walk-forward on the parameter that actually matters (the anchor), and the
fixed vs volatility-adaptive compression filter.

LOOK-AHEAD WARNING built into this file. The suggested adaptive rule is
"body <= 35% of the surrounding 90-minute Q1 range". Quarterly Theory's 90-minute
Q1 on the 18:00 NY daily cycle is 18:00-19:30, which CONTAINS the 19:00-19:30
signal window. Normalising by a range that is not complete until 19:30 and then
trading a 19:05 break uses information that did not exist at the decision. Both
versions are computed below: the leaky one, and a causal one that closes the
range at 19:00, the last instant available when the anchor completes.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/microq3/code")
import engine as E
import microq3 as M
from engine import PTS

SL, TP = 15.5, 25.5
ANCHORS = list(range(18 * 60 + 15, 19 * 60 + 45, 5))
pd.set_option("display.width", 240)


def trades_for(anchor, **kw):
    return M.apply(M.signals(anchor_start=anchor, win_from=anchor + 15,
                             win_to=anchor + 45, **kw), SL, TP)


print("=" * 100)
print("K-bis. WALK-FORWARD — the anchor is chosen ONLY from past data, then traded forward")
print("=" * 100)
cache = {a: trades_for(a).assign(anchor=a) for a in ANCHORS}
allt = pd.concat(cache.values()).sort_values("t_entry")
dates = np.array(sorted(allt.date.unique()))
print(f"anchors scanned: {len(ANCHORS)}   candidate trade-dates across all anchors: {len(dates)}")

folds, oos = [], []
n_tr = int(len(dates) * 0.40)
step = int(len(dates) * 0.15)
i = n_tr
while i < len(dates):
    tr_end = dates[i - 1]; te_end = dates[min(i + step, len(dates)) - 1]
    best, bexp = None, -1e9
    for a, d in cache.items():
        s = E.stats(d[d.date <= tr_end].pnl.tolist())
        if s["n"] >= 8 and s["exp"] > bexp:
            best, bexp = a, s["exp"]
    if best is None:
        i += step; continue
    d = cache[best]
    te = d[(d.date > tr_end) & (d.date <= te_end)]
    s = E.stats(te.pnl.tolist())
    folds.append(dict(train_to=tr_end, test_to=te_end, picked=f"{best//60:02d}:{best%60:02d}",
                      train_exp=bexp, n=s["n"], pf=s["pf"], exp=s["exp"], net=s["net"]))
    oos += te.pnl.tolist()
    i += step
F = pd.DataFrame(folds)
print(F.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
S = E.stats(oos)
print(f"\nPOOLED OUT-OF-SAMPLE: n={S['n']}  PF={S['pf']:.2f}  exp={S['exp']:+.2f}  "
      f"net={S['net']:+.1f}  maxDD={S['mdd']:.1f}")
print(f"anchors picked across folds: {F.picked.tolist()}")
print(f"distinct anchors picked: {F.picked.nunique()} of {len(F)} folds "
      f"-- a stable edge should keep picking the same one")
fx = pd.concat([cache[18*60+45][(cache[18*60+45].date > F.iloc[0].train_to)]])
sf = E.stats(fx.pnl.tolist())
print(f"FIXED 18:45 over the same post-train period: n={sf['n']}  PF={sf['pf']:.2f}  exp={sf['exp']:+.2f}")
F.to_csv("research/microq3/results/K_walkforward.csv", index=False)

print("\n" + "=" * 100)
print("VOLATILITY-ADAPTIVE COMPRESSION vs the FIXED $6.25 CAP")
print("=" * 100)


def ratios(anchor=18 * 60 + 45):
    """body / normaliser, for several normalisers. Flags the leaky one."""
    out = []
    for day in E.DAYS:
        day = int(day)
        a = E.candle(day, anchor, anchor + 15, "mid")
        if a is None or a["nmin"] < 5:
            continue
        o, c = a["o"] / PTS, a["c"] / PTS
        if c >= o:
            continue
        body = o - c
        causal = E.candle(day, 18 * 60, 19 * 60, "mid")           # complete at 19:00
        leaky = E.candle(day, 18 * 60, 19 * 60 + 30, "mid")       # NOT complete until 19:30
        prev = E.candle(day - 1, 18 * 60, 23 * 60 + 59, "mid")
        out.append(dict(day=day, body=body,
                        q1_causal=(causal["h"] - causal["l"]) / PTS if causal else np.nan,
                        q1_leaky=(leaky["h"] - leaky["l"]) / PTS if leaky else np.nan,
                        anchor_rng=(a["h"] - a["l"]) / PTS,
                        prev_rng=(prev["h"] - prev["l"]) / PTS if prev else np.nan))
    return pd.DataFrame(out)


R = ratios()
base_days = {t["day"] for t in M.signals()}
print(f"bearish anchor days: {len(R)}")
for nm in ("q1_causal", "q1_leaky", "anchor_rng", "prev_rng"):
    R[f"r_{nm}"] = R.body / R[nm]
print(R[[c for c in R.columns if c.startswith('r_')]].describe().loc[
    ["mean", "25%", "50%", "75%", "max"]].to_string(float_format=lambda v: f"{v:,.3f}"))

allc = M.signals(body_min=0, body_max=None)
AD = M.apply(allc, SL, TP)
AD = AD.merge(R.assign(date=[pd.Timestamp(d * 86400000, unit="ms").date() for d in R.day]),
              on="date", how="left")
print(f"\nunfiltered bearish-anchor trades: {len(AD)}   net {AD.pnl.sum():+.1f}")
print(f"\n{'filter':<42}{'n':>5}{'PF':>9}{'exp':>9}{'net':>9}{'maxDD':>9}")


def show(tag, m):
    s = E.stats(AD[m].pnl.tolist())
    print(f"{tag:<42}{s['n']:>5}{s['pf']:>9.2f}{s['exp']:>9.2f}{s['net']:>9.1f}{s['mdd']:>9.1f}")


show("FIXED  body in [1.00, 6.25]", (AD.anchor_body >= 1) & (AD.anchor_body <= 6.25))
for f in (0.20, 0.25, 0.30, 0.35, 0.40, 0.50):
    show(f"ADAPT  body <= {f:.0%} of causal Q1 (18:00-19:00)",
         (AD.anchor_body >= 1) & (AD.r_q1_causal <= f))
for f in (0.25, 0.35, 0.50):
    show(f"LEAKY  body <= {f:.0%} of Q1 18:00-19:30  [look-ahead]",
         (AD.anchor_body >= 1) & (AD.r_q1_leaky <= f))
for f in (0.30, 0.40, 0.50):
    show(f"ADAPT  body <= {f:.0%} of prior session range",
         (AD.anchor_body >= 1) & (AD.r_prev_rng <= f))
