# Gold 10AM — robustness (Phases 28–34)

_Round-trip cost of **$1.26** (twice the measured median spread) is charged to every trade in this file._


## Phase 28 — Chronological out-of-sample

Split declared before any parameter search:

- **DEV** 2024-08-20 → 2025-08-19
- **VAL** 2025-08-20 → 2026-02-19
- **HOLD** 2026-02-20 → 2026-08-19 (opened once, below)

Baseline SL $17 / TP $39, round-trip cost $1.26 charged to P&L.

| Set | N | Win % | Avg win | Avg loss | Expectancy | PF | Net $ | Max DD | Payoff | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A Short DEV | 71 | 42.3 | 21.16 | -15.70 | -0.121 | 0.987 | -8.61 | 276.98 | 1.35 | -0.03 |
| A Short VAL | 22 | 27.3 | 18.68 | -17.54 | -7.660 | 0.399 | -168.51 | 189.21 | 1.07 | -0.89 |
| A Short HOLD | 54 | 40.7 | 36.04 | -17.76 | 4.156 | 1.395 | 224.45 | 234.94 | 2.03 | 0.96 |
| A Long DEV | 85 | 41.2 | 16.75 | -13.65 | -1.133 | 0.859 | -96.32 | 291.17 | 1.23 | -0.33 |
| A Long VAL | 27 | 63.0 | 20.10 | -18.26 | 5.892 | 1.871 | 159.09 | 36.52 | 1.10 | 4.36 |
| A Long HOLD | 53 | 35.8 | 35.65 | -18.26 | 1.065 | 1.091 | 56.44 | 125.38 | 1.95 | 0.45 |
| Flip Long DEV | 73 | 49.3 | 19.59 | -12.84 | 3.154 | 1.485 | 230.26 | 160.93 | 1.53 | 1.43 |
| Flip Long VAL | 24 | 50.0 | 26.95 | -15.67 | 5.640 | 1.720 | 135.36 | 91.30 | 1.72 | 1.48 |
| Flip Long HOLD | 53 | 32.1 | 32.21 | -18.09 | -1.957 | 0.841 | -103.70 | 249.18 | 1.78 | -0.42 |
| Flip Short DEV | 75 | 44.0 | 14.45 | -11.06 | 0.163 | 1.026 | 12.20 | 179.02 | 1.31 | 0.07 |
| Flip Short VAL | 23 | 26.1 | 18.10 | -17.87 | -8.487 | 0.357 | -195.20 | 198.21 | 1.01 | -0.98 |
| Flip Short HOLD | 47 | 48.9 | 33.25 | -17.96 | 7.100 | 1.774 | 333.72 | 91.30 | 1.85 | 3.66 |


## Phase 29 — Walk-forward

Each fold optimises SL and TP on its training window over the same coarse grid, then applies the single best cell to the immediately following test window. All planned folds are reported — none are dropped.


**6m train / 2m test**

| Logic | Folds | Profitable folds | OOS trades | Win % | Expectancy | PF | Net $ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A Short | 6 | 0/6 | 90 | 31.1 | -5.033 | 0.498 | -453.00 |
| A Long | 7 | 3/7 | 113 | 31.9 | -0.786 | 0.906 | -88.86 |
| Flip Long | 7 | 3/7 | 110 | 36.4 | -0.455 | 0.955 | -50.03 |
| Flip Short | 7 | 4/7 | 102 | 55.9 | 3.937 | 1.540 | 401.53 |


**9m train / 3m test**

| Logic | Folds | Profitable folds | OOS trades | Win % | Expectancy | PF | Net $ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A Short | 3 | 1/3 | 78 | 43.6 | -4.295 | 0.632 | -335.04 |
| A Long | 3 | 1/3 | 78 | 29.5 | -1.173 | 0.856 | -91.48 |
| Flip Long | 3 | 1/3 | 81 | 43.2 | 0.708 | 1.066 | 57.31 |
| Flip Short | 3 | 0/3 | 70 | 45.7 | -3.011 | 0.676 | -210.78 |


## Phase 30 — Clock placebo: is 09:50/10:00 special?

The whole method is rebuilt at nearby anchor pairs, keeping the 10-minute reference→body spacing. To make the comparison fair, **only days on which every anchor pair exists** are used, so a pair is never flattered by trading a different set of days.

Days on which all 8 anchor pairs exist: **338** (the baseline alone has 339; the shared set is smaller because the earlier anchors fall inside the maintenance break on more days).

