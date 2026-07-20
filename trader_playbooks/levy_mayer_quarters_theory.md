# Ilan Levy-Mayer — "The Quarters Theory" (voice #18)
Source: two AllThingsForex.com/FXStreet webinar transcripts by Ilan
Levy-Mayer, FX strategist and founder of AllThingsForex.com/
TraderTape.com, author of "The Quarters Theory" (published by Wiley,
January of the source year), supplied 2026-07-20 as spoken-word
transcripts (webinar #1: the core price-grid theory; webinar #2, same
author/book, extends it with "Quarters Theory Trend Waves").

**NAMING COLLISION WARNING — read this before touching either file.**
This is a COMPLETELY DIFFERENT, UNRELATED methodology from
`quarterly_theory.md` / `quarterly_theory_engine.pine` (voice #4,
Trader Daye/ICT lineage) despite the near-identical name ("Quarters
Theory" vs. "Quarterly Theory"). Trader Daye's school is TIME-based
(session/quarter fractals, true opens, AMDX phases). Levy-Mayer's is
purely PRICE-based (static round-number grids, no session/time
component at all, no ICT terminology, no relation to it whatsoever).
Different author, different book, different mechanism, coincidentally
similar name. Kept as a fully separate voice/file pair — never merge
these two, and always double-check which "quarter[ly] theory" file is
meant when either is referenced in future sessions.

**Credibility tier: LOW-MEDIUM.** A named, identifiable public figure
(published by a real publisher, hosts a long-running daily broadcast,
built a named brand around this specific methodology) — stronger
identity-accountability than most anonymous sources in this register.
But: zero backtested statistics offered in either transcript, every
example is a retrospective "look, prices did what I predicted"
walkthrough (illustrative, not a controlled forward test), and the
core sales pitch ("these price points never change, it's like a GPS
for traders") is the kind of certainty-marketing this project treats
skeptically by default.

## 1. THE PRICE GRID (core mechanic, webinar #1)
- Between every two **major whole numbers** (round decimal handles —
  in FX, e.g. $1.30 and $1.40 on EUR/USD) there is a fixed 1,000-pip
  range. Divide it into 4 equal **large quarters** of 250 pips each;
  the boundary prices are **large quarter points** (e.g. 1.30, 1.3250,
  1.35, 1.3750, 1.40).
- Between every two **regular whole numbers** (e.g. 1.30 and 1.31, a
  100-pip range) there are 4 **small quarters** of 25 pips each —
  exactly 10 small quarters per large quarter (250/25=10).
- **Core thesis**: every significant price move starts at one large
  quarter point and targets another. If the target isn't reached, the
  alternative is a reversal back to the PRECEDING large quarter point
  (a large quarter is a binary outcome: completed, or reversed).
- **"Successful completion" rule (precise, quotable)**: price does not
  need to touch the exact large quarter point — reaching within one
  small quarter (25 pips) of it, whether short of it or overshooting
  past it, counts as a completed large quarter. This is the single
  most concrete, directly implementable rule in either transcript.
- **The major half point**: the exact midpoint of a 1,000-pip range
  (e.g. 1.35 between 1.30-1.40) is called out repeatedly across both
  transcripts' worked examples as an extra-significant level —
  structurally it's just the 2nd of the 4 large quarter points, but
  the source treats it with extra weight (a common consolidation/
  correction point in every worked example).
- **1,000-pip range transitions**: when price breaks past a major
  whole number into a new 1,000-pip range, that's a "major shift,"
  claimed to be driven by a genuine fundamental regime change (not a
  random event). Decisiveness test: the transition is "decisive" only
  if the FIRST large quarter of the NEW range also completes; if it
  doesn't, expect a reversal back across the major whole number into
  the previous range.
- **Levels are static and never recalculated** — this is the source's
  main selling point ("a GPS for traders"): pure modulo arithmetic on
  absolute price, not derived from swings, pivots, or history at all.

### Gold adaptation (our own convention, NOT source-given)
Every worked example in both transcripts is a G7 FX pair (EUR/USD,
USD/JPY, USD/CAD) at their standard pip conventions. Gold is never
mentioned. To apply the same STRUCTURE (4-way division, major/large/
small nesting, 25%-of-range completion tolerance) to XAUUSD we had to
pick a scale, exactly the same kind of judgment call as the Gann
"three-digit controversy" and the "which timeframe justifies which
scale" problem already flagged elsewhere in this repo. Chosen
convention: **major whole number = $100 handle** (e.g. 3300, 3400),
large quarter = $25, regular whole number = $10 handle, small quarter
= $2.50. This preserves the source's exact ratio (large:small = 10:1,
4-way division at every level) but the absolute dollar widths are our
own choice, adjustable via input, and UNTESTED against the source's
intent since the source never addresses a 4-digit metal price at all.

## 2. QUARTERS THEORY TREND WAVES (webinar #2, same author/book)
Levy-Mayer's own simplified variant of Elliott Wave, explicitly
designed to fix what he calls Elliott's biggest practical problem —
traders can't agree on a wave count, especially around "complex" waves
(a wave secretly containing 3 sub-waves). His fix: no sub-waves
allowed, no fixed cap on wave count, and corrections get NAMED
relative to the wave they follow instead of being counted as their own
waves.

- **Reversal Trigger Wave**: the wave that ends a previous cycle and
  starts a new one — concretely, a leg that breaks the most recent
  counter-trend swing extreme (a bullish reversal trigger wave breaks
  the most recent swing high made during the preceding downtrend, even
  by a small margin — one worked example breaks a prior high by only
  14 pips and that's still sufficient). This is the SAME underlying
  mechanic as this repo's existing structure-break/BOS family (IDM-
  gated BOS in the Alchemist engine, Dave's swing count, MM Cycle's
  taps) — logged as corroboration of that family for the trigger
  condition itself; what's NEW is the wave-numbering/naming system
  built on top of it (see below).
- **Correction N**: the pullback after wave N, named/numbered for the
  wave it follows (C1 follows wave 1, etc.) — not itself a counted
  wave, unlike Elliott's waves 2 and 4.
- **Progressive Wave** (wave 2): the wave following correction 1 that
  CONFIRMS the new cycle by exceeding wave 1's extreme (new higher
  high for a bullish cycle, new lower low for bearish).
  **Conclusive Wave** (wave 3): Elliott's wave-5 equivalent — but
  critically, NOT followed by an ABC correction. Any wave after wave 3
  that continues the SAME direction is instead a **Consecutive Wave**
  (wave 4, 5, 6, 7...), unlimited — "if the market wants to give you 10
  waves, so be it."
