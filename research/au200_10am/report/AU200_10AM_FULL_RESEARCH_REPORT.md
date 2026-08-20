# AU200 10AM Strategy — Full Quantitative Research Report

**Date:** 2026-08-20  |  **Data:** AUSIDXAUD (Dukascopy) 2024-01-01 → 2026-08-20  |  **Timezone:** Australia/Melbourne (DST-aware)

---

## EXECUTIVE SUMMARY

### Verdict

> **NO EVIDENCE OF EDGE** — primary branches lose money; results consistent with random noise

### Key Numbers

| Branch | Trades | Win Rate | PF | Total PnL (pts) | Sharpe |
|--------|--------|----------|----|-----------------|--------|
| A Short | 266 | 17.3% | 0.939 | -180.67 | -0.4338 |
| A Long | 234 | 16.2% | 0.8117 | -513.38 | -1.4424 |
| Flip Long | 112 | 21.4% | 1.3843 | 375.03 | 2.1066 |
| Flip Short | 101 | 8.9% | 1.1372 | 102.91 | 0.7793 |
| Primary (A+A) | 500 | 16.8% | 0.878 | -694.05 | -0.8989 |
| All Branches | 713 | 16.4% | 0.9709 | -216.11 | -0.1991 |

---

## 1. DATA & METHODOLOGY

### 1.1 Data Source
- **Instrument:** AUSIDXAUD (Dukascopy AU200 CFD, bid-side M1 candles)
- **Download:** `dukascopy-node` npm library, format=array, batchSize=150
- **Total 1-min bars:** 599,920 (after dedup and OHLC validation)
- **Sessions analysed:** 500 (days with both 09:50 and 10:00 Melbourne 5-min bars)
- **Timezone:** Australia/Melbourne via pytz (AEST UTC+10 / AEDT UTC+11, DST-aware)

### 1.2 Strategy Logic (Pine Script Reference)
```
dOpen = open  of 09:50 Melbourne 5-min bar
bHi   = max(open, close) of 10:00 Melbourne 5-min bar
bLo   = min(open, close) of 10:00 Melbourne 5-min bar
side  = +1 if close(10:00) > dOpen else -1

A Short : side==-1  → entry=bLo,    SL=bHi+17,  TP=bLo-39
A Long  : side==+1  → entry=bHi,    SL=bLo-17,  TP=bHi+39
Flip L  : side==-1, stop entry at bHi+17, SL=bLo-17, TP=entry+39
Flip S  : side==+1, stop entry at bLo-17, SL=bHi+17, TP=entry-39
```

### 1.3 Trade Resolution
- Primary trades: market entry at bar open 10:05, exits resolved bar-by-bar on 1-min data
- Flip trades: stop entry — only executed if price reaches entry level during session
- TP/SL in same bar: SL assumed first (conservative)
- Timeout after 180 minutes: exit at 1-min bar close
- **No slippage, no commissions modelled** (see Section 13)

---

## 2. BASELINE RESULTS — PHASE 1

### A Short (side==-1)
- Trades: 266  |  TP: 46  |  SL: 110  |  Timeout: 110
- Win Rate (TP/all): 17.3%  |  Required for BE: 30.4%
- Profit Factor: 0.939  |  Total PnL: -180.67 pts
- Avg Win: 23.78 pts  |  Avg Loss: -20.02 pts
- Annualised Sharpe: -0.4338
- Max Drawdown: 272.82 pts

### A Long (side==+1)
- Trades: 234  |  TP: 38  |  SL: 101  |  Timeout: 95
- Win Rate (TP/all): 16.2%  |  Required for BE: 30.4%
- Profit Factor: 0.8117  |  Total PnL: -513.38 pts
- Avg Win: 23.05 pts  |  Avg Loss: -19.75 pts
- Annualised Sharpe: -1.4424
- Max Drawdown: 504.14 pts

### Flip Long (conditional on A Short SL hit))
- Trades: 112  |  TP: 24  |  SL: 11  |  Timeout: 77
- Win Rate (TP/all): 21.4%  |  Required for BE: 30.4%
- Profit Factor: 1.3843  |  Total PnL: 375.03 pts
- Avg Win: 22.9 pts  |  Avg Loss: -18.41 pts
- Annualised Sharpe: 2.1066
- Max Drawdown: 225.44 pts

