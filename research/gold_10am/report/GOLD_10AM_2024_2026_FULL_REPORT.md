# Gold 10AM — Full Research Report
### XAU/USD, Australia/Melbourne clock, 2024-08-20 → 2026-08-19

> ## STATUS: FEED-SPECIFIC FALSIFICATION STUDY — NOT THE FINAL GOLD VERDICT
>
> This study was run on **Dukascopy 1-minute** data because `LSE_API_KEY` was
> unavailable. The requested study — **London Strategic Edge XAU/USD TICK
> data** — is pending and is a separate deliverable
> (`GOLD_LSE_TICK_REPLICATION_REPORT.md`).
>
> Until that replication is complete, the verdict below stands as
> *"the negative result holds on the Dukascopy 1-minute feed"*, not as
> *"gold has no edge"*. Two things in particular are feed-sensitive and must be
> re-tested on LSE ticks rather than assumed: the **09:50 maintenance-gap
> finding** (Sections 5–7) and every **execution-dependent** number, which here
> rests on 1-minute OHLC rather than a real bid/ask tape.

**Verdict on the Dukascopy 1-minute feed: NO EVIDENCE OF GOLD EDGE.**

---

## 1. Executive Summary

The 10AM Body Break structure was rebuilt from scratch on two years of authentic
1-minute XAU/USD data, reconstructed on a real `Australia/Melbourne` clock, and
subjected to 34 phases of testing. Four independent findings, any one of which
would be disqualifying on its own:

1. **The signal carries no directional information.** Across 64 first-passage
   tests — four logics × sixteen symmetric barriers from ±$1 to ±$100 — not one
   95% confidence interval excludes the 50% null. The smallest p-value is 0.135.
   If the 10AM structure predicted direction at any horizon, this test would
   show it, and it does not.

2. **The gross profit is not produced by the trade thesis.** Decomposing P&L by
   exit type: dollars won at the target almost exactly equal dollars lost at the
   stop for every branch (A Short +$1,287 vs −$1,309; Flip Long +$1,092 vs
   −$1,122). The entire net sits in the residual bucket of trades that touched
   neither barrier and were marked out at end of day. The barrier contest — which
   is what the strategy actually is — is a coin flip.

3. **09:50/10:00 is not a special time.** Rebuilding the identical method at
   eight nearby anchor pairs on the same 338 days, the traded pair ranks
   mid-pack. Neighbouring clock times score *higher* on every branch: 10:05/10:15
   gives A Short PF 1.34 against the base pair's 1.03; 10:00/10:10 gives A Long
   PF 1.39 against 1.07. There is nothing at 10AM that is not equally present at
   9:45 or 10:05.

4. **Nothing survives the untouched holdout.** Flip Long was the only branch to
   clear the measured spread on the development window (PF 1.485) and it held on
   validation (1.720). On the sealed holdout it returns **PF 0.841** — a loss.
   Meanwhile Flip Short, dead on DEV (1.026) and badly negative on VAL (0.357),
   is the best branch on the holdout (1.774). Branch performance is reshuffled by
   every window boundary. That is the signature of noise, not of a decaying edge.

A fifth finding is structural rather than statistical, and it matters
independently of everything above:

> **For roughly four and a half months a year, this strategy cannot be traded on
> gold at all.** The gold feed's daily maintenance break tracks New York
> 17:00–18:00. When Melbourne is on AEDT and New York is on EST — early November
> to mid-March — that break lands on **09:00–10:00 Melbourne**, and the 09:50
> reference candle does not exist. It was absent on **180 of 180** such weekdays.
> Not most. All.

The `documents/` verification discipline applies to my own source too, so it is
stated plainly: **this study did not use London Strategic Edge data.** LSE is now
reachable from this container, but `LSE_API_KEY` is absent — the container that
held it was recycled, and the key pasted on 2026-08-17 was a live credential in a
public repository that was flagged for rotation. Dukascopy XAU/USD was used
instead, and the fetcher retains a `--source lse` path so the entire study
re-runs against the LSE vault unchanged the moment a key is exported. Section 2
records what this substitution does and does not change.

---

## 2. The Dataset

### 2.1 What was requested, what was used, and why

| | |
|---|---|
| Requested | London Strategic Edge, XAU/USD, 1-minute, 2024-08-20 → 2026-08-19 |
| Blocker | `api.londonstrategicedge.com` returns **HTTP 401** — the host is reachable (the 403 tunnel refusal recorded on 2026-08-17 is gone) but no API key exists in this container's environment |
| Used | **Dukascopy XAU/USD**, 1-minute, both **bid and ask**, same window |
| Re-run path | `python3 code/fetch.py --source lse` — identical pipeline, one flag |

Dukascopy is the same provider whose `E_XJO-ASX` feed passed the ten-item
validation for the AU200 study. The substitution has one advantage over the
original plan worth noting: Dukascopy publishes **bid and ask separately**, so
Phase 27's cost model uses a *measured* historical spread rather than an assumed
one. LSE mid candles could not have supplied that. The repo has carried "measure
the actual spread" as an open gap for months; this closes it for gold.

What the substitution could change: absolute price levels differ slightly between
retail aggregators, and the exact minute at which a maintenance break starts and
ends is broker-specific. The break's *cause* — the CME/LBMA daily settlement
window at New York 17:00–18:00 — is not broker-specific, so the Section 7 finding
should reproduce on any gold feed, but the exact missing-day count may shift by a
few days on a different provider.

### 2.2 Provenance and semantics

