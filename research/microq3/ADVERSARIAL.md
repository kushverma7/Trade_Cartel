# Adversarial validation — MICRO-Q3 COMPRESSION

Strategy **frozen** exactly as specified on 2026-08-22. Nothing in this document
selects a threshold, and no result below was used to change any rule.

Data: the audited year is 91,629,949 Dukascopy XAUUSD ticks (2025-08-21 →
2026-08-20). The holdout is the twelve months immediately preceding it,
downloaded for this test and never previously examined by either researcher.

Scripts: `research/microq3/code/`. Surfaces and ledgers: `research/microq3/results/`.

---

## 11. NEAR-MISS STUDY — which rule actually carries information

All 128 bearish 18:45–19:00 NY anchors that produce a break, grouped by which
filter they fail. Exits frozen at SL 15.50 / TP 25.50. P(TP) = reached +25.5
before −15.5.

| group | n | P(TP) | PF | exp | net | MFE 50/75/90 | MAE 50/75/90 | maxDD | months + |
|---|---|---|---|---|---|---|---|---|---|
| **PASS ALL FILTERS** | 25 | 72% | **5.13** | +15.47 | +386.7 | 59.4 / 84.4 / 139.6 | 32.6 / 50.2 / 67.1 | 15.9 | 9/12 |
| FAIL BODY ONLY | 16 | 50% | 1.95 | +6.47 | +103.5 | 49.7 / 71.0 / 189.8 | 31.4 / 46.7 / 81.4 | 31.7 | 7/11 |
| FAIL SPREAD ONLY | 9 | 33% | 0.82 | −1.88 | −16.9 | 30.5 / 37.1 / 62.4 | 60.0 / 106.8 / 119.4 | 62.5 | 2/5 |
| FAIL $25 DISTANCE ONLY | 22 | 32% | 0.77 | −2.46 | −54.0 | 34.5 / 68.9 / 98.3 | 45.3 / 63.5 / 111.6 | 109.6 | 4/11 |
| FAIL SIGNAL WINDOW ONLY | **1** | 0% | 0.00 | −15.59 | −15.6 | 2.8 | 86.3 | 15.6 | 0/1 |
| FAIL TWO FILTERS | 43 | 37% | 1.06 | +0.59 | +25.5 | 28.6 / 52.8 / 128.4 | 32.3 / 62.2 / 99.7 | 123.1 | 6/12 |
| FAIL THREE OR MORE | 12 | 25% | 0.53 | −5.79 | −69.4 | 44.3 / 87.1 / 151.4 | 96.3 / 106.0 / 146.7 | 90.9 | 3/8 |
| ALL BEARISH ANCHORS | 128 | 43% | 1.33 | +2.81 | +359.7 | 33.7 / 68.4 / 134.0 | 43.1 / 71.7 / 104.9 | 152.9 | 6/13 |

**The filters are not selecting noise.** Trades that fail only the spread test
(PF 0.82) or only the $25 test (PF 0.77) really are worse than trades that pass
everything, and the mechanism is visible in the excursions: the pass group's
median adverse excursion is **32.6** against 45.3 for the $25 rejects, 60.0 for
the spread rejects and 96.3 for the triple failures. The filters are selecting
trades that go against you less, which is a coherent story rather than an
arbitrary partition.

**Two important qualifications.**

The **30-minute expiry rejects exactly one trade in the entire year.** It cannot
be carrying information; it is inert. It should be described as a formality, not
a filter.

The **body filter's rejects are still profitable** (PF 1.95, +6.47 a trade). It
separates, but what it discards is a positive-expectancy population, not a
negative one. That is a weaker claim than the spread and quarter tests support.

---

## Waterfall — and the same waterfall reversed

| submitted order | n | WR | PF | exp | maxDD | Δ exp |
|---|---|---|---|---|---|---|
| unfiltered bearish anchor | 128 | 46% | 1.33 | +2.81 | 152.9 | — |
| + body filter | 60 | 50% | 1.63 | +4.91 | 105.2 | +2.10 |
| + quarter proximity | 35 | 63% | 2.75 | +10.12 | 46.9 | +5.21 |
| + spread filter | 26 | 73% | 4.39 | +14.27 | 31.2 | +4.15 |
| + 30-minute expiry | 25 | 76% | 5.13 | +15.47 | 15.9 | +1.19 |

| reversed order | n | WR | PF | exp | maxDD | Δ exp |
|---|---|---|---|---|---|---|
| unfiltered bearish anchor | 128 | 46% | 1.33 | +2.81 | 152.9 | — |
| + 30-minute expiry | 121 | 46% | 1.34 | +2.85 | 152.9 | **+0.04** |
| + spread filter | 99 | 51% | 1.58 | +4.52 | 152.9 | +1.67 |
| + quarter proximity | 41 | 68% | 3.41 | +11.96 | 31.7 | **+7.44** |
| + body filter | 25 | 76% | 5.13 | +15.47 | 15.9 | **+3.51** |

