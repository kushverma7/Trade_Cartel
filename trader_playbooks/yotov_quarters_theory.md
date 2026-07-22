# Ilian Yotov — "The Quarters Theory" (voice #18)
Source: two AllThingsForex.com/FXStreet webinar transcripts by Ilian
Yotov, FX strategist and founder of AllThingsForex.com/
TraderTape.com, author of "The Quarters Theory" (published by Wiley,
January of the source year), supplied 2026-07-20 as spoken-word
transcripts (webinar #1: the core price-grid theory; webinar #2, same
author/book, extends it with "Quarters Theory Trend Waves").

**NAMING COLLISION WARNING — read this before touching either file.**
This is a COMPLETELY DIFFERENT, UNRELATED methodology from
`quarterly_theory.md` / `quarterly_theory_engine.pine` (voice #4,
Trader Daye/ICT lineage) despite the near-identical name ("Quarters
Theory" vs. "Quarterly Theory"). Trader Daye's school is TIME-based
(session/quarter fractals, true opens, AMDX phases). Yotov's is
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
Yotov's own simplified variant of Elliott Wave, explicitly
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

## 5. v2 — the actual published book's glossary (2026-07-20)
"The Quarters Theory: The Revolutionary New Foreign Currencies Trading
Method," Ilian Yotov, Wiley 2010 — the official Glossary of Terms
chapter, supplied as a clean OCR'd .txt. **Primary published source,
outranks the webinar transcripts** where they differ; also confirmed
the author's name is spelled **Ilian Yotov** (the webinar transcripts'
auto-generated captions garbled it to "Ilan y"/"Ilan yov" — an
earlier pass through this material mis-transcribed it further to a
fabricated surname, "Levy-Mayer," that appears nowhere in any source;
corrected throughout this file, the engine, and the belief register).

Confirms every mechanic already built and adds real precision on
several fronts:

- **The 3-Day Rule (new, not in either webinar, directly buildable)**:
  a Large Quarter must complete within 3 trading days (three 24-hour
  FX sessions) or its failure to do so "should be considered a sign of
  price weakness and potential exhaustion" raising the odds of reversal
  back to the preceding Large Quarter Point instead. Gives our
  zone-reached tracker an actual exhaustion/timeout condition it didn't
  have before. Translating "3 trading days" to a 5m gold chart is our
  own choice (gold trades ~23h/day, not the session-gapped FX week Yotov
  is measuring) — flagged as untested, same caveat pattern as every
  other cross-timeframe translation in this repo.
- **Hesitation Zone (new)**: the first 75 pips (3 small quarters) beyond
  a Large Quarter Point, in the direction of the move; "End of the
  Hesitation Zone" = the price point exactly 75 pips from the LQ point.
  Named trade types exist for both crossing it (Hesitation Zone Trade)
  and fading it (Hesitation Zone Reversal Trade).
- **Overshoot Area / Undershoot Area (precise definitions, confirms
  what was already built)**: exactly one Small Quarter (25 pips) past
  / short of a Large Quarter Point — this is the literal source of the
  "successful completion" tolerance already implemented as `zoneTol`
  (default 1.0x small-quarter width) — confirmed correct, no change.
- **THREE distinct "half point" concepts, previously conflated into
  one**:
  1. **Half Point** — middle of a 100-pip range, coincides with a Small
     Quarter Point (e.g. 1.2950, 1.3050) — a minor level.
  2. **Half Point of a Large Quarter** — middle of a 250-pip Large
     Quarter, exactly 125 pips from each of its two Large Quarter
     Points — has its OWN named trade types (Half Point Trade / Half
     Point Reversal Trade). **This is genuinely new and not yet
     implemented** — the engine currently only plots the 3rd tier below.
  3. **Major Half Point** — middle of the full 1,000-pip range (e.g.
     1.35 between 1.30-1.40) — this is the ONLY one of the three
     already built (the "HALF" tag on large-quarter-index-2 in the
     price grid).
- **Whole Number preceding a Large Quarter Point (new)**: explicitly
  named as a potential final obstacle — "the last support/resistance
  price point that may prevent the successful completion of a Large
  Quarter" — i.e. the nearest regular (non-large-quarter) whole-number
  handle just before the target. Has its own named trade types (Whole
  Number Trade / Whole Number Reversal Trade).
