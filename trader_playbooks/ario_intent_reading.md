# Intent/Momentum Reading (Ario, MMT) — extracted 2026-07-19
# Source: educator video. INDEPENDENT VOICE #6 — LOWEST credibility
# tier (no track record, education content). Mechanics codeable;
# value is in corroboration + one new continuous measure.

## Core claims (mechanical)
1. Three intents only: higher / lower / consolidation. Trend = bull
   legs bigger than bear legs; consolidation = equal legs. Momentum
   is a RATIO (80/20), never binary.
2. TESTED vs NON-TESTED move: a move is evidence only after the
   opposite side tried and FAILED. Big untested moves = possible
   manipulation. Entry = push -> counter fails -> resume.
3. Failure counting: stacked failed attempts (wicks) at a level =
   that side weakening; reversal evidence before any concept prints.
4. Candles are compressed lower-TF trends; wick = failed sub-trend.
   Read candles WHILE forming; lower TF leads higher TF (fractal
   early signs).
5. Concepts (FVG, OB, sweeps) are summaries of momentum — useful
   doors, but limits if depended on. (His framing mirrors our own
   proxy-based engine philosophy.)

## Register impact
- Tested-move rule == confirmation-before-entry: 6th source.
- Failure counting == H8 rejection-weakening: first independent
  corroboration (2 sources).
- NEW: leg-size momentum scoreboard (H17) — continuous trend/consol
  measure from swing legs; potential regime layer for master engine
  if it outperforms the close-cluster VA regime in A/B.

## Implementation
indicators/intent_reader.pine — pivot-leg scoreboard (bull%/bear%,
BULL/BEAR/CONSOLIDATION states, tint), SHIFT flip signals, TESTED
continuation signals (impulse + failed counter-leg + resume close).
Note: pivots confirm after `pw` bars — states lag by design; the
TESTED trigger itself fires on the live close (non-repainting).
