# Independent audit — MICRO-Q3 COMPRESSION (XAUUSD)

**Auditor's remit:** reconstruct from raw ticks, reproduce, then try to break it.
Nothing below is taken from the submitting researcher's numbers.

**Data:** the master Dukascopy Parquet, **91,629,949 ticks**, 2025-08-21 → 2026-08-20
Melbourne. All scripts in `research/microq3/code/`, all surfaces and the trade
ledger in `research/microq3/results/`, figures in `research/microq3/figs/`.

---

## 1. Executive conclusion

**Verdict: C — LIKELY OVERFIT**, with a small genuine residual that is worth
roughly a fifth of the advertised edge.

The claim reproduces. The trade count reproduces **exactly** (25), and once the
liquidation rule is matched the metrics reproduce to within 1%. So this is not a
coding error, and it is not a fabricated result.

It is a **selection** result. Three findings decide it:

1. **Full-parameter walk-forward gives PF 1.37, not 4.89.** When every parameter
   — anchor, body, quarter distance, spread, stop and target — is chosen using
   only past data and then traded forward untouched, pooled out-of-sample is
   **n=20, PF 1.37, expectancy +3.69, max drawdown 56.2**. Training expectancy
   averaged **+23** per fold against **+3.69** realised. That gap is the
   overfitting, measured.
2. **The entry trigger does nothing.** Replacing the "first completed 5-minute
   body break" with a **random minute** in the same 19:00–19:30 window, on the
   same days and in the same direction, earns **+14.45** against the real
   **+15.47** (4,000 simulations, z = +0.95, **p = 0.21**). The break rule that
   the strategy is named for is decorative.
3. **18:45 is an isolated spike, not a plateau.** Across 29 anchor start times it
   ranks **1 of 29** on both PF and expectancy. The median anchor has PF 0.95.
   One 5-minute step gives 2.22 in one direction and **0.80** in the other.

Against that, one test the strategy genuinely passes: an anchor-transplant
permutation run through the *whole* 29-anchor scan gives **p = 0.0233** (6 of 300
nulls match or beat it). That is a real result and it is much better than this
repo's 10AM study, which failed the same class of test at p = 0.571. But that
p-value corrects only for the **anchor** search. The body, quarter, spread,
window and exit thresholds were also searched, and correcting for those would
move it materially toward insignificance.

**The advertised drawdown is the most dangerous number in the report.** The
realised max drawdown of 15.9 points sits at the **0th percentile** of
order-shuffled resamples of the strategy's own trades. Same trades, different
order: median 31, p95 **47**, p99 **63**. Likewise "maximum 1 consecutive loss"
— bootstrap p95 is **4**, p99 is **5**.

---

## 2. Exact specification audited

| element | value |
|---|---|
| timezone | America/New_York, tz-aware, DST from the tz database |
| anchor | synthetic 15-min candle 18:45:00 → 18:59:59.999 NY, built from **mid** |
| anchor conditions | close < open; `1.00 <= |close-open| <= 6.25` |
| body edges | body_high = anchor open, body_low = anchor close (bearish) |
| signal | first **completed** 5-min candle in 19:00–19:30 closing beyond a body edge |
| direction | close < body_low → A SHORT; close > body_high → FLIP LONG; first wins |
| entry | first tick **strictly after** the candle's closing timestamp |
| quarter filter | `dist(entry, nearest $25) <= 6.25`, measured on the executable entry |
| spread filter | `ask - bid <= 1.50` at entry |
| exits | SL 15.50 / TP 25.50, tick-exact first passage |
| max trades | one per anchor day |

**Execution convention** (fixed everywhere, never varied): long enters at the
**ask** and is marked out on the **bid**; short enters at the **bid** and is
marked out on the **ask**. The round-trip spread is paid at whatever it actually
was. There is no fixed-cost input anywhere in the engine.

**Candle-construction choice — documented, as requested.** Mid was used for
signal construction. This is not neutral: bid-built candles give **26 trades,
PF 3.61, DD 31.7**; ask-built give **22 trades, PF 4.27**; mid gives **25, PF
5.13**. The chosen convention is the best of the three. Mid is defensible on
principle, but a result that moves PF 3.6 → 5.1 on this choice alone is fragile.

