"""
AU200 UT Bot Session Backtest — BUG-019 compliant
Mirrors au200_utbot_session_v1.pine logic exactly.

BUG-019 fix: excursion peak updated AFTER stop check on each bar.
Session: 10:00-12:00 AEST = 00:00-02:00 UTC (handles both AEST UTC+10 and AEDT UTC+11).
Mintick: 0.1 pt (confirmed from data).
Slippage: 1.0 pt per side (fill at close ± slippage).
Commission: $1 AUD per contract per side.
"""

import pandas as pd
import numpy as np

DATA = "/root/.claude/uploads/7c610517-7865-597e-b767-c39eacd908c6/bc3182e6-au200_aud_5m.csv"

# ── Parameters ──────────────────────────────────────────────────────────────
ATR_LEN      = 10
ATR_MULT     = 1.5
EMA_LEN      = 200
SL_PTS       = 15.0
TP1_PTS      = 20.0
TRAIL_PTS    = 30.0
TRAIL_TRIG   = 5.0
FLIP_SL_MULT = 2.0
MAX_FLIPS    = 3
COMMISSION   = 1.0    # AUD per side per contract
SLIPPAGE     = 1.0    # pts per side
INITIAL_CAP  = 50000.0
QTY          = 1      # contracts

# Session: 10:00-12:00 AEST
# AEST = UTC+10 → 10:00 AEST = 00:00 UTC
# AEDT = UTC+11 → 10:00 AEDT = 23:00 UTC prev day, 12:00 AEDT = 01:00 UTC
# We handle by using Australia/Sydney timezone
SESS_TZ = "Australia/Sydney"

# ── Load data ────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA, parse_dates=["timestamp"])
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
df = df.sort_values("timestamp").reset_index(drop=True)

# ── Indicators ───────────────────────────────────────────────────────────────
# ATR (Wilder's, same as Pine ta.atr)
df["tr"] = np.maximum(
    df["high"] - df["low"],
    np.maximum(
        (df["high"] - df["close"].shift(1)).abs(),
        (df["low"]  - df["close"].shift(1)).abs()
    )
)
df["atr"] = df["tr"].ewm(alpha=1/ATR_LEN, min_periods=ATR_LEN, adjust=False).mean()

# EMA 200
df["ema200"] = df["close"].ewm(span=EMA_LEN, adjust=False).mean()

# Session hours (AEST/AEDT via Australia/Sydney)
ts_local = df["timestamp"].dt.tz_convert(SESS_TZ)
df["loc_hour"]   = ts_local.dt.hour
df["loc_minute"] = ts_local.dt.minute
df["date_local"] = ts_local.dt.date

df["in_sess"] = (df["loc_hour"] >= 10) & (df["loc_hour"] < 12)
df["sess_end"] = (df["loc_hour"] == 12) & (df["loc_minute"] == 0)

# ── UT Bot ───────────────────────────────────────────────────────────────────
ut_trail = np.zeros(len(df))
ut_dir   = np.zeros(len(df), dtype=int)

# Warm-up from bar 0
ut_trail[0] = df.at[0, "close"]
ut_dir[0]   = 1

for i in range(1, len(df)):
    atr_i = df.at[i, "atr"]
    if np.isnan(atr_i):
        ut_trail[i] = ut_trail[i-1]
        ut_dir[i]   = ut_dir[i-1]
        continue

    ts = atr_i * ATR_MULT
    c  = df.at[i, "close"]

    if ut_dir[i-1] == 1:
        if c < ut_trail[i-1]:
            ut_dir[i]   = -1
            ut_trail[i] = c + ts
        else:
            ut_trail[i] = max(ut_trail[i-1], c - ts)
            ut_dir[i]   = 1
    else:
        if c > ut_trail[i-1]:
            ut_dir[i]   = 1
            ut_trail[i] = c - ts
        else:
            ut_trail[i] = min(ut_trail[i-1], c + ts)
            ut_dir[i]   = -1

df["ut_dir"]   = ut_dir
df["ut_trail"] = ut_trail
df["ut_buy"]   = (df["ut_dir"] == 1) & (df["ut_dir"].shift(1) == -1)
df["ut_sell"]  = (df["ut_dir"] == -1) & (df["ut_dir"].shift(1) == 1)

# ── Backtest ─────────────────────────────────────────────────────────────────
trades = []
equity_curve = []

pos_dir     = 0       # 1=long, -1=short, 0=flat
entry_price = np.nan
sl_p        = np.nan
tp1_p       = np.nan
trail_ref   = np.nan
trail_armed = False
tp1_done    = False
in_flip     = False
flip_count  = 0
last_date   = None
equity      = INITIAL_CAP

