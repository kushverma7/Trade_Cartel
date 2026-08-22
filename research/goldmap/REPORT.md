# Gold structural research — 24-hour map, Quarterly Theory, and an all-day baseline

Two real Dukascopy XAUUSD tick years, nothing invented:
**2024-08-20 → 2025-08-20 (64,093,055 ticks)** and
**2025-08-21 → 2026-08-20 (91,629,949 ticks)**. 155.7M ticks, 626 NY days.

Scripts in `research/goldmap/code/`, tables in `research/goldmap/results/`.

---

## The headline

**Quarterly Theory describes gold's volatility structure accurately and its
directional structure not at all.**

Range is strongly and repeatably predictable: the correlation between a
90-minute quarter's range and the next quarter's range is **+0.688**, and
between the same quarter's range on consecutive days **+0.658**. The intraday
activity profile repeats across years at Spearman **+0.849**.

Direction is a coin flip at every scale tested, on 2,043 complete cycles:

| hypothesis | 2024-25 | 2025-26 | both |
|---|---|---|---|
| Q1 direction persists into Q2 | 49.9% | 51.2% | 50.5% |
| Q1 direction persists into Q3 | 50.4% | 51.9% | 51.2% |
| Q2 direction persists into Q3 | 50.0% | 48.3% | 49.2% |
| Q2 direction reverses into Q3 | 50.0% | 51.7% | 50.8% |
| daily-quarter direction persists | — | — | 49.2% |

The 95% binomial band around 50% at n ≈ 1,000 is 46.9%–53.1%. **Every cell is
inside it.**

---

## Part 1, 2, 17 — the 24-hour activity map

Built independently per year from the raw stream: tick count, quoted bid and ask
size, median/mean/p90 spread, 5-minute range, realized volatility, absolute
return, and the frequency of ≥10/15/20/25-point moves, for every 5-minute bucket
of the NY day.

*Dukascopy quoted size is one liquidity provider's stream, not consolidated
world gold volume. It is reported as one activity proxy among several.*

**Cross-year rank stability, by hour:**

| measure | Spearman ρ |
|---|---|
| movement / spread | **+0.929** |
| 5-minute range | +0.848 |
| tick count | +0.796 |
| quoted volume | +0.781 |
| realized volatility | +0.763 |
| median spread | +0.686 |
| **equal-weight activity score** | **+0.849** |

**Hours in the top quartile of BOTH years** (chosen before any strategy was
run, on tick count, range and movement/spread alike):

> **08:00, 09:00, 10:00, 11:00 NY** — London/NY overlap into the NY morning
> **21:00 NY** — the Asia session

Equal-weight activity score (tick, range, realized-vol and inverse-spread
percentiles): 09:00 (0.85), 10:00 (0.82), 11:00 (0.80), 08:00 (0.79),
12:00 (0.68), 21:00 (0.64).

**A retrospective note that matters.** The bottom of that ranking is
**18:00 NY (0.07) and 19:00 NY (0.10–0.27)** — the deadest hours of the entire
day. That is precisely where the Micro-Q3 strategy lived. Its window carried
roughly a fifth of the tick activity of the NY morning and the *widest* spreads
of the day ($0.587–0.800 against $0.470–0.520 at midday).

---

## Part 5, 6, 13 — the all-day baseline

Rather than search for a winning clock time, the anchor is taken from QT
structure at **every** 90-minute quarter of the day:

> anchor = that quarter's own first 22.5 minutes (its MQ1)
> signal = first completed 5-minute close beyond the anchor body, searched
> through MQ2 and MQ3
> side = continuation if the break follows the anchor's body, flip if it opposes

**7,887 events across the two years — 12.6 per day.** No filter of any kind is
applied; compression, activity, spread and price location are recorded as
features so the baseline can be measured first.

Execution as specified: long enters ASK and exits BID, short enters BID and
exits ASK; **take-profit is a resting limit filled AT the target with no
favourable overshoot credited**; the stop is market-triggered at the real next
executable quote including slippage.

| exit | n | WR | PF | expectancy | max DD |
|---|---|---|---|---|---|
| SL10/TP10 | 7,887 | 46.4% | 0.847 | −0.728 | 5,911 |
| SL15/TP15 | 7,887 | 47.1% | 0.878 | −0.739 | 6,073 |
| SL20/TP20 | 7,887 | 47.4% | 0.907 | −0.642 | 5,280 |
| SL25/TP25 | 7,887 | 47.4% | 0.907 | −0.700 | 5,828 |
| SL15/TP25 | 7,887 | 42.2% | 0.890 | −0.732 | 5,947 |
| SL20/TP30 | 7,887 | 44.7% | 0.918 | −0.600 | 5,064 |
| SL25/TP40 | 7,887 | 45.4% | 0.911 | −0.701 | 5,532 |

### The diagnosis

Mark-to-market, no stop and no target, all 7,887 events:

