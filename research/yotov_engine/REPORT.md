# Yotov Gold Quarter Engine v1 — built and tested

Built to the spec as given: the fixed price map, all four layers, all eight
trade families, the dual-hesitation lockout, the attempt counter, the $100
range-transition rule, and Spaceman structural confluence. Tested on both
XAUUSD Dukascopy tick years with the repo's fill convention, then phase-shift
controlled and zero-cost controlled.

Code: `code/{levels,engine,families,rung_sweep,ladder}.py`.
Results: `results/*.csv`. Reproduce with `python3 research/yotov_engine/code/run_engine.py 0.0 round`.

---

## Verdict

**The engine does not work, and the reason is structural rather than fixable by
tuning.** Every rung progression the spec is built on matches its closed form to
within about two percentage points, the whole engine is a coin flip once
execution cost is removed, and the round grid never beats grids shifted off the
round numbers. The one design choice that would have made it viable — larger
targets — is the opposite of the one the spec makes.

| | asked for | measured |
|---|---|---|
| trades / year | 250–500 | 22,558 (2025-26), 7,932 (2024-25) |
| win rate | ≥ 65% | 23.9% overall; 87.6% available, at PF 0.59 |
| profit factor | ≥ 2.5 | **0.527** |
| expectancy after costs | positive | **−$0.89 / trade** |
| best PF in any slice of the target trade band | — | **0.85** (60 slices searched, none reached 1.0) |

---

## 1. The 89.66% figure — verified, and it is arithmetic

First: `89.66`, `84.76` and `2708` appear nowhere in this repo. They came from
somewhere else, so I measured them here rather than building on them.

Every rung progression has a closed form. From a point x of the way through the
quarter, with the next rung at y and the origin at 0, a driftless walk reaches y
first with probability **x/y** — gambler's ruin, already registered here as H99.

Measured on the round $25 grid, both years, 106,451 attempts:

| step | H99 predicts | 2025-26 | 2024-25 |
|---|---|---|---|
| overshoot → HZ | 33.33% | 37.76% | 35.13% |
| HZ → half | 60.00% | 62.78% | 61.40% |
| half → whole | 62.50% | 64.11% | 63.64% |
| **whole → completion** | **88.89%** | **87.94%** | **87.35%** |
| **completion → target** | **90.00%** | **91.80%** | **91.12%** |

Every rung lands within ~2pp of the closed form, and Whole→Completion lands
*below* it in both years. So the cited 89.66% is real in the sense that a number
near it exists — it is 88.89% wearing a decimal place, and it is a property of
the number 0.8/0.9, not of gold.

**The phase control removes the last doubt.** Same ladder, grid shifted off the
round numbers, 12 phases:

| step | ROUND | shifted mean | round's rank |
|---|---|---|---|
| whole → completion, 2025-26 | 87.94% | 89.36% | **12 of 12** |
| whole → completion, 2024-25 | 87.35% | 89.74% | **11 of 12** |
| completion → target, 2025-26 | 91.80% | 90.36% | 2 of 12 |

On the step the spec calls "the highest-priority high-win-rate leg", the round
$25 grid is the **worst or second-worst of twelve grids**. Roundness is not
helping; it is very slightly hurting.

Two smaller notes: the 84.76% quoted for Completion→LQP does not reproduce — I
get 91.1–91.8%, and 90% is the closed form. And the eligible count of 2,708 is
larger than either year gives (1,608 and 245 live attempts), which suggests the
original counted touches rather than attempts still alive.

---

## 2. The engine as specified

All five priority families, both years, real bid/ask fills, 12-hour clock.
`EDGE` is the number that matters: realised win rate minus each trade's **own**
geometric baseline `p_geom = risk/(risk+reward)`. A rule that merely re-describes
the geometry scores zero here whatever its win rate.

**2025-26**