**The apparent contribution is strongly order-dependent.** Body is worth +2.10
added first and +3.51 added last. Quarter proximity is worth +5.21 in second
position and +7.44 in third. The expiry is worth +0.04 first and +1.19 last.
Any statement of the form "the body filter adds X" is therefore meaningless
without saying what it was added to.

**Marginal contribution, each filter added last to the other three:**

| filter added last | n before | n after | exp before | exp after | Δ |
|---|---|---|---|---|---|
| quarter proximity | 47 | 25 | +7.08 | +15.47 | **+8.39** |
| spread | 34 | 25 | +10.88 | +15.47 | +4.59 |
| body | 41 | 25 | +11.96 | +15.47 | +3.51 |
| 30-minute expiry | 26 | 25 | +14.27 | +15.47 | +1.19 |

The marginals sum to **+17.68** against a total lift of **+12.66**. They
overlap: the filters are substantially selecting the same trades, so their
contributions cannot be added and none of them can be credited individually.

**Is the quarter filter a disguised date filter?** Partly. Its pass rate drifts
across the year — 28.1%, 37.5%, 53.1%, 53.1% by sample quarter — and the pass
and fail groups differ significantly in date (Mann-Whitney p = 0.036), which is
what a fixed $25 grid does when the underlying price trends. But the separation
survives *within* each time block (+17.62, +1.33, +15.86, +8.08), so it is not
purely a proxy for good months either.

---

## 4. MICRO QUARTERS — identical structure at each 22.5-minute quarter

The 90-minute Q1 (18:00–19:30 NY) split into four micro quarters, with the same
15-minute anchor from each quarter's open and the same 30-minute window.
Boundaries at 18:22:30 and 19:07:30 do not fall on minute marks, so these
anchors are built straight from the tick stream at millisecond precision; the
18:45 case reproduces the bar-built result exactly as a control.

| micro quarter | n | PF | exp | net | WR | maxDD |
|---|---|---|---|---|---|---|
| MQ1 18:00:00 | 31 | 0.78 | −2.36 | −73.3 | 32% | 149.0 |
| MQ2 18:22:30 | 36 | 0.92 | −0.76 | −27.4 | 36% | 129.5 |
| **MQ3 18:45:00** | 25 | **5.13** | **+15.47** | +386.7 | 76% | 15.9 |
| MQ4 19:07:30 | 32 | 1.29 | +2.51 | +80.3 | 44% | 83.1 |

One of four works. The other three are flat to negative.

## 5. SESSION QUARTERS — identical structure across the daily cycle

Same 45-minute offset into each of the four 6-hour quarters of the NY daily
cycle, plus the conventional session opens.

| window | n | PF | exp | net | WR | maxDD |
|---|---|---|---|---|---|---|
| **Q1 Asia 18:45** | 25 | **5.13** | +15.47 | +386.7 | 76% | 15.9 |
| Q2 London 00:45 | 31 | 1.54 | +4.37 | +135.4 | 48% | 52.0 |
| Q3 NY AM 06:45 | 33 | 0.93 | −0.67 | −21.9 | 36% | 84.2 |
| Q4 NY PM 12:45 | 36 | 1.04 | +0.39 | +13.9 | 42% | 125.7 |
| Tokyo open 19:45 | 41 | 1.05 | +0.44 | +18.1 | 39% | 189.9 |
| London open 03:45 | 33 | 0.72 | −3.12 | −102.9 | 30% | 209.1 |
| NY open 10:15 | 28 | 0.27 | −9.82 | −274.8 | 14% | 274.8 |

The structure does not generalise to any other session. That cuts both ways: it
is consistent with something specific to the 18:00 NY reopen, and it is equally
consistent with one cell out of many having been found.

## 2. PRICE-GRID PHASE — the $25 grid slid off round numbers in $1 steps

| phase | n | PF | | phase | n | PF |
|---|---|---|---|---|---|---|
| **0 (round)** | 25 | **5.13** | | 14 | 27 | 1.14 |
| 2 | 20 | 4.83 | | 16 | 29 | 1.17 |
| **4** | 16 | **6.95** | | 18 | 30 | 1.85 |
| 6 | 19 | 1.82 | | 20 | 28 | 2.91 |
| 8 | 20 | 1.09 | | 22 | 23 | 5.82 |
| 10 | 24 | 0.82 | | **23** | 24 | **6.15** |
| 12 | 23 | 0.88 | | 24 | 24 | 4.85 |

