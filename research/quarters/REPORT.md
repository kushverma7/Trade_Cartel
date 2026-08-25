# The Quarters Theory, backtested on gold

**Data.** Two independent Dukascopy XAUUSD tick years — **91,629,949 ticks**
(2025-08-21 → 2026-08-20, price range $3,321.45–$5,598.26) and **64,093,055
ticks** (2024-08-20 → 2025-08-20). Real bid/ask throughout.

**Method.** Yotov's rules are all fractions of the large quarter **S** —
tolerance 0.10S, hesitation zone 0.30S, half point 0.50S, target 1.00S — so the
system is scale-free and ports to gold by choosing S. Gold has no pip
convention, so **S is a researcher degree of freedom**: every scale is tested,
and every scale is tested against **11 phase-shifted grids of identical
spacing**. A shifted grid sees the same data, the same drift and the same
volatility, so anything the round grid does that a shifted grid does not is
attributable to roundness and nothing else. This is the GL03 control applied to
Yotov's own premise.

**Scope limit, stated up front.** This is a **gold** test. Yotov's claim is
about **FX**. Test 1's result is market-agnostic mathematics and transfers;
Tests 2 and 3 are gold-specific and do not settle the FX claim.

---

## Test 1 — the first-passage asymmetry

*From a crossing of quarter point Q, does price reach Q+S before Q−S? H99
predicts **0.500** for a driftless walk starting at a boundary — on any grid, in
any market, in simulated noise. Yotov's premise requires the round grid to beat
that.*

### The round grid is indistinguishable from any other phase

| year | S | n (round) | **ROUND** | shifted mean | shifted sd | shifted range |
|---|---|---|---|---|---|---|
| 2025-26 | $2.50 | 2,475,146 | 0.5231 | 0.5232 | 0.00005 | 0.5231–0.5232 |
| 2025-26 | $5.00 | 1,243,408 | 0.5123 | 0.5123 | 0.00009 | 0.5122–0.5125 |
| 2025-26 | $12.50 | 496,281 | 0.5052 | 0.5052 | 0.00004 | 0.5051–0.5052 |
| 2025-26 | $25.00 | 240,876 | 0.5027 | 0.5027 | 0.00007 | 0.5026–0.5028 |
| 2025-26 | $100.00 | 52,589 | 0.5010 | 0.5008 | 0.00004 | 0.5007–0.5009 |
| 2025-26 | $250.00 | 21,160 | 0.5005 | 0.5004 | 0.00008 | 0.5003–0.5005 |
| 2024-25 | $2.50 | 892,147 | 0.5100 | 0.5100 | 0.00005 | 0.5099–0.5100 |
| 2024-25 | $12.50 | 180,597 | 0.5021 | 0.5021 | 0.00004 | 0.5021–0.5022 |
| 2024-25 | $25.00 | 86,485 | 0.5012 | 0.5011 | 0.00007 | 0.5010–0.5012 |

The round grid ranks 1/12 at some scales and 9/12 at others, but the entire
spread across twelve phases is **two parts in ten thousand**. There is nothing
to rank.

### And the excess over 0.500 is a tick artefact, not the market

Prices move in discrete jumps, so the tape lands some distance *past* the line
it crosses. That head start biases the race toward continuation by
**overshoot / 2S**. If that is the whole story, the bias must scale as 1/S and
the mean overshoot must be flat in S. Both hold, and the prediction is
quantitative:

| year | S | mean overshoot | predicted excess | observed excess | ratio |
|---|---|---|---|---|---|
| 2025-26 | $2.50 | $0.1207 | 0.0241 | 0.0231 | **0.96** |
| 2025-26 | $5.00 | $0.1243 | 0.0124 | 0.0123 | **0.99** |
| 2025-26 | $10.00 | $0.1267 | 0.0063 | 0.0065 | **1.03** |
| 2025-26 | $12.50 | $0.1274 | 0.0051 | 0.0052 | **1.02** |
| 2025-26 | $25.00 | $0.1270 | 0.0025 | 0.0027 | **1.06** |
| 2024-25 | $2.50 | $0.0511 | 0.0102 | 0.0100 | **0.98** |
| 2024-25 | $10.00 | $0.0522 | 0.0026 | 0.0026 | **1.00** |
| 2024-25 | $25.00 | $0.0526 | 0.0011 | 0.0012 | **1.14** |