| family | n | PF | WR | p_geom | EDGE | exp $ | net $ |
|---|---|---|---|---|---|---|---|
| F1 sweep + reclaim | 16,596 | 0.48 | 11.3% | 19.2% | −7.8% | −0.82 | −13,625 |
| F2 quarter acceptance | 2,843 | 0.62 | 70.0% | 78.1% | −8.1% | −1.10 | −3,140 |
| F3 whole → completion | 1,487 | 0.44 | 67.7% | 81.9% | −14.2% | −1.52 | −2,263 |
| F4 failed completion | 1,354 | 0.59 | 25.6% | 34.6% | −9.0% | −1.16 | −1,569 |
| F5 major $100 transition | 278 | 0.58 | 56.5% | 69.2% | −12.7% | −4.78 | −1,327 |
| **ALL** | **22,558** | **0.52** | 23.9% | 32.3% | **−8.4%** | **−0.97** | **−21,924** |

**2024-25** reproduces it: ALL n=7,932, PF 0.55, edge −6.6%, −$5,125.

TIME exits are 0.1% of trades, so none of this is unresolved positions.

---

## 3. Why it loses — the zero-cost control

Re-resolving every trade mid-to-mid, no spread, no slippage:

| family | PF real | **PF zero-cost** | EDGE zero-cost |
|---|---|---|---|
| F1 sweep + reclaim | 0.492 | 1.036 | +1.7% |
| F2 acceptance | 0.634 | **0.982** | **+0.1%** |
| F3 whole → completion | 0.464 | 0.782 | −4.2% |
| F4 failed completion | 0.597 | 1.104 | +3.9% |
| F5 major transition | 0.592 | 0.689 | −8.8% |
| **ALL** | **0.527** | **0.984** | **+1.2%** |

**The signal is a coin flip. The entire loss is execution.** PF goes from 0.527
to 0.984 the moment you stop paying the spread, and the residual +1.2% is the
crossing-overshoot artefact already registered as H106.

### The part that bears directly on your objective

You asked for small targets because they give high win rates. On gold that is
the most expensive choice available:

| target size | n | WR | exp zero-cost | exp real | **cost as % of target** |
|---|---|---|---|---|---|
| ≤ $2 | 3,441 | 68.0% | −0.49 | **−2.20** | **108.9%** |
| $2 – $4 | 7,118 | 55.2% | −0.17 | −1.69 | 60.7% |
| $4 – $7 | 23,238 | 39.6% | −0.06 | −1.03 | 20.4% |
| $7 – $12 | 4,413 | 43.1% | −0.16 | −0.85 | 9.6% |

At the $2.50 target the spec specifies for families 3 and 4, **the round-trip
cost exceeds the entire prize.** Median spread is $0.69 and the realised cost is
$1.53–$1.71 per trade once stop slippage is counted. The win rate is real; it is
just sold to you at more than it is worth.

Here is that stated as plainly as the data allows — the wide-stop version of
your highest-priority leg, which is the closest executable analogue of the
89.66% claim:

> **"Whole → Completion, stop at the LQP": 85.1% win rate, 1,712 trades,
> expectancy −$1.46 per trade.** You get the win rate you were promised. It
> loses money on 85% winners.

---

## 4. All eight spec families

Pooled over both years, real fills vs zero-cost:

