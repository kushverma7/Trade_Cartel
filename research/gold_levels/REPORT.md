# Gold price levels: quarters, round numbers, key levels, pivots

One year of Dukascopy XAUUSD ticks (52,223,814 ticks, 2025-08-21 -> 2026-08-20
Melbourne). Every test below carries a control that keeps the geometry and
removes only the claimed cause.

The question is never "do levels work". A grid of lines drawn every $25 will
always produce reactions, because price has to be somewhere. The question is
whether a ROUND grid does anything a grid of the same spacing at a different
phase would not.

---

## 1. Roundness does nothing that spacing does not

`code/grid_study.py` — S in {1, 2.5, 5, 10, 12.5, 25, 50, 100}, each at phase 0
(round), S/2 and S/3 (not round).

* Traverse advantage of the round phase: <= +0.0106, and it changes sign
  (-0.0014 at S=2.5, +0.0091 at S=25, +0.0106 at S=50, -0.0001 at S=100).
* P(continue to the next level) falls monotonically 0.4786 -> 0.0789 as spacing
  widens. That is random-walk geometry and it is identical on shifted grids.
* Magnetism sits at ~33.3% everywhere — the no-preference baseline. Round grids
  show marginally LESS time near their levels (31.6–32.6% at S=10..50) than the
  independent S/3 control (33.3–33.7%).

Only the S/3 column is an independent control; the S/2 column is arithmetically
complementary to the round one.

## 2. The acceptance ladder is the gambler's-ruin formula

`code/acceptance_ladder.py`, tick-exact. For a driftless walk starting x above
the bottom of an interval of width S, P(touch the top before the bottom) = x/S
exactly. Measured against that line:

| grid | x | observed | x/S | diff |
|---|---|---|---|---|
| $25 | $5 | 24.0% | 20.0% | +4.0 |
| $25 | $10 | 43.9% | 40.0% | +3.9 |
| $25 | $12.5 | 53.6% | 50.0% | +3.6 |
| $25 | $15 | 63.0% | 60.0% | +3.0 |
| $25 | $20 | 81.1% | 80.0% | +1.1 |

The ladder tracks x/S at every scale tested ($6.25 through $100), and the
"fractal" finding that 50% acceptance gives ~50% continuation on every grid size
is x/S evaluated at x = S/2. It equals 0.5 for every S, in any market, and in
simulated noise. It is not a property of gold.

Phase-shifted $25 grids reproduce the same ladder (x=12.5: 53.6% round vs
50.7–55.2% across six non-round phases).

What IS left over is the small positive residual, +1 to +5pp, growing with grid
size (+9.2pp at $100/x=$20). That is generic momentum, phase-independent, and it
is the only part of this that is about gold rather than about arithmetic.

**Note on the 8.42% figure.** Immediate continuation is a function of sampling
resolution, not a constant. At tick resolution it is 1.18% on the $25 grid;
coarser sampling implies a minimum acceptance and reads higher. Quoting it
without the resolution attached makes it look like a property of the market.

**Last digit.** 00 / 25 / 50 / 75 buckets: 1.33 / 0.98 / 1.40 / 1.11%. The
spread (0.41pp) is several binomial sd, so it is measurable, but it is a 0.4pp
difference on a ~1.2% base and 00/50 lead — a $50-grid pattern, not a "round
numbers break better" pattern.

## 3. Key levels and pivots: no edge over sham

`code/pivot_study.py` + `code/pdh_significance.py`. Rejection rate on first
touch, control = the same level type from a random other day rescaled to this
day's open, over 400 redraws.

| level | real | n | sham mean | sham sd | edge | p |
|---|---|---|---|---|---|---|
| PDH | 47.5% | 122 | 48.0% | 4.3% | -0.5pp | 0.589 |
| PDL | 53.8% | 93 | 53.2% | 4.8% | +0.6pp | 0.461 |
| PDC | 36.4% | 22 | 48.0% | 8.7% | -11.7pp | 0.925 |
| PP | 48.4% | 157 | 51.3% | 4.0% | -2.9pp | 0.756 |
| R1 | 44.5% | 110 | 47.6% | 4.3% | -3.0pp | 0.756 |
| S1 | 50.9% | 106 | 54.3% | 4.4% | -3.4pp | 0.798 |
| R2 | 48.1% | 54 | 48.1% | 6.0% | +0.1pp | 0.504 |
| S2 | 51.0% | 49 | 54.3% | 6.2% | -3.3pp | 0.703 |

Best edge across all eight is +0.6pp; the best of eight sham levels beats that
by chance with p = 0.998. Displacing the line +-1.5 to +-8 points produces no
peak at zero, so nothing is localised on the level. PDH is flat across horizons
of 3 to 48 bars and across both halves of the year.

**A first pass gave PDH +9.7pp and it was wrong** — see BUG-046. The sham had
been drawn ONCE. A single control draw is itself a random variable with sd
4–9pp here; that draw landed 2.4 sd low. Controls must be measured as
distributions.

## 4. The $25 proximity entry filter

`code/quarter_filter_test.py`. Trade selection reproduces exactly: locked
universe 131 -> 10AM body >= 1.0 -> 104 -> within $7.50 of a $25 quarter -> **59**.

Same filter, grid phase shifted 1..24 (identical spacing, identical tolerance,
numbers no longer round):

* round grid: PF 1.813, minPF 1.28
* 24 non-round grids: PF 1.578 +- 0.141 (1 of 24 beats round);
  minPF 1.01 +- 0.29 (**5 of 24 beat round**)

Adjacent phases share most of their trades, so these are far from 24 independent
draws. And random 59-of-104 subsets with no rule at all reach PF >= 1.81 22% of
the time and minPF >= 1.28 **38.5%** of the time.

The decisive number is on the declared primary metric:

| | n | PF | minPF across DEV/VAL/HOLD |
|---|---|---|---|
| no quarter filter | 104 | 1.580 | **1.36** |
| within $7.50 of a $25 quarter | 59 | 1.813 | **1.28** |

Full-sample PF rises. Minimum chronological PF falls. The filter buys a better
headline by discarding 43% of the sample.

## 5. Confluence (quarter + True Open) did not reproduce

`code/confluence_test.py`. At tick resolution the effect has the OPPOSITE sign:
crossings within $2.50 of the 18:00 NY True Daily Open continue MORE often
(1.74% vs 1.19%), and a displaced anchor at +$5 gives nearly the same lift
(1.59%), so nothing is localised on the open. Caveat: only 127 of ~260 true
daily opens could be located, because 18:00 NY falls inside gold's 09:00–10:00
Melbourne settlement break for much of the year (H92). Weakest test here.

## 6. Does snapping the EXIT to a round number help?

`code/round_tp.py`, locked entry universe, SL 15 fixed, scored on minPF.

Fixed TP 27 gives minPF 1.42. Snapping to the next $5 boundary 1 point short of
it gives 1.51; $10 boundary 1 short, 1.51; $25 boundary, 1.09–1.24; $50,
0.86–1.02. Shifted-grid controls at the same spacings give 1.16 and 1.06. All
differences sit inside the noise established above, and every snapped variant
also changes the mean TP distance (27.0 -> 29.6 -> 38.6 -> 50.8), which is a
simpler explanation for whatever moves.

No support for placing exits on round numbers rather than at a fixed distance.
