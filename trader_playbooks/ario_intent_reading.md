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

---

## Audit pass — original transcript recovered from session log (2026-07-22)
Raw transcript recovered from the session log and permanently saved to
`trader_playbooks/sources/raw_transcripts/line1154_2026-07-19.txt`
("Are you actually a price action trader or do you just know how to
read concepts?"). This transcript had previously been mis-flagged during
a prior audit pass as possible "pure_pa_smc.md companion material" — it
is actually THIS voice's own source. Confirmed match on all 5 core
claims (three intents, momentum-as-ratio, tested/non-tested moves,
failure counting, candles-as-compressed-lower-TF-trends). One naming
gap:

- **Missing the framework's own name**: the instructor explicitly names
  his overall approach "Evidence-Based Decision-Making" (EBDM), and
  frames every read as probabilistic ("70% chance"), never certain —
  the playbook captures the mechanics but never records the EBDM name
  or its explicit anti-certainty framing.

No wrong facts found.