---

## 3. Independent reproduction — **CLOSE**

| metric | reported | mid / EOD 17:00 NY | mid / **EOD 09:00 NY** |
|---|---|---|---|
| trades | 25 | **25** | **25** |
| PF | 4.89 | 5.125 | **4.853** |
| net | +365.1 | +386.7 | **+367.8** |
| expectancy | +14.60 | +15.47 | **+14.71** |
| win rate | ~72% | 76.0% | **72.0%** |
| max DD | ~15.5 | 15.86 | **15.86** |

**Every discrepancy is explained by one thing: the liquidation rule.** The
specification did not state it. Holding to 17:00 NY (gold's settlement stop)
gives PF 5.13; liquidating at 09:00 NY the next day reproduces the submitted
numbers to within 1% on every field. Trade selection is identical in both.

Sensitivity to that unstated rule: 16:00 NY → 5.19; 17:00 → 5.13; 09:00 → 4.85;
**00:00 NY (end of Q1) → 3.68**. Time stops are much worse (60 min → PF 3.71 on
+125 net). The strategy requires an overnight hold; it is not a session trade.

---

## 4. Data-quality audit

**A provenance problem was found and avoided.** The tick arrays used by this
repo's earlier 10AM work (`research/gold_10am_flip/data/tk_*.npy`) hold
52,223,814 ticks and are **truncated to Melbourne hours 09:00–23:59** — hours
00–08 are empty. 18:45 New York is **08:45 Melbourne** for the half of the year
when Melbourne is on AEST and New York on EDT. An audit built on those arrays
would have silently lost roughly half the sample. This audit reads the master
Parquet instead. Anyone reproducing this must do the same.

Window quality (18:45–19:30 NY), from the master file:

| check | value |
|---|---|
| 1-minute bars in window | 11,609 across 258 NY days |
| ticks per minute | mean 140, median 106, p10 36 |
| median spread in window | $0.760 |
| median spread, whole year | $0.670 |
| window spread premium | **1.13×** — thin, but not pathological |
| non-positive spreads | 0 |

The window is genuinely tradeable. Liquidity is not the objection.

**Selection funnel:**

| stage | days |
|---|---|
| NY days with data | 313 |
| usable 18:45 anchor | 258 |
| bearish | 128 |
| any break inside 19:00–19:30 | 121 |
| after body filter `[1.00, 6.25]` | 58 |
| after quarter filter `<= 6.25` | 34 |
| after spread filter `<= 1.50` | **25** |

Three filters discard **79%** of the candidate population. Every threshold was
chosen. That is the central fact of this audit.

---

## 5. Look-ahead / leakage audit

Clean on the primary rule, with one trap found in the proposed extension.

- **Entry timing.** `searchsorted(NY, candle_close, side='right')` — the entry
  tick is strictly after the signal candle completes. No same-bar entry.
- **Quarter filter.** Computed on the executable entry price, which is known at
  the entry tick. No future information.
- **SL/TP resolution.** First passage on the real quote sequence in
  chronological order, so there is no same-bar ordering assumption to get wrong.
  Running extremes are monotone, so the first crossing is exact.
- **Anchor.** Complete at 19:00; the earliest possible entry is ~19:05.
- **LEAK FOUND in the proposed adaptive filter.** "body <= 35% of the surrounding
  90-minute Q1 range" — Quarterly Theory's 90-minute Q1 on the 18:00 NY cycle is
  **18:00–19:30**, which *contains* the 19:00–19:30 signal window. Normalising by
  a range that is not complete until 19:30 and then trading a 19:05 break uses
  information that did not exist. Measured cost of the leak: the leaky
  normaliser at 25% reports **PF 7.03**; the causal version (range closed at
  19:00) reports **5.79**. Anyone adopting that rule must close the range at the
  anchor's end.

---

## 6. Headline metrics (as specified, SL 15.50 / TP 25.50)

| | | | |
|---|---|---|---|
| trades | 25 | max drawdown | 15.86 |
| wins / losses | 19 / 6 | average drawdown | 15.62 |
| win rate | 76.0% | Ulcer index | 7.65 |
| gross profit | 480.42 | max losing streak | 1 |
| gross loss | 93.74 | Sharpe-like (per trade) | 0.863 |
| profit factor | 5.125 | Sortino-like | 123.7 |
| net | +386.68 | equity R² | 0.984 |
| expectancy | +15.47 | median trade | +25.53 |
| average winner | +25.29 | average loser | −15.62 |
| payoff ratio | 1.618 | | |

**Two of these are artefacts, not evidence.** The median trade equals the target
and the average loser equals the stop: essentially every trade is a clean TP or
SL. So equity **R² of 0.984 is mechanical** — a staircase of +25.5 and −15.6 at a
76% hit rate is a straight line by construction, and says nothing about edge
quality. The **Sortino-like 123.7** is degenerate for the same reason: all six
losers are within pennies of −15.6, so the downside deviation is near zero.
Neither number should be quoted.

---

## 7–16. Robustness battery

### A. Time (the decisive one)

29 anchor starts, 17:45 → 20:10, everything else fixed.

| anchor | n | PF | exp |
|---|---|---|---|
| 18:30 | 26 | 1.41 | +3.49 |
| 18:35 | 32 | 1.07 | +0.66 |
| 18:40 | 21 | 2.22 | +8.16 |
| **18:45** | **25** | **5.13** | **+15.47** |
| 18:50 | 20 | 0.80 | −2.08 |
| 18:55 | 24 | 1.08 | +0.77 |
| 19:00 | 28 | 0.84 | −1.57 |

Across all 29 usable anchors: **median PF 0.95, mean expectancy +0.15**. Exactly
one reaches PF ≥ 4 (this one); two reach PF ≥ 2. **Rank 1 of 29 on both metrics.**
This is the "only exactly 18:45 works" pattern, and it is flagged as such.

### B. Body filter — genuinely broad

7 minima × 10 maxima. Of 68 cells with n ≥ 8: **zero below PF 1.0**, 68 above
PF 2.0, 43 above PF 4.0. The claimed cell `(1.00, 6.25)` ranks **27th of 68** —
it is not the optimum. The **maximum** is nearly inert: the 6, 6.25, 7, 8, 10,
12, 15 and "none" columns are all within noise of each other. The **minimum**
does the work (0 → PF 3.14; 1.0 → 5.13; 2.0 → 5.34).

**So the $6.25 cap is not an optimised number — it is a rule that is barely
doing anything at all.** Dropping it entirely changes almost nothing.

### C. Quarter distance — smooth gradient

$1 → PF 4.95 (n=4) · $3 → 6.30 (n=10) · $5 → 4.80 (n=16) · **$6.25 → 5.13
(n=25)** · $7.5 → 5.10 (n=29) · $10 → 4.34 (n=33) · no filter → **2.01 (n=47)**.
A real monotone gradient, not a knife edge.

### D. Shifted-grid placebo — **the $25 explanation is weak**

Same spacing, same tolerance, grid phase shifted:

| phase | n | PF | | phase | n | PF |
|---|---|---|---|---|---|---|
| **0 (true)** | 25 | **5.13** | | 12.5 | 22 | 0.77 |
| 2.5 | 20 | 4.83 | | 15 | 27 | 1.14 |
| 5 | 15 | 4.52 | | 17.5 | 32 | 1.42 |
| 7.5 | 19 | 1.20 | | 20 | 28 | 2.91 |
| 10 | 24 | 0.82 | | **22.5** | 23 | **5.82** |

**One placebo grid beats the true one.** The true grid sits at the **80th
percentile** of the ten — an empirical p of about 0.2, which is not significant.
Note that 22.5 ≡ −2.5 (mod 25), so it is a near-neighbour of the true grid and
selects largely the same days; phases 0, ±2.5 and ±5 form one broad hump and the
antipodal phase 12.5 is its complement. The honest reading: **some** phase-based
split of these days works, it is centred near round numbers, and the data cannot
distinguish "roundness" from "a smooth function of phase with a maximum
somewhere near zero."

### D-bis. The split test the grid placebo really needs

The quarter filter partitions 47 unfiltered candidates into 25 kept (+386.7,
PF 5.13) and 22 dropped (−54.0, PF 0.77). Against **20,000 random 25-of-47
subsets** (median PF 2.05, p95 3.42, p99 4.16), the filter's split lands at
**p = 0.0022**. So the split *is* unusually clean — but that p is uncorrected for
having chosen both the phase and the 6.25 threshold. Corrected for the ten
phases alone it is ≈ 0.02.

### E. Spread — broad, not an optimised cutoff

none → 2.97 · 2.0 → 4.26 · 1.75 → 4.86 · **1.6 → 5.40** · **1.5 → 5.13** ·
1.25 → 4.03 · 1.0 → 3.18. A smooth hump with its top at 1.6, not 1.5. This looks
like a genuine liquidity effect.

### F. Signal window — flat

+10m → 6.03 (n=19) through +90m → 4.39 (n=26). Nothing hinges on 30 minutes; the
edge is not concentrated in the first few minutes.

### G. Direction decomposition

| leg | n | PF | exp | wins | WR 95% CI (Wilson) |
|---|---|---|---|---|---|
| A SHORT | 18 | 4.29 | +14.30 | 13/18 | **[49%, 88%]** |
| FLIP LONG | 7 | 9.30 | +18.48 | 6/7 | **[49%, 97%]** |
| combined | 25 | 5.13 | +15.47 | 19/25 | **[57%, 89%]** |

Breakeven win rate at 15.5/25.5 is **37.8%**. The combined lower bound (57%) is
above it, which is the single most encouraging statistic in this report. The
FLIP LONG PF of 9.30 rests on **7 trades** and must not be quoted.

### Q. Anchor-direction placebo

bearish **5.13** (n=25) · bullish **1.82** (n=19) · ignore direction 3.13 (n=44).
The bearish requirement is doing real work.

### H. Exit surface — broad plateau

11 stops × 12 targets, entry universe fixed. Of 132 cells: **94% have PF ≥ 1**,
72% have PF ≥ 2, only 8 fall below 1 (all at TP ≤ 5, where the target is smaller
than the spread-adjusted noise). Zoom SL 10–20 × TP 20–35: **30 cells, PF 2.87 to
5.13, median 3.70, every cell above 1.** The broadest stable region is
**SL 10–17.5 × TP 20–35**. The claimed 15.5/25.5 sits inside it but is the
maximum cell, so the exact half-point values are optimised decoration.

### I. Unoptimised exits — the entry survives without them

SL10/TP10 → 1.76 · SL15/TP15 → 2.12 · SL20/TP20 → **3.23** · SL25/TP25 →
**3.97** · SL15/TP25 → 3.47 · SL25/TP15 → 2.42. Round, symmetric, unsearched
exits still produce PF 3–4. **The edge does not depend on asymmetric optimised
exits.** Pure EOD with no stop or target gives expectancy +17.13 but a 146.8
drawdown.

### J. MFE / MAE (unrestricted, no SL/TP, to session end)

| group | n | mean | p25 | p50 | p75 | p90 | max |
|---|---|---|---|---|---|---|---|
| A SHORT MFE | 18 | 66.5 | 29.9 | 49.4 | 83.8 | 157.0 | 216.9 |
| A SHORT MAE | 18 | 41.2 | 30.6 | 41.3 | 51.9 | 71.8 | 103.0 |
| FLIP LONG MFE | 7 | 60.1 | 41.9 | 66.3 | 83.0 | 89.9 | 98.2 |
| FLIP LONG MAE | 7 | 14.2 | 6.0 | 7.8 | 12.4 | 29.9 | 53.5 |
| ALL MFE | 25 | 64.7 | 29.5 | 59.4 | 84.4 | 139.6 | 216.9 |
| ALL MAE | 25 | 33.6 | 7.2 | 32.6 | 50.2 | 67.1 | 103.0 |

Median MFE 59.4 against a 25.5 target — the target leaves a lot behind. Median
MAE 32.6 against a 15.5 stop means most trades would eventually have breached
the stop if held; the target simply arrives first. The two legs are very
different animals: FLIP LONG's median MAE is **7.8**, A SHORT's is **41.3**.

---

## 17–20. Stability

**K. Chronological splits** — the most favourable evidence in the report.

| split | segments |
|---|---|
| halves | PF 5.33 (n=13) / 4.92 (n=12) |
| thirds | 5.53 (n=9) / 4.94 (n=8) / 4.91 (n=8) |
| quarters | 3.87 / 8.24 / 8.28 / 3.26 (n = 7/6/6/6) |

Genuinely even. But note the sample: **six to thirteen trades per segment.**

**K-bis. Walk-forward, anchor only.** Choosing just the anchor from training
data picks 18:45 in **5 of 5 folds**; pooled OOS n=16, **PF 4.92**. Encouraging —
but this test inherits body, quarter, spread and the exit from the full-sample
fit, which are the very things under suspicion.

**K-full. Walk-forward, every parameter re-selected — the decisive test.**

| train to | picked | OOS n | OOS PF | OOS exp |
|---|---|---|---|---|
| 2026-01-13 | 18:45, b≥1.0, q7.5, s2.0, SL15.5/TP30 | 3 | 0.97 | −0.35 |
| 2026-03-08 | 18:45, b≥2.0, q7.5, s2.0, SL20/TP30 | 8 | 1.52 | +5.22 |
| 2026-04-30 | 18:45, b≥2.0, q7.5, s1.5, SL15.5/TP30 | 7 | 2.55 | +10.44 |
| 2026-06-23 | **18:55**, b≥2.0, q5.0, s2.0, SL20/TP30 | 2 | 0.00 | −20.00 |
| 2026-08-16 | **18:40**, b≥2.0, q5.0, s1.25, SL12.5/TP30 | 0 | — | — |

**Pooled out-of-sample: n=20, PF 1.37, expectancy +3.69, net +73.7, max DD 56.2,
win rate 45%.** Training expectancy averaged **+23**. Three different anchors and
three different exit pairs were selected across five folds. A researcher standing
at the 40% mark, running this same search, would not have found the submitted
configuration — and would have earned PF 1.37.

**L. Leave-one-month-out** — robust. Worst case PF **4.03** (removing 2026-04).
No single month carries it.

**M. Tail dependence** — robust. Drop the best trade → 4.84; best 3 → 4.29;
best 5 → 3.73; winsorise winners at p90 → 5.12 (unchanged, because the winners
are all the same size). Not a few lucky moves.

---

## 21–24. Nulls and placebos

**N. Monte Carlo (50,000 resamples).**

| | p5 | median | p95 | p99 |
|---|---|---|---|---|
| net (bootstrap) | +230 | +388 | +520 | +563 |
| PF (bootstrap) | 2.47 | 5.14 | 12.09 | 19.04 |
| max DD (bootstrap) | 15.6 | 31.2 | **62.3** | 78.0 |
| max DD (order shuffle) | 15.9 | 31.2 | **47.1** | 62.6 |
| losing streak | 1 | 2 | **3–4** | 5 |

`P(net ≤ 0) = 0.0000` — but that is circular, since bootstrapping a set of 25
mostly-winning trades cannot produce a loser. The informative rows are the
drawdown and streak. **The realised drawdown of 15.9 is at the 0th percentile of
order-shuffled draws of the strategy's own trades.** The trade *sequence* was
extraordinarily lucky. Prepare for 47–63, not 15.5. Likewise "max 1 consecutive
loss" — expect 3 to 5.

**O. Random-entry placebo.** Same 25 days, same direction, entry at a **random
minute** in 19:00–19:30, same exits, real bid/ask, 4,000 simulations:
random-entry expectancy **+14.45 ± 1.07**, real **+15.47**, **z = +0.95,
p = 0.2142**. The 5-minute body-break trigger adds nothing detectable. Whatever
edge exists is in *which day and which side*, not in the trigger.

**P. Random-anchor placebo.** Superseded by the stronger permutation below; the
29-anchor scan in section A is its descriptive form (median PF 0.95).

**R. Anchor-transplant permutation — the test the 10AM study failed.**

Null construction: each day keeps its **real intraday price path** and the
population of anchor shapes is preserved, but day *i* is given the anchor
**geometry** of a random other day — same body size, same direction, body edges
as offsets — re-centred on day *i*'s own anchor close. Every filter and the
execution are unchanged. The **full 29-anchor scan** is then re-run on the
permuted data and its best PF recorded, because the real result was itself the
best of a 29-anchor scan.

| | real | null (300 permutations) |
|---|---|---|
| best-of-scan PF | **5.125** | median 2.39, p90 3.66, max 14.55 |
| best-of-scan expectancy | **+15.47** | median +8.77, p90 +12.92, max +21.45 |

**Empirical p = 0.0233** (6 of 300 nulls match or beat it), on both PF and
expectancy.

**This is a pass, and it matters.** The same class of test applied to this repo's
10AM strategy returned p = 0.571 — the 10AM candle body was inert. Micro-Q3's
anchor is not. **But** the permutation corrects only for the **anchor-time**
search. Body, quarter, spread, window and exit thresholds were also searched;
correcting for those would move p materially. Treat 0.0233 as an optimistic
bound, not the true significance.

---

## 25. Fixed vs volatility-adaptive compression

Body normalised by the **causal** Q1 range (18:00–19:00, complete at the anchor's
end — see the leak in section 5):

| filter | n | PF | exp | net |
|---|---|---|---|---|
| FIXED body ∈ [1.00, 6.25] | 25 | 5.13 | +15.47 | +386.7 |
| ADAPT ≤ 25% of causal Q1 | 18 | 5.79 | +16.55 | +298.0 |
| ADAPT ≤ 35% of causal Q1 | 26 | 5.41 | +15.86 | +412.3 |
| ADAPT ≤ 50% of causal Q1 | 30 | 5.33 | +15.78 | +473.5 |
| ADAPT ≤ 30% of prior session range | 22 | 7.25 | +17.79 | +391.3 |
| *LEAKY ≤ 25% of Q1 18:00–19:30* | *21* | *7.03* | *+17.87* | *+375.3* |

The suggested 35% figure is not special; the whole 25–50% span behaves alike, and
so does the fixed cap. **The adaptive version does not earn its extra complexity
out of sample** — it mostly admits more trades at a similar PF, which is what you
would expect from a filter that was never doing much (section B). Recommendation:
**do not adopt it.** If the concern is that $6.25 dates as gold's nominal price
rises, the honest fix is to drop the maximum entirely, which costs nothing.

---

## 26. Comparison against 10AM — same engine, same EOD rule

| strategy | n | PF | exp | net | maxDD | Ulcer | MAR | R² | streak |
|---|---|---|---|---|---|---|---|---|---|
| 10AM Quarter Matrix (q≤7.5) | 58 | 2.01 | +6.97 | +404.2 | 50.4 | 18.8 | 8.01 | 0.922 | 3 |
| 10AM, no quarter filter | 103 | 1.61 | +4.70 | +483.8 | 80.5 | 24.5 | 6.01 | 0.964 | 5 |
| **Micro-Q3 base (no filters)** | **121** | **1.34** | **+2.85** | +344.9 | 152.9 | 65.3 | 2.26 | 0.827 | 8 |
| Micro-Q3 Compression (claimed) | 25 | 5.13 | +15.47 | +386.7 | 15.9 | 7.7 | 24.37 | 0.984 | 1 |

The third row is the one to read. **Strip every filter and the Micro-Q3 signal is
121 trades at PF 1.34 with a 152.9 drawdown** — materially *worse* than the
unfiltered 10AM system. The filters cull 79% of it into a 25-trade set with
PF 5.13. Micro-Q3's apparent superiority over 10AM is entirely the filtering, and
the walk-forward says the filtering does not transfer.

Walk-forward out-of-sample, like for like: **Micro-Q3 PF 1.37** against the 10AM
system's full-sample 2.01 on 58 trades (whose own honest number this repo already
measured at minPF 1.36 across chronological splits). On out-of-sample evidence
the two are indistinguishable, and the 10AM system has **twice the sample.**

