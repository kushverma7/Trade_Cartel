# ALCHEMIST FOREX CONCEPTS (ICT/SMC market-structure glossary)
# Source: "Alchemist Concepts in Forex Trading" PDF, author credited as
# "White" / "White Seraph," Thai-original machine-translated (DeepL),
# supplied 2026-07-20. INDEPENDENT voice #12 for the SMC market-
# structure layer specifically (IDM/BOS/CHOCH, Classic A/V, SBR/RBS,
# Quasimodo). The Quarterly Theory portions of this same PDF (AMDX/
# XAMD, 90-min cycles, SMT) are the SAME ICT lineage as voice #4/#13's
# existing Quarterly Theory school -- logged as corroboration there,
# NOT double-counted as a new voice. Credibility tier: LOW-MEDIUM --
# anonymous poster, zero stats, translation quality is poor. Fibo
# Circle and Fibo Storyline were reclassified from "too garbled" to
# buildable after re-reviewing the source's page IMAGES (2026-07-20,
# see sections 9a/9b) -- they carry exact numeric ratios the text/
# captions alone did not preserve. OCL remains not built (section 9).

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
  **v2 update (2026-07-20, page IMAGES re-reviewed, not just
  text/captions)**: the diagram clarifies the GEOMETRY -- an HTF
  candle-body level, connected by a diagonal "inducement" trendline,
  down to an intersection point that lines up with an LTF order block
  -- and confirms OCL is reused later (pages 63/66) as the actual
  M5/M15 entry trigger in the source's own trading checklist, in the
  same setup slot as SBR/RBS or Trendline Key. Still NOT built: the
  rule for WHICH HTF candle anchors the level is not stated anywhere
  in the source, image or text -- implementing it would still mean
  guessing that one piece. Upgraded from "too garbled" to "geometry
  clear, one rule still missing" -- worth revisiting if a future
  Alchemist source clarifies the anchor-candle selection.

## 9a. FIBO STORYLINE — v2, RECLASSIFIED as buildable
(2026-07-20, page IMAGES re-reviewed): the source's own Fibonacci-tool
settings page (p.61) shows the EXACT ratio set used throughout, a
custom set, not the standard 0.236/0.382/0.5/0.618/0.786:
**0, 0.109, 0.127, 0.145, 0.214, 0.232, 0.25, 0.618, 0.636, 0.654,
0.786, 0.804, 0.822, 1**. Dense cluster at 0.618-0.822 (read as the
"KEY" entry zone, confirmed by a small reversal candle in the worked
examples -- "cut the stem and leaves"); shallower cluster at
0.109-0.25 (a shallower continuation-pullback band, used less
prominently in the examples). A second stage, "adding wood" (pp.
59-60): after the first Fib-KEY entry (ORDER 1) triggers and price
continues, the trader shifts to a LOWER TIMEFRAME, finds a fresh
Fib/liquidity pullback zone there, and adds a second position
(ORDER 2) -- this is the scale-in mechanic this playbook had only
speculated about before; now confirmed with a name and a diagram.
**Implemented** in alchemist_smc_engine.pine v2: KEY-band retracement
entry on the dominant swing leg (ORDER 1), plus a same-timeframe
re-application on the next leg for ORDER 2 (the source's literal
LTF-shift is NOT implemented -- flagged in-code as a simplification,
not a literal match). Lower-confidence tier than sections 1-4: the
underlying translation is still poor, just less garbled than first
assessed -- off by default, test standalone.

## 9b. FIBO CIRCLE — v2, RECLASSIFIED as buildable
(2026-07-20, page IMAGES re-reviewed): after a dominant swing leg,
price forms a small INTERNAL retracement/zigzag; that internal swing's
two extremes are labeled "LOW CONSO" / "HIGH CONSO" ("low/high
consolidation") in the source's own diagram. A Fibonacci EXTENSION is
drawn from that internal swing using the source's own stated ratios
**1.893 and 2.0** (page 53) -- a projected level ("KEY ENTRY"/"KEY
CIRCLE") that price is expected to reach and retest before the larger
continuation move resumes. Buy/sell setups (pp. 53-54) are exact
mirrors of each other. **Implemented** in alchemist_smc_engine.pine
v2: the pivot pair immediately following the dominant leg's endpoint
is treated as the internal LOW/HIGH CONSO swing; the 1.893x extension
level is plotted and a retest (first cross, then a pullback that holds
beyond it) is tagged as the entry signal. Same lower-confidence tier
as Fibo Storyline -- off by default, test standalone.

## 10. ENGINE
indicators/alchemist_smc_engine.pine — IDM-gated BOS/CHOCH detector,
SBR/RBS role-flip tracker, Quasimodo (QML) pattern detector, Fibo
Storyline KEY-zone entry + scale-in (v2), Fibo Circle KEY extension
retest (v2). All bar-close, non-repainting (pivots confirm with a lag,
structure breaks/role flips/fib checks only fire on closed bars).