### Flip Short (conditional on A Long SL hit)
- Trades: 101  |  TP: 9  |  SL: 8  |  Timeout: 84
- Win Rate (TP/all): 8.9%  |  Required for BE: 30.4%
- Profit Factor: 1.1372  |  Total PnL: 102.91 pts
- Avg Win: 15.79 pts  |  Avg Loss: -16.3 pts
- Annualised Sharpe: 0.7793
- Max Drawdown: 203.34 pts

### Combined Primary (A Short + A Long)
- Trades: 500  |  Win Rate: 16.8%  |  PF: 0.878
- Total PnL: -694.05 pts  |  Sharpe: -0.8989

---

## 3. MFE / MAE ANALYSIS — PHASE 2

MFE = Maximum Favourable Excursion (best point in trade's favour)
MAE = Maximum Adverse Excursion (worst point against trade)

### ASHORT
| Metric | P10 | P25 | P50 | P75 | P90 | P95 | Mean |
|--------|-----|-----|-----|-----|-----|-----|------|
| MFE    | 1.2 | 6.1 | 14.6 | 31.9 | 39.9 | 41.0 | 18.9 |
| MAE    | 4.0 | 9.1 | 18.0 | 23.6 | 29.8 | 33.6 | 17.7 |
- % trades reaching TP level (MFE≥39): 17.3%
- % trades reaching SL level (MAE≥17): 56.4%
- % trades with MFE≥20: 41.7%
- % trades with MFE≥10: 64.3%

### FLIPSHORT
| Metric | P10 | P25 | P50 | P75 | P90 | P95 | Mean |
|--------|-----|-----|-----|-----|-----|-----|------|
| MFE    | 2.0 | 6.0 | 15.1 | 25.1 | 38.1 | 39.4 | 16.7 |
| MAE    | 3.6 | 6.9 | 13.4 | 24.4 | 36.0 | 39.0 | 16.7 |
- % trades reaching TP level (MFE≥39): 8.9%
- % trades reaching SL level (MAE≥17): 41.6%
- % trades with MFE≥20: 33.7%
- % trades with MFE≥10: 65.3%

### ALONG
| Metric | P10 | P25 | P50 | P75 | P90 | P95 | Mean |
|--------|-----|-----|-----|-----|-----|-----|------|
| MFE    | 1.1 | 5.4 | 15.0 | 31.9 | 39.5 | 40.4 | 18.1 |
| MAE    | 4.0 | 10.1 | 18.1 | 22.9 | 29.1 | 31.4 | 17.2 |
- % trades reaching TP level (MFE≥39): 16.2%
- % trades reaching SL level (MAE≥17): 55.1%
- % trades with MFE≥20: 40.6%
- % trades with MFE≥10: 63.7%

### FLIPLONG
| Metric | P10 | P25 | P50 | P75 | P90 | P95 | Mean |
|--------|-----|-----|-----|-----|-----|-----|------|
| MFE    | 2.7 | 5.9 | 13.5 | 31.2 | 39.4 | 40.0 | 18.2 |
| MAE    | 4.1 | 6.0 | 15.5 | 25.3 | 35.8 | 42.4 | 17.2 |
- % trades reaching TP level (MFE≥39): 21.4%
- % trades reaching SL level (MAE≥17): 47.3%
- % trades with MFE≥20: 37.5%
- % trades with MFE≥10: 61.6%

---

## 4. FIRST-PASSAGE ANALYSIS — PHASE 3

Probability of price reaching symmetric excursion levels post-entry:

### ASHORT
| Level | P(reach favour) | P(reach adverse) |
|-------|----------------|-----------------|
| ±5 pts | 77.4% | 86.1% |
| ±10 pts | 64.3% | 72.2% |
| ±15 pts | 49.2% | 60.5% |
| ±17 pts | 45.1% | 56.4% |
| ±20 pts | 41.7% | 39.9% |
| ±25 pts | 36.5% | 20.7% |
| ±30 pts | 28.2% | 10.2% |
| ±39 pts | 17.3% | 3.0% |
| ±50 pts | 1.9% | 1.1% |
| ±75 pts | 0.0% | 0.0% |
| ±100 pts | 0.0% | 0.0% |

### FLIPSHORT
| Level | P(reach favour) | P(reach adverse) |
|-------|----------------|-----------------|
| ±5 pts | 77.2% | 80.2% |
| ±10 pts | 65.3% | 61.4% |
| ±15 pts | 50.5% | 48.5% |
| ±17 pts | 41.6% | 41.6% |
| ±20 pts | 33.7% | 33.7% |
| ±25 pts | 26.7% | 22.8% |
| ±30 pts | 16.8% | 15.8% |
| ±39 pts | 8.9% | 5.0% |
| ±50 pts | 0.0% | 1.0% |
| ±75 pts | 0.0% | 0.0% |
| ±100 pts | 0.0% | 0.0% |

### ALONG
| Level | P(reach favour) | P(reach adverse) |
|-------|----------------|-----------------|
| ±5 pts | 76.1% | 86.3% |
| ±10 pts | 63.7% | 75.2% |
| ±15 pts | 50.4% | 59.8% |
| ±17 pts | 44.9% | 55.1% |
| ±20 pts | 40.6% | 41.9% |
| ±25 pts | 33.3% | 19.7% |
| ±30 pts | 26.9% | 9.0% |
| ±39 pts | 16.2% | 0.4% |
| ±50 pts | 0.0% | 0.4% |
| ±75 pts | 0.0% | 0.0% |
| ±100 pts | 0.0% | 0.0% |

### FLIPLONG
| Level | P(reach favour) | P(reach adverse) |
|-------|----------------|-----------------|
| ±5 pts | 81.2% | 84.8% |
| ±10 pts | 61.6% | 62.5% |
| ±15 pts | 48.2% | 50.9% |
| ±17 pts | 44.6% | 47.3% |
| ±20 pts | 37.5% | 35.7% |
| ±25 pts | 31.2% | 25.0% |
| ±30 pts | 26.8% | 18.8% |
| ±39 pts | 21.4% | 8.9% |
| ±50 pts | 0.0% | 0.9% |
| ±75 pts | 0.0% | 0.0% |
| ±100 pts | 0.0% | 0.0% |

---

## 5. TRADE PATH — FORWARD RETURNS AT N MINUTES — PHASE 4

### ASHORT — Mean forward return at N minutes post-entry
| Minutes | N | Mean PnL | Median | Win% | P25 | P75 |
|---------|---|----------|--------|------|-----|-----|
| 1 | 266 | -1.22 | -0.13 | 43.6% | -3.03 | 2.00 |
| 5 | 266 | -1.74 | -0.73 | 43.2% | -7.02 | 3.90 |
| 10 | 266 | -1.13 | -0.92 | 46.2% | -8.55 | 6.54 |
| 15 | 266 | -0.69 | 0.42 | 50.7% | -9.06 | 7.02 |
| 30 | 266 | -0.24 | 0.05 | 50.0% | -10.39 | 9.26 |
| 60 | 258 | -1.26 | -1.95 | 46.9% | -15.23 | 11.98 |
| 90 | 258 | -2.29 | -4.02 | 44.2% | -19.27 | 18.48 |
| 120 | 258 | -2.90 | -2.08 | 46.1% | -20.30 | 14.95 |
| 180 | 258 | -2.80 | -2.03 | 46.9% | -20.68 | 18.89 |

### ALONG — Mean forward return at N minutes post-entry
| Minutes | N | Mean PnL | Median | Win% | P25 | P75 |
|---------|---|----------|--------|------|-----|-----|
| 1 | 234 | -1.53 | -1.03 | 38.0% | -4.00 | 1.26 |
| 5 | 234 | -1.12 | -0.78 | 46.2% | -5.98 | 3.96 |
| 10 | 234 | -1.78 | -1.08 | 44.9% | -7.28 | 5.36 |
| 15 | 234 | -1.81 | -0.13 | 48.7% | -9.83 | 5.93 |
| 30 | 234 | -1.68 | -1.68 | 46.6% | -11.99 | 8.51 |
| 60 | 221 | -1.62 | -2.47 | 43.4% | -14.00 | 11.03 |
| 90 | 221 | -1.69 | -2.03 | 46.6% | -17.31 | 16.00 |
| 120 | 221 | -2.08 | -2.10 | 47.5% | -18.47 | 14.10 |
| 180 | 221 | -3.33 | -4.69 | 45.2% | -20.94 | 15.00 |

---

## 6. SL / TP MATRIX — PHASE 5

Best SL/TP combinations by Profit Factor (top 10 per primary branch):

### ASHORT
| SL | TP | PF | Win% | Total PnL |
|----|----|----|------|-----------|
| 50 | 25 | 16.167 | 36.5% | 2275.0 |
| 50 | 30 | 15.000 | 28.2% | 2100.0 |
| 50 | 20 | 14.667 | 41.4% | 2050.0 |
| 50 | 15 | 13.000 | 48.9% | 1800.0 |
| 50 | 39 | 11.960 | 17.3% | 1644.0 |
| 50 | 10 | 11.267 | 63.5% | 1540.0 |
| 40 | 25 | 8.571 | 36.1% | 2120.0 |
| 40 | 30 | 8.036 | 28.2% | 1970.0 |
| 40 | 20 | 7.786 | 41.0% | 1900.0 |
| 40 | 15 | 6.857 | 48.1% | 1640.0 |

### ALONG
| SL | TP | PF | Win% | Total PnL |
|----|----|----|------|-----------|
| 40 | 25 | 48.750 | 33.3% | 1910.0 |
| 40 | 20 | 47.500 | 40.6% | 1860.0 |
| 40 | 30 | 47.250 | 26.9% | 1850.0 |
| 40 | 15 | 44.250 | 50.4% | 1730.0 |
| 50 | 25 | 39.000 | 33.3% | 1900.0 |
| 50 | 20 | 38.000 | 40.6% | 1850.0 |
| 50 | 30 | 37.800 | 26.9% | 1840.0 |
| 40 | 10 | 37.250 | 63.7% | 1450.0 |
| 40 | 39 | 37.050 | 16.2% | 1442.0 |
| 50 | 15 | 35.400 | 50.4% | 1720.0 |

---

## 7. TEMPORAL ANALYSIS — PHASE 6

### 7.1 Year-by-Year (all branches combined)
| Year | Trades | Win Rate | Total PnL |
|------|--------|----------|-----------|
| 2024 | 197 | 9.1% | -370.5 |
| 2025 | 298 | 17.8% | 362.8 |
| 2026 | 218 | 21.1% | -208.4 |

### 7.2 Month Breakdown (all branches combined)
| Month | Trades | Win Rate | Total PnL |
|-------|--------|----------|-----------|
| Jan | 84 | 15.5% | -140.1 |
| Feb | 76 | 21.1% | 306.9 |
| Mar | 78 | 17.9% | 26.1 |
| Apr | 58 | 22.4% | -37.5 |
| May | 49 | 18.4% | -84.9 |
| Jun | 53 | 22.6% | 139.4 |
| Jul | 60 | 16.7% | -155.1 |
| Aug | 45 | 11.1% | 0.7 |
| Sep | 40 | 17.5% | 31.8 |
| Oct | 66 | 9.1% | -189.3 |
| Nov | 57 | 10.5% | -75.4 |
| Dec | 47 | 12.8% | -38.8 |

### 7.3 Day-of-Week Breakdown (all branches combined)
| Day | Trades | Win Rate | Total PnL |
|-----|--------|----------|-----------|
| Mon | 146 | 14.4% | -327.0 |
| Tue | 132 | 24.2% | 684.6 |
| Wed | 148 | 14.2% | -445.2 |
| Thu | 140 | 15.0% | -33.6 |
| Fri | 147 | 15.0% | -94.8 |

---

## 8. BOOTSTRAP CONFIDENCE INTERVALS — PHASE 7

2000 bootstrap resamples (n=trades), 95% CI on total PnL:

| Branch | Actual PnL | CI Lo | CI Hi | Profitable? |
|--------|------------|-------|-------|-------------|
| ashort | -180.7 | -935.2 | 615.3 | NO |
| flipshort | 102.9 | -318.4 | 528.4 | NO |
| along | -513.4 | -1259.0 | 182.4 | NO |
| fliplong | 375.0 | -150.9 | 880.1 | NO |
| _primary | -694.0 | -1801.8 | 419.8 | NO |

---

## 9. PLACEBO / RANDOMISATION TESTS — PHASE 8

H0: observed PnL could occur by chance from random outcome ordering
p-value = fraction of 2000 permutations with total PnL ≥ actual

| Branch | Actual PnL | PF | Sign-flip p | t-test p | Rejects H0? |
|--------|------------|-----|-------------|----------|-------------|
| ashort | -180.7 | 0.939 | 0.6685 | 0.6562 | NO |
| flipshort | 102.9 | 1.1372 | 0.3160 | 0.6228 | NO |
| along | -513.4 | 0.8117 | 0.9195 | 0.1659 | NO |
| fliplong | 375.0 | 1.3843 | 0.0765 | 0.1630 | NO |

---

## 10. OUT-OF-SAMPLE (YEAR WALK-FORWARD) — PHASE 9

Train on all prior years, test on current year:

| Test Year | IS Trades | OOS Trades | IS PF | OOS PF | OOS PnL |
|-----------|-----------|-----------|-------|--------|---------|
| 2025 | 197 | 298 | 0.789 | 1.1257 | 362.8 |
| 2026 | 495 | 218 | 0.9983 | 0.9248 | -208.4 |

---

## 11. BUY-AND-HOLD COMPARISON

- Period start price: 7599.6
- Period end price:   9095.0
- B&H return:         1495.3 pts (19.68%)

- All-branch strategy total PnL: -216.1 pts
- Primary-branch total PnL: -694.0 pts

---

## 12. COSTS & REALISTIC EDGE

AU200 (AUS200) typical costs (Dukascopy-style):
- Spread: ~1.5–3 pts (Dukascopy AU200 spread)
- Commission: ~1–2 pts per side
- **Total friction per trade: ~3–7 pts**

Impact on primary branches:
- A Short: Raw PnL=-180.7 → After costs @3pt=-978.7 to @7pt=-2042.7 pts
- A Long: Raw PnL=-513.4 → After costs @3pt=-1215.4 to @7pt=-2151.4 pts

---

## 13. STATISTICAL VALIDITY GATES

| Gate | Requirement | Status |
|------|-------------|--------|
| Random null (primary, p<0.05) | p=0.1659 | FAIL |
| Bootstrap CI entirely positive | CI=[-1801.8,419.8] | FAIL |
| Beats buy-and-hold | Strategy=-694.0 vs BnH=1495.3 | FAIL |
| Sufficient sample (n≥200 primary) | n=500 | PASS |

---

## 14. FINAL VERDICT

### **NO EVIDENCE OF EDGE** — primary branches lose money; results consistent with random noise

**Primary branches (A Short, A Long):**
- Both branches have PF < 1.0 — they are net losers before costs
- Win rate 16.8% vs breakeven required 30.4%
- After realistic costs (3–7 pts/trade), losses deepen significantly
- Placebo tests: results are consistent with random noise
- Conclusion: **No exploitable edge in the primary branches over this sample**

**Flip branches (Flip Long, Flip Short):**
- Flip Long: PF=1.3843 — marginally positive
- Flip Short: PF=1.1372 — marginally positive
- Only 112 and 101 trades respectively — insufficient for statistical confidence
- Flip Long Sharpe: 2.1066 (over 2 years) — possibly overfitted to regime
- Dominant outcome is TIMEOUT (neither TP nor SL hit) — edge is marginal drift, not momentum

**Overall recommendation:** Do not trade the primary branches as described. The flip branches warrant
further investigation with a longer data sample (minimum 5 years, 1000+ flip signals) and
explicit transaction cost modelling before any live consideration.

---

*Report auto-generated by AU200 10AM Research Pipeline v1.0 — 2026-08-20*
*All prices in AU200 index points. No warranty or investment advice.*