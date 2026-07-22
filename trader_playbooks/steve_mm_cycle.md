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
counter, ADR-thirds level counter, HOD/LOD lock timer, peak-to-peak
ADR box stack, EMA level-cross state, daily pivots, ID50 reentry, and
railroad-track candle tagging (v2 additions below). All bar-close,
non-repainting.

---

## v2 — student mentoring call, SAME LINEAGE (2026-07-20)
Source: live webinar, two practitioners ("Nick" and "GP") teaching
newer traders. NOT a new independent voice — one of them explicitly
attributes core terminology to Steve by name ("how Steve says a big
fat... W formation"), and the whole framework (asian box <=50 pips,
25-50 pip stop-hunt zones, peak formation, three-level cycle, DNC)
is this same school. Logged as an elaboration of voice #8, not a new
tally entry -- inflating independence counts with same-lineage
sources would corrupt the register's evidentiary discipline.

Genuinely new, codeable mechanics this call adds on top of the base
model:

- **Peak-to-peak ADR box stacking**: from a locked peak (HOD/LOD that
  held), stack FULL ADR-sized boxes (not ADR/3 like the base level
  count) outward: 1x ADR, 2x ADR, 3x ADR. Price tends to consolidate
  almost exactly at each box boundary. "Locked in" = price traveled
  >= 1x ADR from the peak within one day. Reversal expectation
  strengthens heavily at 3x ADR ("extended ADR" if it overshoots,
  common per the source -- most cycles run 1 ADR past 3x before
  actually turning). NOTE: this is a DIFFERENT box unit than the
  base model's ADR/3 per-level count already coded -- both are kept
  as separate, clearly-labeled measures; do not conflate them.
- **EMA level-classification stack**: 5/13/50/200/800 EMA (H1 chart
  in source). 13-over-50 cross = "Level 1" confirmation; 50-over-200
  cross = "Level 2" confirmation. 200 and 800 EMA act as moving
  support/resistance (price bounces off them repeatedly before a
  real break); 50 EMA is the "trend EMA" -- its curve direction is
  itself a bias tell. EMAs bunched together (no separation) = stay
  out, expect chop; EMAs fanned/separated = trending, trade it.
- **ID50 (intraday-50) reentry**: after an initial peak-formation
  entry, a pullback/rotation back to the 200 EMA on the entry
  timeframe (source uses M15) that then resumes in the original
  direction is an explicitly favored LOW-DRAWDOWN reentry -- described
  by one participant as consistently working "third and fourth
  rotation" after the initial signal.
- **TDI (Traders Dynamic Index) confluence**: RSI-based oscillator
  with a fast "trade signal" line, a slow "market baseline" line, and
  volatility bands. A "shark fin" (RSI spike to the band extreme and
  sharp reversal) at a level-3/peak-formation zone is called out
  repeatedly as very high-conviction confirmation, especially on H4
  ("if you see a shark fin on H4 at a peak formation, you're good").
  We do not fully reproduce the proprietary TDI; we implement the
  well-documented public-domain Dean Malone TDI formula (RSI +
  signal-line smoothing + volatility bands) as the confluence proxy.
- **Railroad tracks**: two consecutive, opposite-colored candles of
  similar size forming a sharp V/inverted-V, especially at a stop-hunt
  zone or EMA level -- treated as a standalone reversal signal, no TDI
  needed. Direction = color of the second (closing) candle.
- **Daily pivot points (M-system)**: classic floor-trader pivots
  (PP/R1-3/S1-3) computed from the prior "most significant candle"
  (usually daily). Source's own M0-M5 numbering is internally
  ambiguous/undocumented in the transcript (never states which M =
  which formula level) -- we implement STANDARD classic pivots
  instead and flag the M-numbering as unresolved. Stated behavior
  regardless of numbering: projections move odd-to-even (a stop hunt
  at one pivot targets the adjacent even/odd pivot); center pivot
  (PP) acts as a major support/resistance once price is clearly on
  one side of it; works notably well on exotics (wide-spread pairs)
  per the source, less reliable on majors.
- **Psychological support/resistance**: a zone the dealer works
  (accumulates/distributes) repeatedly across a session or day,
  independent of any single candle pattern -- identified only by price
  revisiting the same small range 3+ times with EMA-bunching. Purely
  qualitative in source; not separately coded (already covered by the
  existing triple-tap logic).
