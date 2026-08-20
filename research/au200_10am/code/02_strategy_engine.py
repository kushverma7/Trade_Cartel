"""
AU200 10AM Strategy Engine — full trade reconstruction.

Pine Script logic (process_orders_on_close=true):
  dOpen  = open  of the 09:50 Melbourne 5-min bar
  bHi    = max(open, close) of the 10:00 Melbourne 5-min bar
  bLo    = min(open, close) of the 10:00 Melbourne 5-min bar
  side   = +1 if 10:00 close > dOpen else -1

  A Short : side == -1  → entry=bLo,  SL=bHi+17, TP=bLo-39
  A Long  : side == +1  → entry=bHi,  SL=bLo-17, TP=bHi+39
  Flip Long  (triggered after A Short hits SL): entry=bHi+17, SL=bLo-17, TP=(bHi+17)+39
  Flip Short (triggered after A Long  hits SL): entry=bLo-17, SL=bHi+17, TP=(bLo-17)-39

process_orders_on_close=true means the entry/exit prices are exact (no slippage assumed here).

Outputs:
  results/baseline/trades_all.csv          — every trade row
  results/baseline/summary.json            — aggregate stats per branch + combined
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import time as dtime

PROC_DIR    = Path("/home/user/Trade_Cartel/research/au200_10am/data/processed")
RES_DIR     = Path("/home/user/Trade_Cartel/research/au200_10am/results")
BASE_DIR    = RES_DIR / "baseline"
BASE_DIR.mkdir(parents=True, exist_ok=True)

SL_PTS = 17.0
TP_PTS = 39.0

# ─── Load data ────────────────────────────────────────────────────────────────

def load_data():
    import pytz
    mel_tz = pytz.timezone("Australia/Melbourne")

    def read_mel_csv(path):
        df = pd.read_csv(path, index_col=0)
        # Parse with utc=True to handle mixed AEST/AEDT offsets, then convert to Melbourne
        df.index = pd.to_datetime(df.index, utc=True).tz_convert(mel_tz)
        return df

    df5 = read_mel_csv(PROC_DIR / "au200_5m_melbourne.csv.gz")
    df1 = read_mel_csv(PROC_DIR / "au200_1m_melbourne.csv.gz")
    return df5, df1


# ─── Session extraction ────────────────────────────────────────────────────────

T0950 = dtime(9, 50)
T1000 = dtime(10, 0)

def extract_sessions(df5: pd.DataFrame):
    """Extract all sessions where both 09:50 and 10:00 bars exist."""
    df5 = df5.copy()
    df5['bar_time'] = df5.index.time
    df5['date']     = df5.index.date

    rows_0950 = df5[df5['bar_time'] == T0950][['date','open','high','low','close']].copy()
    rows_0950.columns = ['date','o0950','h0950','l0950','c0950']
    rows_0950 = rows_0950.set_index('date')

    rows_1000 = df5[df5['bar_time'] == T1000][['date','open','high','low','close']].copy()
    rows_1000.columns = ['date','o1000','h1000','l1000','c1000']
    rows_1000 = rows_1000.set_index('date')

    sess = rows_0950.join(rows_1000, how='inner')
    sess = sess.dropna()
    sess['dOpen'] = sess['o0950']
    sess['bHi']   = sess[['o1000','c1000']].max(axis=1)
    sess['bLo']   = sess[['o1000','c1000']].min(axis=1)
    sess['side']  = np.where(sess['c1000'] > sess['dOpen'], 1, -1)

    # Exact entry prices per branch
    sess['entry_ashort']    = sess['bLo']
    sess['sl_ashort']       = sess['bHi'] + SL_PTS
    sess['tp_ashort']       = sess['bLo'] - TP_PTS

    sess['entry_along']     = sess['bHi']
    sess['sl_along']        = sess['bLo'] - SL_PTS
    sess['tp_along']        = sess['bHi'] + TP_PTS

    # Flip entries (triggered at the SL level of primary trade)
    sess['entry_fliplong']  = sess['bHi'] + SL_PTS   # = sl_ashort
    sess['sl_fliplong']     = sess['bLo'] - SL_PTS
    sess['tp_fliplong']     = sess['entry_fliplong'] + TP_PTS

    sess['entry_flipshort'] = sess['bLo'] - SL_PTS   # = sl_along
    sess['sl_flipshort']    = sess['bHi'] + SL_PTS
    sess['tp_flipshort']    = sess['entry_flipshort'] - TP_PTS

    return sess


# ─── Forward path resolution ──────────────────────────────────────────────────

def resolve_trade_on_1m(date, entry_price, sl_price, tp_price, direction,
                         df1: pd.DataFrame, is_stop_entry=False, max_bars=180):
    """
    Walk 1-minute bars forward from 10:05 (after 10:00 5-min bar closes).
    direction: +1 = long, -1 = short
    is_stop_entry: if True, wait for price to reach entry_price first
    Returns dict or None (if stop entry never triggered).
    """
    day_bars = df1[df1.index.date == date]
    active_bars = day_bars[day_bars.index.time >= dtime(10, 5)]
    active_bars = active_bars.head(max_bars)

    if active_bars.empty:
        return None

    mfe = 0.0
    mae = 0.0
    entry_triggered = not is_stop_entry  # market entry: already in from bar 0
    bars_to_entry   = 0  # 0 = entered immediately

    for i, (ts, row) in enumerate(active_bars.iterrows()):
        hi = row['high']
        lo = row['low']

        if not entry_triggered:
            # Check if stop entry level reached this bar
            if direction == 1 and hi >= entry_price:
                entry_triggered = True
                bars_to_entry = i + 1
            elif direction == -1 and lo <= entry_price:
                entry_triggered = True
                bars_to_entry = i + 1
            else:
                continue  # not yet entered

        # Trade is active — track excursions and check TP/SL
        if direction == 1:
            fav = hi - entry_price
            adv = entry_price - lo
            tp_hit = hi >= tp_price
            sl_hit = lo <= sl_price
        else:
            fav = entry_price - lo
            adv = hi - entry_price
            tp_hit = lo <= tp_price
            sl_hit = hi >= sl_price

        mfe = max(mfe, fav)
        mae = max(mae, adv)

        if tp_hit and sl_hit:
            # Both in same bar — assume SL hit first (conservative)
            exit_price = sl_price
            pnl = (sl_price - entry_price) * direction
            return dict(outcome='SL', exit_price=exit_price, exit_bar=str(ts),
                        bars_held=i+1, bars_to_entry=bars_to_entry, pnl=pnl, mfe=mfe, mae=mae)

        if tp_hit:
            exit_price = tp_price
            pnl = (tp_price - entry_price) * direction
            return dict(outcome='TP', exit_price=exit_price, exit_bar=str(ts),
                        bars_held=i+1, bars_to_entry=bars_to_entry, pnl=pnl, mfe=mfe, mae=mae)

        if sl_hit:
            exit_price = sl_price
            pnl = (sl_price - entry_price) * direction
            return dict(outcome='SL', exit_price=exit_price, exit_bar=str(ts),
                        bars_held=i+1, bars_to_entry=bars_to_entry, pnl=pnl, mfe=mfe, mae=mae)

    if not entry_triggered:
        return None  # stop entry never triggered

    # Timed out
    last = active_bars.iloc[-1]
    exit_price = last['close']
    pnl = (exit_price - entry_price) * direction
    return dict(outcome='TIMEOUT', exit_price=exit_price, exit_bar=str(active_bars.index[-1]),
                bars_held=len(active_bars), bars_to_entry=bars_to_entry, pnl=pnl, mfe=mfe, mae=mae)


# ─── Run branches ──────────────────────────────────────────────────────────────

def run_branch(sess: pd.DataFrame, df1: pd.DataFrame, branch: str):
    """Run a single branch across all qualifying sessions."""
    trades = []

    for date, row in sess.iterrows():
        side = row['side']

        if branch == 'ashort':
            if side != -1:
                continue
            entry = row['entry_ashort']
            sl    = row['sl_ashort']
            tp    = row['tp_ashort']
            direction = -1

        elif branch == 'along':
            if side != 1:
                continue
            entry = row['entry_along']
            sl    = row['sl_along']
            tp    = row['tp_along']
            direction = 1

        elif branch == 'fliplong':
            if side != -1:
                continue
            entry = row['entry_fliplong']
            sl    = row['sl_fliplong']
            tp    = row['tp_fliplong']
            direction = 1

        elif branch == 'flipshort':
            if side != 1:
                continue
            entry = row['entry_flipshort']
            sl    = row['sl_flipshort']
            tp    = row['tp_flipshort']
            direction = -1

        else:
            raise ValueError(f"Unknown branch: {branch}")

        is_flip = branch in ('fliplong', 'flipshort')
        result = resolve_trade_on_1m(date, entry, sl, tp, direction, df1,
                                     is_stop_entry=is_flip)
        if result is None:
            continue

        trades.append({
            'date': str(date),
            'branch': branch,
            'direction': direction,
            'dOpen': row['dOpen'],
            'bHi': row['bHi'],
            'bLo': row['bLo'],
            'entry': entry,
            'sl': sl,
            'tp': tp,
            **result,
        })

    return pd.DataFrame(trades)


# ─── Stats ────────────────────────────────────────────────────────────────────

def compute_stats(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    n  = len(df)
    tp = (df['outcome'] == 'TP').sum()
    sl = (df['outcome'] == 'SL').sum()
    to = (df['outcome'] == 'TIMEOUT').sum()
    wr = tp / n

    total_pnl = df['pnl'].sum()
    gross_win  = df.loc[df['pnl'] > 0, 'pnl'].sum()
    gross_loss = df.loc[df['pnl'] < 0, 'pnl'].abs().sum()
    pf = gross_win / gross_loss if gross_loss > 0 else np.nan

    avg_win  = df.loc[df['pnl'] > 0, 'pnl'].mean() if tp > 0 else np.nan
    avg_loss = df.loc[df['pnl'] < 0, 'pnl'].mean() if sl + to > 0 else np.nan

    equity = df['pnl'].cumsum()
    dd = (equity.cummax() - equity)
    max_dd = dd.max()

    sharpe = np.nan
    if df['pnl'].std() > 0:
        sharpe = df['pnl'].mean() / df['pnl'].std() * np.sqrt(252)

    return {
        'n_trades': int(n),
        'n_tp': int(tp),
        'n_sl': int(sl),
        'n_timeout': int(to),
        'win_rate': round(float(wr), 4),
        'total_pnl_pts': round(float(total_pnl), 2),
        'profit_factor': round(float(pf), 4) if not np.isnan(pf) else None,
        'avg_win_pts': round(float(avg_win), 2) if not np.isnan(avg_win) else None,
        'avg_loss_pts': round(float(avg_loss), 2) if not np.isnan(avg_loss) else None,
        'max_drawdown_pts': round(float(max_dd), 2),
        'annualized_sharpe': round(float(sharpe), 4) if not np.isnan(sharpe) else None,
        'avg_mfe_pts': round(float(df['mfe'].mean()), 2),
        'avg_mae_pts': round(float(df['mae'].mean()), 2),
        'avg_bars_held': round(float(df['bars_held'].mean()), 1),
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=== AU200 10AM Strategy Engine ===\n")

    print("Loading data...")
    df5, df1 = load_data()
    print(f"  5-min bars: {len(df5):,}")
    print(f"  1-min bars: {len(df1):,}")

    print("Extracting sessions...")
    sess = extract_sessions(df5)
    print(f"  Sessions with both 09:50 and 10:00 bars: {len(sess)}")
    print(f"  Side=+1 (long bias): {(sess['side']==1).sum()}")
    print(f"  Side=-1 (short bias): {(sess['side']==-1).sum()}")

    all_trades = []
    summary = {}

    for branch in ['ashort', 'along', 'fliplong', 'flipshort']:
        print(f"\nRunning branch: {branch}...")
        df_branch = run_branch(sess, df1, branch)
        print(f"  Trades: {len(df_branch)}")
        if not df_branch.empty:
            stats = compute_stats(df_branch)
            summary[branch] = stats
            print(f"  Win rate: {stats['win_rate']:.1%}  PF: {stats['profit_factor']}  Total PnL: {stats['total_pnl_pts']} pts")
            all_trades.append(df_branch)

    # Combined (all branches together as if trading all signals)
    if all_trades:
        df_all = pd.concat(all_trades, ignore_index=True)
        df_all = df_all.sort_values('date').reset_index(drop=True)
        df_all.to_csv(BASE_DIR / "trades_all.csv", index=False)
        print(f"\nAll trades saved: {len(df_all)}")
        summary['_combined_all'] = compute_stats(df_all)

    # Also save per-branch
    for branch in ['ashort', 'along', 'fliplong', 'flipshort']:
        bt = [t for t in all_trades if not t.empty and t['branch'].iloc[0] == branch]
        if bt:
            bt[0].to_csv(BASE_DIR / f"trades_{branch}.csv", index=False)

    # Primary branch: the one the signal fires (A Short when side=-1, A Long when side=+1)
    primary_trades = []
    for branch in ['ashort', 'along']:
        bt = [t for t in all_trades if not t.empty and t['branch'].iloc[0] == branch]
        if bt:
            primary_trades.append(bt[0])
    if primary_trades:
        df_primary = pd.concat(primary_trades, ignore_index=True).sort_values('date')
        summary['_primary'] = compute_stats(df_primary)
        df_primary.to_csv(BASE_DIR / "trades_primary.csv", index=False)

    # Save summary
    out_json = BASE_DIR / "summary.json"
    with open(out_json, 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n=== SUMMARY ===")
    for k, v in summary.items():
        print(f"\n[{k}]")
        for stat, val in v.items():
            print(f"  {stat}: {val}")

    print(f"\nSaved: {out_json}")
    print("Strategy engine complete.")

if __name__ == "__main__":
    main()
