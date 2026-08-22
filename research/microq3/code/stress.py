"""Execution stress and block bootstrap. The strategy is frozen; only the
assumptions about how orders actually fill are varied.

DELAY. The specification enters at the first tick after the signal candle
closes. Real execution has latency and a decision lag. Entry is pushed forward
by a fixed wall-clock delay and re-filled at whatever the market was then.

SLIPPAGE. Applied where it really occurs: a stop is a market order and slips
against you; a take-profit is a resting limit and does not slip in your favour.
Both legs are charged, so the test is deliberately pessimistic on the stop and
neutral on the target.

BLOCK BOOTSTRAP. Trades are resampled in contiguous blocks so that runs of good
and bad market conditions survive the resampling, instead of the iid bootstrap's
implicit assumption that every trade is independent of its neighbours.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/microq3/code")
import engine as E
import microq3 as M
from engine import PTS

SL, TP = 15.5, 25.5
pd.set_option("display.width", 240)
BASE = M.signals()
d0 = M.apply(BASE, SL, TP)
S0 = E.stats(d0.pnl.tolist())
print(f"frozen baseline: n={S0['n']}  PF={S0['pf']:.2f}  exp={S0['exp']:+.2f}  "
      f"net={S0['net']:+.1f}  maxDD={S0['mdd']:.1f}\n")


def with_delay(delay_s, slip_stop=0.0, limit_tp=True):
    """Re-fill every trade `delay_s` seconds later and re-resolve on real quotes."""
    pnl = []
    for t in BASE:
        k0 = int(np.searchsorted(E.NY, t["t_entry"] + int(delay_s * 1000), "left"))
        if k0 >= t["kend"]:
            continue
        r = E.resolve(k0, t["kend"], t["long"], SL, TP)
        if r is None:
            continue
        v = r["pnl"]
        if r["reason"] == "SL":
            v -= slip_stop                       # market stop slips against you
        elif r["reason"] == "TP" and limit_tp:
            v -= (v - TP)                        # resting limit fills AT the target
        pnl.append(v)
    return E.stats(pnl)


print("=" * 104)
print("EXECUTION STRESS — entry delayed, stop slipped, target filled as a resting limit")
print("=" * 104)
print(f"  {'assumption':<44}{'n':>5}{'PF':>9}{'exp':>9}{'net':>9}{'maxDD':>9}")
rows = []
for dl in (0, 1, 5, 15, 30, 60, 120, 300):
    for sp in (0.0, 0.5, 1.0):
        if dl not in (0, 5, 30, 120) and sp != 0.0:
            continue
        s = with_delay(dl, sp)
        tag = f"delay {dl:>3}s" + (f", stop slip ${sp:g}" if sp else "")
        rows.append(dict(delay_s=dl, slip=sp, **{k: s[k] for k in ("n", "pf", "exp", "net", "mdd")}))
        print(f"  {tag:<44}{s['n']:>5}{s['pf']:>9.2f}{s['exp']:>9.2f}{s['net']:>9.1f}{s['mdd']:>9.1f}")
pd.DataFrame(rows).to_csv("research/microq3/results/T_stress.csv", index=False)
base_r = [r for r in rows if r["delay_s"] == 0 and r["slip"] == 0][0]
worst = min(rows, key=lambda r: r["exp"])
print(f"\n  realistic-fill baseline (0s, limit TP): PF {base_r['pf']:.2f}, exp {base_r['exp']:+.2f}")
print(f"  harshest cell tested: delay {worst['delay_s']}s slip ${worst['slip']:g} -> "
      f"PF {worst['pf']:.2f}, exp {worst['exp']:+.2f}")

print("\n" + "=" * 104)
print("BLOCK BOOTSTRAP — contiguous blocks, so runs of conditions survive resampling")
print("=" * 104)
p = d0.pnl.to_numpy(); n = len(p)
rng = np.random.default_rng(11)


def mdd(x):
    eq = np.cumsum(x); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
    return float((pk - eq).max())


def streak(x):
    b = m = 0
    for v in x:
        b = b + 1 if v <= 0 else 0; m = max(m, b)
    return m


print(f"  {'block size':<14}{'':<4}" + "".join(s.rjust(11) for s in ("p5", "p10", "median", "p90", "p95", "p99")))
for L in (1, 3, 5, 8):
    nb = int(np.ceil(n / L))
    DD, ST, NET = [], [], []
    for _ in range(20000):
        st = rng.integers(0, n, nb)
        idx = np.concatenate([np.arange(s, s + L) % n for s in st])[:n]
        x = p[idx]
        NET.append(x.sum())
        if len(DD) < 8000:
            DD.append(mdd(x)); ST.append(streak(x))
    DD, ST, NET = np.array(DD), np.array(ST), np.array(NET)
    q = lambda a: [np.percentile(a, x) for x in (5, 10, 50, 90, 95, 99)]
    print(f"  L={L:<12}{'maxDD':<4}" + "".join(f"{v:>11.1f}" for v in q(DD)))
    print(f"  {'':<14}{'net':<4}" + "".join(f"{v:>11.1f}" for v in q(NET)))
    print(f"  {'':<14}{'strk':<4}" + "".join(f"{v:>11.0f}" for v in q(ST)))
    print(f"  {'':<14}     P(net<=0) = {(NET<=0).mean():.4f}")
print(f"\n  realised maxDD {S0['mdd']:.1f} and realised losing streak 1, against these distributions.")
