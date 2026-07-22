# PBD Logic — extracted from user-supplied transcript (2026-07-19)
# Source: German profile trader (AI-translated video), Traders' magazine
# alum. Auction market theory lineage (Steidlmayer/Dalton).
# EDGE STATUS: UNVERIFIED — zero stats in source. Exploratory only.

## Core claims (mechanical)
1. Markets balance ~70% of time (fade value edges), trend ~30% (P/b).
   [ASSERTED, not evidenced — hypothesis H3]
2. Closing-price clusters approximate the value area (cheap volume
   profile proxy). Closes outside cluster = unfair prices / imbalance.
3. P: impulsive up-move (single prints = forced aggressive buying) into
   balance holding upper half of the leg.
   - Close breaks balance HIGH -> continuation long ("break-in" of buyers)
   - Close breaks balance LOW -> reversal short, TARGET = impulse origin
4. b: mirror image (aggressive selling).
5. D: continuations start failing both ways -> regime flips to range;
   short value-area top, long value-area bottom, rotate toward POC.
6. Break-in: close outside value area then close back inside -> trade
   back toward POC. [= our sweep-reclaim, independently derived]

## Parameters the speaker never defined (my defaults, need tuning)
- Value window 120 bars, 24 bins, 70% VA
- Impulse: >= 2.5x ATR14 over 12 bars; Balance: <= 1.5x ATR14 over 10 bars
- Confirmation: single close beyond edge (his "closing price count" is
  vague; test 1 vs 2 closes)

## Confluence mapping (how this layers onto existing edges)
- BREAK-IN corroborates Reversal Sniper v3 reclaim logic (B2 fix)
- Close-count confirmation corroborates CPI Confirm-Continuation (H1)
- P/b regime tag can act as filter for trendline breakout: only take
  session breakouts when a P/b structure agrees with direction
- D regime = stand down trend entries, or fade edges only

## Implementation
indicators/pbd_logic_engine.pine — 6 scenarios, bar-close, labels+alerts.

---

## Audit pass — original transcript recovered from session log (2026-07-22)
The raw pasted transcript this file was extracted from had no retained
file until now; recovered from the session log and permanently saved to
`trader_playbooks/sources/raw_transcripts/`. Re-diffed in full.

- **Missing methodological rule**: source explicitly warns AGAINST
  filtering/removing outlier-close candlesticks from analysis — "even
  the extremes always have their justification." Not captured anywhere;
  relevant to any future data-cleaning step in this engine's backtests.

Everything else re-verified accurate. Source gives no stats, matching
the playbook's existing UNVERIFIED framing — no change there.