Mean overshoot is constant in S to within 5% across a hundredfold range of S,
and 2.5× larger in the higher-priced, more volatile year — exactly as the
mechanism requires. The ratio drifts above 1 only where the excess is
vanishingly small (S ≥ $50, excess < 0.002).

**Verdict: H99 confirmed on gold at every scale.** P(continuation) = 0.500 plus
a discretisation artefact of the crossing definition. There is no directional
information in a quarter-point crossing, round or otherwise.

---

## Test 2 — do swing extremes cluster near quarter points?

*This tests Yotov's rhetorical core. Throughout webinars 2 and 5 he points at a
daily or weekly extreme and asks whether it is a coincidence that it sits close
to a quarter point — 1.4257 is "only 7 pips" from 1.4250. The completion rule
counts anything within 0.10S as a hit, and that band is **20% of the price
axis** by construction.*

Daily and weekly extremes of mid, both years pooled:

| kind | S | n | **ROUND** | shifted mean | shifted range | rank | p vs 20% |
|---|---|---|---|---|---|---|---|
| daily | $12.50 | 1252 | 0.187 | 0.201 | 0.171–0.220 | 10/12 | 0.884 |
| daily | $25 | 1252 | 0.197 | 0.198 | 0.161–0.232 | 7/12 | 0.606 |
| daily | **$50** | 1252 | **0.225** | 0.199 | 0.179–0.224 | **1/12** | **0.015** |
| daily | $100 | 1252 | 0.201 | 0.199 | 0.177–0.225 | 4/12 | 0.466 |
| daily | $250 | 1252 | 0.196 | 0.203 | 0.164–0.252 | 7/12 | 0.659 |
| weekly | $12.50 | 214 | 0.192 | 0.200 | 0.168–0.229 | 6/12 | 0.647 |
| weekly | $25 | 214 | 0.187 | 0.200 | 0.168–0.238 | 8/12 | 0.710 |
| weekly | **$50** | 214 | **0.252** | 0.201 | 0.168–0.243 | **1/12** | **0.036** |
| weekly | $100 | 214 | 0.220 | 0.196 | 0.164–0.224 | 2/12 | 0.260 |
| weekly | $250 | 214 | 0.192 | 0.203 | 0.159–0.266 | 6/12 | 0.647 |

Eight of ten cells sit at the 20% base rate with the round grid mid-pack. Two
cells clear p < 0.05 — both at S = $50 — but **ten cells were tested**, so the
family-wise corrected p values are 0.15 and 0.36. Neither survives.

### Does the round grid's advantage replicate out of sample?

| kind | S | 2025-26 rank | 2024-25 rank | |
|---|---|---|---|---|
| daily | $12.50 | 9/12 | 11/12 | |
| daily | $25 | 6/12 | 8/12 | |
| daily | **$50** | **1/12** | **3/12** | the only cell that holds up |
| daily | $100 | 1/12 | 9/12 | |
| daily | $250 | 5/12 | 6/12 | |
| weekly | $12.50 | 1/12 | **12/12** | **inverts** |
| weekly | $25 | 4/12 | 12/12 | |
| weekly | $50 | 1/12 | 6/12 | |
| weekly | $100 | 2/12 | 4/12 | |
| weekly | $250 | 2/12 | **11/12** | **inverts** |

Weekly $12.50 goes from best-of-twelve to worst-of-twelve between years; weekly
$250 from 2nd to 11th. That is the **BUG-046** signature — an effect that exists
in one draw and inverts in the next. **Daily S = $50 is the single cell that
ranks top-3 in both years**, and it is one cell out of ten with a corrected
p of 0.15. Reported because it is the only thing here pointing the right way,
not because it is evidence.

**Verdict: extremes land near quarter points at the rate chance dictates, and
the round grid does not beat grids of identical spacing placed elsewhere.**

---

