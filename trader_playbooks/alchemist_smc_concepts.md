# ALCHEMIST FOREX CONCEPTS (ICT/SMC market-structure glossary)
# Source: "Alchemist Concepts in Forex Trading" PDF, author credited as
# "White" / "White Seraph," Thai-original machine-translated (DeepL),
# supplied 2026-07-20. INDEPENDENT voice #12 for the SMC market-
# structure layer specifically (IDM/BOS/CHOCH, Classic A/V, SBR/RBS,
# Quasimodo). The Quarterly Theory portions of this same PDF (AMDX/
# XAMD, 90-min cycles, SMT) are the SAME ICT lineage as voice #4/#13's
# existing Quarterly Theory school -- logged as corroboration there,
# NOT double-counted as a new voice. Credibility tier: LOW-MEDIUM --
# anonymous poster, zero stats, translation quality is poor enough
# that some sections (Fibo Circle, Fibo Storyline, OCL) are too
# garbled to confidently codify and are flagged rather than guessed.

## 1. IDM (INDUCEMENT) — GATES BOS/CHOCH CONFIRMATION [the key new idea]
- A "valid pullback" is a retracement that (a) forms a clear local
  swing extreme, then (b) gets swept (its extreme is taken out) before
  price continues in the original direction.
- **Rule**: a Break of Structure (BOS) or Change of Character (CHOCH)
  is only CONFIRMED once the IDM (the valid pullback's swept extreme)
  has been cleared. A structure break without a prior swept inducement
  is weaker/unconfirmed.
- This is distinct from every sweep-reversal mechanic already in the
  register (JUDAS/QT is specifically prior-day H/L in a session
  window; Wendell is S/D zone freshness; Dave is swing maturity count)
  -- IDM is about the INTERNAL swing between structure points, on any
  swing, not anchored to a session window or daily extreme. Genuinely
  new mechanic, not a restatement.
- Applies symmetrically: uptrend IDM = a pullback low that gets swept
  before the next higher-high confirms; downtrend IDM = a pullback
  high swept before the next lower-low confirms.

## 2. CLASSIC A / CLASSIC V (swing-origin zones)
- Classic A = swing high = potential resistance origin, OB expected on
  LTF at that level. Classic V = swing low = potential demand origin.
  Stronger if the swing was itself a liquidity sweep + reversal (same
  quality upgrade already used everywhere else in the register --
  Wendell, PBD, Dave). Not new mechanically; redundant with
  wendell_zone_engine.pine and dave_swing_count.pine -- not re-coded.

## 3. SBR / RBS — SUPPORT/RESISTANCE ROLE FLIP [genuinely new]
- **SBR (Support Becomes Resistance)**: an old support level, once
  broken (body close beyond it), is expected to act as resistance on
  a later retest -- classic "breaker block" logic.
- **RBS (Resistance Becomes Support)**: mirror -- broken resistance
  flips to support on retest.
- Distinct from Wendell's freshness tracking: Wendell asks "has this
  zone been retraded" (freshness decays through visits); SBR/RBS
  tracks a level's ROLE inverting after a confirmed break, independent
  of how many times it's later retested. Two different, complementary
  properties of the same broken level.

## 4. QUASIMODO (QML) — specific reversal swing structure
- A 5-point swing sequence: higher-high -> higher-low -> a break below
  that higher-low forming a NEW lower-low (structure break) -> a
  retracement that FAILS to reclaim the original higher-high (lower-
  high) -> reversal from there. The defining feature vs. a plain
  ABC/123 (voice #9) or PBD break-in is the specific "fails to reclaim
  the prior high" fourth point -- an extra confirmation step.
- Mirror for bullish QML off a downtrend.

## 5. ENGULFING OB
- An Order Block anchored specifically at an engulfing candle (rather
  than the classic "last opposite candle before the impulse")
  combined with a liquidity sweep = higher-conviction OB. We already
  have engulfing-pattern detection in candlestick_engine.pine (tier-A
  pattern) -- treat this as a CONFLUENCE PAIRING (engulfing pattern +
  SBR/RBS or QML level) rather than a new standalone detector.

## 6. TRENDLINE KEY (TL) — three-touch trendline entry
- A trendline must be touched/respected twice; the THIRD touch is the
  entry trigger. Same "third-time reversal" logic already coded as
  the horizontal triple-tap in mm_cycle_engine.pine (H22, Steve/MMM4x)
  -- this source applies the identical count to a DIAGONAL trendline
  instead of a horizontal extreme. Logged as cross-school corroboration
  of the "third test = decision point" idea (now: Steve/MMM4x triple-
  tap, PBD's original flagship trendline-breakout core, and this),
  not built as new code -- the existing trendline_breakout_fixed.pine
  core already trades trendline breaks; a three-touch-gate variant is
  a cheap A/B for later, not urgent.

## 7. QUARTERLY THEORY / SMT PORTIONS — SAME LINEAGE, NOT NEW
This PDF's AMDX/XAMD quarters, 90-minute cycle table, Asia-range
liquidity, and SMT-x-QT combination are the identical ICT-derived
Quarterly Theory material already in quarterly_theory.md (voice #4).
Logged as an independent-author corroboration of that SAME school
(different teacher, same underlying ICT theory), not tallied as a new
voice. The 90-minute table in this PDF is column-garbled by
translation/table-flattening and less trustworthy than the clean
primary-source video already used to build the engine -- not used to
re-derive timings.

## 8. THE SETUP CHECKLIST (this source's actual trading workflow)
Pages 62-69 lay out the full entry method, worth extracting as a
structured checklist even though the concepts feeding it are already
covered individually above:
1. **H1 POI**: identify the point of interest on H1 using Classic A/V,
   SBR/RBS, or QML.
2. **M1-M5 entry confirmation**: require a market-structure shift
   (BOS/CHOCH) GATED BY IDM (section 1) on the entry timeframe.
3. **One confirming trigger**, any of: Key OCL (see below, under-
   specified), QT 90-minute cycle alignment, or Trendline Key
   three-touch.
This is a clean, portable "HTF zone -> LTF IDM-gated structure shift
-> named trigger" template -- structurally similar to every other
MTF-stack idea already in the register (6 independent sources) but
this is the first to make the LTF CONFIRMATION step (IDM-gated BOS)
an explicit, separate requirement rather than folding it into "wait
for a candle close."

## 9. NOT BUILT — translation too degraded to safely codify
- **OCL (Open-Close Level)**: described as "a moving average with a
  fixed period... similar to Hidden Base of SMC... HTF... P-P
  pattern... LTF order block" -- internally inconsistent across its
  two source pages (one says "P-P pattern," the other "D-P D-P
  pattern"). Likely an anchored/dynamic moving average used as an HTF
  reference for LTF order blocks, but the exact period and pattern
  rule cannot be confidently reconstructed. NOT implemented -- would
  require guessing mechanics the source doesn't clearly state, which
  violates the register's "no fabricated data" rule.
- **Fibo Circle**: "identify LOW consolidation to find HIGH
  consolidation" (buy) / mirror (sell) -- too vague to derive exact
  geometry. Possibly related to Gann/Fibonacci time-price circles but
  not stated clearly enough to implement.
- **Fibo Storyline**: appears to describe scaling into a trend across
  multiple legs using repeated Fibonacci retracement zones per leg
  ("cut the stem and leaves," "neck to shoulder" -- garbled idiom),
  but exact ratios and re-entry rules are not extractable from the
  translation. Conceptually adjacent to standard fib-retracement
  scale-ins already implicit elsewhere; not separately coded.

## 10. ENGINE
indicators/alchemist_smc_engine.pine — IDM-gated BOS/CHOCH detector,
SBR/RBS role-flip tracker, Quasimodo (QML) pattern detector. All
bar-close, non-repainting (pivots confirm with a lag, structure
breaks and role flips only fire on closed bars).