- **Correlation caution**: source explicitly demonstrates that naive
  cross-asset correlation (e.g. USD-quoted pair vs gold "should" move
  inverse) frequently fails to hold over short windows and should NOT
  be traded directly -- trust the peak-formation/level framework over
  correlation assumptions. Direct, if informal, caution against
  over-weighting SMT-style divergence (QT, H14) without also checking
  it against this school's own structural read.
- **Session/pair matching**: explicit reminder to trade pairs whose
  ADR is actually large enough to be worth the risk, and to match
  trading hours to the sessions genuinely open in your timezone
  (Asia+Oceania pairs for off-hours traders, majors/EU crosses for
  London/NY-hours traders) -- operational hygiene, not a new edge
  claim.

---

## Audit pass — original transcripts recovered from session log (2026-07-22)
Raw transcripts recovered from the session log and permanently saved to
`trader_playbooks/sources/raw_transcripts/` (line1291 = day-1 seminar,
line1625 = the already-logged Nick/GP mentoring call). The ET time grid,
25-50 pip stop-hunt zone, three-push vector-candle geometry, DNC rule,
two-hour rule, ADR-thirds level count, and the Nick/GP ADR-box-stacking/
EMA-cross/TDI/pivot content all check out with no numeric contradictions.
Real gaps found:

- **Missing entirely — "weekly net change allowance"**: Steve repeatedly
  teaches that dealers are capped by an IMF/World-Bank-style weekly
  net-change limit ("given a weekly net change of 500... they run at
  600-700 pips... reversal back under the 500 limit by Friday close";
  also "1000 pip movement weekly net change... cannot exceed on the
  close on Friday"). A distinct, falsifiable claim — a hard ceiling
  that forces Friday mean-reversion — currently absent even from the
  "WHAT WE DISCARD" section. Needs a decision: code as a soft cap
  forcing reversion, or explicitly log as discarded/unfalsifiable.
- **Missing — ADR-derived market ceiling**: "average daily range... can
  only move most pairs about 200 pips a day to 600 pips a week."
- **Missing — 50/200 EMA take-profit mapping + "50 fib" calc**: original
  day-1 teaching has 50 EMA = first take-profit, 200 EMA = second
  take-profit, and a "50 fib" = (high-low)/2 added back from the
  extreme. The file's v2 EMA section only covers the 5/13/50/200/800
  stack as level-classification/S-R, dropping this original TP-
  targeting rule and the "50 fib" calculation entirely.
- **Missing terminology**: 200 EMA nickname "mayonnaise" (used
  repeatedly as a TP/reversal reference, e.g. "pin to the mayonnaise is
  a sell") — absent from the playbook's terminology anywhere.
- **Missing swing-trade pip range**: explicit numbers given — "three to
  six hundred pips" and "two to six hundred pips" for a caught
  peak-formation swing — not stated anywhere.
- **Missing named pattern**: "half a batman" / "reverse half a batman"
  — used repeatedly in line1625 for a three-hits/head-and-shoulders-
  style level-3 tell. The v2 section generalizes this only as
  "head-and-shoulders... at level 3," never recording the actual
  nickname. ("Quarter wood pattern" is also named in line1625 but never
  defined in the source itself — flagged as unresolved, not missing.)

### Non-match, logged separately: "Forex James" is NOT this voice
Two further raw transcripts (line1675, line1694, "Forex James" —
"how market makers manipulate retail traders") were checked against
this file on the theory they might be a pen-named extension of Steve's
model. They are NOT: zero shared mechanics (no ET time grid, Brinks
windows, ADR-thirds counting, EMA stack, TDI, railroad tracks,
"mayonnaise," DNC, or level counting), no shared clock times or pip
numbers, and different named references (cites "Anton Kreil" and a
"90/90/90 rule," never used by Steve). Content is generic "how market
makers manipulate retail" 101 (fakeouts, stop hunts, long-wick traps)
plus unrelated broker-selection/risk-management advice — qualitative,
no repeatable counting system, low mechanical value. Per the never-
discard rule this is preserved verbatim at
`trader_playbooks/sources/raw_transcripts/line1675_2026-07-20.txt` and
`line1694_2026-07-20.txt` but NOT built into any engine and NOT given a
voice number — logged here as a source that was found, read, and
deliberately not developed further, rather than silently dropped.
