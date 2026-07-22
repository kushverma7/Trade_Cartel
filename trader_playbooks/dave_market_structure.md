# Dave — Fractal Market Structure Scalping — extracted 2026-07-19
# Source: podcast. INDEPENDENT VOICE #7. SMC school, price-over-time
# philosophy. CORRECTED 2026-07-22: the "$700->$89k in 3 weeks, publicly
# verified" claim was NOT found anywhere in the recovered raw transcript
# (see audit addendum below) -- the transcript instead describes losing
# down to $600 and a stated goal of rebuilding to $20k over 4 months.
# The $89k figure likely came from a video title/description never
# actually pasted into this project. Treat as UNVERIFIED/uncorroborated
# against source until the original video title claim can be checked.

## The falsifiable signature rule [H18]
- SWING MATURITY: expect reversal at a POI only after ~4-6 matured
  swings (4+ HH & HL into supply; 4+ LL & LH into demand). Fewer =
  do NOT fade; the run isn't exhausted. He explicitly dares a
  backtest: "every pair, any market, regardless of time."
  [dave_swing_count.pine implements the counter]

## Setup mechanics
- MMS / previous-range mitigation (his one daily setup): break of
  structure defines the range (breakout swing high to swing low);
  expect 30-70% retrace in; entry ~50%, stop behind 70% (or tighter
  candlestick-structure entry: retrace into last bullish candle,
  stop behind it). Level gives ~3 taps; the break after = the
  manipulation, then the run. 3-5 opportunities per occurrence.
- Sweep prerequisite: "if there is no sweep, you are the sweep."
  Confirmation after sweep = close beyond previous counter-candle
  extreme. NEVER the raw sweep alone.
- Rounding tell: rounded top over consolidation -> the floor gets
  taken; "S-accumulation" break-retest-go distinguishes real
  breakout from trap.
- Prominent wick: standout wick to the left = target the WICK
  ORIGIN; price commonly tags it then retraces hard.
- Trailing: under impulse candle lows; or 21-EMA method (close
  below EMA then reclaim -> stop under that low).

## Craft / risk
- One-in-one-out; no partials, no pyramiding; fixed size always;
  size graduates with equity only (1 micro per $1k), never with
  conviction. Risk 3-5%. Invalidation = whole HTF POI; stop can be
  reduced via candle structure but idea dies only at POI break.
- Top-down compass mandatory: daily -> 4H -> 15m -> 1m; "always in
  a POI at some fractal."
- Avoid first NY hour if inexperienced (manipulation hour).
  [2nd source after Valentini — formal tension with our B1 window]
- Reaction trader: trade the first reaction, one-candle giveback,
  re-enter if resumed. Win rate = plan adherence, not model property.
- Review losses: "losses have a pattern too" — find where you
  repeatedly lose and remove that environment. (= our audit loop)
- Intuition = compounded execution experience; also for staying OUT.

## Register impact
- Sweep-reversal family: 3rd independent support (PBD, QT Judas,
  Dave) vs 1 against -> threshold crossed, doctrine pending backtest
- Confirmation-before-entry: 7th source
- First-hour-NY caution: 2 sources
- H18 swing maturity: new, falsifiable, implemented

---

## v2 additions — DTFS teaching session (same source, 2026-07-19)
- ZONE precisely defined: the PREVIOUS RANGE (prior swing high-to-low
  that price body-broke out of). Fib on the ZONE, not the impulse:
  0.3 / 0.5 / 0.7. Entry ~50%, stop behind 70% or zone extreme.
- VALIDATED structure = BODY close beyond the prior opposing candle.
  Wicks validate nothing (wick through a low != structure break).
- Location over signal: the body-close trigger fires EVERYWHERE;
  only count it INSIDE a zone. (Same law as Nison context gates.)
- Swing-count refinements: personal rule = no fresh CONTINUATIONS
  after 3 swings; count running past ~5-6 with no reversal = HTF in
  control -> go up a timeframe; counter-trend requires CONSOLIDATION
  at the extreme first ("consolidation = the buying ran out").
- Weak-zone tell: price enters zone, FAILS to print the new extreme
  -> exit, expect the flip through the opposite side.
- BE rule: after 50% entry, once prior high breaks, price should not
  return to entry (if it does, idea is degrading).
- Engine v2: auto-drawn previous-range zone with 30/50/70 on each
  body-close structure flip; continuation-caution alert at 3 swings.

---

## v3 additions — teaching batch (same source, 2026-07-19)

