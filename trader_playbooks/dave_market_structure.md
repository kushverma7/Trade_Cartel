# Dave — Fractal Market Structure Scalping — extracted 2026-07-19
# Source: podcast. $700->$89k in 3 weeks claimed ("publicly verified"
# per host — unaudited by us). INDEPENDENT VOICE #7. SMC school,
# price-over-time philosophy.

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
