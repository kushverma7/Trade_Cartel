# One-Year In-Sample Optimisation Study — XAUUSD

> ### *** EVERY NUMBER IN THIS DOCUMENT IS IN-SAMPLE. ***
> Window: **2025-08-21 → 2026-08-20**, one year, 91,629,949 raw Dukascopy ticks.
> The 2024-25 holdout year exists in this repository and was **deliberately not
> used**, at explicit direction. Transferability was **not** an objective. No
> result below has an out-of-sample test, and none is marked VALID.
> Ledger rows: **IS01–IS10** in `RESULTS_LEDGER.md`.

## What was asked

> *On the 2025-26 year alone, with exact raw Dukascopy tick execution, can
> **PF 8.10 with ≥20 trades** and/or **PF 5.29 with ≥25 trades and DD ≤1R** be
> beaten?*

**Yes, both.** PF **8.73** at n=20 (DD 1.00R) and PF **8.09** at n=25 (DD 1.00R).

The rest of this document is the part that matters more than the yes.

## Construction

896 Quarterly Theory cycles. NY daily cycle boundaries 18:00 / 00:00 / 06:00 /
12:00, four 90-minute quarters inside each. Entry at the Q3 open following a Q2
sweep of a Q1 extreme; direction opposite the swept side; structural stop at the
Q2 extreme, structural target at the opposite Q1 extreme. **1R = |entry −
structural stop|.**

**Fill convention.** Long enters ask and is marked out on bid; short the reverse.
A target is a resting limit at an exact price — it fills **at** the target and
favourable overshoot is never credited. A stop is market-triggered and fills at
the real next executable quote, including slippage past the level. A time exit
fills at the quote showing when the clock runs out.

Search: **246,807 grid cells** over eight structural dimensions (cycle, sweep
type, Q2 efficiency, DFR/Q1, Q1 efficiency, reward:risk, sweep depth, activity
band), against a base universe of **PF 0.581 / −0.288R over 896 cycles**.

## The ten model categories

| # | category | rule | n | PF | exp R | net R | DD | R² | mo+ |
|---|---|---|---|---|---|---|---|---|---|
| 1 | absolute highest PF | D123, both-sweep, Q2eff≤0.5, DFR≤0.85, Q1eff≥0.3, RR≤0.75, swd≤9 | 13 | ∞ | +0.205 | +2.67 | 0.00 | 0.928 | 7/7 |
| 2 | highest PF, n≥20 | D123, Q2eff≤0.4, DFR≤0.85, RR≤0.75, act 0.3–0.8 | 20 | **8.73** | +0.387 | +7.74 | 1.00 | 0.965 | 8/9 |
| 3 | highest PF, n≥30 | ALL, Q2eff≤0.4, DFR≤0.75, Q1eff≥0.2, RR≤2, act 0.3–0.8 | 31 | 6.14 | +0.551 | +17.08 | 1.02 | 0.966 | 10/11 |
| 4 | highest net R | ALL, single sweep, DFR≤0.9, Q1eff≥0.2, swd≤0.1 | 45 | 2.93 | +0.707 | **+31.81** | 5.47 | 0.879 | 9/12 |
| 5 | highest expectancy | D123, DFR≤0.7, Q1eff≥0.2, swd≤0.1 | 15 | 5.54 | **+1.781** | +26.72 | 3.60 | 0.922 | 7/9 |
| 6 | smoothest equity | D1, Q2eff≤0.4375, RR≤1, act 0.2–0.8 | 22 | 3.79 | +0.301 | +6.62 | 1.00 | 0.952 | **10/10** |
| 7 | lowest DD, n≥20 | ALL, Q2eff≤0.4375, DFR≤0.75, RR≤1, act 0.3–0.8 | 23 | 8.51 | +0.425 | +9.77 | 1.00 | 0.959 | 10/11 |
| 8 | best activity-gated | *identical to #2* | 20 | 8.73 | +0.387 | +7.74 | 1.00 | 0.965 | 8/9 |
| 9 | best pure QT | ALL, single sweep, DFR≤0.8, Q1eff≥0.2, swd≤0.075 | 20 | 4.55 | +1.165 | +23.30 | 3.04 | 0.868 | 7/9 |
| 10 | best all-day | ALL, Q2eff≤0.4375, DFR≤0.9, Q1eff≥0.2, RR≤0.75, act 0.3–0.8 | 25 | **8.09** | +0.324 | +8.11 | 1.00 | 0.955 | 10/11 |

