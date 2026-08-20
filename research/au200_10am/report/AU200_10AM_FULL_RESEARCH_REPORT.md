# AU200 10AM Strategy — Full Quantitative Research Report

**Date:** 2026-08-20  |  **Data:** AUSIDXAUD (Dukascopy) 2021-08-20 → 2026-08-20  |  **Timezone:** Australia/Melbourne (DST-aware)

---

## EXECUTIVE SUMMARY

### Verdict

> **NO EVIDENCE OF EDGE** — primary branches lose money; results consistent with random noise

### Key Numbers

| Branch | Trades | Win Rate | PF | Total PnL (pts) | Sharpe |
|--------|--------|----------|----|-----------------|--------|
| A Short | 476 | 15.6% | 0.9158 | -420.11 | -0.5973 |
| A Long | 445 | 14.4% | 0.8757 | -575.77 | -0.899 |
| Flip Long | 180 | 15.0% | 1.3289 | 453.35 | 1.7763 |
| Flip Short | 170 | 7.6% | 0.8954 | -146.51 | -0.671 |
| Primary (A+A) | 921 | 15.0% | 0.8965 | -995.88 | -0.7414 |
| All Branches | 1271 | 14.0% | 0.9444 | -689.03 | -0.3786 |

---

## 1. DATA & METHODOLOGY

### 1.1 Data Source
- **Instrument:** AUSIDXAUD (Dukascopy AU200 CFD, bid-side M1 candles)
- **Download:** `dukascopy-node` npm library, format=array, batchSize=150
- **Total 1-min bars:** 1,149,411 (after dedup and OHLC validation)
- **Sessions analysed:** 921 (days with both 09:50 and 10:00 Melbourne 5-min bars)
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
- Trades: 476  |  TP: 74  |  SL: 177  |  Timeout: 225
- Win Rate (TP/all): 15.6%  |  Required for BE: 30.4%
- Profit Factor: 0.9158  |  Total PnL: -420.11 pts
- Avg Win: 21.96 pts  |  Avg Loss: -18.68 pts
- Annualised Sharpe: -0.5973
- Max Drawdown: 900.09 pts

### A Long (side==+1)
- Trades: 445  |  TP: 64  |  SL: 170  |  Timeout: 211
- Win Rate (TP/all): 14.4%  |  Required for BE: 30.4%
- Profit Factor: 0.8757  |  Total PnL: -575.77 pts
- Avg Win: 21.57 pts  |  Avg Loss: -18.02 pts
- Annualised Sharpe: -0.899
- Max Drawdown: 707.05 pts

### Flip Long (conditional on A Short SL hit))
- Trades: 180  |  TP: 27  |  SL: 13  |  Timeout: 140
- Win Rate (TP/all): 15.0%  |  Required for BE: 30.4%
- Profit Factor: 1.3289  |  Total PnL: 453.35 pts
- Avg Win: 19.91 pts  |  Avg Loss: -15.66 pts
- Annualised Sharpe: 1.7763
- Max Drawdown: 225.44 pts

### Flip Short (conditional on A Long SL hit)
- Trades: 170  |  TP: 13  |  SL: 16  |  Timeout: 141
- Win Rate (TP/all): 7.6%  |  Required for BE: 30.4%
- Profit Factor: 0.8954  |  Total PnL: -146.51 pts
- Avg Win: 15.88 pts  |  Avg Loss: -15.56 pts
- Annualised Sharpe: -0.671
- Max Drawdown: 319.32 pts

### Combined Primary (A Short + A Long)
- Trades: 921  |  Win Rate: 15.0%  |  PF: 0.8965
- Total PnL: -995.88 pts  |  Sharpe: -0.7414

---

## 3. MFE / MAE ANALYSIS — PHASE 2

