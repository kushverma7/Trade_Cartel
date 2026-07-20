# STEVE (MMM4x) — MARKET MAKER CYCLE MODEL
# Source: 4-day seminar, day 1 (transcript supplied 2026-07-20)
# School: "market maker manipulation" model. INDEPENDENT voice #8.
# Credibility tier: LOW-MEDIUM — seminar seller, "90% accurate /
# will not fail" marketing claims, no verified track record, and a
# conspiratorial frame (MT4 back-office plugins, net-change
# "allowances") that is unverifiable. BUT: the timing grid, stop-hunt
# geometry, and cycle counts are fully mechanical and falsifiable.
# We keep the mechanics, discard the mythology. Every claim below is
# a hypothesis until our own gold backtests say otherwise.

## 1. THE DAILY TIME GRID (all times ET / New York)
| Window | Name | Behavior claimed |
|---|---|---|
| 17:00 | Daily reset | High/low of day reset; MM "spread" (initial range) set ~17:15-17:30 |
| 17:00-20:00 | Dead gap | Nothing tradeable |
| 20:00-20:30 | Asia gap | MM gets instructions |
| 20:30-03:00 | Asia session | Accumulation inside the initial range ("Tokyo channel", ideal <= 50 pips FX; range widens 01:00-02:00 to validate pendings) |
| 03:00-03:30 | London gap | Shift change; stop-hunt may begin |
| 03:30 | LONDON OPEN | False move / stop hunt AGAINST the real daily intent |
| 03:30-03:45 | **BRINKS #1** | If second leg of M/W completes here as a hammer/spike forming HOD/LOD → high-probability reversal entry |
| 08:00-11:00 | London end run | Real move completes; reversal window ~09:00-10:00 |
| 09:00-09:30 | NY gap | Shift change |
| 09:30 | NY OPEN | Aligned with equities open; false move/spike |
| 09:30-09:45 | **BRINKS #2** | Same rule as Brinks #1 on the 09:45 close |
| 12:00-13:00 | NY dies | Consolidation; day effectively over |
| End of day | Park move | Day ends 25-50 pips off the extreme, back into consolidation, trapping late chasers |

Winter time: London-side moves shift ~1h; the 09:30 equities anchor never moves.

## 2. STOP-HUNT GEOMETRY
- Stop hunts extend 25-50 pips (FX) beyond the accumulation range — a
  pre-measurable zone box above/below the Asian range.
- The hunt comes as THREE pushes ("vector" candles) — 1-2-3 into the
  zone — engineered so the third push makes the retail trader chase.
- Three hits at a level WITHOUT a body break = reversal imminent.
  "When they take the trouble to come back a third time and don't
  break it, the correction is imminent."
- A wick through the level is acceptable (grabs the orders); a body
  close beyond it is not.
- HOD/LOD that holds for 30-90 minutes = "locked" — safe to trade
  away from it, stop goes beyond the day's extreme (never 5-7 pips
  behind entry — that is exactly where the herd's stops sit).

## 3. THE CYCLE (levels / the count)
- Intraday: 3 levels per day, each ≈ ADR/3 (150-pip pair → three
  ~50-pip bursts), each followed by its own mini consolidation with
  stop runs BOTH ways (the "pennant" is manufactured).
- Levels 1 and 3 are MM-driven (fast, aggressive); level 2 is drift
  ("MM steps aside"). Heaviest volume at level 3, then reversal.
- Weekly: 3-day / 3-level unidirectional cycle. Anchors:
  - False move week-beginning (Sun/Mon trap, often gap)
  - Midweek reversal Tue-Thu, "almost every week"
  - Friday: aggressive move then pullback into consolidation, ends the
    week 25-50 pips off the extreme; never carry over the weekend
    (gap fills your stop at first available price).
- Cycle shapes: W-V-V-M / M-A-A-W. Multi-session M/W (level set in one
  session, repeated in a later session/day without breaking) is the
  highest-grade pattern.
- Level-3 tells: wicks/pins flip to the trap side; head-and-shoulders
  lives at level 3 (trade the shoulder retest, not the neckline).
- After 3 levels the count RESETS: old level 3 becomes new level 1 if
  the move continues.

## 4. THE FOUR TRADES (his entire trade universe)
1. Stop hunt HIGH → M formation → short
2. Stop hunt LOW → W formation → long
3. Straightaway rise (day after a trapped low, out of level-1
   consolidation — the one day breakout traders get paid; DNC: do NOT
   counter-trend out of level-1 consolidation)
4. Straightaway drop (mirror)
Entries: second leg of the M/W near the locked extreme, ideally in a
Brinks window; confirmation = hammer close at the right time + the
one-candle "zone shift" away from the trap (25-50 pips in 1-2 candles).

## 5. HARD RULES (mechanical, portable)
- **Two-hour rule**: a trade that shows no substantial profit within
  2 hours is scratched — setup thesis is broken, not negotiable. A new
  second leg restarts the clock.
- London trades exit by London end; NY entries 08:00-11:00 (9:30 focus),
  out by 12:00-13:00.
- Never counter the move out of level-1 consolidation (straightaway day).
- Never carry Friday → Sunday.
- Oversized entry bar (zone already shifted) = PASS, don't chase.
- Stop beyond the day's extreme or you are inside the hunt zone.
- His "support/resistance is manufactured" claim = don't trust chart
  S/R lines as standalone edge (tension with PBD/Dave level trading —
  logged in register).

## 6. WHAT WE DISCARD
- Back-office plugin narrative, net-change "allowances", dealer
  villain framing: unfalsifiable, not needed for the mechanics.
- "90% accurate, will not fail": marketing.
- Gold translation: FX pip constants (25-50) must be rescaled — we use
  ATR/ADR-proportional zones in the engine and will measure actual
  sweep depths beyond the Asia range on XAUUSD (H21).

## 7. ENGINE
indicators/mm_cycle_engine.pine — time grid shading, Asia-range box +
stop-hunt zone tiers, Brinks-window second-leg detection, triple-tap
counter, ADR-thirds level counter, HOD/LOD lock timer. All bar-close,
non-repainting.
