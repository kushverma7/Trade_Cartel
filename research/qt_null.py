"""
The null the Quarterly Theory anatomy numbers have to beat.

The corrected run produced large-looking z-scores: sweeping the high in Q3 is
followed by a reversal only 25% of the time (z = -16). That LOOKS like strong
structure. It is almost certainly geometry.

  If a cycle sets its extreme in a LATE quarter, the cycle closes near that
  extreme simply because there is little time left to move away from it. If it
  sets the extreme EARLY, there is a whole cycle left in which to reverse. So
  "reversal rate falls as the sweep quarter gets later" is what a driftless
  random walk does. It is not a claim about accumulation or manipulation.

This file measures exactly that. The bar-to-bar returns are shuffled -- which
destroys every real time-of-day, day-of-week and autocorrelation structure while
preserving the return distribution and the quarter geometry exactly -- and the
same statistics are recomputed. Whatever the surrogate reproduces was never
evidence for the theory.
"""
import numpy as np, pandas as pd

from backtest.io import load_csv
from research.qt_corrected import to_local, label, anatomy, reversal

SEED = 20260805


def surrogate(df, rng):
    """Shuffle log returns, rebuild OHLC around the new close path.

    The intrabar shape (high/low relative to the close) is carried along with
    its own bar so bar ranges stay realistic; only the ORDER of bars changes.
    """
    c = df["close"].to_numpy(float)
    r = np.diff(np.log(c), prepend=np.log(c[0]))
    hr = np.log(df["high"].to_numpy(float) / c)
    lr = np.log(df["low"].to_numpy(float) / c)
    orr = np.log(df["open"].to_numpy(float) / c)
    p = rng.permutation(len(r))
    nc = np.exp(np.log(c[0]) + np.cumsum(r[p]))
    return pd.DataFrame({"open": nc * np.exp(orr[p]), "high": nc * np.exp(hr[p]),
                         "low": nc * np.exp(lr[p]), "close": nc}, index=df.index)


def profile(d_df, loc, tz, name):
    q, cyc = label(d_df, loc, name, tz)
    res = anatomy(d_df, q, cyc, name)
    if res is None:
        return {}
    tab, d = res
    out = {f"Q{int(r.q)}_high": r.sets_high for _, r in tab.iterrows()}
    for sq in (2, 3):
        for row in reversal(d, sq, name, tz):
            out[f"sweep{sq}_{row['swept']}"] = row["reverse_close"]
    return out


def main(n_surr=20):
    raw = load_csv("data/xauusd_15m.csv.gz")
    loc = to_local(raw.index, "ny")
    rng = np.random.default_rng(SEED)

    for name in ("daily", "weekly", "session"):
        real = profile(raw, loc, "ny", name)
        sims = [profile(surrogate(raw, rng), loc, "ny", name) for _ in range(n_surr)]
        print(f"\n{'='*84}\n{name} cycle -- real vs {n_surr} return-shuffled surrogates\n{'='*84}")
        print(f"  {'stat':<18} {'real':>8} {'surr mean':>10} {'surr sd':>8} {'z':>7}   verdict")
        for k in real:
            v = np.array([s[k] for s in sims if k in s], float)
            if len(v) < 5:
                continue
            mu, sd = v.mean(), v.std(ddof=1)
            z = (real[k] - mu) / sd if sd > 0 else np.nan
            tag = "REAL STRUCTURE" if abs(z) > 3 else "explained by geometry"
            print(f"  {k:<18} {real[k]:8.3f} {mu:10.3f} {sd:8.3f} {z:+7.2f}   {tag}")


if __name__ == "__main__":
    main()
