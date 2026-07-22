# Orderflow Effort vs Result — extracted 2026-07-19
# Source: Valentini orderflow foundations video (SAME source family as
# valentini_scalping.md — no new independence tally).
# EDGE STATUS: framework/education; no stats given. Confluence layer.

## Market mechanics (foundations)
- Two forces: aggressive (market orders: execution certainty, price
  uncertainty) vs passive (limit orders: price certainty, execution
  uncertainty). Aggression = pressure; passive book = resistance.
- Price moves along the path of least resistance: through the THIN
  side of the book. Thick passive clusters are walls.
- Slippage = aggression exceeding available passive liquidity.

## The effort/result 2x2 (per-candle classification)
| Effort | Result | Name        | Meaning |
|--------|--------|-------------|---------|
| High   | None   | ABSORPTION  | aggression eaten by passive side; delta one way, close the other. Reversal fuel. |
| High   | High   | INITIATIVE  | aggression rewarded; full-body close, vol above avg. Continuation. |
| Low    | High   | BOOK SWEEP  | hollow move through thin book. Do not trust/chase. |
| Fading | Push   | EXHAUSTION  | price pushes on declining volume; snap-back risk. |

## Volume profile theory (his framing)
- Value area = 68% of volume (Gaussian); POC = max transaction level;
  acceptance inside VA = balance; acceptance outside = trend starting.
- LVNs = inefficient delivery, poor fills; market likes to REBALANCE
  the LVN before continuing (pivot/rejection levels).
- Cash-session-only profile for US indices (London pollutes it).

## Daily profile framing workflow (bias construction)
- Merge overlapping daily value areas into composite balance zones.
- P-shape day (POC high in range, aggressive up) -> continuation bias
  next day. b-shape mirror. Value MIGRATION = the bias.
- Rejection tails (gray, no acceptance) = support/resistance zones.
- The HOOK: failed poke of VAH/VAL that rejects -> price slices through
  the whole value area to the opposite side. His named high-WR setup.
- Repeated same-level VA rejection days = wall forming; breakout of the
  merged balance = trend day confirmation.

## Trade management notes
- Qualify area first (profile/VWAP/S&D) -> then wait for effort/result
  confirmation from big participants at the level -> risk-free fast on
  the first rewarded aggression after entry.
- Trail behind successive aggression clusters in trend (momentum model).

## Implementation
indicators/effort_result_engine.pine — ABSORB/DRIVE/THIN/DRY-UP labels
+ alerts, volume+wick proxy (no bid/ask data in Pine — stated).
Candidates for MASTER ENGINE v2: ABSORB at extreme as reversal-side
confluence; THIN as veto on breakout candles (hollow break = fake risk);
DRY-UP as exit/de-risk trigger.

---

## v2 additions (same source, 2026-07-19)
- TRUE FVG = the LVN inside a fixed-range profile of the impulse (often
  ~1 tick wide), NOT the 3-candle price-action gap zone. Price rejects
  at the volume hole, not the candle geometry. [pbd engine plots it]
- CVD absorption divergence: CVD fresh low while price low HOLDS =
  passive buyers eating aggression -> failed auction confirmed, day
  direction set. Mirror for highs. Distinct from pivot divergence
  (that one = price extreme unsupported; this one = level defended).
  [effort_result engine detects both now]
- Breakout-anticipation tell: repeated punches absorbed at both edges
  with an aggression record candle = compression before expansion; the
  side with absorbed AGGRESSORS loses, the absorbing side wins the break.

---

## Audit pass — original transcripts recovered from session log (2026-07-22)
Raw transcripts recovered from the session log and permanently saved to
`trader_playbooks/sources/raw_transcripts/` (line1000, line1032). Strong
match overall (effort/result matrix, 68% Gaussian value area,
cash-session-only rationale, P/b-shape + HOOK setup, "fixed profile"/
true-FVG concept, LVN example, CVD-absorption divergence — all correctly
reflected). One missing piece:

- **Concrete order-book mechanics walkthrough (teaching example)**: a
  25-lot market order absorbed by 33 passive contracts at price 101; a
  75-lot order slipping 3 ticks through 101->103 when the book is thin.
  This worked numeric example of the effort/result mechanic has no
  analogue anywhere in the file — everything else is stated as
  principle without this concrete illustration.

Live absorption trade-print examples (e.g. "72/61/60/62 = 300
contracts") and the specific LVN/delta numbers from line1032 are
illustrative only, correctly omitted as non-critical.