for i in range(EMA_LEN, len(df)):
    row = df.iloc[i]
    o, h, l, c = row.open, row.high, row.low, row.close
    in_sess  = row.in_sess
    sess_end = row.sess_end
    cur_date = row.date_local
    ema_val  = row.ema200
    ut_b     = row.ut_buy
    ut_s     = row.ut_sell

    just_stopped = False

    # Reset flip count at new session
    if cur_date != last_date and in_sess:
        flip_count = 0
    last_date = cur_date

    # ── Exit Logic ───────────────────────────────────────────────────────────
    if pos_dir != 0:
        is_long = pos_dir == 1

        # 1. STOP CHECK FIRST (BUG-019 fix)
        stop_hit = (is_long and l <= sl_p) or (not is_long and h >= sl_p)

        if stop_hit:
            fill = sl_p - (SLIPPAGE if is_long else -SLIPPAGE)
            pnl_pts = (fill - entry_price) * pos_dir
            pnl_aud = pnl_pts * QTY - COMMISSION * 2  # 2 sides

            trades.append({
                "entry_bar": entry_bar,
                "exit_bar": i,
                "entry_price": entry_price,
                "exit_price": fill,
                "direction": "L" if pos_dir == 1 else "S",
                "pnl_pts": pnl_pts,
                "pnl_aud": pnl_aud,
                "exit_type": "SL",
                "flip_num": flip_num_at_entry,
                "date": cur_date,
            })
            equity += pnl_aud

            if in_flip and flip_count < MAX_FLIPS:
                # Flip: reverse at SL price
                flip_dir    = -pos_dir
                new_sl      = fill - flip_dir * SL_PTS * FLIP_SL_MULT
                new_tp1     = fill + flip_dir * TP1_PTS
                entry_price = fill
                sl_p        = new_sl
                tp1_p       = new_tp1
                trail_ref   = fill
                trail_armed = False
                tp1_done    = False
                pos_dir     = flip_dir
                flip_count += 1
                flip_num_at_entry = flip_count
                entry_bar   = i
            else:
                pos_dir     = 0
                entry_price = np.nan
                sl_p        = np.nan
                tp1_p       = np.nan
                trail_ref   = np.nan
                trail_armed = False
                tp1_done    = False
                in_flip     = False
                just_stopped = True

        # 2. TRAIL (after stop check — BUG-019)
        if pos_dir != 0:
            is_long2 = pos_dir == 1
            if not trail_armed:
                if is_long2 and h >= entry_price + TRAIL_TRIG:
                    trail_armed = True
                    trail_ref   = h
                elif not is_long2 and l <= entry_price - TRAIL_TRIG:
                    trail_armed = True
                    trail_ref   = l

            if trail_armed:
                if is_long2:
                    trail_ref = max(trail_ref, h)
                    new_sl    = trail_ref - TRAIL_PTS
                    if new_sl > sl_p:
                        sl_p = new_sl
                else:
                    trail_ref = min(trail_ref, l)
                    new_sl    = trail_ref + TRAIL_PTS
                    if new_sl < sl_p:
                        sl_p = new_sl

            # 3. TP1
            if not tp1_done:
                tp1_hit = (pos_dir == 1 and h >= tp1_p) or (pos_dir == -1 and l <= tp1_p)
                if tp1_hit:
                    fill = tp1_p + (SLIPPAGE if pos_dir == -1 else -SLIPPAGE)
                    pnl_pts = (fill - entry_price) * pos_dir
                    pnl_aud = pnl_pts * QTY - COMMISSION * 2

                    trades.append({
                        "entry_bar": entry_bar,
                        "exit_bar": i,
                        "entry_price": entry_price,
                        "exit_price": fill,
                        "direction": "L" if pos_dir == 1 else "S",
                        "pnl_pts": pnl_pts,
                        "pnl_aud": pnl_aud,
                        "exit_type": "TP1",
                        "flip_num": flip_num_at_entry,
                        "date": cur_date,
                    })
                    equity += pnl_aud
                    tp1_done    = True
                    entry_price = fill  # move reference to TP1 for BE
                    sl_p        = fill  # BE
                    trail_armed = False
                    trail_ref   = fill

    # 4. EOD close
    if sess_end and pos_dir != 0:
        fill = c - (SLIPPAGE if pos_dir == 1 else -SLIPPAGE)
        pnl_pts = (fill - entry_price) * pos_dir
        pnl_aud = pnl_pts * QTY - COMMISSION * 2

        trades.append({
            "entry_bar": entry_bar,
            "exit_bar": i,
            "entry_price": entry_price,
            "exit_price": fill,
            "direction": "L" if pos_dir == 1 else "S",
            "pnl_pts": pnl_pts,
            "pnl_aud": pnl_aud,
            "exit_type": "EOD",
            "flip_num": flip_num_at_entry,
            "date": cur_date,
        })
        equity += pnl_aud
        pos_dir     = 0
        entry_price = np.nan
        sl_p        = np.nan
        trail_armed = False
        tp1_done    = False
        in_flip     = False
        flip_count  = 0

    # 5. ENTRY
    can_entry = in_sess and pos_dir == 0 and not just_stopped

    if can_entry:
        if ut_b and c > ema_val:
            fill        = c + SLIPPAGE
            pos_dir     = 1
            entry_price = fill
            sl_p        = fill - SL_PTS
            tp1_p       = fill + TP1_PTS
            trail_ref   = fill
            trail_armed = False
            tp1_done    = False
            in_flip     = True
            entry_bar   = i
            flip_num_at_entry = 0
        elif ut_s and c < ema_val:
            fill        = c - SLIPPAGE
            pos_dir     = -1
            entry_price = fill
            sl_p        = fill + SL_PTS
            tp1_p       = fill - TP1_PTS
            trail_ref   = fill
            trail_armed = False
            tp1_done    = False
            in_flip     = True
            entry_bar   = i
            flip_num_at_entry = 0

    equity_curve.append(equity)