MFE = Maximum Favourable Excursion (best point in trade's favour)
MAE = Maximum Adverse Excursion (worst point against trade)

### ASHORT
| Metric | P10 | P25 | P50 | P75 | P90 | P95 | Mean |
|--------|-----|-----|-----|-----|-----|-----|------|
| MFE    | 2.0 | 6.1 | 14.8 | 30.6 | 39.6 | 40.5 | 18.3 |
| MAE    | 4.0 | 9.1 | 17.4 | 23.0 | 29.3 | 32.0 | 16.8 |
- % trades reaching TP level (MFE≥39): 15.5%
- % trades reaching SL level (MAE≥17): 52.7%
- % trades with MFE≥20: 39.7%
- % trades with MFE≥10: 62.8%

### FLIPSHORT
| Metric | P10 | P25 | P50 | P75 | P90 | P95 | Mean |
|--------|-----|-----|-----|-----|-----|-----|------|
| MFE    | 2.0 | 5.0 | 13.2 | 22.8 | 34.6 | 39.2 | 15.5 |
| MAE    | 3.6 | 7.0 | 13.2 | 23.1 | 35.5 | 38.5 | 16.2 |
- % trades reaching TP level (MFE≥39): 7.6%
- % trades reaching SL level (MAE≥17): 38.2%
- % trades with MFE≥20: 31.8%
- % trades with MFE≥10: 59.4%

### ALONG
| Metric | P10 | P25 | P50 | P75 | P90 | P95 | Mean |
|--------|-----|-----|-----|-----|-----|-----|------|
| MFE    | 1.1 | 6.0 | 14.0 | 28.5 | 39.4 | 40.3 | 17.6 |
| MAE    | 3.4 | 8.5 | 17.4 | 22.1 | 28.0 | 31.0 | 16.2 |
- % trades reaching TP level (MFE≥39): 14.4%
- % trades reaching SL level (MAE≥17): 52.1%
- % trades with MFE≥20: 39.1%
- % trades with MFE≥10: 62.7%

### FLIPLONG
| Metric | P10 | P25 | P50 | P75 | P90 | P95 | Mean |
|--------|-----|-----|-----|-----|-----|-----|------|
| MFE    | 2.1 | 5.6 | 13.2 | 25.2 | 39.1 | 39.9 | 16.8 |
| MAE    | 2.9 | 5.1 | 11.0 | 22.0 | 32.6 | 41.9 | 15.2 |
- % trades reaching TP level (MFE≥39): 15.0%
- % trades reaching SL level (MAE≥17): 40.0%
- % trades with MFE≥20: 34.4%
- % trades with MFE≥10: 62.2%

---

## 4. FIRST-PASSAGE ANALYSIS — PHASE 3

Probability of price reaching symmetric excursion levels post-entry:

### ASHORT
| Level | P(reach favour) | P(reach adverse) |
|-------|----------------|-----------------|
| ±5 pts | 77.9% | 86.1% |
| ±10 pts | 62.8% | 71.6% |
| ±15 pts | 49.4% | 58.4% |
| ±17 pts | 44.1% | 52.7% |
| ±20 pts | 39.7% | 37.0% |
| ±25 pts | 33.0% | 17.4% |
| ±30 pts | 26.3% | 8.6% |
| ±39 pts | 15.6% | 2.1% |
| ±50 pts | 1.1% | 0.8% |
| ±75 pts | 0.0% | 0.0% |
| ±100 pts | 0.0% | 0.0% |

### FLIPSHORT
| Level | P(reach favour) | P(reach adverse) |
|-------|----------------|-----------------|
| ±5 pts | 75.3% | 81.8% |
| ±10 pts | 59.4% | 59.4% |
| ±15 pts | 45.3% | 45.3% |
| ±17 pts | 39.4% | 38.2% |
| ±20 pts | 31.8% | 30.6% |
| ±25 pts | 22.9% | 20.6% |
| ±30 pts | 14.7% | 15.3% |
| ±39 pts | 7.6% | 4.1% |
| ±50 pts | 0.6% | 1.2% |
| ±75 pts | 0.0% | 0.0% |
| ±100 pts | 0.0% | 0.0% |

### ALONG
| Level | P(reach favour) | P(reach adverse) |
|-------|----------------|-----------------|
| ±5 pts | 78.0% | 84.7% |
| ±10 pts | 62.7% | 71.2% |
| ±15 pts | 48.1% | 56.4% |
| ±17 pts | 44.3% | 52.1% |
| ±20 pts | 39.1% | 37.3% |
| ±25 pts | 30.8% | 16.6% |
| ±30 pts | 23.2% | 7.2% |
| ±39 pts | 14.4% | 0.7% |
| ±50 pts | 0.2% | 0.2% |
| ±75 pts | 0.0% | 0.0% |
| ±100 pts | 0.0% | 0.0% |

### FLIPLONG
| Level | P(reach favour) | P(reach adverse) |
|-------|----------------|-----------------|
| ±5 pts | 78.9% | 78.3% |
| ±10 pts | 62.2% | 55.6% |
| ±15 pts | 48.3% | 43.3% |
| ±17 pts | 42.2% | 40.0% |
| ±20 pts | 34.4% | 27.8% |
| ±25 pts | 26.1% | 20.0% |
| ±30 pts | 21.1% | 14.4% |
| ±39 pts | 15.0% | 6.7% |
| ±50 pts | 0.0% | 0.6% |
| ±75 pts | 0.0% | 0.0% |
| ±100 pts | 0.0% | 0.0% |

---

## 5. TRADE PATH — FORWARD RETURNS AT N MINUTES — PHASE 4

### ASHORT — Mean forward return at N minutes post-entry
| Minutes | N | Mean PnL | Median | Win% | P25 | P75 |
|---------|---|----------|--------|------|-----|-----|
| 1 | 476 | -1.06 | -0.13 | 43.7% | -3.02 | 1.90 |
| 5 | 476 | -1.44 | -0.88 | 43.7% | -6.24 | 3.97 |
| 10 | 476 | -0.59 | -0.91 | 47.5% | -7.08 | 5.94 |
| 15 | 476 | -0.22 | -0.60 | 48.9% | -7.47 | 6.70 |
| 30 | 476 | -0.17 | -0.15 | 49.2% | -9.98 | 9.00 |
| 60 | 442 | -1.15 | -1.54 | 47.5% | -14.26 | 12.00 |
| 90 | 442 | -2.24 | -2.88 | 45.2% | -16.32 | 14.85 |
| 120 | 442 | -2.92 | -2.06 | 45.9% | -19.75 | 13.62 |
| 180 | 442 | -2.83 | -2.56 | 45.7% | -19.93 | 14.06 |

### ALONG — Mean forward return at N minutes post-entry
| Minutes | N | Mean PnL | Median | Win% | P25 | P75 |
|---------|---|----------|--------|------|-----|-----|
| 1 | 445 | -1.24 | -0.91 | 40.7% | -3.10 | 1.17 |
| 5 | 444 | -0.65 | -0.92 | 45.5% | -5.03 | 4.00 |
| 10 | 444 | -1.00 | -0.97 | 46.0% | -6.47 | 5.37 |
| 15 | 444 | -1.03 | 0.00 | 49.1% | -8.33 | 6.09 |
| 30 | 444 | -0.93 | -1.12 | 47.8% | -10.62 | 9.31 |
| 60 | 395 | -1.39 | -1.94 | 45.1% | -13.35 | 10.03 |
| 90 | 395 | -1.04 | -0.90 | 48.6% | -15.97 | 13.80 |
| 120 | 395 | -0.75 | -0.13 | 49.4% | -17.22 | 13.54 |
| 180 | 395 | -1.53 | -3.97 | 45.3% | -17.97 | 14.98 |

---

## 6. SL / TP MATRIX — PHASE 5

Best SL/TP combinations by Profit Factor (top 10 per primary branch):

### ASHORT
| SL | TP | PF | Win% | Total PnL |
|----|----|----|------|-----------|
| 50 | 25 | 19.625 | 33.0% | 3725.0 |
| 50 | 20 | 18.800 | 39.5% | 3560.0 |
| 50 | 30 | 18.750 | 26.3% | 3550.0 |
| 50 | 15 | 17.550 | 49.2% | 3310.0 |
| 50 | 10 | 14.850 | 62.4% | 2770.0 |
| 50 | 39 | 14.430 | 15.5% | 2686.0 |
| 40 | 25 | 10.833 | 32.8% | 3540.0 |
| 40 | 30 | 10.417 | 26.3% | 3390.0 |
| 40 | 20 | 10.333 | 39.1% | 3360.0 |
| 40 | 15 | 9.625 | 48.5% | 3105.0 |

### ALONG
| SL | TP | PF | Win% | Total PnL |
|----|----|----|------|-----------|
| 50 | 20 | 69.600 | 39.1% | 3430.0 |
| 50 | 25 | 68.500 | 30.8% | 3375.0 |
| 50 | 15 | 64.200 | 48.1% | 3160.0 |
| 50 | 30 | 61.800 | 23.1% | 3040.0 |
| 50 | 10 | 55.800 | 62.7% | 2740.0 |
| 50 | 39 | 49.920 | 14.4% | 2446.0 |
| 40 | 20 | 28.833 | 38.9% | 3340.0 |
| 40 | 25 | 28.333 | 30.6% | 3280.0 |
| 40 | 15 | 26.500 | 47.6% | 3060.0 |
| 40 | 30 | 25.750 | 23.1% | 2970.0 |

---

## 7. TEMPORAL ANALYSIS — PHASE 6

### 7.1 Year-by-Year (all branches combined)
| Year | Trades | Win Rate | Total PnL |
|------|--------|----------|-----------|
| 2021 | 104 | 24.0% | 327.4 |
| 2022 | 168 | 10.1% | -440.0 |
| 2023 | 216 | 6.5% | -131.1 |
| 2024 | 267 | 8.6% | -599.8 |
| 2025 | 298 | 17.8% | 362.8 |
| 2026 | 218 | 21.1% | -208.4 |

### 7.2 Month Breakdown (all branches combined)
| Month | Trades | Win Rate | Total PnL |
|-------|--------|----------|-----------|
| Jan | 109 | 12.8% | -166.1 |
| Feb | 116 | 19.8% | 368.0 |
| Mar | 109 | 17.4% | 146.2 |
| Apr | 106 | 14.1% | -266.6 |
| May | 87 | 11.5% | -227.3 |
| Jun | 86 | 19.8% | 284.2 |
| Jul | 113 | 14.2% | -240.2 |
| Aug | 104 | 9.6% | -179.6 |
| Sep | 85 | 20.0% | 308.3 |
| Oct | 117 | 8.6% | -475.1 |
| Nov | 119 | 13.5% | 41.7 |
| Dec | 120 | 9.2% | -282.4 |

### 7.3 Day-of-Week Breakdown (all branches combined)
| Day | Trades | Win Rate | Total PnL |
|-----|--------|----------|-----------|
| Mon | 241 | 13.3% | -300.7 |
| Tue | 242 | 19.0% | 714.9 |
| Wed | 272 | 12.9% | -799.3 |
| Thu | 256 | 13.3% | -27.8 |
| Fri | 260 | 11.9% | -276.2 |

---

## 8. BOOTSTRAP CONFIDENCE INTERVALS — PHASE 7

2000 bootstrap resamples (n=trades), 95% CI on total PnL:

| Branch | Actual PnL | CI Lo | CI Hi | Profitable? |
|--------|------------|-------|-------|-------------|
| ashort | -420.1 | -1408.5 | 603.8 | NO |
| flipshort | -146.5 | -646.3 | 368.6 | NO |
| along | -575.8 | -1498.0 | 432.8 | NO |
| fliplong | 453.4 | -162.7 | 1023.7 | NO |
| _primary | -995.9 | -2408.5 | 416.7 | NO |

---

## 9. PLACEBO / RANDOMISATION TESTS — PHASE 8

H0: observed PnL could occur by chance from random outcome ordering
p-value = fraction of 2000 permutations with total PnL ≥ actual

| Branch | Actual PnL | PF | Sign-flip p | t-test p | Rejects H0? |
|--------|------------|-----|-------------|----------|-------------|
| ashort | -420.1 | 0.9158 | 0.7880 | 0.4121 | NO |
| flipshort | -146.5 | 0.8954 | 0.7045 | 0.5823 | NO |
| along | -575.8 | 0.8757 | 0.8805 | 0.2328 | NO |
| fliplong | 453.4 | 1.3289 | 0.0670 | 0.1350 | NO |

---

## 10. OUT-OF-SAMPLE (YEAR WALK-FORWARD) — PHASE 9

Train on all prior years, test on current year:

| Test Year | IS Trades | OOS Trades | IS PF | OOS PF | OOS PnL |
|-----------|-----------|-----------|-------|--------|---------|
| 2022 | 104 | 168 | 1.3228 | 0.7425 | -440.0 |
| 2023 | 272 | 216 | 0.9587 | 0.9162 | -131.1 |
| 2024 | 488 | 267 | 0.9432 | 0.7553 | -599.8 |
| 2025 | 755 | 298 | 0.8748 | 1.1257 | 362.8 |
| 2026 | 1053 | 218 | 0.9501 | 0.9248 | -208.4 |

---

## 11. BUY-AND-HOLD COMPARISON

- Period start price: 7479.7
- Period end price:   9095.0
- B&H return:         1615.3 pts (21.60%)

- All-branch strategy total PnL: -689.0 pts
- Primary-branch total PnL: -995.9 pts

---

## 12. COSTS & REALISTIC EDGE

AU200 (AUS200) typical costs (Dukascopy-style):
- Spread: ~1.5–3 pts (Dukascopy AU200 spread)
- Commission: ~1–2 pts per side
- **Total friction per trade: ~3–7 pts**

Impact on primary branches:
- A Short: Raw PnL=-420.1 → After costs @3pt=-1848.1 to @7pt=-3752.1 pts
- A Long: Raw PnL=-575.8 → After costs @3pt=-1910.8 to @7pt=-3690.8 pts

---

## 13. STATISTICAL VALIDITY GATES

| Gate | Requirement | Status |
|------|-------------|--------|
| Random null (primary, p<0.05) | p=0.2328 | FAIL |
| Bootstrap CI entirely positive | CI=[-2408.5,416.7] | FAIL |
| Beats buy-and-hold | Strategy=-995.9 vs BnH=1615.3 | FAIL |
| Sufficient sample (n≥200 primary) | n=921 | PASS |

---

## 14. FINAL VERDICT

### **NO EVIDENCE OF EDGE** — primary branches lose money; results consistent with random noise

**Primary branches (A Short, A Long):**
- Both branches have PF < 1.0 — they are net losers before costs
- Win rate 15.0% vs breakeven required 30.4%
- After realistic costs (3–7 pts/trade), losses deepen significantly
- Placebo tests: results are consistent with random noise
- Conclusion: **No exploitable edge in the primary branches over this sample**

**Flip branches (Flip Long, Flip Short):**
- Flip Long: PF=1.3289 — marginally positive
- Flip Short: PF=0.8954 — marginally positive
- Only 180 and 170 trades respectively — insufficient for statistical confidence
- Flip Long Sharpe: 1.7763 (over 2 years) — possibly overfitted to regime
- Dominant outcome is TIMEOUT (neither TP nor SL hit) — edge is marginal drift, not momentum

**Overall recommendation:** Do not trade the primary branches as described. The flip branches warrant
further investigation with a longer data sample (minimum 5 years, 1000+ flip signals) and
explicit transaction cost modelling before any live consideration.

---

*Report auto-generated by AU200 10AM Research Pipeline v1.0 — 2026-08-20*
*All prices in AU200 index points. No warranty or investment advice.*