| family | n | tgt $ | PF | WR | EDGE | PF free | EDGE free | exp $ |
|---|---|---|---|---|---|---|---|---|
| 1 HZ → Half | 4,558 | 4.55 | 0.69 | 57.3% | −8.2% | 0.987 | **+0.3%** | −1.14 |
| 2 Half → Whole | 2,861 | 7.03 | 0.64 | 36.8% | −9.4% | 0.942 | **−0.1%** | −1.39 |
| 3 Whole → Completion | 1,712 | 2.03 | 0.46 | 67.8% | −13.6% | 0.782 | −4.2% | −1.45 |
| 4 Completion → LQP | 1,488 | 2.02 | 0.37 | 40.3% | −22.6% | 0.851 | −2.1% | −1.28 |
| 5 Failed HZ → LQP | 4,570 | 6.80 | 0.65 | 38.3% | −9.1% | 0.933 | **−0.3%** | −1.36 |
| 6 Failed Half → HZ | 2,846 | 4.29 | 0.66 | 58.6% | −8.7% | 0.987 | **+0.7%** | −1.24 |
| 7 Failed Whole → Half | 1,829 | 6.78 | 0.68 | 28.8% | −6.0% | 1.195 | **+6.2%** | −0.86 |
| over → HZ (control) | 12,285 | 4.58 | 0.52 | 28.7% | −13.0% | 0.946 | +0.6% | −1.16 |
| Whole → Comp, wide stop | 1,712 | 2.03 | 0.52 | **85.1%** | −6.6% | 0.804 | −2.4% | −1.46 |
| Comp → LQP, wide stop | 1,488 | 2.02 | 0.59 | **87.6%** | −4.9% | 0.990 | −0.5% | −1.12 |

Eight of eleven sit within ±1.0% of their own geometric baseline at zero cost.
Family 7 is the one exception at +6.2% — it got a full 12-phase control and an
out-of-sample split, and died on the second. See §6.

---

## 5. The phase control on the whole engine

Identical rules, grid moved off the round numbers. If the engine is about
quarters, the round grid must win.

| family | ROUND PF | shifted range | shifted mean | round's rank |
|---|---|---|---|---|
| F1 sweep + reclaim | 0.492 | 0.392 – 0.525 | 0.472 | 3 / 6 |
| F2 acceptance | 0.634 | 0.590 – 0.642 | 0.617 | 2 / 6 |
| F3 whole → completion | 0.464 | 0.458 – 0.549 | 0.500 | 5 / 6 |
| F4 failed completion | 0.597 | 0.473 – 0.599 | 0.557 | 2 / 6 |
| **F5 major $100 transition** | **0.592** | 0.778 – 1.086 | **0.902** | **6 / 6** |
| **ALL** | **0.527** | 0.457 – 0.554 | 0.522 | **4 / 6** |

The engine as a whole ranks mid-pack among grids that are not round. **The $100
range-transition rule — the most explicitly round-number-dependent rule in the
whole spec — is worst of six on the round grid**, and is the only family that
turns profitable anywhere, on the +11/12 shifted grid (PF 1.086). That is the
signature of noise, not of a boundary effect.

---

## 6. What the conditioning layers were worth

Layers 2–4 were built and measured, not assumed:

- **Structural confluence (Layer 2)** — distance to the nearest Spaceman level
  (DO, PDH/PDL, WO, PWH/PWL, Monday H/L, Asia H/L). Edge at ≤$0.50: −6.6%. At
  >$6.25: −9.8%. A 3pp ordering in the right direction, swamped by an 8pp cost.
  No individual level breaks out — all ten sit between −6.6% and −10.6%.
- **Attempt number (Layer 1)** — after fixing my first implementation, which
  counted *lifetime* attempts at each LQP (median 303, so the rule was never
  actually being tested) and re-running it as a 24-hour recency window: attempt 1
  scores +4.3% zero-cost edge against +1.0% for attempt 4+. **Your intuition here
  is directionally right** — fresh attempts genuinely do better. It is 3pp, and
  the spread costs 8pp.
- **Dual hesitation** — flagged trades score −9.2% against −7.8% unflagged. The
  filter points the right way and is worth 1.4pp.
- **Timing (Layer 4)** — the worst band is 18:00–20:00 NY at −16.4%, the rest sit
  between −6.2% and −8.5%. No band is positive.
### Family 7 — the one result that looked real, and how it died

**Failed Whole → Half** was the only family with a materially positive zero-cost
edge: +6.2% on n=1,829. It got the full treatment, because it deserved it.

