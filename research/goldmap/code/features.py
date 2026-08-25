"""Parts 4, 7, 8, 19, 22 — causal features. EVERY value uses PAST DATA ONLY.

Each feature is computed as a rolling statistic over the PRIOR occurrences of
the same structural slot, then shifted by one so the current event never sees
itself. Percentiles are ranks inside that trailing window. Nothing here uses a
full-year ranking, which is the leak Part 3 warns about.
"""
import numpy as np, pandas as pd

E = pd.read_parquet("research/goldmap/results/events_resolved.parquet")
E = E.sort_values(["year", "t_entry"]).reset_index(drop=True)
E["dt"] = pd.to_datetime(E.t_entry, unit="ms")


def trail_pct(df, value, by, window):
    """Percentile of `value` within the prior `window` observations of the same
    `by` slot. Strictly causal: the current row is excluded."""
    out = np.full(len(df), np.nan)
    for _, idx in df.groupby(by, observed=True).groups.items():
        idx = np.array(sorted(idx))
        v = df.loc[idx, value].to_numpy()
        for i in range(len(v)):
            lo = max(0, i - window)
            prior = v[lo:i]
            if len(prior) >= max(10, window // 4):
                out[idx[i]] = (prior < v[i]).mean()
    return out


def trail_med(df, value, by, window):
    out = np.full(len(df), np.nan)
    for _, idx in df.groupby(by, observed=True).groups.items():
        idx = np.array(sorted(idx))
        v = df.loc[idx, value].to_numpy()
        for i in range(len(v)):
            lo = max(0, i - window)
            prior = v[lo:i]
            if len(prior) >= max(10, window // 4):
                out[idx[i]] = np.median(prior)
    return out


print("building causal features ...", flush=True)
frames = []
for yr, d in E.groupby("year"):
    d = d.reset_index(drop=True)

    # --- daily ATR proxy from PRIOR days only ---
    day_rng = d.groupby("date").agg(hi=("anchor_h", "max"), lo=("anchor_l", "min"))
    day_rng["r"] = day_rng.hi - day_rng.lo
    atr = day_rng.r.rolling(14, min_periods=5).median().shift(1)
    d["atr"] = d.date.map(atr)

    # --- compression, normalised and as a trailing percentile of its own slot ---
    d["comp_atr"] = d.anchor_rng / d.atr
    for w in (20, 40, 60):
        d[f"comp_p{w}"] = trail_pct(d, "anchor_rng", "q_open_s", w)

    # --- activity: anchor tick count against its own slot's recent history ---
    for w in (20, 40, 60):
        d[f"act_p{w}"] = trail_pct(d, "anchor_ticks", "q_open_s", w)
    # --- execution quality: spread against the same slot's trailing median ---
    d["spread_med_slot"] = trail_med(d, "spread", "q_open_s", 40)
    d["spread_rel"] = d.spread / d.spread_med_slot
    d["spread_p40"] = trail_pct(d, "spread", "q_open_s", 40)

    # --- True Opens, all strictly in the past at signal time ---
    d["s_open"] = d.q_open_s
    tdo = d[d.q_open_s == 18 * 3600].set_index("date").anchor_o          # 18:00 NY open
    dts = sorted(d.date.unique())
    tdo_map, last = {}, np.nan
    for dd in dts:
        tdo_map[dd] = last
        if dd in tdo.index:
            last = float(tdo.loc[dd]) if np.isscalar(tdo.loc[dd]) else float(tdo.loc[dd].iloc[0])
    d["true_daily_open"] = d.date.map(tdo_map)
    d["dist_tdo"] = (d.entry - d.true_daily_open)
    d["dist_tdo_atr"] = d.dist_tdo / d.atr
    d["above_tdo"] = (d.dist_tdo > 0).astype(float)
    d["with_tdo"] = np.where(d.long, d.above_tdo, 1 - d.above_tdo)       # trading away from TDO

    # --- price location inside the anchor, and anchor shape ---
    d["loc_in_anchor"] = (d.entry - d.anchor_l) / (d.anchor_rng.replace(0, np.nan))
    d["body_ratio"] = d.anchor_body / d.anchor_rng.replace(0, np.nan)

    # --- how fast the break came ---
    d["speed"] = d.sig_min_in
    frames.append(d)

F = pd.concat(frames, ignore_index=True)
F.to_parquet("research/goldmap/results/events_features.parquet", index=False)
print(f"wrote events_features.parquet  rows={len(F):,}")
cov = {c: f"{100*F[c].notna().mean():.0f}%" for c in
       ("atr", "comp_p40", "act_p40", "spread_rel", "dist_tdo_atr", "loc_in_anchor")}
print("feature coverage:", cov)