- **Large Quarter Corrections (new, distinct from Trend Wave failure)**:
  reversal moves "triggered by over-bought/over-sold conditions as a
  result of series of multiple Large Quarter Completions" — i.e. after
  several consecutive Large Quarter completions in the same direction
  (not wave count — LQ-completion count specifically), expect an
  exhaustion pullback. A parallel, LQ-grid-native version of the same
  "extension breeds correction" idea the Trend Wave section already
  captures via wave count — different counting unit, same underlying
  claim, not yet implemented as its own counter.
- **Extended Trend Waves vs. Extended Cycle — a distinction this repo's
  first pass had CONFLATED, now corrected**: "Extended [Trend Waves]
  Cycle" = more than 3 waves in the same direction (what's built,
  correctly). "Extended Trend Waves" (no "Cycle") is a SEPARATE,
  DURATION-based definition: a single wave lasting more than 5
  consecutive time periods (bars, on whatever timeframe is charted) —
  not implemented, flagged here rather than silently guessed at.
- **Ideal / Shortened / Extended Cycle, precise thresholds (confirms
  what's built)**: Ideal = exactly 3 waves. Shortened = fewer than 3.
  Extended = more than 3. Matches the engine's existing
  `isExtended = waveCount > 3` exactly — no change needed.
- **Sign of Strength / Sign of Weakness**: simple named terms for
  price sustaining above (strength) or remaining below (weakness) a
  Large Quarter Point — descriptive vocabulary, not a new mechanic.
- **Time Stops**: a stop-loss variant defined by elapsed time rather
  than price — close the trade if it hasn't reached its objective
  within a set window. Generic money-management idea, not LQ-specific.
  Corroborates the existing time-stop candidate already in this
  register (H24, Steve/MMM4x) — not a new H-number, logged as a second
  independent source for that idea.
- **Full named trade-type taxonomy** (useful as documentation, not
  separately coded — each is just a different entry trigger keyed to
  one of the price points above, already covered structurally by the
  zone-reached tracker + transition tracker): Large Quarter Trade /
  Inverse Large Quarter Trade (fade), Hesitation Zone Trade / Reversal,
  Overshoot Trade / Reversal, Half-Point Trade / Reversal, Whole
  Number Trade / Reversal.

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

## 6. v3 — audit pass against original glossary source (2026-07-22)
Re-read `TheQuartersTheory2012YotovGlossaryofTerms.txt` in full to verify
the v2 pass. Terms/omissions, not factual errors — no numbers contradicted:

- **Major Small Quarter Points (missing)**: Small Quarter Points that
  coincide with regular Whole Numbers (e.g. 1.31/1.32/1.33) — mark the
  end/start of a 100-pip range. Distinct from Large Quarter Points; not
  in section 1 above.
- **"Important Price Points within the Large Quarters" (missing as a named
  term)**: source's formal grouping = End of Hesitation Zone + Half Point
  of a Large Quarter + Whole Number preceding a Large Quarter Point + "any
  major Short/Mid/Long-Term S/R level positioned within the range of a
  Large Quarter." The individual pieces are covered above but the general
  "any major S/R level inside the LQ range also counts" clause is new.
- **Trade-objective taxonomy (missing)**: source splits ALL named trades
  into two categories — "Large Quarter Completion Trades" vs. "Intra-Large
  Quarter Trades." Neither term appears above, though the trade list
  itself is otherwise reproduced.
- **Large Quarter Transitions (missing, distinct from what's built)**: the
  transfer of price from one Large Quarter's 250-pip range into the next
  Large Quarter's range WITHIN the same 1,000-pip range — smaller/more
  frequent than the "Major range transition" (crossing a major whole
  number) already tracked. Not yet a separate tag.
- **Unsuccessful Large Quarter Completion / 1000 PIP Range Completion
  (missing)**: both explicitly named/defined in the glossary; only the
  positive/successful case is covered above.
- **PIP baseline definition (missing)**: source gives the precise unit
  chain — EUR/USD 1 PIP = .0001 USD; 100 PIPs = 1 sub-unit; 1000 PIPs =
  10 cents/pence/yen; 10,000 PIPs = 1 full unit. Never restated here,
  relevant context for the gold $-scale conversion in section 1.

No factual contradictions found — all gaps are omitted terms, not wrong
numbers. Not yet ported to the engine.