Round grid PF 5.13. The 24 shifted grids average 2.86 ± 2.07 and **four of them
match or beat it** — phase +4 reaches **6.95**. Empirical p for roundness =
**0.20**, and because adjacent phases share most of their trades those 24 are
far from independent draws, so that p is optimistic rather than conservative.

There is real *phase* structure — a smooth hump peaking somewhere near 0–4 and
23–24, with the antipodal phases 10–14 as its trough — but its maximum is not at
zero. **Roundness is not established. Proximity to *a* grid of 25-point spacing
is doing the work, and the grid need not be round.**

## 9. EXECUTION STRESS

Entry pushed forward by a wall-clock delay and re-filled at whatever the market
then was; the stop charged as a slipping market order; the target filled as a
resting limit that does not slip in your favour.

| assumption | n | PF | exp | maxDD |
|---|---|---|---|---|
| 0s, limit TP (realistic baseline) | 25 | 5.08 | +15.30 | 15.9 |
| delay 30s | 25 | 5.08 | +15.29 | 15.8 |
| delay 300s | 25 | 5.05 | +15.29 | 16.0 |
| delay 5s + $1.00 stop slip | 25 | 4.72 | +15.01 | 17.6 |
| delay 120s + $1.00 stop slip | 25 | 4.76 | +15.04 | 16.9 |

**Execution is not the fragility.** A five-minute entry delay costs almost
nothing, and a full dollar of stop slippage costs 0.36 of profit factor. That a
300-second delay is harmless is not a surprise — it is the same fact the
random-entry placebo established, arriving from a second direction: timing
inside the window carries no information.

## 10. BLOCK BOOTSTRAP — reported with a caveat that matters

| block length | maxDD p50 | maxDD p95 | maxDD p99 | streak p95 | streak p99 |
|---|---|---|---|---|---|
| L = 1 (iid) | 31.2 | 62.3 | 77.9 | 4 | 5 |
| L = 3 | 15.9 | 31.5 | 36.4 | 2 | 2 |
| L = 5 | 15.9 | 31.4 | 31.5 | 2 | 2 |
| L = 8 | 15.9 | 31.4 | 31.5 | 2 | 2 |

The block bootstrap returns **smaller** tails than the iid version, which is the
opposite of its usual purpose, and the reason disqualifies it here. The realised
sequence contains 6 losers among 25 trades and **never two in a row**. A block
resampler can only reproduce patterns that occurred, so blocks of length 3 or
more are structurally incapable of generating the losing streak the iid
bootstrap puts at 4–5. On a 25-trade sample with no observed clustering, the
block bootstrap is not a more realistic tail estimate — it is a narrower one for
a mechanical reason.

**Use the iid figures for risk planning: drawdown p95 62, p99 78; losing streak
p95 4, p99 5.**

---

## 1. THE HOLDOUT YEAR — genuinely unseen data

The twelve months immediately preceding the audited sample were downloaded for
this test: **64,093,055 Dukascopy XAUUSD ticks, 2024-08-20 → 2025-08-20**. No
part of it had been examined by either researcher, and the specification was
frozen before the download began. It was run **once**. Nothing was re-fitted.

**Data quality.** 5,905 hourly files, 0 undecodable. `bid > ask`: 0. Zero
spreads: 0. Non-positive prices: 0. Out-of-order timestamps: 0. Median spread
**$0.510** (against $0.670 in the audited year — a tighter market). Price range
$2,470.70–$3,500.51. Nine of 8,760 hours never resolved; **none of them falls
inside the 18:00–19:30 NY window**, so the test is unaffected. 3,865 one-minute
bars inside 18:45–19:00 NY across the year.

### Result

| | audited 2025-26 | **HOLDOUT 2024-25** |
|---|---|---|
| trades | 25 | **11** |
| profit factor | 5.125 | **1.361** |
| expectancy | +15.47 | **+3.10** |
| net points | +386.7 | **+34.1** |
| win rate | 76.0% | **45.5%** |
| max drawdown | 15.9 | **63.1** |

Exits: 5 take-profits, 6 stops. Legs: 7 A-SHORT, 4 FLIP-LONG. Four of six active
months positive.

**The walk-forward called it.** The honest walk-forward on the audited year
predicted PF 1.37 and expectancy +3.69. The unseen year delivered **PF 1.361 and
+3.10**. Two independent methods — one simulating honest parameter selection
inside the sample, one using data that never touched the sample — agree to two
decimal places on profit factor. The advertised 4.89 does not appear in either.

### The filter stack does not transfer