## Test 3 — the Hesitation Zone system, tick-exact

*The full system from webinars 4 and 5: trigger on a 0.30S penetration past a
quarter point, abort if price falls 0.10S back first, stop at Q, target the next
quarter point, 3-day clock. Real bid/ask fills, no overlapping trades.
1R = the realised entry-to-stop distance (≈ 0.30S plus the spread).*

### Round grid vs 11 shifted grids

| year | S | n | **ROUND PF** | shifted mean | shifted range | round's rank | ROUND net $ | phases with PF>1 |
|---|---|---|---|---|---|---|---|---|
| 2025-26 | $25 | 7381 | 0.811 | 0.797 | 0.783–0.832 | 2/12 | **−$9,187** | **0/12** |
| 2025-26 | $50 | 1931 | 0.852 | 0.897 | 0.843–0.953 | 10/12 | −$3,486 | **0/12** |
| 2025-26 | $100 | 528 | 0.942 | 0.984 | 0.902–1.096 | 9/12 | −$721 | 4/12 |
| 2025-26 | $250 | 87 | 1.059 | 1.149 | 0.883–1.552 | 10/12 | +$145 | 11/12 |
| 2024-25 | $25 | 1148 | 0.859 | 0.881 | 0.838–0.922 | 8/12 | −$965 | **0/12** |
| 2024-25 | $50 | 286 | 1.044 | 1.024 | 0.920–1.159 | 4/12 | +$117 | 8/12 |
| 2024-25 | $100 | 77 | 1.028 | 1.177 | 0.867–1.559 | 9/12 | +$26 | 9/12 |
| 2024-25 | $250 | 10 | 1.868 | 1.441 | 0.218–4.488 | 3/12 | +$172 | 5/12 |

Four things, in order of importance:

1. **The round grid is never the best.** Its ranks across the eight cells are
   2, 10, 9, 10, 8, 4, 9, 3 — median 8.5 of 12. It is a below-average member of
   its own phase family.
2. **Where the sample is large the system loses, on every phase.** At S = $25,
   **zero of twelve phases are profitable in either year**, and the round grid
   loses $9,187 on 7,381 trades.
3. **Where it makes money the sample has collapsed.** The profitable cells are
   n = 87 and n = 10, and their phase distributions span 0.883–1.552 and
   0.218–4.488. That is noise with a wide error bar, not an edge.
4. **The scale that "works" does not replicate.** In 2025-26 only $250 is
   positive; in 2024-25, $50, $100 and $250 are. Nothing holds across years.

### Config variants (round grid, both years)

No variant rescues it where the sample is big enough to mean anything:

| year | S | tol-target | wide-stop | long-clock |
|---|---|---|---|---|
| 2025-26 | $25 | 0.798 (−$9,976) | 0.832 (−$7,218) | 0.811 (−$9,187) |
| 2025-26 | $50 | 0.863 (−$3,180) | 0.867 (−$2,760) | 0.852 (−$3,485) |
| 2025-26 | $100 | 0.952 (−$566) | 0.936 (−$650) | 0.969 (−$382) |
| 2024-25 | $25 | 0.879 (−$853) | 0.888 (−$632) | 0.864 (−$932) |

`tol-target` credits Yotov's 25-pip completion tolerance (target at 0.90S);
`wide-stop` puts the stop one overshoot area past Q; `long-clock` relaxes the
Three-Day Rule to ten days.

### The dominant pattern is trade count

Expectancy improves monotonically as S grows and trades thin out, crossing zero
only where n is too small to trust:

| S | risk (0.30S) | spread as % of risk | n (2025-26) | expectancy |
|---|---|---|---|---|
| $25 | $7.50 | 8.9% | 7381 | −0.138R |
| $50 | $15.00 | 4.5% | 1931 | −0.107R |
| $100 | $30.00 | 2.2% | 528 | −0.022R |
| $250 | $75.00 | 0.9% | 87 | +0.118R |

That is the signature of a rule paying the spread without an edge to cover it —
the same verdict the all-day QT sweep reached in Phase 9.

### One config was mis-specified and is discarded

