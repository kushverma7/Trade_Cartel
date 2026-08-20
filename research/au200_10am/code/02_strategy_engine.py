"""
AU200 10AM Strategy Engine — vectorized, memory-efficient.

Pre-groups 1-min data by date into numpy arrays. Resolves exits without pandas iterrows.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import time as dtime
import pytz

PROC_DIR = Path("/home/user/Trade_Cartel/research/au200_10am/data/processed")
BASE_DIR = Path("/home/user/Trade_Cartel/research/au200_10am/results/baseline")
BASE_DIR.mkdir(parents=True, exist_ok=True)

SL_PTS = 17.0
TP_PTS = 39.0
MAX_BARS = 180
MEL_TZ = pytz.timezone("Australia/Melbourne")


# ─── Load + pre-group 1-min data by date ─────────────────────────────────────

def load_1m_by_date():
    """Returns dict: date -> {'hi': np.array, 'lo': np.array, 'cl': np.array, 'times': list}
    Only bars at/after 10:05 Melbourne time."""
    print("  Loading 1-min data...")
    df = pd.read_csv(PROC_DIR / "au200_1m_melbourne.csv.gz", index_col=0)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(MEL_TZ)

    # Filter to bars >= 10:05 (after 10:00 5-min bar closes)
    df = df[df.index.time >= dtime(10, 5)].copy()
    df['date'] = df.index.date

    print(f"  Bars at/after 10:05: {len(df):,}")

    by_date = {}
    for date, grp in df.groupby('date'):
        grp_sorted = grp.head(MAX_BARS)
        by_date[date] = {
            'hi': grp_sorted['high'].values,
            'lo': grp_sorted['low'].values,
            'cl': grp_sorted['close'].values,
        }
    print(f"  Unique dates: {len(by_date)}")
    return by_date


# ─── Load + extract sessions ──────────────────────────────────────────────────

def load_sessions():
    print("  Loading 5-min data...")
    df5 = pd.read_csv(PROC_DIR / "au200_5m_melbourne.csv.gz", index_col=0)
    df5.index = pd.to_datetime(df5.index, utc=True).tz_convert(MEL_TZ)

    df5['bar_time'] = df5.index.time
    df5['date'] = df5.index.date

    T0950 = dtime(9, 50)
    T1000 = dtime(10, 0)

    r0950 = df5[df5['bar_time'] == T0950][['date','open']].copy()
    r0950.columns = ['date','o0950']
    r0950 = r0950.set_index('date')

    r1000 = df5[df5['bar_time'] == T1000][['date','open','close']].copy()
    r1000.columns = ['date','o1000','c1000']
    r1000 = r1000.set_index('date')

    sess = r0950.join(r1000, how='inner').dropna()
    sess['dOpen'] = sess['o0950']
    sess['bHi']   = sess[['o1000','c1000']].max(axis=1)
    sess['bLo']   = sess[['o1000','c1000']].min(axis=1)
    sess['side']  = np.where(sess['c1000'] > sess['dOpen'], 1, -1)

    print(f"  Sessions (both 09:50 + 10:00): {len(sess)}")
    return sess


# ─── Resolve single trade via numpy ──────────────────────────────────────────

def resolve(hi, lo, cl, entry, sl, tp, direction, is_stop):
    """
    hi/lo/cl: numpy arrays of 1-min bars from 10:05
    is_stop: if True, wait for price to reach entry level first (flip trades)
    direction: +1 long, -1 short
    Returns: (outcome, bars_held, pnl, mfe, mae) or None if stop never triggered
    """
    n = len(hi)
    if n == 0:
        return None

    mfe = 0.0
    mae = 0.0
    entry_bar = 0

    if is_stop:
        # Find first bar where entry level is reached
        if direction == 1:
            triggered = np.where(hi >= entry)[0]
        else:
            triggered = np.where(lo <= entry)[0]
        if len(triggered) == 0:
            return None
        entry_bar = triggered[0]

    # Slice from entry bar
    hi_s = hi[entry_bar:]
    lo_s = lo[entry_bar:]
    cl_s = cl[entry_bar:]

    if direction == 1:
        fav = hi_s - entry
        adv = entry - lo_s
        tp_hit = hi_s >= tp
        sl_hit = lo_s <= sl
    else:
        fav = entry - lo_s
        adv = hi_s - entry
        tp_hit = lo_s <= tp
        sl_hit = hi_s >= sl

    for i in range(len(hi_s)):
        mfe = max(mfe, float(fav[i]))
        mae = max(mae, float(adv[i]))

        both = tp_hit[i] and sl_hit[i]
        if both or sl_hit[i]:
            pnl = (sl - entry) * direction
            return ('SL', entry_bar + i + 1, float(pnl), mfe, mae)
        if tp_hit[i]:
            pnl = (tp - entry) * direction
            return ('TP', entry_bar + i + 1, float(pnl), mfe, mae)

    # Timeout
    pnl = (float(cl_s[-1]) - entry) * direction
    return ('TIMEOUT', entry_bar + len(hi_s), float(pnl), mfe, mae)


# ─── Run branches ──────────────────────────────────────────────────────────────

def run_branch(sess, by_date, branch):
    trades = []

    for date, row in sess.iterrows():
        side  = int(row['side'])
        bHi   = float(row['bHi'])
        bLo   = float(row['bLo'])

        if branch == 'ashort':
            if side != -1: continue
            entry, sl, tp, direction, is_stop = bLo, bHi+SL_PTS, bLo-TP_PTS, -1, False
        elif branch == 'along':
            if side != 1: continue
            entry, sl, tp, direction, is_stop = bHi, bLo-SL_PTS, bHi+TP_PTS, 1, False
        elif branch == 'fliplong':
            if side != -1: continue
            entry = bHi + SL_PTS
            entry, sl, tp, direction, is_stop = entry, bLo-SL_PTS, entry+TP_PTS, 1, True
        elif branch == 'flipshort':
            if side != 1: continue
            entry = bLo - SL_PTS
            entry, sl, tp, direction, is_stop = entry, bHi+SL_PTS, entry-TP_PTS, -1, True

        bars = by_date.get(date)
        if bars is None:
            continue

        res = resolve(bars['hi'], bars['lo'], bars['cl'], entry, sl, tp, direction, is_stop)
        if res is None:
            continue

        outcome, bars_held, pnl, mfe, mae = res
        trades.append({
            'date': str(date), 'branch': branch, 'direction': direction,
            'bHi': bHi, 'bLo': bLo, 'dOpen': float(row['dOpen']),
            'entry': entry, 'sl': sl, 'tp': tp,
            'outcome': outcome, 'bars_held': bars_held,
            'pnl': round(pnl, 4), 'mfe': round(mfe, 4), 'mae': round(mae, 4),
        })

    return pd.DataFrame(trades)


# ─── Stats ────────────────────────────────────────────────────────────────────

def compute_stats(df):
    if df.empty: return {}
    n   = len(df)
    tp  = (df['outcome'] == 'TP').sum()
    sl  = (df['outcome'] == 'SL').sum()
    to  = (df['outcome'] == 'TIMEOUT').sum()
    wr  = tp / n
    gw  = df.loc[df['pnl'] > 0, 'pnl'].sum()
    gl  = df.loc[df['pnl'] < 0, 'pnl'].abs().sum()
    pf  = gw / gl if gl > 0 else float('nan')
    equity = df['pnl'].cumsum()
    mdd = (equity.cummax() - equity).max()
    sh  = df['pnl'].mean() / df['pnl'].std() * np.sqrt(252) if df['pnl'].std() > 0 else float('nan')
    return {
        'n_trades': int(n), 'n_tp': int(tp), 'n_sl': int(sl), 'n_timeout': int(to),
        'win_rate': round(float(wr), 4),
        'total_pnl_pts': round(float(df['pnl'].sum()), 2),
        'profit_factor': round(float(pf), 4) if not np.isnan(pf) else None,
        'avg_win_pts': round(float(df.loc[df['pnl']>0,'pnl'].mean()), 2) if gw > 0 else None,
        'avg_loss_pts': round(float(df.loc[df['pnl']<0,'pnl'].mean()), 2) if gl > 0 else None,
        'max_drawdown_pts': round(float(mdd), 2),
        'annualized_sharpe': round(float(sh), 4) if not np.isnan(sh) else None,
        'avg_mfe_pts': round(float(df['mfe'].mean()), 2),
        'avg_mae_pts': round(float(df['mae'].mean()), 2),
        'avg_bars_held': round(float(df['bars_held'].mean()), 1),
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=== AU200 10AM Strategy Engine (vectorized) ===\n")
    print("Loading data...")
    by_date = load_1m_by_date()
    sess    = load_sessions()

    all_trades = []
    summary    = {}

    for branch in ['ashort', 'along', 'fliplong', 'flipshort']:
        print(f"\nRunning branch: {branch}...")
        df_b = run_branch(sess, by_date, branch)
        print(f"  Trades: {len(df_b)}")
        if not df_b.empty:
            st = compute_stats(df_b)
            summary[branch] = st
            print(f"  Win rate: {st['win_rate']:.1%}  PF: {st['profit_factor']}  PnL: {st['total_pnl_pts']} pts")
            all_trades.append(df_b)
            df_b.to_csv(BASE_DIR / f"trades_{branch}.csv", index=False)

    if all_trades:
        df_all = pd.concat(all_trades).sort_values('date').reset_index(drop=True)
        df_all.to_csv(BASE_DIR / "trades_all.csv", index=False)
        summary['_combined_all'] = compute_stats(df_all)

        primary = pd.concat([t for t in all_trades if t['branch'].iloc[0] in ('ashort','along')])
        primary = primary.sort_values('date').reset_index(drop=True)
        primary.to_csv(BASE_DIR / "trades_primary.csv", index=False)
        summary['_primary'] = compute_stats(primary)

    with open(BASE_DIR / "summary.json", 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n=== SUMMARY ===")
    for k, v in summary.items():
        print(f"\n[{k}]")
        for stat, val in v.items():
            print(f"  {stat}: {val}")

    print("\nDone.")

if __name__ == "__main__":
    main()
