"""
ES1 CLC System — Local Python Backtest
Uses SPY (5-min bars via yfinance) as ES1 proxy.
Implements: Supertrend context + VWAP bias + Sweep detection + CVD + Aggression

Install: pip install yfinance pandas numpy matplotlib
Run    : python es1_local_backtest.py
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, time as dtime

# ── CONFIG ─────────────────────────────────────────────────────────────────
SYMBOL         = "SPY"          # ES1 proxy (use "MES=F" or "ES=F" if you have futures data)
START          = "2019-01-01"
END            = "2026-06-12"
INTERVAL       = "5m"           # yfinance max 60 days per request for 5m — chunked below
INITIAL_CASH   = 100_000.0
COMMISSION_PCT = 0.0005         # 0.05% per side
SLIPPAGE_TICKS = 0.05           # $0.05 slippage per share

# Session: 09:30–11:30 NY
SESSION_START  = dtime(9, 30)
SESSION_END    = dtime(11, 30)

# CLC params
ST_MULT        = 3.0
ST_PERIOD      = 14
SWEEP_LOOKBACK = 20
SWEEP_BODY_PCT = 0.30
CVD_LENGTH     = 14
AGG_MULT       = 2.0
AGG_BODY_PCT   = 0.30
LOSS_ZONE_PTS  = 0.50           # SPY points proximity for 3-loss rule

# Risk
ATR_SL_MULT    = 1.5
TP1_R          = 1.0
TP1_PCT        = 0.60           # close 60% at TP1
DAILY_LOSS_R   = -2.0


# ── DATA FETCH (chunked — yfinance 5m limit = 60 days per call) ────────────
def fetch_data(symbol: str, start: str, end: str) -> pd.DataFrame:
    print(f"Fetching {symbol} 5m data {start} → {end} (chunked)...")
    all_chunks = []
    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    chunk_size = pd.Timedelta(days=55)

    while s < e:
        chunk_end = min(s + chunk_size, e)
        try:
            df = yf.download(symbol, start=s.strftime("%Y-%m-%d"),
                             end=chunk_end.strftime("%Y-%m-%d"),
                             interval="5m", progress=False, auto_adjust=True)
            if not df.empty:
                all_chunks.append(df)
                print(f"  {s.date()} → {chunk_end.date()}: {len(df)} bars")
        except Exception as ex:
            print(f"  Chunk error {s.date()}: {ex}")
        s = chunk_end

    if not all_chunks:
        raise RuntimeError("No data fetched. Check ticker and date range.")

    data = pd.concat(all_chunks)
    data = data[~data.index.duplicated(keep="first")].sort_index()
    data.columns = [c.lower() for c in data.columns]
    data.index = pd.to_datetime(data.index)
    if data.index.tz is None:
        data.index = data.index.tz_localize("UTC")
    data.index = data.index.tz_convert("America/New_York")
    print(f"Total bars: {len(data)}")
    return data


# ── INDICATORS ─────────────────────────────────────────────────────────────
def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False).mean()


def supertrend(df: pd.DataFrame, mult: float = 3.0, period: int = 14):
    atr_val = atr(df, period)
    hl2 = (df["high"] + df["low"]) / 2
    upper = hl2 + mult * atr_val
    lower = hl2 - mult * atr_val

    st    = pd.Series(np.nan, index=df.index)
    bull  = pd.Series(False, index=df.index)
    final_upper = upper.copy()
    final_lower = lower.copy()

    for i in range(1, len(df)):
        final_upper.iloc[i] = upper.iloc[i] if upper.iloc[i] < final_upper.iloc[i-1] or df["close"].iloc[i-1] > final_upper.iloc[i-1] else final_upper.iloc[i-1]
        final_lower.iloc[i] = lower.iloc[i] if lower.iloc[i] > final_lower.iloc[i-1] or df["close"].iloc[i-1] < final_lower.iloc[i-1] else final_lower.iloc[i-1]

        if st.iloc[i-1] == final_upper.iloc[i-1]:
            st.iloc[i] = final_lower.iloc[i] if df["close"].iloc[i] > final_upper.iloc[i] else final_upper.iloc[i]
        else:
            st.iloc[i] = final_upper.iloc[i] if df["close"].iloc[i] < final_lower.iloc[i] else final_lower.iloc[i]

        bull.iloc[i] = df["close"].iloc[i] > st.iloc[i]

    return bull


def session_vwap(df: pd.DataFrame):
    tp  = (df["high"] + df["low"] + df["close"]) / 3
    date = df.index.date
    pv  = (tp * df["volume"]).groupby(date).cumsum()
    v   = df["volume"].groupby(date).cumsum()
    pv2 = (tp**2 * df["volume"]).groupby(date).cumsum()
    vwap = pv / v
    var  = (pv2 / v - vwap**2).clip(lower=0)
    sd   = np.sqrt(var)
    return vwap, sd


def cvd(df: pd.DataFrame, length: int = 14) -> tuple[pd.Series, pd.Series]:
    rng = (df["high"] - df["low"]).replace(0, np.nan)
    buy_frac = (df["close"] - df["low"]) / rng
    buy_frac = buy_frac.fillna(0.5).clip(0, 1)
    delta = df["volume"] * buy_frac - df["volume"] * (1 - buy_frac)
    date  = df.index.date
    cvd_cum = delta.groupby(date).cumsum()
    cvd_sma = cvd_cum.ewm(span=length, adjust=False).mean()
    cvd_rising  = cvd_sma > cvd_sma.shift(length)
    cvd_falling = cvd_sma < cvd_sma.shift(length)
    avg_delta   = delta.abs().rolling(20).mean()
    delta_bull  = (delta.abs() > avg_delta * 2.5) & (delta > 0)
    delta_bear  = (delta.abs() > avg_delta * 2.5) & (delta < 0)
    return cvd_rising, cvd_falling, delta_bull, delta_bear


# ── MAIN BACKTEST ──────────────────────────────────────────────────────────
def run_backtest(df: pd.DataFrame) -> dict:
    print("Computing indicators...")

    atr14      = atr(df, 14)
    st_bull    = supertrend(df, ST_MULT, ST_PERIOD)
    st_bear    = ~st_bull
    vwap, vsd  = session_vwap(df)
    vwap_u1    = vwap + 1.0 * vsd
    vwap_l1    = vwap - 1.0 * vsd
    vwap_u2    = vwap + 2.0 * vsd
    vwap_l2    = vwap - 2.0 * vsd

    cvd_up, cvd_dn, d_bull, d_bear = cvd(df, CVD_LENGTH)

    # Session mask
    t = df.index.time
    in_sess = (t >= SESSION_START) & (t <= SESSION_END)

    # Aggression
    avg_vol   = df["volume"].rolling(20).mean()
    vol_spike = df["volume"] > avg_vol * AGG_MULT
    rng       = df["high"] - df["low"]
    body      = (df["close"] - df["open"]).abs()
    body_pct  = (body / rng.replace(0, np.nan)).fillna(0)
    bull_agg  = vol_spike & (body_pct >= AGG_BODY_PCT) & (df["close"] > df["open"]) & in_sess
    bear_agg  = vol_spike & (body_pct >= AGG_BODY_PCT) & (df["close"] < df["open"]) & in_sess

    # Sweep
    ph = df["high"].rolling(SWEEP_LOOKBACK).max().shift(1)
    pl = df["low"].rolling(SWEEP_LOOKBACK).min().shift(1)
    sweep_low  = (df["low"] < pl) & (df["close"] > pl) & (body_pct >= SWEEP_BODY_PCT)
    sweep_high = (df["high"] > ph) & (df["close"] < ph) & (body_pct >= SWEEP_BODY_PCT)

    # CLC pillars
    ctx_long   = st_bull
    ctx_short  = st_bear
    loc_long   = sweep_low  | (df["close"] <= vwap_l1 + atr14 * 0.3)
    loc_short  = sweep_high | (df["close"] >= vwap_u1 - atr14 * 0.3)
    conf_long  = (cvd_up  | d_bull) & (bull_agg | sweep_low)
    conf_short = (cvd_dn  | d_bear) & (bear_agg | sweep_high)

    long_pts  = ctx_long.astype(int)  + loc_long.astype(int)  + conf_long.astype(int)
    short_pts = ctx_short.astype(int) + loc_short.astype(int) + conf_short.astype(int)

    a_long  = (long_pts  == 3) & in_sess
    b_long  = (long_pts  == 2) & in_sess & loc_long  & conf_long
    a_short = (short_pts == 3) & in_sess
    b_short = (short_pts == 2) & in_sess & loc_short & conf_short

    signal_long  = a_long  | b_long
    signal_short = a_short | b_short

    print(f"Total A/B long signals : {signal_long.sum()}")
    print(f"Total A/B short signals: {signal_short.sum()}")

    # ── Trade simulation ───────────────────────────────────────────────────
    equity        = INITIAL_CASH
    position      = 0       # shares
    entry_price   = 0.0
    stop_price    = 0.0
    tp1_price     = 0.0
    tp1_done      = False
    trade_dir     = 0
    daily_pnl_r   = 0.0
    daily_r_count = 0
    last_trade_date = None
    loss_level    = 0.0
    loss_count_l  = 0
    loss_count_s  = 0

    trades = []
    equity_curve = [equity]
    equity_dates = [df.index[0]]

    shares_per_trade = lambda price: max(1, int(equity * 0.02 / (atr14.loc[df.index[i]] * ATR_SL_MULT * price + 1e-9)))

    for i in range(len(df)):
        idx   = df.index[i]
        bar   = df.iloc[i]
        atr_v = float(atr14.iloc[i])
        close = float(bar["close"])
        high  = float(bar["high"])
        low   = float(bar["low"])

        # Daily reset
        cur_date = idx.date()
        if cur_date != last_trade_date:
            daily_pnl_r   = 0.0
            daily_r_count = 0
            last_trade_date = cur_date

        # Manage open trade
        if position != 0:
            risk = abs(entry_price - stop_price)
            tp1  = entry_price + risk * TP1_R * trade_dir

            # Stop hit
            if trade_dir == 1 and low <= stop_price:
                pnl = (stop_price - entry_price - SLIPPAGE_TICKS) * position
                pnl -= abs(pnl) * COMMISSION_PCT * 2
                equity += pnl
                r = -1.0 if not tp1_done else 0.0
                daily_pnl_r += r
                trades.append({"date": idx, "dir": "LONG", "entry": entry_price,
                                "exit": stop_price, "pnl": pnl, "r": r, "grade": "SL"})
                position = 0
            elif trade_dir == -1 and high >= stop_price:
                pnl = (entry_price - stop_price - SLIPPAGE_TICKS) * abs(position)
                pnl -= abs(pnl) * COMMISSION_PCT * 2
                equity += pnl
                r = -1.0 if not tp1_done else 0.0
                daily_pnl_r += r
                trades.append({"date": idx, "dir": "SHORT", "entry": entry_price,
                                "exit": stop_price, "pnl": pnl, "r": r, "grade": "SL"})
                position = 0
            # TP1 hit
            elif not tp1_done:
                if (trade_dir == 1 and high >= tp1) or (trade_dir == -1 and low <= tp1):
                    close_qty = max(1, int(abs(position) * TP1_PCT))
                    pnl_partial = abs(tp1 - entry_price) * close_qty
                    pnl_partial -= pnl_partial * COMMISSION_PCT * 2
                    equity += pnl_partial
                    position = (abs(position) - close_qty) * trade_dir
                    stop_price = entry_price  # BE
                    tp1_done   = True
                    daily_pnl_r += 0.6
                    trades.append({"date": idx, "dir": "LONG" if trade_dir==1 else "SHORT",
                                   "entry": entry_price, "exit": tp1,
                                   "pnl": pnl_partial, "r": 0.6, "grade": "TP1"})
            # VWAP 2SD exit
            elif trade_dir == 1 and high >= float(vwap_u2.iloc[i]):
                exit_p = float(vwap_u2.iloc[i])
                pnl = (exit_p - entry_price - SLIPPAGE_TICKS) * abs(position)
                pnl -= pnl * COMMISSION_PCT * 2
                equity += pnl
                r = (exit_p - entry_price) / risk if risk > 0 else 0
                daily_pnl_r += r
                trades.append({"date": idx, "dir": "LONG", "entry": entry_price,
                                "exit": exit_p, "pnl": pnl, "r": r, "grade": "2SD"})
                position = 0
            elif trade_dir == -1 and low <= float(vwap_l2.iloc[i]):
                exit_p = float(vwap_l2.iloc[i])
                pnl = (entry_price - exit_p - SLIPPAGE_TICKS) * abs(position)
                pnl -= pnl * COMMISSION_PCT * 2
                equity += pnl
                r = (entry_price - exit_p) / risk if risk > 0 else 0
                daily_pnl_r += r
                trades.append({"date": idx, "dir": "SHORT", "entry": entry_price,
                                "exit": exit_p, "pnl": pnl, "r": r, "grade": "2SD"})
                position = 0

        # New entry
        if position == 0 and daily_pnl_r > DAILY_LOSS_R:
            # 3-loss rule check
            def near(level): return abs(close - level) <= LOSS_ZONE_PTS

            if signal_long.iloc[i]:
                if near(loss_level): loss_count_l += 1
                else:
                    loss_level = close; loss_count_l = 1
                if loss_count_l < 3:
                    sl = low - atr_v * 0.1
                    qty = shares_per_trade(close)
                    cost = close * qty * (1 + COMMISSION_PCT) + SLIPPAGE_TICKS * qty
                    if cost <= equity:
                        entry_price = close + SLIPPAGE_TICKS
                        stop_price  = sl
                        tp1_price   = entry_price + (entry_price - sl) * TP1_R
                        position    = qty
                        trade_dir   = 1
                        tp1_done    = False
                        equity     -= cost

            elif signal_short.iloc[i]:
                if near(loss_level): loss_count_s += 1
                else:
                    loss_level = close; loss_count_s = 1
                if loss_count_s < 3:
                    sl = high + atr_v * 0.1
                    qty = shares_per_trade(close)
                    rev = close * qty * (1 - COMMISSION_PCT) - SLIPPAGE_TICKS * qty
                    entry_price = close - SLIPPAGE_TICKS
                    stop_price  = sl
                    tp1_price   = entry_price - (sl - entry_price) * TP1_R
                    position    = -qty
                    trade_dir   = -1
                    tp1_done    = False

        equity_curve.append(equity)
        equity_dates.append(idx)

    # Force close any open position
    if position != 0:
        last_close = float(df["close"].iloc[-1])
        pnl = (last_close - entry_price) * position if position > 0 else (entry_price - last_close) * abs(position)
        equity += pnl
        equity_curve[-1] = equity

    return {
        "trades":       pd.DataFrame(trades),
        "equity_curve": pd.Series(equity_curve, index=equity_dates),
        "final_equity": equity,
        "signals_long": signal_long.sum(),
        "signals_short":signal_short.sum(),
    }


# ── STATS ──────────────────────────────────────────────────────────────────
def print_stats(result: dict):
    trades = result["trades"]
    eq     = result["equity_curve"]

    if trades.empty:
        print("No trades executed.")
        return

    total_trades = len(trades[trades["grade"] != "TP1"])
    wins  = trades[trades["pnl"] > 0]
    loss  = trades[trades["pnl"] <= 0]
    wr    = len(wins) / max(len(trades), 1) * 100
    net   = result["final_equity"] - INITIAL_CASH
    ret_pct = net / INITIAL_CASH * 100

    # Drawdown
    peak   = eq.cummax()
    dd     = (eq - peak) / peak * 100
    max_dd = dd.min()

    # Sharpe (annualised daily)
    daily_ret = eq.resample("D").last().pct_change().dropna()
    sharpe    = (daily_ret.mean() / daily_ret.std() * np.sqrt(252)) if daily_ret.std() > 0 else 0

    # Profit factor
    gross_profit = wins["pnl"].sum() if not wins.empty else 0
    gross_loss   = abs(loss["pnl"].sum()) if not loss.empty else 1
    pf = gross_profit / gross_loss if gross_loss > 0 else 0

    avg_win  = wins["pnl"].mean()  if not wins.empty else 0
    avg_loss = loss["pnl"].mean()  if not loss.empty else 0
    expectancy = trades["pnl"].mean()

    print("\n" + "="*55)
    print(f"  ES1 CLC SYSTEM BACKTEST — {SYMBOL} 5m 2019→2026")
    print("="*55)
    print(f"  Initial Capital    : ${INITIAL_CASH:>12,.2f}")
    print(f"  Final Equity       : ${result['final_equity']:>12,.2f}")
    print(f"  Net Profit         : ${net:>12,.2f}  ({ret_pct:+.1f}%)")
    print(f"  Max Drawdown       : {max_dd:.2f}%")
    print(f"  Sharpe Ratio       : {sharpe:.2f}")
    print(f"  Profit Factor      : {pf:.2f}")
    print("-"*55)
    print(f"  Total Trades       : {len(trades)}")
    print(f"  Win Rate           : {wr:.1f}%")
    print(f"  Avg Win            : ${avg_win:,.2f}")
    print(f"  Avg Loss           : ${avg_loss:,.2f}")
    print(f"  Expectancy/Trade   : ${expectancy:,.2f}")
    print(f"  Long Signals       : {result['signals_long']}")
    print(f"  Short Signals      : {result['signals_short']}")
    print("="*55)

    # By year
    if not trades.empty:
        trades["year"] = pd.to_datetime(trades["date"]).dt.year
        print("\n  By Year:")
        print(f"  {'Year':>6} {'Trades':>7} {'WR%':>6} {'PnL':>10}")
        for yr, g in trades.groupby("year"):
            yr_wr  = (g["pnl"] > 0).mean() * 100
            yr_pnl = g["pnl"].sum()
            print(f"  {yr:>6} {len(g):>7} {yr_wr:>5.1f}% ${yr_pnl:>9,.0f}")


# ── PLOT ───────────────────────────────────────────────────────────────────
def plot_results(result: dict):
    trades = result["trades"]
    eq     = result["equity_curve"]

    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    fig.suptitle(f"ES1 CLC System — {SYMBOL} 5m | 2019–2026", fontsize=13, color="white")
    fig.patch.set_facecolor("#0D1117")

    for ax in axes:
        ax.set_facecolor("#161B22")
        ax.tick_params(colors="gray")
        ax.spines["bottom"].set_color("#30363D")
        ax.spines["top"].set_color("#30363D")
        ax.spines["left"].set_color("#30363D")
        ax.spines["right"].set_color("#30363D")

    # Equity curve
    ax1 = axes[0]
    ax1.plot(eq.index, eq.values, color="#00E676", linewidth=1.5, label="Equity")
    ax1.fill_between(eq.index, INITIAL_CASH, eq.values,
                     where=eq.values >= INITIAL_CASH, alpha=0.15, color="#00E676")
    ax1.fill_between(eq.index, INITIAL_CASH, eq.values,
                     where=eq.values < INITIAL_CASH, alpha=0.15, color="#FF1744")
    ax1.axhline(INITIAL_CASH, color="#FFD700", linewidth=0.8, linestyle="--", alpha=0.5)
    ax1.set_ylabel("Equity ($)", color="gray")
    ax1.set_title("Equity Curve", color="#8B949E", fontsize=10)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax1.legend(facecolor="#0D1117", labelcolor="white", fontsize=8)

    # Drawdown
    ax2 = axes[1]
    peak = eq.cummax()
    dd   = (eq - peak) / peak * 100
    ax2.fill_between(dd.index, 0, dd.values, color="#FF1744", alpha=0.6)
    ax2.set_ylabel("Drawdown %", color="gray")
    ax2.set_title("Drawdown", color="#8B949E", fontsize=10)
    ax2.set_ylim(min(dd.min() * 1.2, -1), 1)

    plt.tight_layout()
    plt.savefig("es1_clc_backtest_results.png", dpi=150, bbox_inches="tight",
                facecolor="#0D1117")
    print("\nChart saved → es1_clc_backtest_results.png")
    plt.show()


# ── ENTRY POINT ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df     = fetch_data(SYMBOL, START, END)
    result = run_backtest(df)
    print_stats(result)
    plot_results(result)

    # Save trades CSV
    if not result["trades"].empty:
        result["trades"].to_csv("es1_clc_trades.csv", index=False)
        print("Trades saved → es1_clc_trades.csv")
