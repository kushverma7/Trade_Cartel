# FOREX MASTER PATTERN (three-phase cycle school)
# Source: introductory course video, unnamed instructor referencing
# proprietary "our software" (chart auto-boxing/liquidity lines),
# supplied 2026-07-20. INDEPENDENT voice #11.
# Credibility tier: LOW-MEDIUM — course/software seller, "90% of
# traders lose" and belief-driven-markets framing are unfalsifiable
# philosophy; the operational mechanics (phase classification, average
# price, two-timeframe fade-into-trend entries) are fully codeable.

## 1. THE THREE PHASES (claimed to classify every candle, every TF)
1. **Contraction** — the setup. Low (institutional) volume proxy, range
   compresses, sideways/tight. "Neutral belief zone." Do not trade here.
2. **Expansion** — the trap. Range opens, takes out the contraction
   box's highs/lows on BOTH sides before resolving (his "whipsaw").
   Framed as smart money accumulating at a discount while retail chases
   the breakout and gets stopped both ways. This is the SAME shape as
   the sweep-fade family already dominant in the register (PBD, QT
   Judas, Dave, Steve/MMM4x, voice #9 ABC/123, voice #10 Wendell) —
   SEVENTH independent voice on essentially the same manipulation-leg
   concept, though framed here as a full phase rather than a single
   sweep event.
3. **Trend** — the payout. Directional move away from the contraction
   box; only phase he wants retail (or us) actually trading.
- Cycle repeats indefinitely: Contraction -> Expansion -> Trend ->
  Contraction... Fractal across every timeframe simultaneously — a
  higher-TF trend phase implies the same directional bias governs
  every lower TF's big moves ("the higher TF is the authority").

## 2. AVERAGE PRICE (his belief "tipping point")
- Average price = midpoint of the most recent contraction box, drawn
  forward as a line.
- Above it: dumb money wants to buy, smart money is selling.
  Below it: dumb money wants to sell, smart money is buying.
- Where price "settles" (sustained closes on one side) after breaking
  the contraction box establishes directional bias for that timeframe.
- Converges loosely with True Opens (QT, voice #4/#8) and premium/
  discount framing — a different construction (box midpoint vs a fixed
  session/day/week clock time) landing on the same operational idea:
  a single reference price splits the chart into a bullish/bearish
  belief frame. Logged as a related-but-distinct construction, not a
  straight corroboration (different inputs, same output shape).

## 3. TWO-TIMEFRAME STRATEGY (his full, explicit trading plan)
- Pick two timeframes far enough apart (his example: 4H bias / 15m
  entry; also daily/monthly for swing traders — ratio matters more
  than the specific pair, matches every other MTF-stack idea already
  in the register).
- **HTF (bias chart)**: find the most recent contraction box, draw
  average price, wait for price to break out and SETTLE on one side =
  directional bias for everything below it.
- **LTF (entry chart)**: once HTF bias is set, find LTF contraction
  boxes; when LTF price expands to the COUNTER-TREND side of its own
  average price (an "expansion leg" against the HTF direction), that
  is the entry SETUP — not the trigger.
- **Entry trigger**: price crossing back through the LTF average price
  in the HTF trend direction. Never enter on the counter-trend
  expansion leg itself — wait for the cross-back.
- **Take profit**: baseline TP = return to LTF average price. Optional
  runner: if the move is clearly a sustainable break, hold until LTF
  re-enters its own contraction phase (a trailing structural exit, not
  a fixed target).
- **Invalidation / stop-out condition**: if the HTF rotates back
  against the position before its own trend confirms (i.e., it turns
  out the HTF was still in ITS expansion phase, not yet trending),
  exit and reassess — the higher-TF thesis was wrong, not the entry
  mechanics.

## 4. NEWS / FUNDAMENTALS (explicit position, worth logging against B3/B4)
- Scheduled news (NFP, GDP, CPI-type releases) does NOT create a
  separate regime — it simply ACCELERATES whichever of the three
  phases is already running ("gasoline on a fire"). No special CPI
  logic needed under this model; the phase classification already
  covers it.
- Unscheduled shocks (natural disasters etc.) can spike price outside
  the pattern briefly but the market snaps back into the three-phase
  cycle immediately after.
- Fundamentals matter only insofar as they seed a trader's BELIEF,
  which price action then confirms or punishes — same causal chain as
  scheduled news, just a slower trigger.
- Relation to our B3/B4 (CPI direction unknowable pre-print; surprise
  size drives the move; in-line prints produce no event candle): NOT a
  contradiction — both models still say CPI direction can't be
  predicted pre-print. This source reframes WHY post-CPI moves matter:
  not because news is special, but because it's fuel for whatever
  phase transition was already due. Testable overlap: does classifying
  the pre-CPI phase (contraction vs expansion vs trend) predict
  whether the print produces a real event candle better than raw
  surprise size alone (B4)? New hypothesis, H33.

## 5. SIZING INSIGHT (his closing point, worth keeping)
- Probability of a fresh trend leg paying out is HIGHEST on the FIRST
  re-entry after HTF bias confirms, and decays with each subsequent
  re-entry in the same trend (the trend is statistically closer to its
  own eventual contraction each time). Explicit sizing implication: the
  first confirmed entry in a new trend cycle deserves the largest size
  of the sequence, not equal-weighted scaling. New idea, not previously
  in the register (existing scale-out rules cover exiting a single
  trade, not decaying size ACROSS a sequence of same-trend re-entries).

## 6. WHAT WE DISCARD
- "90% of traders lose because of this" and "belief-driven not price-
  driven" as unfalsifiable marketing/philosophy framing.
- Proprietary software references (auto-boxing, liquidity lines) —
  we build our own equivalent, documented below.

## 7. ENGINE
indicators/fx_master_pattern_engine.pine — contraction-box detection
(range-compression proxy), average-price projection, HTF bias via
request.security (function-call pattern, non-repainting), LTF
expansion-leg + cross-back entry signals, first-vs-later opportunity
counter since the last HTF bias confirmation.