**A full 12-phase control separated it.** Round scored +6.23% against a shifted
range of +0.36% to +3.96% (mean +2.36%, sd 1.22) — **rank 1 of 12, z = +3.16**.
That is the first time in this repo that a level-based rule has beaten its own
phase control. Across the other four reversal families the ranks were 2, 2, 8
and 11, so it was not a general "round is special" pattern either.

**A quote-clustering artefact was ruled out** before believing it: if gold quotes
piled up on round increments, a phase-0 grid line would sit on a popular quote
while shifted lines sat between them, manufacturing the effect. They do not —
quotes land on exact $0.25 boundaries **25× less often than uniform** (0.016% vs
0.400%), and the sub-cell structure is half-cent granularity spread evenly across
the cell.

**Then the out-of-sample split killed it:**

| | n | ROUND free edge | shifted mean | round's rank | z |
|---|---|---|---|---|---|
| 2025-26 (in-sample) | 1,596 | **+6.99%** | +2.60% | **1 / 12** | **+3.80** |
| 2024-25 (holdout) | 233 | +1.00% | +0.73% | **5 / 12** | **+0.06** |

In the unseen year the round grid sits dead centre of the shifted distribution.
The pooled result was carried entirely by the in-sample year, which supplies 87%
of the trades. **It does not replicate.**

And even taken at face value it was never tradeable: zero-cost expectancy
+$0.402/trade against an execution cost of $1.263. Break-even needs a spread
under $0.32; the measured median on those trades is $0.81.

---

## 7. Could any slice have hit the bar?

Exhaustive search over family × confluence × attempt × dual-hesitation × 6-hour
band × spread, keeping only slices that land in your 250–500 trades/year window:
**60 slices qualified. The best PF was 0.85. None reached 1.0.**

The best-scoring stack was "any family, no dual hesitation, 18:00–24:00 NY,
spread ≤ $0.50" — PF 0.85, WR 19.3%, −$0.18/trade. That is a search result over
60 candidates, so its true expectation is worse than it reads.

---

## 8. What this does and does not rule out

**Ruled out, on gold, on these two years:** that the $25 quarter ladder carries
directional information; that roundness contributes anything over an arbitrary
grid of the same spacing; that acceptance, dual hesitation, attempt count,
structural confluence or session timing convert the ladder into an edge; and
that a $2–2.50 target is executable on this instrument at this spread.

**Not ruled out, and worth saying:**
- **The FX claim.** Yotov's claim is about currencies. §1's mathematics carries
  to any market, but §2–§7 are gold-specific. The Dukascopy pipeline needs only
  a symbol change to test EURUSD.
- **The fundamental-catalyst gate.** The spec keeps Yotov's "quarters tell you
  where, fundamentals tell you when". Nothing here tests that, and as stated it
  is not falsifiable without a specified catalyst set.
- **Larger targets.** The cost table is the constructive finding: cost drag falls
  from 108.9% of target at $2 to 9.6% at $7–12. If an edge is worth hunting, it
  is at targets of $10+ where execution stops dominating — the opposite direction
  from the one the spec chose.
- **Displacement, not location.** The only thing in this repo that has ever
  survived its own control is displacement from the 10:00 open (z = 5.81). That
  is a momentum measurement, not a level measurement. Every level-based result
  tested here and in `research/quarters/` has failed a phase shift.

---

## 9. What I would not repeat

The spec's closing instruction — "don't search for another indicator, build a
hierarchy" — is good methodology and I followed it. It is worth recording that
the hierarchy did not fail because it was assembled wrongly. It failed because
its foundation, the rung ladder, is arithmetic, and no amount of conditioning
on top of a coin flip produces an edge; it only produces a smaller sample of the
same coin flip. The conditioning layers each moved the number by 1–3 percentage
points, in the direction the spec predicted, against an 8-point cost.

That is the useful part of this result: **the layers were not wrong, they were
too small.** Any future version needs an entry whose zero-cost edge is
materially above zero before any of the location, timing and state machinery is
worth adding.