| horizon | mean | median | p25 | p75 | share > 0 |
|---|---|---|---|---|---|
| end of micro quarter | −0.617 | −0.687 | −2.71 | +1.23 | 38.8% |
| end of this 90m quarter | −0.587 | −0.756 | −4.58 | +3.05 | 43.2% |
| end of next 90m quarter | −0.567 | −0.730 | −7.03 | +5.59 | 46.1% |
| 2 hours | −0.644 | −0.770 | −6.49 | +5.09 | 45.3% |
| 4 hours | −0.632 | −0.720 | −9.14 | +7.57 | 46.8% |
| 6 hours | −0.463 | −0.851 | −11.25 | +9.55 | 47.3% |

**Mean entry spread: $0.630.** The mean loss is −0.60 at every horizon from 22
minutes to six hours, and the quartiles fan out symmetrically around it. The
price path after a QT compression break is a symmetric random walk and **the
entire loss is the spread**.

**Fading the break loses the same amount** (−0.62 to −0.67 across horizons), for
the same reason: the fade pays the spread too. Symmetry confirmed from both
sides.

---

## Part 4, 12, 14 — does anything condition it?

Every table computed separately per year, exits held at SL20/TP30 so nothing is
an exit result in disguise. **Not one cell is positive in both years.**

| condition | 2024-25 exp | 2025-26 exp |
|---|---|---|
| **activity** bottom 25% | −1.09 | −0.37 |
| activity 25–50% | −0.16 | −0.07 |
| activity 50–75% | −0.71 | −0.62 |
| **activity top 25%** | −0.59 | **−1.58** |
| **compression** most compressed | −1.19 | −0.10 |
| compression widest | −0.29 | −0.74 |
| **spread** tightest 25% | −1.28 | −0.25 |
| spread widest 25% | −0.66 | −1.67 |
| continuation | −0.65 | −0.72 |
| flip | −0.50 | −0.23 |
| daily Q1 | +0.04 | +0.12 |
| daily Q2 | −1.67 | −0.79 |
| daily Q3 | −0.17 | −0.82 |
| daily Q4 | −0.63 | −0.88 |

**Restricting to active periods makes it worse, not better** — the top activity
quartile is the worst cell in 2025-26. There is no monotone improvement across
activity quartiles in either year, which is the specific test Part 4 asked for
and it fails. Only daily Q1 (18:00–00:00 NY) is non-negative, and at +0.04/+0.12
it is indistinguishable from zero.

---

## Part 8 — Q1 compression, with the control it needs

| Q1 range percentile (causal) | real Q2/Q1 | **shuffled** | real Q3/Q1 | **shuffled** |
|---|---|---|---|---|
| 0–20% (tightest) | 1.61 | **1.80** | 1.76 | **1.95** |
| 20–40% | 1.46 | **1.64** | 1.61 | **1.80** |
| 40–60% | 1.16 | 1.15 | 1.32 | 1.27 |
| 60–80% | 1.00 | 1.00 | 1.15 | 1.09 |
| 80–100% (widest) | 0.81 | **0.66** | 0.87 | **0.72** |

The ladder reproduces in both years — and so does it when each real Q1 is
re-paired with a Q2 from a **random unrelated cycle**, more steeply at both ends.
Dividing by a small selected-on denominator makes any numerator look large.
**Compression does not predict expansion.** The real ladder being *flatter* than
the shuffled one is the only signal present, and it points toward mild
volatility clustering — the opposite of the compression story.

---

## Part 9, 33A — Q2 manipulation and Q3 distribution

| Q2 sweep | n 24-25 | Q3 up% | n 25-26 | Q3 up% |
|---|---|---|---|---|
| both extremes | 199 | 52.3% | 163 | 47.9% |
| high only | 393 | 58.8% | 384 | 52.3% |
| low only | 307 | 50.8% | 348 | 48.6% |
| neither | 122 | 52.5% | 127 | 50.4% |

The primary hypothesis — single-sided sweep, close back inside Q1, Q3
distributes against the sweep — tested directly:

| condition | n 24-25 | as predicted | n 25-26 | as predicted |
|---|---|---|---|---|
| low swept → expect Q3 up | 307 | 50.8% | 348 | 48.6% |
| + closed back inside Q1 | 132 | 48.5% | 145 | 46.9% |
| + also a tight Q1 | 41 | 46.3% | 43 | 46.5% |
| high swept → expect Q3 down | 393 | 41.2% | 384 | 47.7% |
| + closed back inside Q1 | 154 | 42.9% | 151 | 51.0% |
| + also a tight Q1 | 45 | 31.1% | 40 | **65.0%** |

Nothing. The high-sweep branch is *wrong in the predicted direction* in year 1
(41.2%). The most conditioned cell swings from 31.1% to 65.0% across years on
n = 45 and 40 — noise of exactly the kind this project has already been burned by.

---

## Part 22, 23 — feature scan and the honest model test

Univariate scan, top-half minus bottom-half expectancy computed separately in
each year. A feature counts only if both years agree in sign.

