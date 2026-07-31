"""
Key-level construction, ported from key_levels_spaceman_edition.pine.

NON-LOOKAHEAD IS THE WHOLE POINT HERE. Every level is derived only from
periods that had already CLOSED when the bar being evaluated opened. The
Pine original uses request.security(..., lookahead=barmerge.lookahead_on)
with a [1] offset, which is the safe idiom; this reproduces that offset
explicitly with .shift(1) so there is no way for future data to leak in.

Level ids match the Pine sigIds so the two implementations can be compared
row for row.
"""
import pandas as pd

LEVEL_NAMES = [
    "DO", "PDH", "PDL",            # 0,1,2   daily
    "WO", "PWH", "PWL",            # 3,4,5   weekly
    "MO", "PMH", "PML",            # 6,7,8   monthly
    "H4O", "P4HH", "P4HL",         # 9,10,11 4-hour
    "MONH", "MONL",                # 12,13   Monday range
    "LONH", "LONL",                # 14,15   London range
    "NYH", "NYL",                  # 16,17   NY range
]

# The Pine module exports 36 levels, not 18: every range also contributes
# its MIDPOINT, and it carries quarterly and yearly periods too. Measuring
# against the 18 understated how DENSE the drawn grid actually is -- the
# nearest level ahead of an entry is roughly half as far away on the chart
# as it was in the first test, which is why the first live run cut its
# winners far earlier than the research said it would. build(dense=True)
# reproduces the chart's real density.
MID_PAIRS = [("PDM", "PDH", "PDL"), ("PWM", "PWH", "PWL"),
             ("PMM", "PMH", "PML"), ("P4HM", "P4HH", "P4HL"),
             ("MONM", "MONH", "MONL"), ("LONM", "LONH", "LONL"),
             ("NYM", "NYH", "NYL"), ("PQM", "PQH", "PQL"),
             ("CYM", "CYH", "CYL")]
DENSE_NAMES = LEVEL_NAMES + [
    "QO", "PQH", "PQL",            # quarterly
    "YO", "CYH", "CYL",            # yearly
] + [m[0] for m in MID_PAIRS]

OHLC = {"open": "first", "high": "max", "low": "min", "close": "last"}


def _period_levels(df, key, open_col, prev_hi, prev_lo):
    """Aggregate by a period key; current-period open + PREVIOUS period H/L."""
    g = df.groupby(key).agg(OHLC)
    prev = g.shift(1)
    out = pd.DataFrame(index=df.index)
    out[open_col] = g["open"].reindex(key).values
    out[prev_hi] = prev["high"].reindex(key).values
    out[prev_lo] = prev["low"].reindex(key).values
    return out


def _session_running(df, start, end, hi_col, lo_col):
    """Running high/low inside a session window; NaN outside it.

    Running -- not final -- so there is no lookahead: at any bar it is the
    extreme SO FAR, exactly what the Pine version tracks bar by bar.
    """
    t = df.index.time
    s, e = pd.to_datetime(start).time(), pd.to_datetime(end).time()
    mask = (t >= s) & (t < e) if s < e else ((t >= s) | (t < e))
    out = pd.DataFrame(index=df.index, columns=[hi_col, lo_col], dtype=float)
    day = df.index.normalize()
    grp = day.where(mask)
    inside = df[mask]
    if len(inside):
        gk = inside.index.normalize()
        out.loc[mask, hi_col] = inside.groupby(gk)["high"].cummax().values
        out.loc[mask, lo_col] = inside.groupby(gk)["low"].cummin().values
    return out


def build(df, london=("08:00", "12:00"), ny=("13:30", "16:30"), dense=False):
    """df: DatetimeIndex, columns open/high/low/close. Returns level frame."""
    df = df.sort_index()
    idx = df.index
    lv = pd.DataFrame(index=idx)

    lv = lv.join(_period_levels(df, idx.normalize(), "DO", "PDH", "PDL"))
    lv = lv.join(_period_levels(df, idx.to_period("W"), "WO", "PWH", "PWL"))
    lv = lv.join(_period_levels(df, idx.to_period("M"), "MO", "PMH", "PML"))
    lv = lv.join(_period_levels(df, idx.floor("4h"), "H4O", "P4HH", "P4HL"))

    # Monday range: the completed Monday, usable from Tuesday onward.
    # The Pine version reads it via request.security on the CURRENT day,
    # which can see Monday's finished high while Monday is still running --
    # a real lookahead the port deliberately does not reproduce.
    wk = idx.to_period("W")
    mon = df[idx.dayofweek == 0]
    if len(mon):
        mh = mon.groupby(mon.index.to_period("W"))["high"].max()
        ml = mon.groupby(mon.index.to_period("W"))["low"].min()
        lv["MONH"] = mh.reindex(wk).values
        lv["MONL"] = ml.reindex(wk).values
        lv.loc[idx.dayofweek == 0, ["MONH", "MONL"]] = float("nan")
    else:
        lv["MONH"] = lv["MONL"] = float("nan")

    lv = lv.join(_session_running(df, london[0], london[1], "LONH", "LONL"))
    lv = lv.join(_session_running(df, ny[0], ny[1], "NYH", "NYL"))
    if not dense:
        return lv[LEVEL_NAMES]
    lv = lv.join(_period_levels(df, idx.to_period("Q"), "QO", "PQH", "PQL"))
    lv = lv.join(_period_levels(df, idx.to_period("Y"), "YO", "CYH", "CYL"))
    for name, hi, lo in MID_PAIRS:
        lv[name] = (lv[hi] + lv[lo]) / 2
    return lv[DENSE_NAMES]