An early `no-filter` control put both the entry and the stop at Q, leaving risk
≈ the spread; it stopped out almost instantly (PF 0.065, WR 0.3%). That is a
spec error, not a result. It is re-run correctly as `entry-at-level` in
`run_controls.py`, with the stop 0.30S the wrong side of Q so the risk matches
the baseline.

### Why it loses — the zero-cost control settles it

Refilling the identical trades on **mid** instead of bid/ask:

| S | real quotes | **zero cost** | execution cost | nominal spread/risk | ratio |
|---|---|---|---|---|---|
| $25 | PF 0.811 (−0.1383R) | **PF 1.011 (+0.0080R)** | 0.146R | 0.089R | 1.64× |
| $50 | PF 0.852 (−0.1075R) | **PF 0.987 (−0.0093R)** | 0.098R | 0.045R | 2.20× |
| $100 | PF 0.942 (−0.0405R) | **PF 1.010 (+0.0070R)** | 0.048R | 0.022R | 2.15× |
| $250 | PF 1.059 (+0.0342R) | PF 1.082 (+0.0469R) | 0.013R | 0.009R | 1.44× |

**Zero-cost profit factor is 0.99–1.01 at every scale with a real sample.** The
signal is a coin flip. The entire loss is execution.

And execution costs **1.4–2.2× the nominal spread**, not 1×. Half the spread is
paid at entry and half at exit, but there is a third cost: with real quotes the
**bid** reaches a long's stop before the mid would, while having to climb an
extra half-spread to reach its target. Some would-be winners become losers.

### The Hesitation Zone filter does not earn its keep

Entering **at** the quarter point with the same dollar risk (stop 0.30S the
wrong side, so risk matches the baseline) loses less at three of four scales:

| S | with the 0.30S filter | entering at Q |
|---|---|---|
| $25 | 0.811 (−$9,187) | **0.871** (−$5,064) |
| $50 | 0.852 (−$3,486) | **0.885** (−$1,947) |
| $100 | **0.942** (−$721) | 0.901 (−$934) |
| $250 | 1.059 (+$145) | **1.273** (+$759) |

The two constructions differ in reward:risk (2.33 vs 3.33), which is the
mechanism — but that *is* the choice Yotov's filter makes, and it is the worse
one on this data.

### It is not an artefact of gold's +34% year

Longs and shorts lose at about the same rate: PF **0.828** and **0.793** at
S = $25, **0.890** and **0.813** at S = $50.

### What "inverted" does and does not say

Negating the R series gives PF 1.233 / +0.138R. That is **arithmetic, not a
tradeable result** — actually trading the inverse would pay the spread again
rather than receive it, and would mirror the geometry to RR 0.43 instead of
2.33. The row is a **sign check**: it confirms the loss is real and not a coding
error. The substantive statement is the zero-cost one — expectancy ≈ 0 means
there is no directional information to invert, and both sides lose once the
spread is paid. Which is the Phase 9 verdict reached a second way.

---

## Answering the two fair objections

### Objection 1 — "tick-touch overtrades; Yotov reads bar closes"

True, and it is the most aggressive possible reading. Re-run with the trigger
being the first **H1 or D1 close** beyond Q + 0.30S, entered at the next tick:

| bar | year | S | n | **ROUND PF** | ROUND net $ | shifted PF range | round's rank |
|---|---|---|---|---|---|---|---|
| H1 | 2025-26 | $25 | 819 | 0.817 | −$984 | 0.781–0.895 | 3/4 |
| H1 | 2025-26 | $50 | 273 | 0.954 | −$176 | 0.717–1.218 | 3/4 |
| H1 | 2025-26 | $100 | 70 | 0.828 | −$203 | 0.541–0.921 | 3/4 |
| H1 | 2024-25 | $25 | 179 | 0.714 | −$335 | 0.768–0.815 | **4/4** |
| H1 | 2024-25 | $50 | 33 | 0.619 | −$193 | 0.676–0.786 | **4/4** |
| D1 | 2025-26 | $25 | 152 | 1.058 | −$75 | 0.726–1.195 | 2/4 |
| D1 | 2025-26 | $50 | 111 | 1.152 | −$234 | 0.691–1.154 | 2/4 |
| D1 | 2024-25 | $50 | 41 | 1.353 | +$102 | 1.017–1.104 | 1/4 |

