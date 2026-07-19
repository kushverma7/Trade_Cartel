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
