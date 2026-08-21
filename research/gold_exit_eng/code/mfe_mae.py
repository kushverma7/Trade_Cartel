"""How far does each printed signal actually run, for and against?

For every signal the indicator prints, this walks the real tick stream from the
entry quote to the end of the session and records:

  MFE  maximum favourable excursion, in points, measured on the side you would
       actually EXIT on -- a long is marked out on the BID, a short on the ASK.
       This is the best exit the trade ever offered.
  MAE  maximum adverse excursion, same convention. This is the deepest the
       trade ever went against you.

Both are measured with NO stop and NO target, because a stop truncates the very
distribution you are trying to see: a trade stopped at -15 can never reveal that
it would have run +40.

The ordering matters as much as the magnitudes. A trade with MFE 30 and MAE 20
is only a winner if the 30 came FIRST, so the script also records MFE-BEFORE-
STOP for each candidate stop distance: the best excursion available while the
trade was still alive. That is what actually determines a workable target.

Signals measured are the FIRST of each kind per day -- the one the strategy can
actually take, given the per-day latch.
"""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "code")

PTS = 1000.0
prep = pickle.load(open("data/prep10.pkl", "rb"))
class TK:
    t = np.load("data/tk_t.npy"); bid = np.load("data/tk_bid.npy"); ask = np.load("data/tk_ask.npy")


def first_signals(day):
    """-> list of (kind, long_, bar_index). First of each kind for the day."""
    side, bhi, blo = day["side"], day["bhi"], day["blo"]
    c = day["c"]
    up = c > bhi
    dn = c < blo
    kL, kS = ("A_L", "F_S") if side == 1 else ("F_L", "A_S")
    out = []
    iu = int(np.argmax(up)) if up.any() else -1
    idn = int(np.argmax(dn)) if dn.any() else -1
    if iu >= 0:
        out.append((kL, True, iu))
    if idn >= 0:
        out.append((kS, False, idn))
    return out


rows = []
for day in prep:
    for kind, long_, i in first_signals(day):
        te = int(day["t_close"][i])
        e = int(day["ask_c"][i] if long_ else day["bid_c"][i])
        i0, j0 = day["i0"], day["j0"]
        k0 = i0 + int(np.searchsorted(TK.t[i0:j0], te, side="right"))
        if k0 >= j0:
            continue
        ex = TK.bid[k0:j0] if long_ else TK.ask[k0:j0]
        tt = TK.t[k0:j0]
        if len(ex) == 0:
            continue
        fav = (ex - e) if long_ else (e - ex)          # signed, in points*1000
        run_fav = np.maximum.accumulate(fav)
        mfe = int(run_fav[-1])
        mae = int(-np.minimum.accumulate(fav)[-1])
        i_mfe = int(np.argmax(fav))
        i_mae = int(np.argmin(fav))
        rows.append(dict(date=day["date"], kind=kind, side="long" if long_ else "short",
                         entry=e / PTS, mfe=mfe / PTS, mae=mae / PTS,
                         min_to_mfe=(int(tt[i_mfe]) - te) / 60000.0,
                         min_to_mae=(int(tt[i_mae]) - te) / 60000.0,
                         mfe_first=bool(i_mfe < i_mae),
                         eod_pnl=int(fav[-1]) / PTS,
                         _k0=k0, _j0=j0, _e=e, _long=long_))
D = pd.DataFrame(rows)
D.drop(columns=[c for c in D.columns if c.startswith("_")]).to_csv("results/mfe_mae.csv", index=False)

pd.set_option("display.width", 220)
PC = [10, 25, 50, 60, 70, 75, 80, 90, 95]
print(f"signals measured: {len(D)}  (first of each kind per day, {len(prep)} days)\n")
print("="*100)
print("MAXIMUM FAVOURABLE EXCURSION (points) — how far it ran FOR the signal")
print("="*100)
print(f"{'leg':<7}{'n':>5}{'mean':>8}", "".join(f"{'p'+str(p):>8}" for p in PC), f"{'max':>9}")
for k in ["A_L","A_S","F_L","F_S"]:
    g = D[D.kind==k]["mfe"]
    if len(g)==0: continue
    print(f"{k:<7}{len(g):>5}{g.mean():>8.2f}", "".join(f"{np.percentile(g,p):>8.2f}" for p in PC), f"{g.max():>9.2f}")
for lbl, sel in [("A both", D.kind.isin(["A_L","A_S"])), ("Flip both", D.kind.isin(["F_L","F_S"]))]:
    g = D[sel]["mfe"]
    print(f"{lbl:<7}{len(g):>5}{g.mean():>8.2f}", "".join(f"{np.percentile(g,p):>8.2f}" for p in PC), f"{g.max():>9.2f}")

print("\n" + "="*100)
print("MAXIMUM ADVERSE EXCURSION (points) — how far it ran AGAINST the signal")
print("="*100)
print(f"{'leg':<7}{'n':>5}{'mean':>8}", "".join(f"{'p'+str(p):>8}" for p in PC), f"{'max':>9}")
for k in ["A_L","A_S","F_L","F_S"]:
    g = D[D.kind==k]["mae"]
    if len(g)==0: continue
    print(f"{k:<7}{len(g):>5}{g.mean():>8.2f}", "".join(f"{np.percentile(g,p):>8.2f}" for p in PC), f"{g.max():>9.2f}")
for lbl, sel in [("A both", D.kind.isin(["A_L","A_S"])), ("Flip both", D.kind.isin(["F_L","F_S"]))]:
    g = D[sel]["mae"]
    print(f"{lbl:<7}{len(g):>5}{g.mean():>8.2f}", "".join(f"{np.percentile(g,p):>8.2f}" for p in PC), f"{g.max():>9.2f}")

print("\n" + "="*100)
print("TIMING AND ORDER")
print("="*100)
for k in ["A_L","A_S","F_L","F_S"]:
    g = D[D.kind==k]
    if len(g)==0: continue
    print(f"  {k}: MFE came before MAE on {100*g.mfe_first.mean():5.1f}% of signals | "
          f"median min-to-MFE {g.min_to_mfe.median():6.0f} | median min-to-MAE {g.min_to_mae.median():6.0f} | "
          f"mean EOD P&L {g.eod_pnl.mean():+6.2f}")
np.save("results/_mfe_idx.npy", np.array([1]))
pickle.dump(rows, open("data/mfe_rows.pkl","wb"))