Note #8 is not a separate model — the activity-gated search returns #2 exactly.
Nine distinct models, not ten.

## Ranking, and why it is not by PF

Ranked by **how much of the result survives contact with a question**, not by PF:

1. **#4 highest net R** (n=45, PF 2.93, +31.81R). The largest sample, the least
   extreme PF, the only model whose drawdown (5.47R) is large enough to have been
   *measured* rather than avoided. Ranked first because it is the only one that
   would still be recognisable if three trades were deleted.
2. **#3 highest PF at n≥30** (n=31, PF 6.14, +17.08R). Best compromise on the
   sample-size axis; survives the exit substitution better than #2 or #10 (see
   below); 10 of 11 months positive.
3. **#9 best pure QT** (n=20, PF 4.55, +23.30R). No activity gate, no efficiency
   filters — sweep depth ≤0.075 and DFR ≤0.8 only. The rule closest to a stated
   structural hypothesis rather than a fitted one.
4. **#5 highest expectancy** (n=15, +1.781R a trade). Real money per trade but
   fifteen trades is fifteen trades.
5. **#6 smoothest equity** (n=22, PF 3.79, 10 of 10 months positive). The
   smoothness is real on this year; the PF is modest, which is the honest trade.
6. **#10 best all-day** and **#2 highest PF at n≥20**, the two benchmark-beaters.
   Ranked *below* models with worse PF, for the reason in the next section.
7. **#7 lowest DD** (n=23, PF 8.51, DD 1.00R). Same objection as #2/#10.
8. **#1 absolute highest PF** (n=13, PF ∞, DD 0.00R). PF is infinite because no
   trade lost. Thirteen trades, zero losses, zero drawdown — reported for
   completeness and for nothing else. **Rule 4 of the evidence hierarchy applies:
   a drawdown of 0.00R is a bug until proven otherwise; here it is not a bug, it
   is a selection.**

## What the exit study found — the most important section

34 exit families × 6 universes, plus a 5×6 stop×target surface, all tick-exact.
Full output: `results/exits.log`.

**1. The high PF belongs to the target definition, not to the trade selection.**
Every benchmark-beating model carries **RR ≤ 0.75** — the filter *guarantees* the
structural target sits closer than the structural stop. Replace it with any fixed
multiple of R and the result collapses:

| universe | structural target | best of the whole 5×6 fixed-R surface |
|---|---|---|
| #2 n=20 | **PF 8.73** | PF 3.93 (1R target) |
| #10 n=25 | **PF 8.09** | PF 4.17 (SL 1.25R, TP 0.75R) |
| #3 n=31 | **PF 6.14** | PF 3.27 (SL 1R, TP 0.75R) |

A PF above 8 is what a sub-1R target with a 92–95% win rate produces. It is not
evidence of a better entry.

**2. PF and money point at different exits.** For #2, the structural target
returns PF 8.73 / **+7.74R**, while a plain fixed 1R target returns PF 3.93 /
**+10.87R** — 40% more money at less than half the profit factor. For #10, fixed
3R returns +10.41R against the structural +8.11R. Optimising PF actively selected
*against* expectancy.

**3. The stop is barely a participant.** For #2 and #10, results at stop 1.25R,
1.5R and 2R are **identical to three decimals** (PF 11.95 / 10.58, DD 0.73R):
**no trade in either subset ever ran more than 1.25R against**. This is the same
pathology as the MaxPF audit — PF 21.3 on 15 trades none of which touched a stop,
worth **3.35** once stops are enforced.