- **Extended cycle**: more than 3 waves. **Overextended cycle**: more
  than 4 waves — used qualitatively as an exhaustion/overbought-
  oversold-style warning, no numeric edge given beyond "the more waves,
  the more you should suspect the trend is stretched."
- **Wave failure rule (precise, quotable)**: a new same-direction wave
  FAILS if it does not exceed the extreme of the prior same-direction
  wave (e.g. the 2nd bullish wave's high must exceed the 1st bullish
  wave's high — ordinary higher-high logic, already this repo's
  baseline trend definition). When a wave fails, "the main consequence
  ... is the development, in most instances, of a reversal trigger wave
  in the opposite direction" — i.e. wave failure is itself a
  reversal-warning condition, not just a "wait and see."
- **The 100%-retracement-becomes-a-reversal-trigger rule (precise,
  quotable, the single most novel piece of this section)**: if the
  correction FOLLOWING a reversal trigger wave retraces MORE than 100%
  of that wave (i.e. breaks back past the wave's own starting point),
  that correction is no longer just a correction — it becomes a NEW
  reversal trigger wave in the opposite direction, restarting the
  count. Both worked EUR/USD examples in webinar #2 hinge on this
  exact rule.
- **Cross-validation claim**: the worked EUR/USD daily-chart example
  (the four-consecutive-bullish-wave sequence from ~1.1875 through
  ~1.30) shows every wave's start/end coinciding with large quarter
  points from section 1 — offered as evidence the two halves of his
  own methodology reinforce each other. Interesting but this is the
  author validating his own theory with his own cherry-picked example;
  not independent confirmation of anything.

## 3. What's built
`indicators/quarters_theory_price_engine.pine`:
- **Price grid**: static large-quarter and small-quarter horizontal
  levels computed by pure modulo arithmetic on absolute price (no
  pivot/anchor needed at all, redrawn only when the visible major-
  handle range changes) — `majorRangeWidth` input, default $100 for
  gold, explicitly flagged as our own convention.
- **Large quarter zone reached**: tags when price closes within one
  small-quarter width of any large quarter level (source's own
  "successful completion" tolerance rule, applied literally).
- **Major range transition tracking**: flags when price crosses a
  major handle, then tracks whether the first large quarter beyond it
  completes (confirmed transition) or price re-crosses the major
  handle first (failed transition / reversal back into the old range)
  — both outcomes explicitly named by the source.
- **Trend Wave cycle counter**: zigzag swing tracker (reusing the same
  pivot/leg-tracking technique already used elsewhere in this repo,
  e.g. the Fibo Storyline leg tracker) implementing the Reversal
  Trigger / Progressive / Conclusive / Consecutive wave-numbering
  scheme, the wave-failure flag, and the 100%-retracement-becomes-new-
  reversal-trigger rule. Extended/Overextended cycle tags at wave
  counts >3/>4.

## 4. What's NOT built
- No attempt to detect "complex wave" patterns or reproduce classic
  Elliott labeling (1-2-3-4-5-A-B-C) — the whole point of this source
  is that it explicitly REJECTS that scheme; building it would be
  building the wrong thing.
- No claim that gold's own natural round-number psychology matches the
  $100/$25/$10/$2.50 scale chosen here — untested, flagged, adjustable.
- The overextended-cycle "warning" has no numeric edge in the source
  (no stated win-rate change at wave 4 vs wave 7) — implemented only
  as a descriptive tag, not a sizing or entry/exit rule.

## Register impact
- New voice, no existing lineage.
- The Reversal Trigger Wave's trigger condition (break of the most
  recent counter-trend swing extreme) corroborates the existing
  structure-break/BOS family (now yet another independent
  construction of "a break of the last counter-trend extreme changes
  the trend") — not a new H-number for that specific piece.
- The static, non-recalculated, round-number price grid is a
  genuinely new mechanism — nothing else in this repo derives S/R
  purely from modulo arithmetic on absolute price with no reference to
  market history at all. Closest analogue is round-number-as-magnet
  (Valentini/Roppel, already 2 independent sources) but that's a much
  looser "round numbers matter" observation, not a precise nested
  25%-division grid with a stated completion tolerance.