| Field | Value |
|---|---|
| Dataset | Dukascopy Bank SA historical feed, `XAU/USD` |
| Asset type | Spot gold CFD, US dollars per troy ounce |
| Underlying | Dukascopy's own aggregated liquidity pool (their internal ECN) |
| Price type | **Bid** and **ask** pulled separately. All strategy work uses **bid**; ask is used only to measure the spread |
| Timestamp zone | **UTC** in the raw store |
| Timestamp semantics | Bar **open** time (verified: the 09:50 bucket's first minute carries local time 09:50, not 09:51 or 09:55) |
| Candle convention | Open = first tick of the minute, Close = last tick of the minute |
| Raw resolution | 1 minute |
| Retrieved via | `dukascopy-python`, monthly chunks, 4 retries with exponential backoff, hard-fail on a permanent chunk error rather than proceeding with a hole |

### 2.3 Volume

| | |
|---|---|
| Bid rows | **708,679** |
| Ask rows | 708,679 |
| First timestamp | 2024-08-20 00:00:00+00:00 |
| Last timestamp | 2026-08-19 23:59:00+00:00 |
| Duplicates | **0** |
| Zero-price rows | **0** |
| Invalid OHLC rows (`h < max(o,c)`, `l > min(o,c)`, `h < l`) | **0** |
| Distinct minute-gaps > 1 minute | 576 |

---

## 3. Data Audit

The 576 gaps are not defects. They decompose into exactly two populations:

**Weekend closures.** 104 gaps of roughly 47–48 hours, running from Saturday
~07:00 Melbourne to Monday ~07:00 Melbourne. Every one falls on a weekend
boundary. Gold does not trade then.

**The daily maintenance break.** ~470 gaps of almost exactly 60 minutes, one per
trading day. Section 7 characterises these precisely, because they are the single
most consequential fact in this study.

There is no third population — no random dropouts, no missing hours inside the
session, no stale-price runs. Weekend minute rows: 51,731, all in the Saturday
00:00–07:00 Melbourne window that is really Friday's New York session spilling
across the Melbourne date line. They are correctly excluded from setup days by
the weekday filter.

Nothing in this study is forward-filled, interpolated, or substituted. A missing
minute stays missing, and a 5-minute bucket records how many of its five
constituent minutes were actually present (`n_min`).

---

## 4. Melbourne Time Conversion

Every timestamp is converted through `zoneinfo.ZoneInfo("Australia/Melbourne")`,
**per bar**. The string `+10`, `+11`, `AEST` and `AEDT` appear nowhere in the
conversion path — the tz database decides the offset from the actual historical
date, which is the only way to get the four DST transitions inside this window
right.

Verified by hand reconstruction (`logs/validate.log`):

| Date | Melbourne | UTC of the 09:50 bucket | Implied offset |
|---|---|---|---|
| 2024-10-03 | 09:50 **AEST** | 23:50 (previous day) | UTC+10 ✓ |
| 2024-10-10 | 09:50 **AEDT** | 22:50 (previous day) | UTC+11 ✓ |
| 2025-04-23 | 09:50 **AEST** | 23:50 (previous day) | UTC+10 ✓ |
| 2025-10-17 | 09:50 **AEDT** | 22:50 (previous day) | UTC+11 ✓ |

5-minute candles are built by bucketing **Melbourne local** minutes, not by
resampling UTC and hoping the grids coincide. Because Australia's offsets are
whole hours the grids do in fact coincide, but that is verified rather than
assumed.

---

## 5. DST Analysis

This is the finding the brief anticipated, and it is larger than expected.

Gold's trading day is anchored to New York. Melbourne and New York change
daylight saving on different dates and in opposite hemispheres, so the Melbourne
clock time of the daily break moves through **three distinct regimes** in a year:

| Melbourne | New York | Break, Melbourne local | 09:50 present | 10:00 present |
|---|---|---|---:|---:|
| AEST | EDT | 07:00–08:00 | 261 / 263 | 261 / 263 |
| AEDT | EDT | 08:00–09:00 | 78 / 80 | 79 / 80 |
| **AEDT** | **EST** | **09:00–10:00** | **0 / 180** | 164 / 180 |

The third row is the whole story. When Melbourne springs forward in October and
New York has not yet fallen back, the break sits harmlessly at 08:00. When New
York falls back in early November, the break slides to **09:00–10:00 Melbourne**
and swallows the 09:50 reference candle whole. It stays there until New York
springs forward in mid-March.

Note the asymmetry in that row: 09:50 is gone on **all 180** days, but 10:00
survives on 164 of them — the break ends *at* 10:00, so the body candle is the
first candle of the new session. A naive implementation that only checked for the
10:00 candle would find it, compute a body, and then take `dOpen` from whatever
level a "daily open" happened to resolve to. That is precisely the failure mode
registered as BUG-039 in this repo. The engine here refuses: no 09:50 bucket, no
setup, day recorded as missing.

---

## 6. 09:50 / 10:00 Coverage

Denominator is Melbourne **weekdays** with any data (523). Saturdays carry data
from Friday's New York session but never contain a Melbourne morning, and are
excluded.

| | Days | 09:50 | 10:00 | Both |
|---|---:|---:|---:|---:|
| **All weekdays** | 523 | 339 (64.8%) | 501 (95.8%) | **339 (64.8%)** |
| AEST | 263 | 261 (99.2%) | 261 (99.2%) | 260 |
| AEDT | 260 | 78 (30.0%) | 240 (92.3%) | 79 |

By year (setup days available):

| Year | Weekdays | Both present |
|---|---:|---:|
| 2024 (from 08-20) | 95 | 53 |
| 2025 | 261 | 169 |
| 2026 (to 08-19) | 167 | 117 |

By month — the seasonal signature is unmistakable. Every November, December,
January and February in the sample sits near **zero**; every April through
September sits near **100%**. See `charts/coverage_by_month.png`.

**The usable research sample is 339 setup days out of 523 weekdays.** One third of
the calendar is structurally unavailable, and it is the same third every year.

---

## 7. Maintenance Gap Analysis

The gap is one hour, once per trading day, and it tracks **New York 17:00–18:00**
without exception across all three regimes above. That is the CME/LBMA daily
settlement and rollover window. Its Melbourne clock time is therefore fully
determined by the two DST calendars, and is predictable years in advance.

**This is a structural property of the gold market, not a data defect and not a
Dukascopy artefact.** No feed will have those candles, because no trading occurred
in them. The practical consequence for the user:

> Between roughly the first Sunday in November and the second Sunday in March,
> there is no 09:50 Melbourne gold candle to reference. The 10AM Body Break, as
> specified, is unavailable on gold for that entire period. This is not a
> filter that can be optimised away — the input data does not exist.

---

## 8. Baseline Reproduction

The Pine implementation is reproduced exactly for compatibility:

```
cost input = 2
SL = 18 − cost/2  →  $17.00 per ounce
TP = 40 − cost/2  →  $39.00 per ounce
```

These are **dollars per troy ounce**, not points, ticks or pips — a $17 stop on
gold at $4,000 is 0.43% of price. Entry is on the 5-minute close that confirms the
signal (`process_orders_on_close = true`). After entry the trade is resolved on
the **1-minute** path.

**Ambiguity: 0 of 607 trades (0.00%).** Not one trade had its stop and target
inside the same 1-minute bar — unsurprising at a $56 barrier separation. Every
headline number would be identical under the optimistic assignment. No tick data
was needed, and the "assume the target was hit first" hazard never arises.

Daily state: each logic fires at most once per day, on its first qualifying
close. Combinations use a no-pyramiding state machine — a second logic's trigger
is admitted only after the first trade has exited.

### Master baseline (full sample, SL $17 / TP $39, $1.26 round-trip cost charged)

| Logic | Trades | Win % | Avg Win | Avg Loss | Expectancy | PF | Net $ | Max DD | Winner Median MAE | Median MFE | Holdout PF |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A Short | 147 | 39.5 | 26.55 | −16.77 | 0.32 | 1.032 | +47 | 469 | 9.25 | 18.68 | 1.395 |
| A Long | 165 | 43.0 | 22.61 | −15.81 | 0.72 | 1.080 | +119 | 291 | 4.36 | 15.84 | 1.091 |
| Flip Long | 150 | 43.3 | 24.25 | −15.46 | 1.75 | 1.199 | +262 | 258 | 5.56 | 20.93 | **0.841** |
| Flip Short | 145 | 42.8 | 21.77 | −14.45 | 1.04 | 1.126 | +151 | 259 | 7.21 | 18.35 | 1.774 |
| Flip Both | 295 | 43.1 | 23.04 | −14.96 | 1.40 | 1.164 | +413 | 262 | 6.47 | 19.33 | 1.213 |
| A Short + Flips | 323 | 42.4 | 24.73 | −15.54 | 1.54 | 1.172 | +498 | 455 | 7.14 | 20.06 | 1.548 |
| Final Gold Candidate | — | — | — | — | — | — | — | — | — | — | **none** |

Two years, 339 setup days, and the best branch nets **$262 per ounce traded** —
about $2.60 a week on a single ounce. Against a max drawdown of $258. The whole
sample's profit is roughly one and a half stop-losses.

---

## 9. A Short

147 trades, PF 1.032 net of cost, expectancy $0.32. Gross of cost it is 1.168.
DEV 0.987, VAL 0.399, HOLD 1.395. AEST 1.465, AEDT 0.441.

The branch is a coin flip whose sign is set by whichever window you look at. It
has the largest drawdown of any branch ($469) and the worst validation result.

**No edge.**

## 10. A Long

165 trades, PF 1.080, expectancy $0.72. DEV 0.859, VAL 1.871, HOLD 1.091. The
control branch exists to detect long/short asymmetry, and it does show the
sample's one genuinely asymmetric feature: A Long's winners have a **median MAE
of $4.36** and an 80th percentile of $11.86 — far tighter than A Short's $9.25 /
$14.42. A Long winners tend to work immediately or not at all.

That is a real property of the *path*, but it is not an edge: the branch's
first-passage favourable rate never separates from 50% (best: 56.1% at ±$3,
p=0.138), and its DEV expectancy is negative.

**No edge.**

## 11. Flip Long

150 trades, PF 1.199, expectancy $1.75 — the best branch in the study, and the
only one to clear the measured spread on DEV (1.485) and hold on VAL (1.720).

**On the sealed holdout it returns PF 0.841, expectancy −$1.96 across 53 trades.**

Block bootstrap on the full sample gives an expectancy 90% CI of
**[−$1.31, +$5.05]** — containing zero. Monte Carlo gives a 5th percentile of
**+$3 net over two years**, which is to say the pessimistic case is exactly break
even. Walk-forward: 3 of 7 folds profitable, aggregate expectancy −$0.46 in the
6/2 design.

**No edge.** It is the branch that happened to win the in-sample lottery.

## 12. Flip Short

145 trades, PF 1.126, expectancy $1.04. DEV 1.026, VAL **0.357**, HOLD **1.774**.
Walk-forward 6/2: **+1.540**. Walk-forward 9/3: **0.676**.

This branch is the study's clearest demonstration of noise. Its rank among the
four logics changes with every partition, and two walk-forward designs applied to
the same data disagree in sign. AEST 1.681 vs AEDT 0.461.

**No edge.**

## 13. Combinations

| Combination | N | PF | Expectancy | Max DD |
|---|---:|---:|---:|---:|
| Flip Long + Flip Short | 295 | 1.164 | 1.40 | 262 |
| A Short + Flip Long | 178 | 1.366* | 3.21* | 231 |
| A Short + Flip Short | 292 | 1.228* | 1.94* | 495 |
| A Short + both Flips | 323 | 1.172 | 1.54 | 455 |
| A Long + A Short | 312 | 1.204* | 1.79* | 389 |
| All four | 362 | 1.210 | 1.90 | 462 |

\* gross of cost, from the Phase 1 table; costed figures for the three main
combinations are in the master table above.

Combining does not rescue anything. It cannot: the components are individually
indistinguishable from coin flips, and averaging coin flips produces a coin flip
with a smoother equity curve. "All four" looks tidiest precisely because it has
the most trades, which is a variance effect, not an edge.

---

## 14. MAE

Full distributions are in `tables/phases_1_27.md`. The structurally important
rows:

| Set | N | Mean | Median | p25 | p75 | p80 | p90 | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A Short winners | 58 | 14.75 | 9.25 | 3.82 | 13.45 | 14.42 | 37.27 | 105.46 |
| A Short losers | 89 | 39.72 | 31.81 | 21.35 | 54.51 | 62.50 | 75.03 | 124.98 |
| A Long winners | 72 | 6.02 | 4.36 | 1.54 | 10.14 | 11.86 | 13.07 | 25.29 |
| A Long losers | 93 | 40.76 | 31.96 | 21.21 | 51.40 | 55.02 | 87.89 | 145.66 |
| Flip Long winners | 68 | 7.63 | 5.56 | 2.39 | 11.30 | 11.67 | 13.58 | 69.10 |
| Flip Long losers | 82 | 47.90 | 35.70 | 18.75 | 59.00 | 63.58 | 98.04 | 303.23 |
| Flip Short winners | 66 | 8.81 | 7.21 | 3.70 | 12.17 | 13.72 | 15.57 | 38.87 |
| Flip Short losers | 79 | 35.58 | 26.28 | 16.04 | 44.37 | 51.65 | 67.89 | 141.82 |

Winners and losers separate cleanly on MAE — winner medians $4–9, loser medians
$26–36. That separation is real but it is **not tradeable information**: it is
measured after the fact, and the whole question is whether anything knowable at
the moment of a given adverse excursion tells you which population you are in.
Section 16 answers that.

## 15. MFE

| Set | N | Mean | Median | p75 | p90 | Max |
|---|---:|---:|---:|---:|---:|---:|
| A Short winners | 58 | 53.18 | 42.77 | 62.54 | 94.44 | 396.43 |
| A Short losers | 89 | 20.84 | 10.33 | 22.20 | 37.56 | 299.04 |
| A Long winners | 72 | 41.58 | 32.73 | 57.99 | 73.10 | 138.58 |
| A Long losers | 93 | 13.71 | 8.03 | 18.55 | 32.09 | 85.05 |
| Flip Long winners | 68 | 39.16 | — | — | — | 117.78 |
| Flip Long losers | 82 | 18.25 | 11.56 | — | — | — |
| Flip Short winners | 66 | 42.24 | — | — | — | — |
| Flip Short losers | 79 | 15.68 | 9.08 | — | — | — |

Winners typically run $33–43 before reversing; the $39 target sits right at that
median, which is why raising it does not help (Phase 9) — beyond ~$40 the sample
of trades that get there collapses.

## 16. Winner MAE — the stop-survival curve

Percentage of eventual winners that first suffered each adverse excursion:

| Logic | −$2 | −$3 | −$5 | −$7.50 | −$10 | −$12.50 | −$15 |
|---|---:|---:|---:|---:|---:|---:|---:|
| A Short | 65.5 | 58.6 | 43.1 | 32.8 | 27.6 | 19.0 | 12.1 |
| A Long | 40.3 | 33.3 | 25.0 | 18.1 | 12.5 | 8.3 | 5.6 |
| Flip Long | 45.6 | 39.7 | 27.9 | 20.6 | 14.7 | 8.8 | 5.9 |
| Flip Short | 61.9 | 53.0 | 34.8 | 21.2 | 13.6 | 9.1 | 6.1 |

Read this as the price of a tight stop. A $10 stop would have killed 12.5–27.6%
of the eventual winners; a $5 stop, 25–43%. The current $17 stop kills roughly
5% of them, which is defensible — **the stop is not the problem.**

**Recovery probability by adverse excursion reached** — of trades that got this
far against, what share still finished as winners:

| Logic | ≥$1 | ≥$3 | ≥$5 | ≥$10 | ≥$15 |
|---|---|---|---|---|---|
| A Short | 38% (n=145) | 33% (n=137) | 27% (n=125) | 19% (n=105) | 9% (n=90) |
| A Long | 40% (n=157) | 32% (n=132) | 27% (n=124) | 15% (n=107) | 6% (n=92) |
| Flip Long | 40% (n=145) | 34% (n=132) | 27% (n=119) | 17% (n=105) | 8% (n=88) |
| Flip Short | 41% (n=142) | 36% (n=131) | 32% (n=112) | 16% (n=92) | 8% (n=83) |

Recovery probability collapses through **$10–15 of adverse excursion**, at which
point it is under 20% and falling. This is consistent across all four branches —
the one genuinely stable pattern in the study.

## 17. Loser MFE

Percentage of eventual losers that first reached each favourable excursion:

| Logic | +$1 | +$2 | +$3 | +$5 | +$7.50 | +$10 | +$15 | +$20 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A Short | 84.3 | 74.2 | 65.2 | 51.7 | 40.4 | 30.3 | 20.2 | 14.6 |
| A Long | 78.5 | 68.8 | 60.2 | 45.2 | 33.3 | 23.7 | 15.1 | 9.7 |
| Flip Long | 86.6 | 79.3 | 72.0 | 58.5 | 46.3 | 35.4 | 22.0 | 15.9 |
| Flip Short | 82.3 | 72.2 | 62.0 | 48.1 | 34.2 | 24.1 | 13.9 | 8.9 |

Around half of all losing trades first showed **+$5** of profit, and roughly a
quarter to a third showed **+$10**. That looks like an argument for a breakeven
stop — and Phase 24 tests exactly that. It does not work, for the reason the
survival curve above explains: the winners that get through are the ones that
never came back to entry, and a breakeven stop set early converts a large number
of eventual winners into scratches. Only Flip Long's BE-at-$5 shows an
improvement (PF 1.750 → 3.381 on DEV), and it does so by cutting the win rate
from 52% to 26% while barely changing expectancy ($4.414 → $4.490). That is a
cosmetic PF, produced by shrinking the denominator, on the branch that then fails
the holdout.

---

## 18. First Passage

**This is the central test of the study.** For every entry, which symmetric
barrier ±$X is touched first on the 1-minute path.

Summary across all 64 tests (4 logics × 16 barriers):

| | |
|---|---|
| Tests where the 95% Wilson CI excludes 50% | **0 of 64** |
| Smallest p-value observed | **0.135** (Flip Short at ±$3, in the *wrong* direction — 43.4% favourable) |
| Range of favourable-first rates | 27.3% – 65.0%, all with CIs spanning 50% |
| Any monotonic structure across barriers | **None** |

Selected rows (full tables in `tables/phases_1_27.md`, chart in
`charts/first_passage.png`):

| Logic | ±$5 | ±$10 | ±$20 | ±$30 |
|---|---|---|---|---|
| A Short | 48.3% [40.3, 56.3] | 50.3% [42.3, 58.4] | 53.0% [44.0, 61.9] | 53.1% [43.2, 62.8] |
| A Long | 55.5% [47.8, 62.9] | 55.3% [47.6, 62.7] | 52.3% [43.7, 60.8] | 53.6% [43.7, 63.2] |
| Flip Long | 50.7% [42.7, 58.6] | 47.6% [39.7, 55.7] | 55.7% [46.5, 64.4] | 48.3% [38.2, 58.5] |
| Flip Short | 50.7% [42.6, 58.7] | 52.5% [44.3, 60.5] | 56.2% [46.6, 65.3] | 56.8% [45.9, 67.0] |

Unresolved days rise with barrier distance as expected (0% at ±$3, ~35% at ±$30,
~90% at ±$100) and ambiguous same-minute touches occur only at ±$1–$2.

**Where the money actually comes from.** Decomposing baseline P&L by exit type
makes the point unanswerable:

| Logic | Targets | Stops | EOD | $ from targets | $ from stops | $ from EOD |
|---|---:|---:|---:|---:|---:|---:|
| A Short | 33 | 77 | 37 | +1,287 | −1,309 | **+255** |
| A Long | 28 | 76 | 61 | +1,092 | −1,292 | **+527** |
| Flip Long | 28 | 66 | 56 | +1,092 | −1,122 | **+481** |
| Flip Short | 25 | 57 | 63 | +975 | −969 | **+327** |

Target dollars and stop dollars cancel to within 2% for every branch. The
strategy's stated thesis — that the break predicts which barrier gets hit — is
worth **zero**. Everything positive is in the residual: trades that never
resolved and were marked out at the end of the Melbourne day.

And that residual does not survive scrutiny either. Held to EOD with no barriers
at all, A Short returns PF 1.005 and Flip Long returns **0.952**.

---

## 19. Trade Path

Median forward movement in the trade's direction:

| Logic | 5m | 15m | 30m | 60m | 120m | 180m |
|---|---:|---:|---:|---:|---:|---:|
| A Short | −0.30 | −0.32 | −0.02 | −0.21 | 0.30 | 1.13 |
| A Long | −0.13 | 0.02 | 0.19 | −0.14 | 0.77 | 0.90 |
| Flip Long | 0.06 | 0.20 | −0.14 | −0.55 | −1.20 | 0.67 |
| Flip Short | −0.10 | −0.38 | −0.38 | −0.71 | 0.43 | −0.10 |

Median forward movement is within ±$1.30 of zero at every horizon out to three
hours, on a market whose median pre-entry 5-minute ATR is $2.79 — and it is
**negative** at most horizons for three of the four branches. The share of trades
positive at each horizon sits between 42% and 55% throughout. There is no burst
of directional follow-through after the break, at any timescale.

**Time-stop scan** (DEV, expectancy $): no horizon dominates. Flip Long improves
monotonically toward EOD (0.42 → 5.04 at 360m), A Long deteriorates toward EOD
(2.08 at 30m → 0.13), and the other two are flat. Two branches wanting opposite
time stops on the same data is not a finding, it is noise.

---

## 20. Fixed Stop Study

DEV, TP held at $39, stops from $2 to $100. Every branch's PF curve is flat and
jagged — the difference between the best and worst stop in the $10–$30 range is
within the noise band established by the bootstrap. There is no plateau.
Full table in `tables/phases_1_27.md`.

## 21. Fixed Target Study

DEV, SL held at $17, targets from $2 to $200. Same result. Very small targets
(≤$5) produce high win rates and negative expectancy — the classic
tight-target trap. Nothing above $40 has a usable sample.

## 22. SL/TP Heatmaps

400 cells per branch (10 stops × 10 targets × 4 logics). **No branch shows a
contiguous warm region.** Profitable cells are scattered singletons adjacent to
losing cells, which is the visual signature of fitting noise. The user's own
stated criterion — "I care much more about a BROAD profitable region than the
highest single cell" — is the correct one, and by that criterion every surface
fails. Full surfaces in `tables/phases_1_27.md`.

## 23. ATR-Normalised Stops / 24. ATR-Normalised Targets

Gold's volatility did not merely drift across this window, it transformed:
median pre-entry 5-minute ATR was **$0.82 in 2024 against $4.68 in 2026** — a
factor of 5.7. Sample median $2.79, computable on all 607 trades. A $17 stop is therefore a materially
different instrument at the two ends of the sample, and the brief was right to
demand normalisation.

ATR-normalised first passage (Phase 7b) tests barriers from 0.10× to 3.00× ATR.
The result is the same as the dollar version: favourable-first rates cluster
around 50% with CIs spanning it at every scale. Normalisation removes a genuine
confound and reveals nothing underneath it.

## 25. Entry Confirmation

Requiring the confirming close to clear the body edge by an extra buffer
($0.25 → $5) reduces N monotonically and moves expectancy without pattern. No
branch improves consistently. ATR-scaled buffers behave identically.

## 26. Exit Management

Full comparison in `tables/phases_1_27.md`. Against plain fixed 17/39 on DEV:

- **Breakeven stops**: help A Short (+$15 variant), hurt A Long, mixed for the
  Flips. Not consistent.
- **50% off at 1R**: hurts A Short and A Long, helps Flip Short. Not consistent.
- **Trailing stops**: $10 trail helps A Long dramatically (1.017 → 1.431) and
  hurts every other branch. Not consistent.

Not one management rule improves more than two of four branches. The brief's
standard — *must outperform simple rules out of sample before being accepted* —
is not met by any of them, and none is carried forward.

## 27. Flip Mechanism

The brief asks whether Flip is capturing a failed breakout, a stop run, a
liquidity sweep, trapped participants, mean reversion, or noise — and asks that
no label be assigned without evidence. The evidence is unusually clear, and it
points the opposite way to the intuition:

| Set | N | Win % | Expectancy | PF |
|---|---:|---:|---:|---:|
| Flip Long — **after** a real opposite breakout | 85 | 44.7 | 1.84 | 1.221 |
| Flip Long — **no** prior opposite breakout | 65 | 46.2 | **4.53** | **1.588** |
| Flip Short — **after** a real opposite breakout | 84 | 44.0 | 0.95 | 1.122 |
| Flip Short — **no** prior opposite breakout | 61 | 47.5 | **4.16** | **1.571** |

If Flip were capturing failed breakouts, stop runs or swept liquidity, the
"after a real opposite breakout" rows would be the strong ones — those are the
days on which the original direction genuinely committed and then failed. They
are the **weak** rows, on both flips, by a factor of two to four.

The flips that do better are the ones where price simply crossed back through a
level it had never meaningfully left. That is not a sweep. It is a narrow-range
morning producing a mechanical crossing, and it performs "better" mainly because
narrow mornings have smaller adverse excursions relative to a fixed $17 stop.

Geometry: median flip fires 5–7 five-minute bars after 10:00 (10:25–10:35
Melbourne), $1.46–1.82 beyond the body edge and $1.21–1.30 beyond dOpen. These
are small distances — comparable to two spreads.

**Verdict on mechanism: statistical noise, with a mild volatility artefact. The
sweep / trapped-participant reading is affirmatively contradicted.** This
matches the AU200 Phase 3 result, where the opposite-side sweep hypothesis was
rejected on all seven pre-registered criteria. Two independent markets, same
answer.

## 28. 10AM Structure

Seven structural variables (body size, full range, body/range ratio, upper wick,
lower wick, close−dOpen, 09:50 range) × 3 terciles × 4 branches = 84 cells on DEV.

No variable produces a monotonic relationship that holds in more than one branch.
A Short likes a large lower wick (−6.60 / −5.40 / +15.14) while Flip Long likes a
small one (7.78 / 4.97 / 0.47). Body/range ratio is decreasing for A Short and
increasing for Flip Short. Straddle flags are equally unstable.

With 84 cells examined, several will look monotonic by chance. None of them
replicate.

## 29. Volatility Regimes

ATR quintiles on DEV (cuts: $0.86, $1.39, $2.05, $2.88). No branch shows a
monotonic relationship between pre-entry volatility and expectancy. The largest
apparent effects sit on quintiles with n≈14–17 and are not stable.

**The strategy should not use a volatility regime filter** — there is nothing to
filter on. What volatility *does* affect is the meaning of the fixed dollar
exits, which is why Section 23/24 exists.

## 30. AEST vs AEDT

| Logic | AEST N | AEST PF | AEDT N | AEDT PF |
|---|---:|---:|---:|---:|
| A Short | 115 | 1.465 | 32 | **0.441** |
| A Long | 123 | 1.239 | 42 | 1.240 |
| Flip Long | 115 | 1.347 | 35 | 1.460 |
| Flip Short | 108 | **1.681** | 37 | **0.461** |

Two branches invert completely. But the honest reading is that **the AEDT sample
barely exists**: 79 setup days, all from the October and March/April shoulders,
because the November–March core is structurally absent (Section 5). Those 32–42
trades cannot support a conclusion in either direction.

The correct statement is not "the edge is weaker in AEDT" but "**the strategy is
untestable, and untradeable, for most of AEDT.**"

## 31. Session Context

Entries mapped to international sessions using real historical `Europe/London`
and `America/New_York` clocks — three zones with three different DST calendars,
so no fixed offset is used anywhere.

A 10:00 Melbourne setup entering between 10:05 and 16:00 Melbourne falls almost
entirely in the **Asian session**, with late entries reaching the London open.
No session shows a consistent advantage across branches. The London–NY overlap
has almost no trades, because it occurs after midnight Melbourne.

## 32. Entry Time

Ten Melbourne bands. Scattered results with no band good for more than two
branches, and the bands with the largest apparent effects have the smallest n.
The bulk of trades enter 10:05–12:00, as expected from the flip geometry.

## 33. Weekday

Expectancy $ / PF (n), gross of cost:

| Day | A Short | A Long | Flip Long | Flip Short |
|---|---|---|---|---|
| Mon | −2.25 / 0.79 (30) | 3.90 / 1.50 (32) | 9.64 / 2.53 (29) | 6.59 / 2.17 (27) |
| Tue | 6.44 / 1.78 (28) | 2.74 / 1.37 (32) | 4.74 / 1.69 (30) | 0.55 / 1.07 (30) |
| Wed | 1.78 / 1.23 (25) | 3.01 / 1.36 (38) | 2.66 / 1.41 (26) | 1.08 / 1.15 (33) |
| Thu | −0.75 / 0.93 (30) | −4.01 / 0.61 (35) | −1.92 / 0.83 (30) | 2.92 / 1.37 (32) |
| Fri | 2.88 / 1.31 (34) | 5.02 / 1.68 (28) | 0.50 / 1.06 (35) | 0.43 / 1.05 (23) |

Monday looks outstanding for both Flips (PF 2.53 and 2.17) and is the worst day
for A Short (0.79). Thursday inverts it. With n = 23–38 per cell and 20 cells
examined, spreads of this size are exactly what chance produces — a PF of 2.53 on
29 trades has a bootstrap interval that comfortably includes 1.0.

**No weekday is removed.** None has a defensible reason to be, and the brief
correctly forbids dropping a day for a bad in-sample number.

## 34. Monthly Performance

Full month-by-month table in `tables/phases_1_27.md`. The pattern that matters:
**November, December, January and February are empty or near-empty every year**,
for the structural reason in Section 7. Of the months that do trade, the all-four
net is positive in roughly 60% and the largest single month contributes about 20%
of the two-year total. Removing the best two months takes the aggregate to
approximately break even.

So: yes, the result depends on a handful of months, and it has no choice but to —
the strategy only has eight months a year to work with.

## 35. Economic News Analysis

**Partially completed, and the gap is disclosed rather than papered over.**

US Non-Farm Payrolls releases on the **first Friday of the month at 08:30 New
York** — a deterministic calendar rule requiring no external data. Those days are
tagged, and show no material difference in expectancy, PF or MAE against other
days on any branch.

CPI, PPI, PCE, FOMC decisions and Powell appearances are **not** rule-derivable.
No verified historical economic calendar was reachable from this container, and
this repo's evidence hierarchy forbids promoting an unverified external document
into an analysis. Rather than reconstruct dates from memory — which is exactly
the "plausible research document mixing real infrastructure with invented
specifics" hazard the standing rules warn about — those events are **left
untagged**, and this is logged in the failed-experiments section.

This does not change the verdict. A news filter can only remove trades; with no
edge in the retained population there is nothing for it to protect.

## 36. Costs and Slippage

The Pine `costPts` mechanism is not cost accounting. Setting `cost = 2` moves the
stop from $18 to $17 and the target from $40 to $39 — it **relocates the orders**
rather than charging the fill, so a winning trade still books its full target with
no deduction. Every result in this report charges the round trip to P&L and leaves
the orders where the rule puts them.

**Measured spread** — from the bid and ask feeds, across the 339 setup days,
10:00–16:00 Melbourne, 185,601 minute observations:

| | |
|---|---|
| Median | **$0.630** |
| p90 | $0.860 |
| p99 | $1.660 |

A round trip crosses the spread twice: **$1.26** before any slippage. All costed
results in this report use that figure, which is *generous* — it assumes zero
slippage on a 5-minute-close market order and no commission.

Cost sensitivity (DEV, expectancy $ / PF):

| Logic | $0.00 | $0.60 | $1.26 | $2.00 | $3.00 |
|---|---|---|---|---|---|
| A Short | 1.14 / 1.14 | 0.54 / 1.06 | ≈0.00 / ≈1.00 | −0.86 / 0.91 | −1.86 / 0.82 |
| A Long | 0.13 / 1.02 | −0.47 / 0.94 | −1.13 / 0.86 | −1.87 / 0.78 | −2.87 / 0.68 |
| Flip Long | 4.41 / 1.75 | 3.81 / 1.62 | 3.15 / 1.48 | 2.41 / 1.35 | 1.41 / 1.19 |
| Flip Short | 1.42 / 1.26 | 0.82 / 1.14 | 0.16 / 1.03 | −0.58 / 0.91 | −1.58 / 0.78 |

**At the measured spread alone, three of four branches are at or below break even
before a single cent of slippage.** Flip Long survives here — and then fails the
holdout.

## 37. Parameter Stability

Covered by Sections 20–22: no plateau in either dimension, no contiguous warm
region in the joint surface, and walk-forward re-optimisation selects different
cells in adjacent folds. Parameters are not stable because there is no underlying
quantity for them to be stable *about*.

## 38. Development Results

DEV = 2024-08-20 → 2025-08-19 (costed):

| Logic | N | Win % | Expectancy | PF | Net $ |
|---|---:|---:|---:|---:|---:|
| A Short | 71 | 42.3 | −0.12 | 0.987 | −9 |
| A Long | 85 | 41.2 | −1.13 | 0.859 | −96 |
| Flip Long | 73 | 49.3 | **+3.15** | **1.485** | +230 |
| Flip Short | 75 | 44.0 | +0.16 | 1.026 | +12 |

One candidate emerges: **Flip Long**.

## 39. Validation Results

VAL = 2025-08-20 → 2026-02-19 (costed):

| Logic | N | Win % | Expectancy | PF | Net $ |
|---|---:|---:|---:|---:|---:|
| A Short | 22 | 27.3 | −7.66 | 0.399 | −169 |
| A Long | 27 | 63.0 | +5.89 | 1.871 | +159 |
| Flip Long | 24 | 50.0 | **+5.64** | **1.720** | +135 |
| Flip Short | 23 | 26.1 | −8.49 | 0.357 | −195 |

Flip Long holds. Note the small n — VAL spans the southern summer, when most days
have no setup at all (Section 7). 24 trades in six months.

## 40. Final Holdout

HOLD = 2026-02-20 → 2026-08-19. **Opened once, after everything above was
written. Not used to choose any parameter.**

| Logic | N | Win % | Expectancy | PF | Net $ |
|---|---:|---:|---:|---:|---:|
| A Short | 54 | 40.7 | +4.16 | 1.395 | +224 |
| A Long | 53 | 35.8 | +1.07 | 1.091 | +56 |
| **Flip Long** | **53** | **32.1** | **−1.96** | **0.841** | **−104** |
| Flip Short | 47 | 48.9 | +7.10 | 1.774 | +334 |

**The candidate fails.** And the two branches that look best on the holdout are
the two that were worst on validation. Rank correlation between VAL and HOLD is
negative. This is not an edge degrading — it is a random reshuffle.

## 41. Walk-Forward

Rolling re-optimisation of SL and TP on the training window, applied to the next
test window. All planned folds reported.

**6 months train / 2 months test**

| Logic | Folds | Profitable | OOS trades | Expectancy | PF | Net $ |
|---|---:|---:|---:|---:|---:|---:|
| A Short | 6 | 0/6 | 90 | −5.03 | 0.498 | −453 |
| A Long | 7 | 3/7 | 113 | −0.79 | 0.906 | −89 |
| Flip Long | 7 | 3/7 | 110 | −0.46 | 0.955 | −50 |
| Flip Short | 7 | 4/7 | 102 | +3.94 | 1.540 | +402 |

**9 months train / 3 months test**

| Logic | Folds | Profitable | OOS trades | Expectancy | PF | Net $ |
|---|---:|---:|---:|---:|---:|---:|
| A Short | 3 | 1/3 | 78 | −4.30 | 0.632 | −335 |
| A Long | 3 | 1/3 | 78 | −1.17 | 0.856 | −91 |
| Flip Long | 3 | 1/3 | 81 | +0.71 | 1.066 | +57 |
| Flip Short | 3 | 0/3 | 70 | −3.01 | 0.676 | −211 |

Seven of eight logic-design combinations are negative. The one positive result —
Flip Short at 1.540 in the 6/2 design — **reverses to 0.676 in the 9/3 design on
the same data**. Neither design was cherry-picked; both were planned and both are
reported. Their disagreement is the finding.

## 42. Placebo Tests

### 42.1 Clock placebo — is 10AM special?

The identical method rebuilt at eight anchor pairs, on the 338 days where **all
eight pairs exist**, so no pair trades a different day set. Expectancy $ (PF, n),
net of cost:

| Anchor pair | A Short | A Long | Flip Long | Flip Short |
| --- | --- | --- | --- | --- |
| 09:30/09:40 | −0.04 (1.00) | −0.09 (0.99) | 1.41 (1.15) | −0.94 (0.90) |
| 09:35/09:45 | 1.16 (1.13) | 1.66 (1.18) | 0.37 (1.04) | −1.06 (0.89) |
| 09:40/09:50 | 1.98 (1.22) | 0.31 (1.03) | −0.81 (0.92) | −1.02 (0.90) |
| 09:45/09:55 | 2.35 (1.26) | 2.21 (1.25) | −0.45 (0.95) | −1.64 (0.83) |
| **09:50/10:00 (traded)** | **0.32 (1.03)** | **0.64 (1.07)** | **1.75 (1.20)** | **1.17 (1.14)** |
| 09:55/10:05 | −0.92 (0.91) | 1.67 (1.19) | 0.12 (1.01) | 1.89 (1.22) |
| 10:00/10:10 | −0.81 (0.92) | **3.12 (1.39)** | −0.48 (0.95) | 1.13 (1.13) |
| 10:05/10:15 | **2.91 (1.34)** | 1.70 (1.20) | 0.58 (1.07) | −2.64 (0.75) |

The traded pair ranks **6th of 8** on A Short, **7th of 8** on A Long, 1st on Flip
Long and 3rd on Flip Short. A time that mattered would dominate its neighbours on
most branches. This one is indistinguishable from a clock time picked at random
within the half hour.

Chart: `charts/clock_placebo.png`.

### 42.2 Random placebos

Three nulls, 2,000 iterations each, each preserving something real and destroying
the claimed edge:

| Logic | Observed exp $ | Null 1: random direction | p | Null 2: sign flip | p | Null 3: random entry time | p |
|---|---|---|---|---|---|---|---|
| A Short | 0.322 | 0.09 [−2.59, 2.73] | 0.448 | −1.27 [−4.35, 1.88] | 0.205 | −0.58 [−2.26, 1.42] | 0.237 |
| A Long | 0.722 | −0.02 [−2.44, 2.56] | 0.308 | −1.25 [−3.97, 1.60] | 0.123 | −0.67 [−2.26, 0.86] | 0.075 |
| Flip Long | 1.746 | 0.06 [−2.43, 2.75] | 0.142 | −1.18 [−4.34, 1.76] | 0.051 | −0.29 [−2.20, 1.46] | **0.033** |
| Flip Short | 1.039 | −0.79 [−3.40, 1.72] | 0.108 | −1.29 [−4.07, 1.61] | 0.093 | −0.37 [−2.09, 1.25] | 0.077 |

Every observed value falls inside its null distribution's 90% band. The smallest
p across twelve tests is 0.033 — which does not survive Section 45's threshold.

Note what Null 1 shows: **entering these same trades in a randomly chosen
direction produces a median expectancy of ≈$0.00**, and the observed values sit
comfortably within that distribution. The entry timing and the barriers are doing
the work; the direction is not.

## 43. Bootstrap

Block bootstrap, block = 10 consecutive trades (dependence within a regime is
real), 5,000 resamples, costed:

| Logic | N | Expectancy median [5, 95] | PF | Net $ | Max DD | P(net > 0) |
|---|---:|---|---|---|---|---:|
| A Short | 147 | −0.22 [−4.23, 4.17] | 0.98 [0.63, 1.45] | −32 [−622, 613] | 388 [185, 776] | 46.7% |
| A Long | 165 | 0.48 [−2.37, 3.23] | 1.05 [0.77, 1.40] | 79 [−390, 533] | 266 [135, 537] | 60.8% |
| Flip Long | 150 | 1.93 [−1.31, 5.05] | 1.22 [0.87, 1.70] | 290 [−197, 757] | 221 [124, 438] | 83.8% |
| Flip Short | 145 | 0.62 [−2.37, 3.77] | 1.07 [0.74, 1.49] | 90 [−343, 546] | 249 [129, 495] | 63.2% |

**Every 90% expectancy interval contains zero. Every PF interval contains 1.0.**

## 44. Monte Carlo

5,000 runs. Each reshuffles trade order, draws a round-trip cost uniformly from
$0.90–$2.50 (measured spread plus plausible slippage), and drops 10% of trades as
missed fills:

| Logic | Median net $ | 5th | 95th | P(profit) | Median DD | 95th DD | Median losing streak | 95th |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A Short | −17 | −188 | 155 | 43.3% | 283 | 450 | 8 | 13 |
| A Long | 42 | −141 | 218 | 64.9% | 255 | 414 | 8 | 12 |
| Flip Long | 176 | 3 | 340 | 95.4% | 206 | 336 | 7 | 12 |
| Flip Short | 78 | −86 | 228 | 78.5% | 221 | 355 | 7 | 12 |

Flip Long's 95.4% probability of profit looks encouraging until the magnitude is
read: the **5th percentile is +$3 over two years**, against a median drawdown of
$206. The distribution is centred on a rounding error. And this is the same
in-sample trade population that returns 0.841 on the holdout — Monte Carlo
reshuffles the trades it is given; it cannot detect that the population itself
was selected.

Expect losing streaks of **7–8 trades routinely and 12–13 at the 95th
percentile**, on a strategy that generates about six trades a month per branch.
That is a two-month losing run as a normal event.

## 45. Multiple-Testing Risk

| Family | Evaluations |
|---|---:|
| Logic branches and combinations | 10 |
| First-passage barriers | 64 |
| ATR-scaled barriers | 48 |
| Fixed stops | 76 |
| Fixed targets | 76 |
| SL × TP surface cells | 400 |
| Time stops | 44 |
| Structure terciles | 84 |
| Side definitions | 16 |
| Volatility regimes | 20 |
| Entry-time bands | 40 |
| Sessions | 16 |
| Weekdays | 20 |
| Entry buffers | 32 |
| Breakout-strength terciles | 48 |
| Exit-management variants | 32 |
| Cost levels | 36 |
| Walk-forward fold optimisations | 64 |
| Clock placebos | 32 |
| **Total** | **1,158** |

With K ≈ 1,158, the selection-adjusted significance bar is
**t ≥ √(2·ln K) = 3.76**, corresponding to p ≈ 0.0002. The best p-value produced
anywhere in this study is **0.033**, from a single cell of a twelve-cell placebo
family. It is not close.

Every finding in Sections 20–33 is labelled **EXPLORATORY**. The only
**CONFIRMATORY** results are the pre-registered ones: the first-passage tests, the
holdout, the walk-forward, the clock placebo, and the coverage audit — and all
five are negative.

## 46. Failed Experiments

Kept deliberately, per the standing rule that failed tests stay in the ledger.

1. **London Strategic Edge as the data source.** Host reachable, key absent.
   Pipeline retains `--source lse`. (G01)
2. **A verified historical economic calendar** for CPI/PPI/PCE/FOMC. No
   reachable, verifiable source; events left untagged rather than reconstructed
   from memory. (G19)
3. **The sweep / failed-breakout reading of Flip.** Tested directly and
   contradicted — flips *without* a prior opposite breakout perform better. (G11)
4. **A tighter stop justified by winner-MAE percentiles.** The percentiles do
   support a tighter stop a priori (winner MAE p80 is $11.67–14.42 against a $17
   stop); the parameter sweep shows no plateau there or anywhere. (G08)
5. **Breakeven exits justified by loser-MFE.** Half of all losers first showed
   +$5. Implementing BE at +$5 cuts win rates by half and leaves expectancy
   unchanged. (G18)
6. **Every conditioning variable**: structure, volatility regime, entry time,
   session, weekday, breakout strength, entry buffer, side definition. (G12–G18)
7. **Kronos foundation-model validation of the timeframe.** Not run — HuggingFace
   remains blocked at the proxy, so `NeoQuasar/Kronos-*` weights are unavailable.
   Standing limitation, unchanged.

## 47. Research Ledger

`results/research_ledger.csv` — 26 numbered experiments (G01–G26) with
hypothesis, sample, parameters, result, verdict, exploratory/confirmatory label
and notes. Failed tests retained.

## 48. Final Strategy

**None.**

The brief asks for up to three candidates — Simple Robust, Best Risk-Adjusted,
Best Performance — and explicitly permits returning fewer, or none, and forbids
manufacturing versions for presentation.

No branch clears the untouched holdout. No branch beats its own clock placebos.
No branch's bootstrap interval excludes zero. No branch shows first-passage
asymmetry at any barrier or any ATR scale. There is nothing here to promote.

## 49. Exact Trading Rules

Not issued, because Section 48 produces no candidate. The reconstruction used
throughout is fully specified in `code/core.py` and reproduced in Section 8, so
the negative result is checkable and re-runnable against a different feed.

## 50. Forward-Testing Plan

There is nothing to forward-test on gold. If the user wishes to re-open this,
the two things that would change the picture are:

1. **A different reference candle.** The 09:50 anchor is unavailable for a third
   of the year on gold and produced nothing in the two-thirds that remain. An
   anchor tied to gold's own session structure — the post-break reopen, the
   London fix, the New York cash open — is a different hypothesis, not a tuning
   of this one, and would need its own pre-registration.
2. **LSE data, if a key is supplied.** `code/fetch.py --source lse` re-runs the
   entire study unchanged. I would expect the same answer: the negative results
   here are driven by first-passage symmetry and clock placebos, neither of which
   is feed-specific. But the check is one command and the holdout discipline is
   already in place.

## 51. Final Verdict

# NO EVIDENCE OF GOLD EDGE

Not "weak", not "inconclusive", not "promising but not yet robust". The
distinction matters: an inconclusive result means the tests lacked power to
separate signal from noise. These tests had power and returned a clean negative.

- 64 first-passage tests, zero significant, at a search-adjusted bar of t ≥ 3.76.
- Target dollars equal stop dollars to within 2% on every branch — the trade
  thesis contributes nothing.
- The traded clock time ranks mid-pack against its own neighbours.
- The sole candidate returns PF 0.841 on data it never saw.
- Every bootstrap interval contains zero.

And separately from all of that: **for four and a half months a year the strategy
cannot be traded on gold at all**, because the candle it references does not
exist.

This is not the same claim as "the 10AM Body Break does not work". It is the
claim that **it does not work on gold, on this two-year window, in a way any of
these thirty-four tests can detect** — and that the structure that made it
attractive on AU200 does not transfer to a market whose session is anchored to
New York.

---

## Answers to the 30 Final Questions

1. **Does A Short have an edge on Gold?** No. PF 1.032 costed; DEV 0.987; 0 of 6
   walk-forward folds profitable; bootstrap CI [−4.23, 4.17].
2. **Does A Long?** No. PF 1.080; DEV 0.859; first passage never separates from
   50%.
3. **Does Flip Long?** No. Best in-sample branch (PF 1.199, DEV 1.485, VAL 1.720)
   and **0.841 on the untouched holdout**. Bootstrap CI [−1.31, 5.05].
4. **Does Flip Short?** No. PF 1.126, but VAL 0.357 against HOLD 1.774, and the
   two walk-forward designs disagree in sign.
5. **Which combination is strongest?** "All four", PF 1.210 — and it is strongest
   only because more trades means smoother noise. No combination is significant.
6. **Does the edge exist during both AEST and AEDT?** There is no edge in either.
   AEDT additionally has only 79 setup days, all from the shoulder months.
7. **How often is 09:50 unavailable?** On **184 of 523 weekdays (35.2%)** —
   including **180 of 180** AEDT + NY-EST weekdays.
8. **Is that caused by a daily Gold trading break?** Yes. The break tracks New
   York 17:00–18:00 and lands on 09:00–10:00 Melbourne from early November to
   mid-March. Structural, not a data defect.
9. **How far do eventual winners typically move against entry?** Median MAE
   $4.36–9.25 by branch; 80th percentile $11.67–14.42.
10. **How far do eventual losers move in favour before failing?** Median MFE
    $8.03–11.56. About half of all losers first showed +$5; a quarter to a third
    showed +$10.
11. **At what MAE does recovery probability collapse?** Through **$10–15**.
    Beyond $10 adverse, recovery is 15–19%; beyond $15, 6–9%. Consistent across
    all four branches — the study's one stable pattern.
12. **How quickly should a winning trade work?** Median time to a favourable $10
    touch is 57–72 minutes. But median forward movement is within ±$2 of zero at
    every horizon to three hours, so "quickly" is not diagnostic here.
13. **At what MFE should profits statistically be protected?** No level works.
    Breakeven and partial-exit rules were tested at +$5/$10/$15 and 1R and none
    improved more than two of four branches.
14. **Should the branches have different stops?** There is no basis to choose
    any stop. No branch shows a parameter plateau.
15. **Different targets?** Same answer.
16. **Are fixed-dollar exits appropriate?** Not across this window — median
    pre-entry 5-minute ATR went from $0.82 in 2024 to $4.68 in 2026, so a $17
    stop is a wholly different instrument at the two ends of the sample. ATR-scaled exits are the right *construction*; they do not create an
    edge.
17. **Are ATR-normalised exits more stable?** More principled, not more
    profitable. ATR-scaled first passage is as flat as the dollar version.
18. **Which volatility regimes work?** None consistently. No monotonic
    relationship in any branch.
19. **Which entry times work?** None consistently.
20. **Does the strategy depend on a handful of months?** Yes, unavoidably —
    removing the best two months takes the aggregate to roughly break even, and
    four months a year produce no trades at all.
21. **Does high-impact US news materially change the result?** Not for NFP, the
    only rule-derivable event. CPI/PPI/PCE/FOMC untagged — see Section 35.
22. **Does 09:50/10:00 outperform nearby-time placebos?** **No.** It ranks 6th of
    8 on A Short and 7th of 8 on A Long against its own neighbours.
23. **Does it survive realistic spreads/slippage?** No. At the measured $1.26
    round trip, three of four branches are at or below break even before
    slippage.
24. **Does it survive chronological validation?** Only Flip Long did, and only to
    the validation window.
25. **Does it survive the untouched holdout?** **No.** Flip Long: PF 0.841.
26. **Does it survive walk-forward?** No. Seven of eight logic-design
    combinations negative, and the one positive reverses under the other design.
27. **Does it survive bootstrap / Monte Carlo?** No. Every bootstrap expectancy
    interval contains zero; Monte Carlo's best 5th percentile is +$3 over two
    years.
28. **What is the simplest robust Gold version?** There isn't one.
29. **What is the actual market behaviour creating the edge?** There is no edge
    to explain. The gross positive P&L is entirely end-of-day residual drift on
    trades that touched neither barrier; the barrier contest itself is a coin
    flip. The apparent Flip advantage comes from flips on *narrow* mornings —
    which is a volatility artefact against a fixed dollar stop, and is the
    opposite of the sweep story.
30. **What would cause the strategy to stop working?** It is not working now, so
    the question inverts: what would have to be true for it to start? A genuine
    directional asymmetry at the break, which first passage says is absent at
    every barrier from $1 to $100 and every ATR scale from 0.10× to 3.00×.

---

## Reproducing this study

```
python3 code/fetch.py --source dukascopy --side both   # ~9 MB per side
python3 code/audit.py                                  # coverage + DST
python3 code/build_trades.py                           # ledger + paths
python3 code/validate.py                               # V1-V7 + hand checks
python3 code/analysis.py                               # phases 1-27
python3 code/robustness.py                             # phases 28-34
python3 code/charts.py
```

| Artefact | Path |
|---|---|
| Raw 1-minute bid / ask | `data/raw/xauusd_1m_{bid,ask}_dukascopy.csv.gz` |
| Setup days (339) | `data/processed/setups.csv` |
| Trade ledger (607) | `data/processed/trades.csv` |
| Per-day coverage | `tables/coverage_by_day.csv` |
| Phase tables | `tables/phases_1_27.md`, `tables/phases_28_34.md` |
| Audit JSON | `results/audit.json` |
| Research ledger | `results/research_ledger.csv` |
| Validation log | `logs/validate.log` |
| Charts | `charts/*.png` |