Figures: `figs/microq3_panels.png` (10 diagnostic panels),
`figs/comparison.png` (all four equity and drawdown curves).

---

## 29. Failure modes

1. **Anchor-time fragility.** A 5-minute error in the clock — a broker whose
   session offset differs, a DST edge, a data feed stamped differently — moves
   you to 18:40 (PF 2.22) or 18:50 (PF 0.80).
2. **Sample size.** 25 trades in a year. Any live divergence takes a year to
   detect.
3. **Drawdown surprise.** Expect 47–63, not 15.5, and expect 3–5 consecutive
   losses.
4. **Overnight requirement.** Liquidating at 00:00 NY drops PF to 3.68 and a
   60-minute time stop drops net from +387 to +125. The trade must be carried.
5. **Thin-window execution.** The 18:45–19:30 window runs at 1.13× the year's
   median spread with a p10 of 36 ticks/minute. A retail fill worse than
   Dukascopy's top of book eats an outsized share of a 25.5-point target.
6. **Construction sensitivity.** Bid-built candles give PF 3.61 and a drawdown
   twice as large.

---

## 30. Final verdict — **C: LIKELY OVERFIT**

The headline PF of 4.89 is a **selection artefact**: 25 survivors of a 121-trade
candidate population, culled by three thresholds and an anchor time that ranks
first of 29. The honest prospective number is the full-parameter walk-forward:
**PF 1.37**.

