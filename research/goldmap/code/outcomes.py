"""Part 28/29 — resolve every all-day event on raw ticks, once, into a compact
form from which any exit rule can be scored exactly.

FILL CONVENTION, as specified:
  long enters at the ASK and is marked out on the BID; short enters at the BID
  and is marked out on the ASK.
  TAKE PROFIT is a resting limit: it fills AT the target. Favourable overshoot
  is NOT credited -- a fill beyond the level is booked at the level.
  STOP is market-triggered: it fills at the real next executable quote, so the
  recorded loss is whatever the book actually showed, including slippage.

Rather than storing tick paths, each event stores the FIRST-PASSAGE TIME to a
ladder of favourable and adverse levels, plus the true slipped fill at each
adverse level. Any (stop, target) pair drawn from the ladder then resolves
exactly by comparing two times, and any structural time exit resolves from the
stored mark-to-market series. Nothing is re-simulated later.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/goldmap/code")
from qt_engine import Book, PTS, qt_labels

LV = np.array([3, 5, 7.5, 10, 12.5, 15, 17.5, 20, 25, 30, 40, 50])
HORIZON_S = 6 * 3600
TIME_EXITS = dict(mq=1350, q90=5400, q90_next=10800, dailyq=21600,
                  h2=7200, h4=14400, h6=21600)


def resolve_all(book, ev):
    n = len(ev); L_i = (LV * PTS).astype(np.int64)
    out = {f"t_up_{i}": np.full(n, np.inf) for i in range(len(LV))}
    out.update({f"t_dn_{i}": np.full(n, np.inf) for i in range(len(LV))})
    out.update({f"fill_dn_{i}": np.full(n, np.nan) for i in range(len(LV))})
    out.update({f"pnl_{k}": np.full(n, np.nan) for k in TIME_EXITS})
    out["mfe"] = np.zeros(n); out["mae"] = np.zeros(n); out["n_ticks"] = np.zeros(n, int)

    for r, (k0, long_, t0) in enumerate(zip(ev.k0.to_numpy(), ev.long.to_numpy(),
                                            ev.t_entry.to_numpy())):
        k1 = int(np.searchsorted(book.ny, t0 + HORIZON_S * 1000, "right"))
        k1 = min(k1, len(book.ny))
        if k1 - k0 < 5:
            continue
        e = int(book.ask[k0]) if long_ else int(book.bid[k0])
        ex = book.bid[k0:k1] if long_ else book.ask[k0:k1]
        fav = (ex.astype(np.int64) - e) if long_ else (e - ex.astype(np.int64))
        tms = book.ny[k0:k1]
        rmax = np.maximum.accumulate(fav); rmin = np.minimum.accumulate(fav)
        m = len(fav)
        out["mfe"][r] = rmax[-1] / PTS; out["mae"][r] = rmin[-1] / PTS
        out["n_ticks"][r] = m
        for i, lv in enumerate(L_i):
            j = int(np.searchsorted(rmax, lv, "left"))
            if j < m:
                out[f"t_up_{i}"][r] = (int(tms[j]) - t0) / 1000.0
            j = int(np.searchsorted(-rmin, lv, "left"))
            if j < m:
                out[f"t_dn_{i}"][r] = (int(tms[j]) - t0) / 1000.0
                out[f"fill_dn_{i}"][r] = fav[j] / PTS          # the real slipped fill
        s_entry = (t0 % 86_400_000) // 1000
        for k, sec in TIME_EXITS.items():
            if k in ("mq", "q90", "q90_next", "dailyq"):
                span = {"mq": 1350, "q90": 5400, "q90_next": 5400, "dailyq": 21600}[k]
                nxt = (int(s_entry) // span + 1) * span
                if k == "q90_next":
                    nxt += 5400
                dt_s = nxt - s_entry
            else:
                dt_s = sec
            j = int(np.searchsorted(tms, t0 + dt_s * 1000, "left"))
            out[f"pnl_{k}"][r] = fav[min(j, m - 1)] / PTS
    return pd.DataFrame(out, index=ev.index)


def score(df, sl, tp):
    """Exact P&L for one (stop, target) pair from the stored ladder."""
    i_tp = int(np.where(LV == tp)[0][0]); i_sl = int(np.where(LV == sl)[0][0])
    tu = df[f"t_up_{i_tp}"].to_numpy(); td = df[f"t_dn_{i_sl}"].to_numpy()
    fill = df[f"fill_dn_{i_sl}"].to_numpy()
    eod = df["pnl_h6"].to_numpy()
    pnl = np.where(tu < td, tp, np.where(np.isfinite(td), fill, eod))
    why = np.where(tu < td, "TP", np.where(np.isfinite(td), "SL", "TIME"))
    return pnl, why


if __name__ == "__main__":
    import time
    E = pd.read_parquet("research/goldmap/results/events_allday.parquet")
    parts = []
    for dd, yr in (("research/microq3/data_holdout", "2024-25"),
                   ("research/microq3/data", "2025-26")):
        t0 = time.time()
        b = Book(dd, yr)
        sub = E[E.year == yr].copy()
        res = resolve_all(b, sub)
        parts.append(pd.concat([sub, res], axis=1))
        print(f"{yr}: resolved {len(sub):,} events ({time.time()-t0:.0f}s)", flush=True)
    R = pd.concat(parts, ignore_index=True)
    R.to_parquet("research/goldmap/results/events_resolved.parquet", index=False)
    print(f"\nwrote events_resolved.parquet  rows={len(R):,}")

    print("\n" + "=" * 96)
    print("PART 5 BASELINE — the all-day setup, NO filters, unoptimised symmetric exits")
    print("=" * 96)
    print(f"  {'exit':<14}{'n':>7}{'WR':>8}{'PF':>8}{'exp':>9}{'net':>10}{'maxDD':>9}{'TP%':>7}{'SL%':>7}{'TIME%':>7}")
    for sl, tp in ((10, 10), (15, 15), (20, 20), (25, 25), (15, 25), (20, 30), (25, 40)):
        p, w = score(R, sl, tp)
        ok = np.isfinite(p)
        p2 = p[ok]
        eq = np.cumsum(p2); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
        pf = p2[p2 > 0].sum() / -p2[p2 < 0].sum() if (p2 < 0).any() else np.inf
        print(f"  SL{sl:>3}/TP{tp:<6}{len(p2):>7}{100*(p2>0).mean():>7.1f}%{pf:>8.3f}"
              f"{p2.mean():>9.3f}{p2.sum():>10.1f}{float((pk-eq).max()):>9.1f}"
              f"{100*(w[ok]=='TP').mean():>6.0f}%{100*(w[ok]=='SL').mean():>6.0f}%"
              f"{100*(w[ok]=='TIME').mean():>6.0f}%")