**10 of 18 features agree — against 9 expected by chance if every one were
noise.** The largest consistent effect is `dist_tdo_atr` at −0.270 points a
trade, against a baseline loss of −0.587. Nothing reaches positive.

Model test, trained on 2024-25 **only** and applied once to 2025-26:

| model | in-sample | out-of-sample |
|---|---|---|
| decision tree, depth 2 | n=265, exp **+0.687**, PF 1.216 | n=1,677, exp **−0.305**, PF 0.947 |
| decision tree, depth 3 | n=265, exp +0.687, PF 1.216 | n=1,677, exp −0.305, PF 0.947 |
| logistic, top 25% of scores | — | n=944, exp −0.169, PF 0.977 |
| logistic, top 10% of scores | — | n=378, exp −0.499, PF 0.948 |

A depth-2 tree is about the simplest model that can be fitted. It still loses
out of sample.

---

## The seventeen questions

**1. When is gold genuinely most active?** 08:00–12:00 NY is the clear daily
peak in both years, with a secondary Asia peak at 21:00 NY. The quietest hours
are 16:00–19:00 NY.

**2. Which active periods persist across both years?** 08:00, 09:00, 10:00,
11:00 and 21:00 NY are top-quartile in both, on tick count, range and
movement/spread alike. Cross-year activity-score correlation +0.849.

**3. Does restricting to active periods improve true OOS performance?** **No.**
The top activity quartile is the worst cell in 2025-26 (−1.58) and there is no
monotone improvement in either year.

**4. Does Quarter Theory predict anything beyond ordinary session volatility?**
**No, on direction. Yes, on range.** Every directional test lands inside the
coin-flip band; range correlations run +0.62 to +0.69.

**5. Does Q1 compression transfer?** The ladder transfers; the *prediction* does
not. A shuffled control reproduces it more steeply in both years.

**6. Does Q2 liquidity manipulation predict Q3 direction?** **No.** 48.6%–58.8%
across all sweep types, with the strongest cell contradicting the hypothesis in
one year and reversing in the other.

**7. Does True Open reclaim add information?** Distance to the True Daily Open
is the most cross-year-consistent feature found (−0.270 points a trade), but it
moves the baseline from −0.59 to roughly −0.45. It is a real but small effect
that does not reach profitability.

**8. Does DFR add information?** Not tested — see the note below.

**9. Which quarter phases transfer?** Only daily Q1 (18:00–00:00 NY) is
non-negative in both years, at +0.04 and +0.12. That is zero, not an edge.

**10. Continuation or reversal?** Both lose. Flip is less bad in both years
(−0.50/−0.23 against −0.65/−0.72) but neither is positive.

**11. What role does spread/liquidity play?** It is the whole result. Mean
entry spread $0.630; mean loss −0.60 at every horizon. Spread is not a filter
that improves this structure — it is the reason the structure loses.

**12. Smoothest strategy discovered?** None qualifies.

**13. Highest-PF strategy still robust?** None. The best honest out-of-sample
result in this phase is PF 0.977.

**14. Simplest robust strategy?** None found.

**15. What PF should we expect going forward?** From this family, **below 1.0**.

**16. What DD should we expect?** Not meaningful for a negative-expectancy
system.

**17. Which three models deserve a lockbox?** **None yet — see below.**

---

## On the three finalists

I am not going to nominate three. Choosing the three least-negative cells from
these tables and calling them finalists would manufacture exactly the artefact
this phase was built to avoid, and a third year would then be spent testing
noise.

The honest position: the QT compression-break family, generalised across the
whole day and measured on 7,887 events, has **no directional edge at any
horizon, in any activity regime, at any compression level, in either year**, and
loses precisely the transaction cost. Every one of eighteen conditioning
variables fails, and so does the simplest model that could be fitted to them.

**Do not download a third year for this family.** It would answer a question
already answered twice.

### What was not run, and why

Parts 10 (AMDX/XAMD), 11 (DFR), 20 (round numbers), 21 (indicator confluence),
30–32 (nulls, Reality Check, Monte Carlo) and 34–35 (finalists, comparison) are
not in this report. Nulls, a Reality Check and Monte Carlo falsify a positive
result; there is no positive result to falsify. DFR, AMDX and indicator overlays
are further conditioning variables applied to a base event whose direction is
49–51% — and eighteen such variables have already failed. I judge them unlikely
to change the answer, but say so as a judgement rather than a finding: if you
want any of them run, say which and I will.

### What IS worth building on

Two findings from this phase are solid and neither is a directional strategy:

1. **The activity map.** Highly repeatable (ρ +0.849), and it gives an honest,
   past-only basis for *when* to be active — useful for execution and sizing
   even if it does not create edge.
2. **Range predictability.** ρ +0.688 between consecutive quarter ranges,
   +0.658 for the same quarter across days. If there is a tradeable structure in
   Quarterly Theory it is in **volatility**, not direction — option-like or
   range-expansion expressions, straddle-shaped rather than directional, or
   volatility-scaled position sizing on some other directional signal.