**4. Every management overlay is neutral or harmful.** Break-even at ≥0.75R,
trailing at 1.5R, and all six partial-profit variants return the *exact baseline*
for #2 and #10 — median hold is 23 minutes, so they never trigger. The ones that
do trigger destroy the result: break-even at +0.25R takes #2 from 8.73 to 3.61;
trailing 0.5R takes #3 from 6.14 to 2.14. **There is no management overlay worth
adding.**

**5. Time bound is close to irrelevant, and longer is mildly better.** +6h beats
the +3h baseline on #10 (9.92 vs 8.09) and #3 (6.93 vs 6.14); ending at Q3 is
worse everywhere. Given the 23-minute median hold, these are a handful of trades.

**6. Nothing rescues the base universe.** Across all 34 families the best base
result is **PF 0.66** (no target, time only); the 30-cell stop×target surface spans
0.41 to 0.66. Consistent with the all-day finding that the QT sweep's
mark-to-market loss *is* the spread.

**7. No activity band is profitable.** The activity × cycle heatmap has **20 cells
and not one above PF 1.04** (best: D2 at 80-100% activity, PF 1.03 on n=55). The
0.3–0.8 activity gate in five of the winning models is not selecting a profitable
activity regime — it is selecting a particular set of 20-31 trades.

**8. "Months positive" hides the empty months.** #10's 10-of-11 excludes February
2026, in which it took **zero** trades. At 20–31 trades spread over 12 months,
monthly consistency is close to uninformative.

## Parameter surfaces — plateau or one cell?

| surface | shape | verdict |
|---|---|---|
| **sweep depth** | PF 3.97 → 2.72 → 2.54 → 1.69 → 1.49 → 1.49 → 1.40 → 1.33 → 1.13 → 1.02 → 0.99 → 0.90 → **0.74**, across 363 events | **PLATEAU / GRADIENT.** Thirteen thresholds: eleven strict decreases, one flat step (0.15→0.175), **no reversal anywhere**. Shallow sweeps really do behave differently from deep ones — the one finding here that looks structural. |
| **Q2 efficiency "cliff" at 0.45** | 6.14 → 3.87 | **ARTEFACT.** The drop is three trades entering the sample: −0.04R, −1.01R, −1.02R. Naming a threshold there is naming three trades. |
| **activity deciles** | PF 0.28, 0.61, 0.60, 0.36, 0.35, 0.88, 0.42, 0.79, 0.76, 0.77 | **NO STRUCTURE.** Negative in all ten deciles, no hump, no monotonicity. |
| **stop × target (fixed R)** | coherent ridge around TP 0.75R, SL 1–1.25R | shape is real, level is ~4 not ~8 |

## The honest answer

Both benchmarks were beaten. The number that should be carried forward is not
8.73; it is this:

- The PF-8 models achieve it with a **sub-1R target and a 92–95% win rate**, and
  lose 40% of their money doing so.
- Their stops **were never tested** — widening them by 100% changes nothing.
- **One** of the three parameter surfaces looks like structure (sweep depth). The
  other two are three trades and noise.
- The base universe loses under **every** exit rule tried, in a year where the
  same signal family was already shown to lose exactly the spread.

If a single artefact leaves this phase, it should be the **sweep-depth gradient**,
because it is the only finding with an ordered, many-step shape rather than a
selected cell. Everything else is a one-year in-sample maximum, and the label is
the deliverable.

## Reproducing

```
python3 research/insample/code/cycles.py     # 896 QT cycles from 91.6M ticks
python3 research/insample/code/resolve.py    # tick-exact resolution + benchmarks
python3 research/insample/code/search.py     # 246,807 grid cells
python3 research/insample/code/models.py     # ten categories + parameter surfaces
python3 research/insample/code/exits.py      # 34 exit families, surfaces, curves
```

Outputs: `results/{models.log, exits.log, top100.csv}`.