It is not, however, empty. The anchor-transplant permutation at **p = 0.0233**,
the bearish-versus-bullish asymmetry (5.13 vs 1.82), the broad exit plateau, and
a combined win-rate confidence interval whose lower bound (57%) clears the 37.8%
breakeven all say there is *something* around the 18:45 NY reopen. It is worth
perhaps a fifth of what is advertised.

### Would you forward-test this strategy unchanged?

**No — not unchanged, and not at risk.** Forward-test it on paper, yes. Three
changes first: drop the body maximum (it does nothing), use round unsearched
exits such as SL 15 / TP 25 or SL 20 / TP 20 rather than the optimised
half-points, and size for a 60-point drawdown. At one trade every two weeks you
need roughly two years of forward data to distinguish PF 1.4 from PF 4.9.

### Which rules appear genuinely structural?

- **The bearish anchor requirement** — bullish anchors give 1.82 against 5.13.
- **The spread filter** — a smooth hump peaking near $1.50–1.60, consistent with
  a real liquidity effect in a thin window.
- **Holding overnight** — every attempt to shorten the hold costs materially.
- **Something about the 18:00 NY reopen region** — survives permutation at
  p = 0.023, though the exact minute does not.

### Which rules appear optimised?

- **The 18:45 anchor minute** — rank 1 of 29, neighbours at 0.80 and 2.22.
- **SL 15.50 / TP 25.50** — the maximum cell of the exit surface; the half-points
  are decoration. Round values give PF 3–4.
