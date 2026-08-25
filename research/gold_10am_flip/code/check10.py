import sys, time, numpy as np, pandas as pd
sys.path.insert(0,"code")
from engine import Ticks, build_days, run, stats
from fastsim import prepare, simulate

bars = pd.read_parquet("data/bars_5m_melbourne.parquet")
raw = np.load("data/session_ticks.npy")
class TK:
    t = np.ascontiguousarray(raw[:,0]); bid = np.ascontiguousarray(raw[:,1]); ask = np.ascontiguousarray(raw[:,2])
    @staticmethod
    def slice_from(t0, t1):
        return (int(np.searchsorted(TK.t, t0, side="right")),
                int(np.searchsorted(TK.t, t1, side="right")))
del raw
print(f"ticks in memory: {len(TK.t):,}")

# ANCHOR = the 10:00 candle itself: line open AND body come from the same bar.
days = build_days(bars, line_hhmm=1000, body_hhmm=1000)
ok = sum(1 for v in days.values() if v["ok"])
print(f"constructible days (10:00 anchor): {ok} of {len(days)}")

t0=time.time(); prep = prepare(bars, days, TK); print(f"prepared {len(prep)} days in {time.time()-t0:.1f}s")
t0=time.time(); a = simulate(prep, TK, 18, 40, True, True, True); print(f"sim {time.time()-t0:.2f}s")
b = run(bars, TK, sl_pts=18, tp_pts=40, days=days, use_A=True, a_short_only=True, use_flip=True)
sa, sb = stats(a,"fast"), stats(b,"ref")
print(f"  fast: n={sa['n']} net={sa['net']:.3f}")
print(f"  ref : n={sb['n']} net={sb['net']:.3f}")
print("  MATCH — fast path validated" if (sa['n']==sb['n'] and abs(sa['net']-sb['net'])<1e-9) else "  *** MISMATCH ***")
np.save("data/tk_t.npy", TK.t); np.save("data/tk_bid.npy", TK.bid); np.save("data/tk_ask.npy", TK.ask)
import pickle; pickle.dump(prep, open("data/prep10.pkl","wb"))
print("cached prep10.pkl")
