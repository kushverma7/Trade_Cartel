# Quarterly Theory (Trader Daye / ICT lineage) — extracted 2026-07-19
# Source: compiled PDF, user-supplied. INDEPENDENT SOURCE #4.
# EDGE STATUS: pure theory, ZERO stats or track record in source.
# ICT-derived material is partly unfalsifiable; only the testable
# time/price skeleton is implemented. Observation + confluence only.

## Codeable skeleton
1. Fractal time quarters. Daily (ET): Q1 Asia 18-00, Q2 London 00-06,
   Q3 NY AM 06-12, Q4 NY PM 12-18. Sessions subdivide into 90-min
   quarters; those into 22.5-min quarters.
2. True Opens (reference prices): Daily = 00:00 ET open, Weekly =
   Tuesday 00:00 open, NY AM = 07:30 open. Above/below = premium/
   discount frame; reversals cluster near them (claim).
3. AMDX phase template per cycle: Accumulate -> Manipulate (Judas
   swing = deliberate false move) -> Distribute -> Reverse/Continue.
   Alternate form XAMD (shifted one quarter).
4. Session quarter behavior: Q1 range/liquidity build, Q2 expansion,
   Q3 continuation/pullback, Q4 reversal/profit-taking. Asia = trap
   setting, London = strongest expansion, NY = continue/reverse.
5. SMT divergence: correlated asset fails to confirm a sweep ->
   sweep was manipulation. Levels: standard (daily+), session (SSMT),
   90-minute (90SSMT). For gold: silver or DXY(inverse) reference.
6. Strategy chain: identify quarter/phase -> SMT -> PD-array tap
   (OB/FVG in premium/discount) -> CONFIRMATION (structure shift or
   liquidity grab) -> stop beyond the grab, laddered TPs (1:3/1:6+).
7. Risk notes from source: 1-2%/trade, high-liquidity sessions only,
   not every quarter offers a trade.

## Register impact
- SWEEP-REVERSAL FAMILY: first independent SUPPORT (Judas swing IS
  sweep-then-reverse). Tally: 2 support (PBD, Quarterly) vs 1 against
  (Valentini).
- CONFIRMATION FAMILY: 5th independent source (even ICT school
  requires structure shift after the tap).
- B1 CORROBORATION: Q2 expansion windows = London open + NY open =
  exactly our backtested gold session windows, via different reasoning.

## Implementation
indicators/quarterly_theory_engine.pine — daily quarter shading, true
opens, prev-day liquidity lines, real SMT vs reference symbol (silver
default, DXY-inverse toggle), JUDAS sweep+reclaim+SMT signals, alerts.
NOTE: SMT needs the reference symbol available on user's data plan.

---

## v2 additions — second QT compilation (2026-07-19)
Source: community doc (mostly chart images; text layer extracted;
image examples not recoverable). Same school, richer mechanics.

- Q-ALTERNATION RULE [H15, highly testable]: consolidating Q ->
  expect expansion next Q; expanding Q -> expect consolidation next.
  Session form: Asia consolidates -> trade London; Asia expands ->
  skip London, trade NY. [engine: forecast label at each Q open]
- Every Q open is a True Open (not only Q2).
- TF pairing model: 1m entry <- 15m context, 5m <- 1h, 15m <- 4h.
- SSMT (sequential SMT): SMT across/just after a Q boundary =
  higher probability than generic SMT ("time factor engaged").
  Mapping: Monthly SSMT->4h PSP, Weekly->1h, Daily->15m,
  Session/90m->5m, Micro->1m. [engine: SSMT vs SMT label grades]
- PSP (Precision Swing Point): the swing candle formed at the SSMT
  (correlated triad diverges). ENTRY = CLOSE of that candle ->
  confirmation-before-entry family, 5th source holds here too.

---

## v3 — PRIMARY SOURCE (Trader Daye's own intro video, 2026-07-19)
Primary outranks compilations. Corrections + precision:

- TRUE WEEKLY OPEN = MONDAY 18:00 ET (compilation #1 said "Tuesday
  midnight" — garbled; Mon 18:00 IS the start of the Tuesday trading
  day in the 18:00-rollover convention). ENGINE CORRECTED.
- Session true opens = Q2 of each session's 90-min cycle:
  Asia 19:30, London 01:30, NY 07:30, PM 13:30 ET. All now plotted.
- True year open = first Monday of April; true month open = second
  Monday. Monthly counting uses first FULL week; partial = distortion.
- Trading rule (crisp): bullish in a cycle -> buy BELOW its true
  open; bearish -> sell ABOVE it. Key levels rest beyond true opens.
- Q1 is the barometer (his words): Q1 overextended -> Q2 consolidates;
  Q1 tight -> Q2 expands. Confirms H15 is faithful to the original.
- PD-array TF pairing (full map): 1m->15m, 5m->1H, 15m->4H, 1H->D,
  4H->W.
- Lineage note: he states openly it is reverse-engineered ICT. Still
  zero statistics offered in the primary source either.
