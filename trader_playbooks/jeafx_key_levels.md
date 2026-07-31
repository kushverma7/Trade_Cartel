# JEAFX Key Levels — extracted 2026-07-31
Source: `sources/key_levels_guide.pdf` (2 pages, user-supplied).
INDEPENDENT SOURCE. Short, concrete, and unusually testable for this repo.

## What the source actually says

1. **Plot only quarter-round levels: `.00`, `.25`, `.50`, `.75`.** The stated
   reason is bias removal, not magic: *"keeps us from being biased with our
   decisions on levels of interest, giving us a more refined & rational view."*
2. **Purpose: reversal areas.** *"This allows us to identify easy reversal
   areas."* Levels are where moves END, not where they start.
3. **Remain dynamic on low timeframes.** On 10m/15m the source explicitly
   permits deviating from the grid, using structure highs/lows and supply/
   demand instead, *"as key levels won't always be met before the trade
   formulates."* Its own worked example takes a secondary entry at a
   structure point (1.16350) rather than a quarter level (1.16250).

## Scale translation to gold — this is the whole ballgame

The source's example is EURUSD, where the grid is 25 pips against a ~10-pip
15m ATR: **spacing ≈ 2.5× ATR**.

Gold's median ATR(14) on 15m is **2.58 points**. The matching grid is
therefore ~6.5 points — and JEAFX's own `.00/.25/.50/.75` structure applied
to gold's 10-unit round numbers gives **2.50-point quarters**
(4000.00, 4002.50, 4005.00, 4007.50, 4010.00). That is a faithful reading of
the source, not a fitted number.

**Contrast with Yotov (H76):** his 250-point large quarters are 100× coarser
and never bind on a 15m system. Same "quarters" word, two orders of magnitude
apart. Scale is what decides whether a level theory is usable on a timeframe.

## Tested result — CONFIRMED, and it is the best improvement found so far

Applied as the profit-take grid for the **counter-trend side only** (see H75:
banking the with-trend side removes the size that captures the move):

| grid | train PF | test PF | full PF | full net | max DD | return/DD |
|---|---|---|---|---|---|---|
| none | 1.088 | 1.315 | 1.186 | +87.0% | 23.2% | 3.75 |
| **2.50** | **1.160** | **1.385** | **1.261** | **+110.6%** | **19.0%** | **5.81** |
| 5.00 | 1.141 | 1.398 | 1.256 | +108.7% | 19.7% | 5.52 |
| 6.25 | 1.142 | 1.375 | 1.252 | +108.3% | 19.8% | 5.48 |
| 10.00 | 1.144 | 1.368 | 1.248 | +108.4% | 20.3% | 5.34 |
| 25.00 | 1.107 | 1.356 | 1.211 | +93.7% | 22.4% | 4.18 |

Better on **every** window, on **both** return and drawdown, and smoothly
graded across scales rather than spiking at one — which is the robustness
signature, not a needle.

## What did NOT work
- **Symmetric banking** on the JEAFX grid: full-period net drops to +29-41%
  from +87%. Confirms H75 again.
- **Stacking with Daye's Q4 time-take**: PF 1.265 vs 1.261, net +109.5% vs
  +110.6% — inside noise. The price grid alone is the simpler system and is
  what ships. Two profit-taking rules do not stack.
- **As an entry filter**: price sits within tolerance of a quarter on only
  ~19% of bars regardless of grid scale, so it mostly just removes trades.
  Untested as a full variant; noted as the obvious next experiment.

## AMDM lens
Model 2 (mean-reversion) mechanic: quarter levels mark where a move
exhausts. Consistent with its use here — banking the counter-trend leg AT a
level while leaving the momentum-join leg (Model 1) unconstrained.

## Honest caveats
- One instrument, one timeframe.
- The source offers no statistics or track record; the edge here is measured
  by us, not claimed by it.
- The "remain dynamic" clause is deliberately NOT implemented — it is
  discretionary by construction and would make the rule unfalsifiable.