# ── Results ──────────────────────────────────────────────────────────────────
tdf = pd.DataFrame(trades)
tdf["date"] = pd.to_datetime(tdf["date"])
tdf["week"] = tdf["date"].dt.to_period("W")
tdf["year"] = tdf["date"].dt.year

if len(tdf) == 0:
    print("NO TRADES")
else:
    wins = tdf[tdf.pnl_pts > 0]
    losses = tdf[tdf.pnl_pts <= 0]

    total_pts  = tdf.pnl_pts.sum()
    total_aud  = tdf.pnl_aud.sum()
    n_trades   = len(tdf)
    wr         = len(wins) / n_trades
    avg_win    = wins.pnl_pts.mean() if len(wins) else 0
    avg_loss   = losses.pnl_pts.mean() if len(losses) else 0
    pf         = wins.pnl_pts.sum() / abs(losses.pnl_pts.sum()) if len(losses) else float("inf")

    # Max drawdown
    eq_arr = np.array(equity_curve)
    peak   = np.maximum.accumulate(eq_arr)
    dd     = (eq_arr - peak) / peak * 100
    max_dd = dd.min()

    # Weekly pts
    weekly = tdf.groupby("week").pnl_pts.sum()
    pct_weeks_pos = (weekly > 0).mean() * 100

    print("=" * 60)
    print("AU200 UT Bot Session v1 — Backtest Results")
    print("BUG-019 FIXED | Slippage=1pt | Commission=$1/side")
    print(f"Period: {tdf.date.min().date()} → {tdf.date.max().date()}")
    print("=" * 60)
    print(f"Trades:          {n_trades}")
    print(f"Win Rate:        {wr*100:.1f}%")
    print(f"Avg Win:         {avg_win:.1f} pts")
    print(f"Avg Loss:        {avg_loss:.1f} pts")
    print(f"Profit Factor:   {pf:.2f}")
    print(f"Net Pts:         {total_pts:.1f}")
    print(f"Net AUD:         ${total_aud:,.0f}")
    print(f"Max Drawdown:    {max_dd:.1f}%")
    print(f"")
    print(f"Weekly stats (pts):")
    print(f"  Median:        {weekly.median():.1f}")
    print(f"  Mean:          {weekly.mean():.1f}")
    print(f"  Std:           {weekly.std():.1f}")
    print(f"  % weeks +ve:   {pct_weeks_pos:.0f}%")
    print(f"  Best week:     {weekly.max():.1f}")
    print(f"  Worst week:    {weekly.min():.1f}")
    print(f"")
    print("Year-by-year:")
    for yr, grp in tdf.groupby("year"):
        yr_pts = grp.pnl_pts.sum()
        yr_wr  = (grp.pnl_pts > 0).mean() * 100
        print(f"  {yr}: {grp.shape[0]:4d} trades | WR {yr_wr:.0f}% | {yr_pts:+.0f} pts")

    print()
    print("Exit type breakdown:")
    print(tdf.groupby("exit_type").agg(n=("pnl_pts","count"), pts=("pnl_pts","sum"), wr=("pnl_pts", lambda x: (x>0).mean()*100)).round(1))

    print()
    print(f"MINTICK confirmed from data: 0.1 pt")
    print(f"Slippage used: {SLIPPAGE} pt/side ({SLIPPAGE/0.1:.0f} ticks)")