Totals: **H1 round −$1,890**, D1 round **−$492** against shifted grids averaging
**+$492 per phase**. The round grid is the worst or second-worst of its four
phases in every H1 cell. Bar-close entry cuts the trade count by an order of
magnitude and does not turn the system profitable.

*Reading note: with a close-based entry the per-trade risk varies over
[0.30S, S), so net R and net dollars can disagree in sign. Dollars are the
honest measure here.*

### Objection 2 — "you left out the Trend Waves"

Also true. The Trend Wave layer's testable core is momentum, so the crudest
proxy is applied — only take longs when price is above where it was N days ago —
**to the round grid and the shifted grids alike**. The question is not whether
momentum helps. It is whether the quarters contribute anything once it does.

| filter | round mean PF | shifted mean PF | round net $ | shifted net $ per phase |
|---|---|---|---|---|
| none | 0.967 | **1.060** | −$4,063 | −$1,674 |
| 1-day trend | 0.996 | **1.107** | −$2,179 | **+$174** |
| 3-day trend | 1.001 | **1.082** | −$2,888 | −$308 |
| 10-day trend | 0.924 | **1.000** | −$2,632 | −$959 |

Momentum helps a little — and it helps the **shifted** grids more. Under every
filter the round grid's mean PF is below the shifted mean, and its net dollars
stay negative while the shifted average turns positive at the 1-day filter.
Bolting Yotov's trend layer onto his quarters makes the case for roundness
*worse*, not better.

---

## Verdict

**The Quarters Theory does not work on gold, and the roundness of the grid
contributes nothing.** Three independent tests agree, both fair objections were
tested and neither changes the answer, and the mechanism is settled:

1. The premise's own decisive measurement returns **0.500** — the gambler's-ruin
   value — plus a tick-discretisation artefact that is fully explained and has
   no market content. Largest round-vs-shifted gap across 192 cells: **0.0002**.
2. Swing extremes land near quarter points at exactly the rate chance dictates.
3. The traded system loses. At the trade-dense scales **no phase is profitable
   in either year**, and the round grid is a below-average member of its own
   phase family (median rank 8.5 of 12).
4. **With zero costs the profit factor is 0.99–1.01 at every scale with a real
   sample.** The signal is a coin flip; the entire loss is execution.
5. Yotov's own Hesitation Zone filter makes it worse than entering at the level
   with identical dollar risk.

### What this does not settle

- **Gold, not FX.** Test 1 is market-agnostic mathematics and transfers. Tests 2
  and 3 are gold-specific and do not refute the FX claim, which remains untested
  here. Running the same phase-shift control on EUR/USD, GBP/USD, USD/JPY and
  AUD/USD is the obvious next step and needs only a symbol change in the
  Dukascopy pipeline.
- **The discretionary overlay.** The "strong enough fundamental reason" gate is
  unfalsifiable and was not tested; it cannot be.
- **The Trend Waves layer on its own.** It was tested only as a *filter on the
  quarters*. As standalone swing-structure analysis it may have merit — but that
  is a separate claim with nothing to do with round numbers.

---

## Reproducing

```
python3 research/quarters/code/run_asymmetry.py   # Test 1
python3 research/quarters/code/overshoot.py       # why the excess exists
python3 research/quarters/code/run_extremes.py    # Test 2
python3 research/quarters/code/run_system.py      # Test 3: round vs 11 phases
python3 research/quarters/code/run_controls.py    # entry-at-level, zero-cost, inverted
python3 research/quarters/code/run_barclose.py    # H1/D1 close trigger
python3 research/quarters/code/summarise.py       # the tables above
```

Engine verified by hand against the raw tape: a long (Q $3,900, trigger $3,930,
entry $3,930.335 paying the ask, target $4,000, stop $3,900) and a short
(Q $4,300, trigger $4,270, entry $4,268.084 paying the bid, target $4,200)
reconcile to the cent on entry side, P&L and risk.