| stage | audited PF | **holdout PF** |
|---|---|---|
| bearish anchor + any break | 1.33 | **1.03** |
| + body 1.00–6.25 | 1.63 | 1.25 |
| + within $6.25 of a $25 level | 2.75 | **1.17** ↓ |
| + spread ≤ $1.50 | 4.39 | 1.36 |
| + 30-minute expiry | 5.13 | 1.36 |

On the audited year the stack lifts 1.33 → 5.13. On unseen data it lifts
1.03 → 1.36, and **the quarter filter actively reduces profit factor** (1.25 →
1.17) rather than raising it. It also culls far harder — 38 candidates down to
12, against 60 down to 35 in the audited year — which is exactly what a fixed
$25 grid does when the price regime moves ($2,470–3,500 against $3,300–5,500).

### 18:45 is not special on unseen data

| anchor | n | PF | exp |
|---|---|---|---|
| 19:30 | 24 | **2.60** | +9.33 |
| 18:35 | 13 | **2.47** | +8.86 |
| 19:40 | 29 | 1.68 | +4.79 |
| 19:00 | 22 | 1.45 | +3.53 |
| 19:10 | 19 | 1.42 | +3.01 |
| **18:45** | 11 | **1.36** | **+3.10** |
| median of all 29 | — | 1.17 | +0.33 |

**Rank 9 of 29 by profit factor, 7 of 29 by expectancy** — against rank **1 of
29** on the audited year. It sits barely above the median anchor. Five other
anchors beat it, two of them by roughly double.

That is the whole case. On the year it was found in, 18:45 was the single best
of twenty-nine. On the year before, it is unremarkable.

---

## 8 & 31. DATA-SNOOPING CONTROL — White-style Reality Check over the whole search

The earlier permutation corrected for the anchor dimension alone (p = 0.0233).
But the anchor was not the only thing swept. This test re-runs the **entire
search** on data where the anchor carries no information, and compares the real
best-of-search against the distribution of null best-of-search.

Family of hypotheses: 18 anchors × 5 body minima × 3 body maxima × 4 quarter
distances × 4 spread caps × 3 windows × 3 stops × 3 targets = **116,640**.
Null: each day keeps its own real intraday path and receives the anchor geometry
of a random other day, re-centred on its own anchor close. 150 permutations,
each a full 116,640-point search.

| | value |
|---|---|
| real best-of-search expectancy | **+22.436** |
| null best-of-search, median | +17.096 |
| null best-of-search, p90 | +21.682 |
| null best-of-search, max | +30.252 |
| **corrected p** | **0.0662** (9 of 150 nulls match or beat it) |

Correcting for the anchor search alone gave p = 0.0233. Correcting for the
**full** search gives **p = 0.0662 — not significant at 5%**. The gap between
those two numbers is the price of the body, quarter, spread, window and exit
sweeps, and it is what the earlier figure was quietly not paying.

---

## CLASSIFICATION

### **LIKELY DATA-SNOOPED**

Three independent lines converge and none of them is close:

| test | result |
|---|---|
| holdout year, frozen spec | **PF 1.361**, expectancy +3.10, DD 63.1 |
| walk-forward, honest selection | **PF 1.37**, expectancy +3.69, DD 56.2 |
| Reality Check, 116,640 hypotheses | **p = 0.0662** |
| 18:45 anchor rank, unseen year | **9 of 29** (was 1 of 29 in-sample) |
| $25 grid vs 24 shifted phases | **p = 0.20**; phase +4 scores higher |

The advertised PF 4.89 is a selection artefact. Two methods that cannot see the
answer — honest in-sample selection and a year of untouched data — agree on
**PF ≈ 1.36** to two decimal places.

### But not NO EDGE

The residual is real and it is small. On the unseen year the filter stack still
lifted 1.03 → 1.36 and expectancy stayed positive at +3.10. The near-miss study
shows the filters separate on a coherent mechanism rather than arbitrarily —
median adverse excursion runs 32.6 for the pass group against 45.3, 60.0 and
96.3 as more filters fail. Something is there. It is worth roughly a quarter of
what was claimed.

### What survives, ranked by evidence

| component | verdict |
|---|---|
| low spread / execution quality | **transfers** — smooth hump, coherent MAE mechanism, and the holdout's final step is the one that helps |
| compression (body filter) | **partial** — separates, but its rejects are still profitable (PF 1.95) |
| bearish anchor direction | **in-sample only** — untested on the holdout as an isolated component |
| 18:45 exact minute | **fails** — rank 9 of 29 on unseen data |
| fixed $25 proximity | **fails** — reduces PF on the holdout; a shifted grid scores higher in-sample |
| 30-minute expiry | **inert** — rejects one trade in a year |
| 5-minute break timing | **worthless** — a random minute matches it (p = 0.23) |