| Anchor pair | A Short | A Long | Flip Long | Flip Short |
| --- | --- | --- | --- | --- |
| 09:30/09:40  | -0.04 (1.00, n=170) | -0.09 (0.99, n=149) | 1.41 (1.15, n=167) | -0.94 (0.90, n=135) |
| 09:35/09:45  | 1.16 (1.13, n=144) | 1.66 (1.18, n=178) | 0.37 (1.04, n=140) | -1.06 (0.89, n=160) |
| 09:40/09:50  | 1.98 (1.22, n=134) | 0.31 (1.03, n=186) | -0.81 (0.92, n=136) | -1.02 (0.90, n=167) |
| 09:45/09:55  | 2.35 (1.26, n=140) | 2.21 (1.25, n=177) | -0.45 (0.95, n=139) | -1.64 (0.83, n=161) |
| 09:50/10:00 **BASE** | 0.32 (1.03, n=147) | 0.64 (1.07, n=164) | 1.75 (1.20, n=150) | 1.17 (1.14, n=144) |
| 09:55/10:05  | -0.92 (0.91, n=147) | 1.67 (1.19, n=161) | 0.12 (1.01, n=148) | 1.89 (1.22, n=142) |
| 10:00/10:10  | -0.81 (0.92, n=160) | 3.12 (1.39, n=152) | -0.48 (0.95, n=154) | 1.13 (1.13, n=131) |
| 10:05/10:15  | 2.91 (1.34, n=143) | 1.70 (1.20, n=175) | 0.58 (1.07, n=129) | -2.64 (0.75, n=150) |


## Phase 31 — Random placebos

Three nulls, each preserving something real about the strategy and destroying the claimed edge. The observed value must sit outside the null distribution to mean anything.

| Logic | Observed exp $ | Null 1 random direction | p | Null 2 sign flip | p | Null 3 random entry time | p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A Short | 0.322 | 0.09 [-2.59,2.73] | 0.448 | -1.27 [-4.35,1.88] | 0.205 | -0.58 [-2.26,1.42] | 0.237 |
| A Long | 0.722 | -0.02 [-2.44,2.56] | 0.308 | -1.25 [-3.97,1.60] | 0.123 | -0.67 [-2.26,0.86] | 0.075 |
| Flip Long | 1.746 | 0.06 [-2.43,2.75] | 0.142 | -1.18 [-4.34,1.76] | 0.051 | -0.29 [-2.20,1.46] | 0.033 |
| Flip Short | 1.039 | -0.79 [-3.40,1.72] | 0.108 | -1.29 [-4.07,1.61] | 0.093 | -0.37 [-2.09,1.25] | 0.077 |


## Phase 32 — Block bootstrap (block = 10 trades, 5,000 resamples)

Trades from the same regime are not independent, so the resample is by blocks of ten consecutive trades rather than by single trades.

| Logic | N | Expectancy (median [5,95]) | PF | Net $ | Max DD | P(net > 0) |
| --- | --- | --- | --- | --- | --- | --- |
| A Short | 147 | -0.22 [-4.23, 4.17] | 0.98 [0.63, 1.45] | -32 [-622, 613] | 388 [185, 776] | 46.7% |
| A Long | 165 | 0.48 [-2.37, 3.23] | 1.05 [0.77, 1.40] | 79 [-390, 533] | 266 [135, 537] | 60.8% |
| Flip Long | 150 | 1.93 [-1.31, 5.05] | 1.22 [0.87, 1.70] | 290 [-197, 757] | 221 [124, 438] | 83.8% |
| Flip Short | 145 | 0.62 [-2.37, 3.77] | 1.07 [0.74, 1.49] | 90 [-343, 546] | 249 [129, 495] | 63.2% |


## Phase 33 — Monte Carlo

Each run reshuffles trade order, draws a round-trip cost from the measured spread distribution scaled for slippage, and randomly drops 10% of trades as missed fills.

| Logic | Median net $ | 5th pct | 95th pct | P(profit) | Median DD | 95th DD | Median losing streak | 95th streak |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A Short | -17 | -188 | 155 | 43.3% | 283 | 450 | 8 | 13 |
| A Long | 42 | -141 | 218 | 64.9% | 255 | 414 | 8 | 12 |
| Flip Long | 176 | 3 | 340 | 95.4% | 206 | 336 | 7 | 12 |
| Flip Short | 78 | -86 | 228 | 78.5% | 221 | 355 | 7 | 12 |


## Phase 34 — Multiple-testing accounting

| Family | Combinations evaluated |
| --- | --- |
| logic branches and combinations (Phase 1) | 10 |
| first-passage barriers (Phase 6) | 64 |
| ATR-scaled barriers (Phase 7b) | 48 |
| fixed stops (Phase 8) | 76 |
| fixed targets (Phase 9) | 76 |
| SL x TP surface cells (Phase 10) | 400 |
| time stops (Phase 11) | 44 |
| structure terciles (Phase 13) | 84 |
| side definitions (Phase 14) | 16 |
| volatility regimes (Phase 15) | 20 |
| entry-time bands (Phase 16) | 40 |
| sessions (Phase 17) | 16 |
| weekdays (Phase 19) | 20 |
| entry buffers (Phase 22) | 32 |
| breakout-strength terciles (Phase 23) | 48 |
| exit-management variants (Phase 24) | 32 |
| cost levels (Phase 27) | 36 |
| walk-forward fold optimisations (Phase 29) | 64 |
| clock placebos (Phase 30) | 32 |
| **Total distinct evaluations** | **1158** |


With **K ≈ 1158** evaluations, the selection-adjusted significance bar is t ≥ √(2·ln K) = **3.76**. A result must clear that, not t ≈ 2, before it counts as a discovery rather than as the maximum of a search.