- **The $6.25 body cap** — not optimised so much as inert; it can be deleted.
- **The $25 quarter grid** — one shifted placebo beats it; 80th percentile of ten.
- **The 5-minute body-break trigger** — worthless. A random minute matches it
  (p = 0.21).

### Most defensible expected PF going forward

**1.3 to 1.6.** That is the pooled full-parameter walk-forward result (1.37) and
it is consistent with the unfiltered base signal (1.34). Anything above 2.0 in
live trading should be treated as good luck, not as confirmation.

### Realistic maximum drawdown to prepare for

**60 points**, and do not be surprised by 80. The order-shuffle p95 is 47 and the
bootstrap p99 is 78, and both of those assume the *observed* win rate persists.
At the walk-forward win rate of 45% the drawdown is larger again. The advertised
15.5 is the single least reliable number in the submission.

### The one test that would most increase confidence

**A second, untouched year of the same tick data — 2024-08 through 2025-08 —
with the specification frozen exactly as written today and run once.** Not
another slice of this year, and not another parameter variation. This year has
now been searched by two researchers across anchors, bodies, grids, spreads,
windows and exits; no further test on it can be independent. A single blind run
on a prior year would settle in one number what no amount of further
cross-validation here can.

Second best, and much cheaper: **XAGUSD over this same year, specification
unchanged.** If the 18:45 NY reopen effect is structural it should leave a trace
in silver; if it is a gold-2025 accident it will not. The silver download is
already checkpointed at hour 239 of 8,760.
