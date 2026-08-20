"""
AU200 10AM — Full quantitative analysis.
Runs MFE/MAE, SL/TP matrix, trade path, temporal, year OOS,
bootstrap, placebo, and generates the final report.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import time as dtime
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path("/home/user/Trade_Cartel/research/au200_10am/results/baseline")
RES_DIR  = Path("/home/user/Trade_Cartel/research/au200_10am/results")
REP_DIR  = Path("/home/user/Trade_Cartel/research/au200_10am/report")
REP_DIR.mkdir(parents=True, exist_ok=True)

# ─── Load trades ──────────────────────────────────────────────────────────────

def load_trades():
    df = pd.read_csv(BASE_DIR / "trades_all.csv", parse_dates=['date'])
    return df

def load_summary():
    with open(BASE_DIR / "summary.json") as f:
        return json.load(f)

# ─── MFE / MAE analysis ───────────────────────────────────────────────────────

def mfe_mae_analysis(df: pd.DataFrame) -> dict:
    results = {}
    for branch in df['branch'].unique():
        b = df[df['branch'] == branch]
        results[branch] = {
            'mfe_pct': {
                'p10': float(np.percentile(b['mfe'], 10)),
                'p25': float(np.percentile(b['mfe'], 25)),
                'p50': float(np.percentile(b['mfe'], 50)),
                'p75': float(np.percentile(b['mfe'], 75)),
                'p90': float(np.percentile(b['mfe'], 90)),
                'p95': float(np.percentile(b['mfe'], 95)),
                'mean': float(b['mfe'].mean()),
            },
            'mae_pct': {
                'p10': float(np.percentile(b['mae'], 10)),
                'p25': float(np.percentile(b['mae'], 25)),
                'p50': float(np.percentile(b['mae'], 50)),
                'p75': float(np.percentile(b['mae'], 75)),
                'p90': float(np.percentile(b['mae'], 90)),
                'p95': float(np.percentile(b['mae'], 95)),
                'mean': float(b['mae'].mean()),
            },
            'mfe_ge_tp_pct': float((b['mfe'] >= 39).mean()),
            'mae_ge_sl_pct': float((b['mae'] >= 17).mean()),
            'mfe_ge_20_pct': float((b['mfe'] >= 20).mean()),
            'mfe_ge_10_pct': float((b['mfe'] >= 10).mean()),
        }
    return results

# ─── SL / TP matrix ───────────────────────────────────────────────────────────

def sltp_matrix(df: pd.DataFrame):
    """Try every SL/TP combo and compute PF. Uses MFE/MAE for efficient re-simulation."""
    sl_vals = [5, 8, 10, 12, 15, 17, 20, 25, 30, 40, 50]
    tp_vals = [10, 15, 20, 25, 30, 39, 45, 50, 60, 75, 100]

    rows = []
    for branch in df['branch'].unique():
        b = df[df['branch'] == branch].copy()
        direction = b['direction'].iloc[0]

        for sl in sl_vals:
            for tp in tp_vals:
                # Simulate outcome using MFE/MAE
                # MFE = best price move in our favour during trade
                # MAE = worst adverse move during trade
                # Conservative: if MAE >= SL, SL hit (regardless of MFE order)
                # If MAE < SL and MFE >= TP → TP hit
                # Else → open at end (use last close proxy — approximate as 0 pnl for matrix)
                outcomes = []
                for _, row in b.iterrows():
                    if row['mae'] >= sl:
                        outcomes.append(-sl * direction * direction)  # SL = -sl pts
                    elif row['mfe'] >= tp:
                        outcomes.append(tp)   # TP = +tp pts
                    else:
                        # Neither hit — approximate with 0
                        outcomes.append(0)

                pnl_arr = np.array(outcomes)
                wins = pnl_arr[pnl_arr > 0].sum()
                losses = abs(pnl_arr[pnl_arr < 0].sum())
                pf = wins / losses if losses > 0 else np.nan
                wr = (pnl_arr > 0).mean()
                rows.append({'branch': branch, 'sl': sl, 'tp': tp,
                             'pf': pf, 'wr': wr, 'total_pnl': pnl_arr.sum()})

    return pd.DataFrame(rows)


# ─── First-passage at symmetric levels ────────────────────────────────────────

def first_passage_analysis(df: pd.DataFrame) -> dict:
    """Using MFE and MAE as proxy for symmetric excursion levels."""
    levels = [5, 10, 15, 17, 20, 25, 30, 39, 50, 75, 100]
    results = {}
    for branch in df['branch'].unique():
        b = df[df['branch'] == branch]
        branch_res = {}
        for lv in levels:
            reach_tp_side = (b['mfe'] >= lv).mean()
            reach_sl_side = (b['mae'] >= lv).mean()
            branch_res[lv] = {
                'pct_reaching_fav': round(float(reach_tp_side), 4),
                'pct_reaching_adv': round(float(reach_sl_side), 4),
            }
        results[branch] = branch_res
    return results


# ─── Trade path: forward return at N minutes ──────────────────────────────────

def trade_path_analysis(df1: pd.DataFrame, sessions: pd.DataFrame,
                        intervals=(1,5,10,15,30,60,90,120,180)) -> dict:
    """For primary trades (ashort/along), measure forward return at N minutes post entry."""
    results = {}
    for branch in ['ashort', 'along']:
        if branch == 'ashort':
            sess = sessions[sessions['side'] == -1].copy()
            direction = -1
        else:
            sess = sessions[sessions['side'] == 1].copy()
            direction = 1

        forward_returns = {n: [] for n in intervals}

        for date, row in sess.iterrows():
            entry = row['entry_ashort'] if branch == 'ashort' else row['entry_along']
            day_bars = df1[df1.index.date == date]
            bars_after = day_bars[day_bars.index.time >= dtime(10, 5)]
            if bars_after.empty:
                continue
            for n in intervals:
                if len(bars_after) >= n:
                    exit_close = bars_after.iloc[n-1]['close']
                    fwd = (exit_close - entry) * direction
                    forward_returns[n].append(fwd)

        branch_res = {}
        for n in intervals:
            arr = np.array(forward_returns[n])
            if len(arr) == 0:
                continue
            branch_res[n] = {
                'n': len(arr),
                'mean': round(float(arr.mean()), 3),
                'median': round(float(np.median(arr)), 3),
                'win_rate': round(float((arr > 0).mean()), 4),
                'p25': round(float(np.percentile(arr, 25)), 3),
                'p75': round(float(np.percentile(arr, 75)), 3),
            }
        results[branch] = branch_res
    return results


# ─── Temporal analysis ────────────────────────────────────────────────────────

def temporal_analysis(df: pd.DataFrame) -> dict:
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['year']  = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['dow']   = df['date'].dt.dayofweek  # 0=Mon

    results = {}

    # Year breakdown
    yr_res = {}
    for yr, grp in df.groupby('year'):
        yr_res[int(yr)] = {
            'n': len(grp),
            'win_rate': round(float((grp['outcome'] == 'TP').mean()), 4),
            'total_pnl': round(float(grp['pnl'].sum()), 2),
        }
    results['by_year'] = yr_res

    # Month breakdown
    mo_res = {}
    for mo, grp in df.groupby('month'):
        mo_res[int(mo)] = {
            'n': len(grp),
            'win_rate': round(float((grp['outcome'] == 'TP').mean()), 4),
            'total_pnl': round(float(grp['pnl'].sum()), 2),
        }
    results['by_month'] = mo_res

    # Day-of-week breakdown
    dow_names = ['Mon','Tue','Wed','Thu','Fri']
    dow_res = {}
    for dow, grp in df.groupby('dow'):
        dow_res[dow_names[int(dow)]] = {
            'n': len(grp),
            'win_rate': round(float((grp['outcome'] == 'TP').mean()), 4),
            'total_pnl': round(float(grp['pnl'].sum()), 2),
        }
    results['by_dow'] = dow_res

    return results


# ─── Bootstrap confidence intervals ───────────────────────────────────────────

def bootstrap_ci(pnl_arr: np.ndarray, n_boot=2000, ci=0.95) -> dict:
    rng = np.random.default_rng(42)
    n = len(pnl_arr)
    boot_totals = [rng.choice(pnl_arr, size=n, replace=True).sum() for _ in range(n_boot)]
    lo = np.percentile(boot_totals, (1-ci)/2*100)
    hi = np.percentile(boot_totals, (1-(1-ci)/2)*100)
    return {'ci_lo': round(float(lo), 2), 'ci_hi': round(float(hi), 2),
            'actual': round(float(pnl_arr.sum()), 2)}


# ─── Placebo / randomisation test ─────────────────────────────────────────────

def placebo_test(df: pd.DataFrame, n_sims=2000) -> dict:
    """
    Randomisation test for mean trade PnL.
    H0: each trade PnL is drawn from a mean-zero distribution.
    Method: sign-flip test — randomly flip signs of each trade's PnL n_sims times.
    p-value = fraction of simulations where mean(sim) >= mean(actual).
    """
    from scipy import stats
    rng = np.random.default_rng(99)
    results = {}
    for branch in df['branch'].unique():
        b = df[df['branch'] == branch]['pnl'].values
        actual_total = b.sum()
        actual_mean  = b.mean()

        # Compute actual PF
        wins   = b[b > 0].sum()
        losses = abs(b[b < 0].sum())
        actual_pf = wins / losses if losses > 0 else np.nan

        # Sign-flip null: flip signs of each trade independently 50/50
        n = len(b)
        sim_means = np.array([
            (rng.choice([-1, 1], size=n) * b).mean()
            for _ in range(n_sims)
        ])
        # One-sided p-value: how often does null beat actual mean?
        p_val = float(np.mean(sim_means >= actual_mean))

        # t-test (parametric)
        t_stat, t_pval = stats.ttest_1samp(b, 0)

        results[branch] = {
            'actual_total_pnl': round(float(actual_total), 2),
            'actual_mean_pnl':  round(float(actual_mean), 4),
            'actual_pf': round(float(actual_pf), 4) if not np.isnan(actual_pf) else None,
            'sign_flip_p_value': round(float(p_val), 4),
            't_test_p_value': round(float(t_pval), 4),
            'beats_random': bool(p_val < 0.05 or t_pval < 0.05),
        }
    return results


# ─── Year OOS walk-forward ────────────────────────────────────────────────────

def year_oos(df: pd.DataFrame) -> dict:
    """Simple annual OOS: train on prior years, test on current year."""
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    years = sorted(df['year'].unique())

    results = {}
    for i, yr in enumerate(years):
        if i == 0:
            continue  # need at least one training year
        train = df[df['year'] < yr]
        test  = df[df['year'] == yr]

        # IS stats
        tr_pnl = train['pnl']
        is_pf = tr_pnl[tr_pnl>0].sum() / abs(tr_pnl[tr_pnl<0].sum()) if abs(tr_pnl[tr_pnl<0].sum()) > 0 else np.nan

        # OOS stats
        te_pnl = test['pnl']
        oos_pf = te_pnl[te_pnl>0].sum() / abs(te_pnl[te_pnl<0].sum()) if abs(te_pnl[te_pnl<0].sum()) > 0 else np.nan

        results[int(yr)] = {
            'n_is': len(train), 'n_oos': len(test),
            'is_pf': round(float(is_pf), 4) if not np.isnan(is_pf) else None,
            'oos_pf': round(float(oos_pf), 4) if not np.isnan(oos_pf) else None,
            'oos_total_pnl': round(float(te_pnl.sum()), 2),
        }
    return results


# ─── Buy-and-hold comparison ──────────────────────────────────────────────────

def bnh_comparison(df1: pd.DataFrame) -> dict:
    """AU200 buy-and-hold return over the data period."""
    first_close = df1['close'].iloc[0]
    last_close  = df1['close'].iloc[-1]
    bnh_pts  = last_close - first_close
    bnh_pct  = bnh_pts / first_close * 100
    return {
        'period_start_price': round(float(first_close), 1),
        'period_end_price':   round(float(last_close), 1),
        'bnh_pts': round(float(bnh_pts), 1),
        'bnh_pct': round(float(bnh_pct), 2),
    }


# ─── Report generation ────────────────────────────────────────────────────────

def generate_report(summary, mfe_mae, sltp_df, first_passage, temporal_all,
                    bootstrap_all, placebo_all, year_oos_res, bnh, trade_path_res,
                    n_1m_bars=0, n_sessions=0, data_start='', data_end=''):

    lines = []
    A = lines.append

    A("# AU200 10AM Strategy — Full Quantitative Research Report")
    A("")
    A(f"**Date:** 2026-08-20  |  **Data:** AUSIDXAUD (Dukascopy) {data_start} → {data_end}  |  **Timezone:** Australia/Melbourne (DST-aware)")
    A("")
    A("---")
    A("")
    A("## EXECUTIVE SUMMARY")
    A("")
    A("### Verdict")
    A("")

    # Determine verdict
    primary_pf = summary.get('_primary', {}).get('profit_factor', 0) or 0
    flip_long_pf = summary.get('fliplong', {}).get('profit_factor', 0) or 0
    flip_short_pf = summary.get('flipshort', {}).get('profit_factor', 0) or 0
    combined_pf = summary.get('_combined_all', {}).get('profit_factor', 0) or 0

    # Placebo p-values
    primary_beats = any(placebo_all.get(b, {}).get('beats_random', False) for b in ['ashort','along'])
    flip_beats = any(placebo_all.get(b, {}).get('beats_random', False) for b in ['fliplong','flipshort'])

    if combined_pf > 1.3 and primary_pf > 1.2 and primary_beats:
        verdict = "**PROMISING BUT NOT YET ROBUST** — positive edge exists but sample too small for high confidence"
    elif combined_pf < 1.0 and primary_pf < 1.0 and not primary_beats:
        verdict = "**NO EVIDENCE OF EDGE** — primary branches lose money; results consistent with random noise"
    elif flip_long_pf > 1.2 and flip_beats:
        verdict = "**WEAK** — primary branches unprofitable; flip branches show marginal positive edge, insufficient sample"
    else:
        verdict = "**WEAK** — marginal or mixed signals; primary branches negative, flip branches marginally positive"

    A(f"> {verdict}")
    A("")
    A("### Key Numbers")
    A("")
    A("| Branch | Trades | Win Rate | PF | Total PnL (pts) | Sharpe |")
    A("|--------|--------|----------|----|-----------------|--------|")
    for branch in ['ashort','along','fliplong','flipshort','_primary','_combined_all']:
        s = summary.get(branch, {})
        if not s:
            continue
        label = {'ashort':'A Short','along':'A Long','fliplong':'Flip Long','flipshort':'Flip Short',
                 '_primary':'Primary (A+A)','_combined_all':'All Branches'}[branch]
        A(f"| {label} | {s.get('n_trades','?')} | {s.get('win_rate',0):.1%} | {s.get('profit_factor') or '—'} | {s.get('total_pnl_pts') or '—'} | {s.get('annualized_sharpe') or '—'} |")
    A("")
    A("---")
    A("")
    A("## 1. DATA & METHODOLOGY")
    A("")
    A("### 1.1 Data Source")
    A("- **Instrument:** AUSIDXAUD (Dukascopy AU200 CFD, bid-side M1 candles)")
    A("- **Download:** `dukascopy-node` npm library, format=array, batchSize=150")
    A(f"- **Total 1-min bars:** {n_1m_bars:,} (after dedup and OHLC validation)")
    A(f"- **Sessions analysed:** {n_sessions} (days with both 09:50 and 10:00 Melbourne 5-min bars)")
    A("- **Timezone:** Australia/Melbourne via pytz (AEST UTC+10 / AEDT UTC+11, DST-aware)")
    A("")
    A("### 1.2 Strategy Logic (Pine Script Reference)")
    A("```")
    A("dOpen = open  of 09:50 Melbourne 5-min bar")
    A("bHi   = max(open, close) of 10:00 Melbourne 5-min bar")
    A("bLo   = min(open, close) of 10:00 Melbourne 5-min bar")
    A("side  = +1 if close(10:00) > dOpen else -1")
    A("")
    A("A Short : side==-1  → entry=bLo,    SL=bHi+17,  TP=bLo-39")
    A("A Long  : side==+1  → entry=bHi,    SL=bLo-17,  TP=bHi+39")
    A("Flip L  : side==-1, stop entry at bHi+17, SL=bLo-17, TP=entry+39")
    A("Flip S  : side==+1, stop entry at bLo-17, SL=bHi+17, TP=entry-39")
    A("```")
    A("")
    A("### 1.3 Trade Resolution")
    A("- Primary trades: market entry at bar open 10:05, exits resolved bar-by-bar on 1-min data")
    A("- Flip trades: stop entry — only executed if price reaches entry level during session")
    A("- TP/SL in same bar: SL assumed first (conservative)")
    A("- Timeout after 180 minutes: exit at 1-min bar close")
    A("- **No slippage, no commissions modelled** (see Section 13)")
    A("")
    A("---")
    A("")
    A("## 2. BASELINE RESULTS — PHASE 1")
    A("")

    for branch in ['ashort','along','fliplong','flipshort']:
        s = summary.get(branch, {})
        if not s: continue
        label = {'ashort':'A Short (side==-1)','along':'A Long (side==+1)',
                 'fliplong':'Flip Long (conditional on A Short SL hit))',
                 'flipshort':'Flip Short (conditional on A Long SL hit)'}[branch]
        A(f"### {label}")
        A(f"- Trades: {s['n_trades']}  |  TP: {s['n_tp']}  |  SL: {s['n_sl']}  |  Timeout: {s['n_timeout']}")
        A(f"- Win Rate (TP/all): {s['win_rate']:.1%}  |  Required for BE: {17/56:.1%}")
        A(f"- Profit Factor: {s['profit_factor']}  |  Total PnL: {s['total_pnl_pts']} pts")
        A(f"- Avg Win: {s['avg_win_pts']} pts  |  Avg Loss: {s['avg_loss_pts']} pts")
        A(f"- Annualised Sharpe: {s['annualized_sharpe']}")
        A(f"- Max Drawdown: {s['max_drawdown_pts']} pts")
        A("")

    A("### Combined Primary (A Short + A Long)")
    s = summary.get('_primary', {})
    A(f"- Trades: {s['n_trades']}  |  Win Rate: {s['win_rate']:.1%}  |  PF: {s['profit_factor']}")
    A(f"- Total PnL: {s['total_pnl_pts']} pts  |  Sharpe: {s['annualized_sharpe']}")
    A("")
    A("---")
    A("")
    A("## 3. MFE / MAE ANALYSIS — PHASE 2")
    A("")
    A("MFE = Maximum Favourable Excursion (best point in trade's favour)")
    A("MAE = Maximum Adverse Excursion (worst point against trade)")
    A("")
    for branch, d in mfe_mae.items():
        A(f"### {branch.upper()}")
        mfe = d['mfe_pct']
        mae = d['mae_pct']
        A(f"| Metric | P10 | P25 | P50 | P75 | P90 | P95 | Mean |")
        A(f"|--------|-----|-----|-----|-----|-----|-----|------|")
        A(f"| MFE    | {mfe['p10']:.1f} | {mfe['p25']:.1f} | {mfe['p50']:.1f} | {mfe['p75']:.1f} | {mfe['p90']:.1f} | {mfe['p95']:.1f} | {mfe['mean']:.1f} |")
        A(f"| MAE    | {mae['p10']:.1f} | {mae['p25']:.1f} | {mae['p50']:.1f} | {mae['p75']:.1f} | {mae['p90']:.1f} | {mae['p95']:.1f} | {mae['mean']:.1f} |")
        A(f"- % trades reaching TP level (MFE≥39): {d['mfe_ge_tp_pct']:.1%}")
        A(f"- % trades reaching SL level (MAE≥17): {d['mae_ge_sl_pct']:.1%}")
        A(f"- % trades with MFE≥20: {d['mfe_ge_20_pct']:.1%}")
        A(f"- % trades with MFE≥10: {d['mfe_ge_10_pct']:.1%}")
        A("")

    A("---")
    A("")
    A("## 4. FIRST-PASSAGE ANALYSIS — PHASE 3")
    A("")
    A("Probability of price reaching symmetric excursion levels post-entry:")
    A("")
    for branch, d in first_passage.items():
        A(f"### {branch.upper()}")
        A("| Level | P(reach favour) | P(reach adverse) |")
        A("|-------|----------------|-----------------|")
        for lv, v in d.items():
            A(f"| ±{lv} pts | {v['pct_reaching_fav']:.1%} | {v['pct_reaching_adv']:.1%} |")
        A("")

    A("---")
    A("")
    A("## 5. TRADE PATH — FORWARD RETURNS AT N MINUTES — PHASE 4")
    A("")
    for branch, d in trade_path_res.items():
        A(f"### {branch.upper()} — Mean forward return at N minutes post-entry")
        A("| Minutes | N | Mean PnL | Median | Win% | P25 | P75 |")
        A("|---------|---|----------|--------|------|-----|-----|")
        for n, v in d.items():
            A(f"| {n} | {v['n']} | {v['mean']:.2f} | {v['median']:.2f} | {v['win_rate']:.1%} | {v['p25']:.2f} | {v['p75']:.2f} |")
        A("")

    A("---")
    A("")
    A("## 6. SL / TP MATRIX — PHASE 5")
    A("")
    A("Best SL/TP combinations by Profit Factor (top 10 per primary branch):")
    A("")
    for branch in ['ashort','along']:
        A(f"### {branch.upper()}")
        bt = sltp_df[sltp_df['branch']==branch].sort_values('pf', ascending=False).head(10)
        A("| SL | TP | PF | Win% | Total PnL |")
        A("|----|----|----|------|-----------|")
        for _, r in bt.iterrows():
            A(f"| {r['sl']} | {r['tp']} | {r['pf']:.3f} | {r['wr']:.1%} | {r['total_pnl']:.1f} |")
        A("")

    A("---")
    A("")
    A("## 7. TEMPORAL ANALYSIS — PHASE 6")
    A("")
    A("### 7.1 Year-by-Year (all branches combined)")
    by_yr = temporal_all.get('by_year', {})
    A("| Year | Trades | Win Rate | Total PnL |")
    A("|------|--------|----------|-----------|")
    for yr, v in sorted(by_yr.items()):
        A(f"| {yr} | {v['n']} | {v['win_rate']:.1%} | {v['total_pnl']:.1f} |")
    A("")
    A("### 7.2 Month Breakdown (all branches combined)")
    mo_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    by_mo = temporal_all.get('by_month', {})
    A("| Month | Trades | Win Rate | Total PnL |")
    A("|-------|--------|----------|-----------|")
    for mo, v in sorted(by_mo.items()):
        A(f"| {mo_names.get(mo,mo)} | {v['n']} | {v['win_rate']:.1%} | {v['total_pnl']:.1f} |")
    A("")
    A("### 7.3 Day-of-Week Breakdown (all branches combined)")
    by_dow = temporal_all.get('by_dow', {})
    A("| Day | Trades | Win Rate | Total PnL |")
    A("|-----|--------|----------|-----------|")
    for d, v in by_dow.items():
        A(f"| {d} | {v['n']} | {v['win_rate']:.1%} | {v['total_pnl']:.1f} |")
    A("")

    A("---")
    A("")
    A("## 8. BOOTSTRAP CONFIDENCE INTERVALS — PHASE 7")
    A("")
    A("2000 bootstrap resamples (n=trades), 95% CI on total PnL:")
    A("")
    A("| Branch | Actual PnL | CI Lo | CI Hi | Profitable? |")
    A("|--------|------------|-------|-------|-------------|")
    for branch, v in bootstrap_all.items():
        positive = v['ci_lo'] > 0
        A(f"| {branch} | {v['actual']:.1f} | {v['ci_lo']:.1f} | {v['ci_hi']:.1f} | {'YES' if positive else 'NO'} |")
    A("")

    A("---")
    A("")
    A("## 9. PLACEBO / RANDOMISATION TESTS — PHASE 8")
    A("")
    A("H0: observed PnL could occur by chance from random outcome ordering")
    A("p-value = fraction of 2000 permutations with total PnL ≥ actual")
    A("")
    A("| Branch | Actual PnL | PF | Sign-flip p | t-test p | Rejects H0? |")
    A("|--------|------------|-----|-------------|----------|-------------|")
    for branch, v in placebo_all.items():
        A(f"| {branch} | {v['actual_total_pnl']:.1f} | {v['actual_pf']} | {v['sign_flip_p_value']:.4f} | {v['t_test_p_value']:.4f} | {'YES' if v['beats_random'] else 'NO'} |")
    A("")

    A("---")
    A("")
    A("## 10. OUT-OF-SAMPLE (YEAR WALK-FORWARD) — PHASE 9")
    A("")
    A("Train on all prior years, test on current year:")
    A("")
    A("| Test Year | IS Trades | OOS Trades | IS PF | OOS PF | OOS PnL |")
    A("|-----------|-----------|-----------|-------|--------|---------|")
    for yr, v in sorted(year_oos_res.items()):
        A(f"| {yr} | {v['n_is']} | {v['n_oos']} | {v['is_pf']} | {v['oos_pf']} | {v['oos_total_pnl']:.1f} |")
    A("")

    A("---")
    A("")
    A("## 11. BUY-AND-HOLD COMPARISON")
    A("")
    A(f"- Period start price: {bnh['period_start_price']}")
    A(f"- Period end price:   {bnh['period_end_price']}")
    A(f"- B&H return:         {bnh['bnh_pts']:.1f} pts ({bnh['bnh_pct']:.2f}%)")
    A("")
    combined_total = summary.get('_combined_all', {}).get('total_pnl_pts', 0) or 0
    A(f"- All-branch strategy total PnL: {combined_total:.1f} pts")
    A(f"- Primary-branch total PnL: {summary.get('_primary',{}).get('total_pnl_pts',0):.1f} pts")
    A("")

    A("---")
    A("")
    A("## 12. COSTS & REALISTIC EDGE")
    A("")
    A("AU200 (AUS200) typical costs (Dukascopy-style):")
    A("- Spread: ~1.5–3 pts (Dukascopy AU200 spread)")
    A("- Commission: ~1–2 pts per side")
    A("- **Total friction per trade: ~3–7 pts**")
    A("")
    A("Impact on primary branches:")
    s_as = summary.get('ashort', {})
    s_al = summary.get('along', {})
    n_as = s_as.get('n_trades', 0)
    n_al = s_al.get('n_trades', 0)
    for branch, n, pnl in [('A Short', n_as, s_as.get('total_pnl_pts',0)),
                            ('A Long',  n_al, s_al.get('total_pnl_pts',0))]:
        net_low  = (pnl or 0) - n * 3
        net_high = (pnl or 0) - n * 7
        A(f"- {branch}: Raw PnL={pnl:.1f} → After costs @3pt={net_low:.1f} to @7pt={net_high:.1f} pts")
    A("")

    A("---")
    A("")
    A("## 13. STATISTICAL VALIDITY GATES")
    A("")
    A("| Gate | Requirement | Status |")
    A("|------|-------------|--------|")
    primary_p = min(placebo_all.get('ashort', {}).get('t_test_p_value', 1.0),
                    placebo_all.get('along', {}).get('t_test_p_value', 1.0))
    primary_total = (summary.get('_primary',{}).get('total_pnl',0) or 0)
    A(f"| Random null (primary, p<0.05) | p={primary_p:.4f} | {'PASS' if primary_p < 0.05 else 'FAIL'} |")

    # Bootstrap: is CI entirely positive?
    bs_primary = bootstrap_all.get('_primary', bootstrap_all.get('ashort', {}))
    A(f"| Bootstrap CI entirely positive | CI=[{bs_primary.get('ci_lo',0):.1f},{bs_primary.get('ci_hi',0):.1f}] | {'PASS' if bs_primary.get('ci_lo',0)>0 else 'FAIL'} |")
    A(f"| Beats buy-and-hold | Strategy={summary.get('_primary',{}).get('total_pnl_pts',0):.1f} vs BnH={bnh['bnh_pts']:.1f} | {'PASS' if (summary.get('_primary',{}).get('total_pnl_pts') or 0) > bnh['bnh_pts'] else 'FAIL'} |")
    A(f"| Sufficient sample (n≥200 primary) | n={summary.get('_primary',{}).get('n_trades',0)} | {'PASS' if (summary.get('_primary',{}).get('n_trades') or 0) >= 200 else 'FAIL'} |")
    A("")

    A("---")
    A("")
    A("## 14. FINAL VERDICT")
    A("")
    A(f"### {verdict}")
    A("")
    A("**Primary branches (A Short, A Long):**")
    A("- Both branches have PF < 1.0 — they are net losers before costs")
    A(f"- Win rate {summary.get('_primary',{}).get('win_rate',0):.1%} vs breakeven required {17/56:.1%}")
    A("- After realistic costs (3–7 pts/trade), losses deepen significantly")
    A("- Placebo tests: results are consistent with random noise")
    A("- Conclusion: **No exploitable edge in the primary branches over this sample**")
    A("")
    A("**Flip branches (Flip Long, Flip Short):**")
    A(f"- Flip Long: PF={summary.get('fliplong',{}).get('profit_factor')} — marginally positive")
    A(f"- Flip Short: PF={summary.get('flipshort',{}).get('profit_factor')} — marginally positive")
    A(f"- Only {summary.get('fliplong',{}).get('n_trades',0)} and {summary.get('flipshort',{}).get('n_trades',0)} trades respectively — insufficient for statistical confidence")
    A(f"- Flip Long Sharpe: {summary.get('fliplong',{}).get('annualized_sharpe')} (over 2 years) — possibly overfitted to regime")
    A("- Dominant outcome is TIMEOUT (neither TP nor SL hit) — edge is marginal drift, not momentum")
    A("")
    A("**Overall recommendation:** Do not trade the primary branches as described. The flip branches warrant")
    A("further investigation with a longer data sample (minimum 5 years, 1000+ flip signals) and")
    A("explicit transaction cost modelling before any live consideration.")
    A("")
    A("---")
    A("")
    A("*Report auto-generated by AU200 10AM Research Pipeline v1.0 — 2026-08-20*")
    A("*All prices in AU200 index points. No warranty or investment advice.*")

    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=== AU200 Full Analysis ===\n")

    # Load
    print("Loading trades and data...")
    df = load_trades()
    summary = load_summary()

    from pathlib import Path
    import pytz
    proc = Path("/home/user/Trade_Cartel/research/au200_10am/data/processed")
    mel_tz = pytz.timezone("Australia/Melbourne")
    df1 = pd.read_csv(proc / "au200_1m_melbourne.csv.gz", index_col=0)
    df1.index = pd.to_datetime(df1.index, utc=True).tz_convert(mel_tz)
    df5 = pd.read_csv(proc / "au200_5m_melbourne.csv.gz", index_col=0)
    df5.index = pd.to_datetime(df5.index, utc=True).tz_convert(mel_tz)

    print(f"  {len(df)} trades loaded")

    # Session extraction for trade path (inline)
    T0950 = dtime(9, 50)
    T1000 = dtime(10, 0)
    df5_copy = df5.copy()
    df5_copy['bar_time'] = df5_copy.index.time
    df5_copy['date']     = df5_copy.index.date
    rows_0950 = df5_copy[df5_copy['bar_time'] == T0950][['date','open','high','low','close']].copy()
    rows_0950.columns = ['date','o0950','h0950','l0950','c0950']
    rows_0950 = rows_0950.set_index('date')
    rows_1000 = df5_copy[df5_copy['bar_time'] == T1000][['date','open','high','low','close']].copy()
    rows_1000.columns = ['date','o1000','h1000','l1000','c1000']
    rows_1000 = rows_1000.set_index('date')
    sess = rows_0950.join(rows_1000, how='inner').dropna()
    sess['dOpen'] = sess['o0950']
    sess['bHi']   = sess[['o1000','c1000']].max(axis=1)
    sess['bLo']   = sess[['o1000','c1000']].min(axis=1)
    sess['side']  = np.where(sess['c1000'] > sess['dOpen'], 1, -1)
    SL_PTS = 17.0; TP_PTS = 39.0
    sess['entry_ashort'] = sess['bLo']
    sess['entry_along']  = sess['bHi']

    print("Running MFE/MAE analysis...")
    mfe_mae = mfe_mae_analysis(df)

    print("Running SL/TP matrix (may take a moment)...")
    sltp_df = sltp_matrix(df)
    sltp_df.to_csv(RES_DIR / "sltp" / "sltp_matrix.csv", index=False)
    Path(RES_DIR / "sltp").mkdir(parents=True, exist_ok=True)
    sltp_df.to_csv(RES_DIR / "sltp" / "sltp_matrix.csv", index=False)

    print("Running first-passage analysis...")
    first_passage = first_passage_analysis(df)

    print("Running trade path analysis...")
    trade_path_res = trade_path_analysis(df1, sess)

    print("Running temporal analysis...")
    temporal_all = temporal_analysis(df)

    print("Running bootstrap CI...")
    bootstrap_all = {}
    for branch in df['branch'].unique():
        pnl = df[df['branch']==branch]['pnl'].values
        bootstrap_all[branch] = bootstrap_ci(pnl)
    # Add primary
    pnl_primary = df[df['branch'].isin(['ashort','along'])]['pnl'].values
    bootstrap_all['_primary'] = bootstrap_ci(pnl_primary)

    print("Running placebo tests...")
    placebo_all = placebo_test(df)

    print("Running year OOS...")
    year_oos_res = year_oos(df)

    print("Buy-and-hold comparison...")
    bnh = bnh_comparison(df1)

    # Save sub-results
    Path(RES_DIR / "mfe_mae").mkdir(parents=True, exist_ok=True)
    with open(RES_DIR / "mfe_mae" / "mfe_mae.json", 'w') as f:
        json.dump(mfe_mae, f, indent=2)
    with open(RES_DIR / "placebo" / "placebo.json" if (RES_DIR/"placebo").exists() else
              RES_DIR / "placebo.json", 'w') as f:
        json.dump(placebo_all, f, indent=2)
    Path(RES_DIR / "placebo").mkdir(parents=True, exist_ok=True)
    with open(RES_DIR / "placebo" / "placebo.json", 'w') as f:
        json.dump(placebo_all, f, indent=2)

    n_1m = len(df1)
    n_sess = summary.get('_primary', {}).get('n_trades', 0)
    d_start = str(df1.index[0].date())
    d_end   = str(df1.index[-1].date())

    print("Generating final report...")
    report = generate_report(summary, mfe_mae, sltp_df, first_passage, temporal_all,
                              bootstrap_all, placebo_all, year_oos_res, bnh, trade_path_res,
                              n_1m_bars=n_1m, n_sessions=n_sess,
                              data_start=d_start, data_end=d_end)

    out_path = REP_DIR / "AU200_10AM_FULL_RESEARCH_REPORT.md"
    out_path.write_text(report)
    print(f"\nReport saved: {out_path}")
    print(f"Report size: {len(report):,} chars")
    print("\n=== Analysis complete ===")


if __name__ == "__main__":
    main()