### Multi-TF swing counting (precision)
- Internal swings do NOT count toward the run; an internal swing is
  INVALIDATED when price takes its high/low and replaces it.
- Count from exactly TWO timeframes: the one you trade + one above.
  Smaller swings belong to lower TFs; each leg has its own count that
  facilitates the higher-TF count. Never mix counts across TFs.

### Candlestick structure flip (exact template)
- Low -> high -> lower low -> BODY close above the prior high = flip.
- Zone = old high into the pre-reversal low; tap ~50% -> target 1:1
  out of the zone (not the high — highs invite full retraces).
- A flip is a REVERSAL only inside a higher-TF zone; otherwise it's
  just facilitating a higher-TF pullback. HTF zones need 2-3 candles
  of their TF to leave — manage lower-TF entries accordingly.

### TIME-BASED RANGES [H19 — new, testable]
- The 09:00 ET and 15:00 ET hourly candles are POIs. Next closes set
  bias; price tends to tap back into the candle range (fib 30/50/70
  ON the candle) and reject with bias. Sweeps of the far side tend
  to reverse back through the range. 9AM serves NY; 3PM serves next
  London. [timebase_range.pine implements]
- INTERNAL TENSION: contradicts his own "structure doesn't need
  time" stance; corroborates the QT time-anchor family (true opens).

### 21-EMA trailing (exact algorithm)
- Trail stop ONLY to lows that closed below the 21 EMA and were then
  reclaimed (per traded TF). BE when the high that made your low is
  taken. After swing 3-4 of the run, switch to aggressive candle-low
  trailing (reversal imminent per swing count).

### Craft / psychology (from his story)
- Discipline should match desperation; honoring the plan = honoring
  the family. 10-minute no-touch timer after every entry.
- What you don't kill on the way up (ego, impulse, revenge) kills
  you on the way down. Slow markets (Asia) are the classroom.
- Losses have patterns too: find where you repeatedly lose, remove
  that environment entirely.

---

## Audit pass — original transcripts recovered from session log (2026-07-22)
Three raw transcript messages (one continuous session) recovered from
the session log and permanently saved to
`trader_playbooks/sources/raw_transcripts/` (line1170, line1187,
line1200). Swing-maturity, MMS/zone mechanics, sweep rule, rounding/
S-accumulation, 21-EMA trailing (incl. swing-3/4 aggressive-trail
switch), time-based ranges, and multi-TF swing counting all verified
thoroughly accurate. One important flag and several real gaps:

- **Header claim NOT found in the source (flag, not yet corrected)**:
  none of these three transcripts state "$700 -> $89,000 in three
  weeks" or "publicly verified." What the transcript actually describes
  is a DIFFERENT, less flattering money story — lost down to $18,000,
  then to $600, with a stated target of rebuilding to $20,000 over 4
  months trading EUR/USD, US30, and Oil via offshore 500x leverage. The
  $89k/3-weeks figure used elsewhere in this project (including the
  published Source Dossier) appears to come from a video title/
  description that isn't in these transcripts — needs verification
  against the actual source before repeating that claim again.
- **Missing entry-type distinction**: "generation of liquidity" (trading
  within a still-forming range) vs. "sweep of liquidity" (trading the
  breakout run) presented as two separate tradeable events; only the
  sweep side is currently captured.
- **Prop firms — explicit stance missing**: he states he would not use
  them again, calls the model predatory ("their rules exhaust you"),
  while framing leverage itself as fine (analogy to a mortgage/auto
  loan down payment).
- **Risk-per-trade evolution, not just the end-state**: industry-
  standard 1-2% cited as a benchmark vs. his own historical 5-8% when
  trading out of need, settling to the current 3-5% (file only states
  the 3-5% end-state).
- **Trade cadence**: ~2-3 trades/day average — missing.
- **Instrument selection for beginners**: deliberately traded slower
  pairs (EUR/USD, US30, Oil) and avoided NQ/Gold while building
  consistency — concrete, teachable, and missing.
- **Range mechanics, generalized**: "price sweeps high, sweeps low,
  doesn't respect S/D inside a range until ready to break" — only the
  first-NY-hour caution is currently captured, not this general
  range-rebound behavior.
- **Psychology addition**: "don't confuse yourself flip-flopping short/
  long" ("trading like a squirrel") — not captured.

Extended childhood/family backstory in the source is psychologically
interesting but correctly left undistilled — only the actionable line
("what you don't kill on the way up kills you on the way down") was
kept, matching this file's existing content.
