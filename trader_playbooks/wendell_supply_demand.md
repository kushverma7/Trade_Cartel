# WENDELL / ONLINE TRADING ACADEMY — SUPPLY & DEMAND ZONE RULES
# Source: Brandon Wendell (OTA instructor, Sam Seiden/Wyckoff-descended
# institutional S/D lineage), live webinar transcript, supplied 2026-07-20.
# INDEPENDENT voice #10.
# Credibility tier: MEDIUM-HIGH — established trading education firm,
# ex-hedge-fund instructor, explicit auction/order-flow rationale (not
# marketing hype), but still zero backtested statistics in source.
#
# ** DIRECTLY ACTIONABLE AGAINST BELIEF B2 **
# B2: "Auto-generated 5m S/D zone reclaims are noise on gold" — PF 0.731,
# 313 trades (Reversal Sniper v2). B2's stated invalidation: "reworked
# zone logic showing PF > 1.5 on matched sample." This lecture is the
# most precise, rule-based zone-construction methodology in the register
# so far — a strong candidate for that rework. PBD's value-area logic is
# the same lineage in looser auction-theory language; this is the
# textbook mechanical version.

## 1. ZONE CONSTRUCTION (exact line rules)
- **Search direction**: from current price, look LEFT and DOWN for the
  origin of a strong rally (demand) or LEFT and UP for the origin of a
  strong drop (supply). NOT just any pause-then-reversal — the ORIGIN of
  the overall move, which may be further back than the nearest pause.
- **Distal line** (far/risk line): demand = below the wick/low of the
  basing candles (or body low if no wick); supply = above the wick/high.
  This is the objective line — always the extreme.
- **Proximal line** (near/entry line): demand = across the TOP of the
  BODIES of the basing candles (not wicks); supply = across the BOTTOM
  of the bodies. This is the subjective line but has a fixed rule:
  bodies, not wicks, and only the basing candles, not the departure leg.
- Pattern names: **drop-base-rally** (demand) / **rally-base-drop**
  (supply) — classic Wyckoff-lineage shorthand for the same shape as
  our P/b structure (PBD) and the ABC/123 swing failure (voice #9).
  SIXTH independent voice landing on essentially the same swing-origin
  shape (see Contradiction Tallies).

## 2. ZONE QUALITY — ODDS ENHANCERS (the actual filter B2 was missing)
- **Basing candle count**: ≤4 candles at the base = strong/fresh; more
  candles = orders more likely already filled = weaker. 7 candles at
  the base (the source's one worked example, an 8-day base counted live
  on the chart) is explicitly called "a little long" / lower quality in the
  transcript's own worked example.
- **Departure speed/size**: large candles (or gaps, where applicable)
  LEAVING the zone = strong imbalance, more likely leftover unfilled
  orders. A slow, small-candle departure = weak zone, skip it.
- **Freshness (hard filter, not a scoring input)**: look further left —
  has price traded through/tested this exact zone before? If yes, it is
  NOT fresh; do not trade it. First test after formation = full
  probability; second/third test = lower probability (still valid, just
  demoted) — because each visit consumes the leftover resting orders
  that make the zone work in the first place.
- **Retest penetration depth**: on a retest, if price only penetrates
  ~50% or less of the zone before reversing, that confirms strong
  leftover interest (fewer orders got filled the first time = zone still
  has ammunition). Deep/full penetration on retest = zone is weaker or
  exhausted.
- **Trend position ("the curve," undetailed in source)**: zones deep
  into a mature trend are weaker than zones near the start of a trend —
  institutions buy/sell wholesale early, not retail late. Source
  explicitly reserves the full mechanics for another lecture; treat as
  a qualitative caution, not yet a codeable rule.

## 3. MULTI-TIMEFRAME STRUCTURE ("walls vs chairs")
- Higher-timeframe zones are "walls" — real turning points that will
  stop or reverse a move.
- Lower-timeframe zones are "chairs" — momentum can push straight
  through them if the higher-timeframe trend favors that direction.
- Workflow: identify HTF trend/turning zones first, then only take LTF
  zone entries that align WITH the HTF trend, aiming at the LTF zone in
  the direction of (and stopping at/before) the next HTF wall.
- **"Don't trade in the middle"** (attributed to fellow OTA instructor
  Michelle Wulmering): if price is not currently at a fresh demand or
  supply zone on the timeframe you're trading, there is no trade — full
  stop, no exceptions, switch instruments or timeframes instead of
  forcing an entry between zones.

## 4. ENTRY MECHANICS
- Entries do not require deep penetration into the zone — many of the
  best trades only tap the proximal line and reverse immediately. Be
  ready to act the instant the proximal line is touched, not after
  confirmation deep inside the zone.
- News is explicitly framed as a DELIVERY MECHANISM, not a cause: "the
  news will simply drive price into an area of demand or supply" — the
  zone is what matters, the news is just what got price there fast.
  Direct tension-free complement to B3/B4 (CPI is unknowable pre-print,
  the tradeable edge is post-spike) — this gives a mechanism for WHY
  news spikes so often resolve at pre-existing structural levels.

## 5. WHAT WE DISCARD
- "Identifying the curve" — referenced but not taught in this source;
  do not implement speculative logic for it.
- Anecdotal trade examples (BP doubling, student wins) as evidence.

## 6. REGISTER IMPACT
- Break-of-structure/swing-origin family: 6th independent voice (PBD,
  QT Judas, Dave, Steve/MMM4x, voice #9 ABC/123, now Wendell drop-base-
  rally/rally-base-drop).
- **Direct B2 rework candidate**: our failed Reversal Sniper v2 zones
  almost certainly violated multiple rules here at once — no freshness
  filter (traded pre-tested zones), no basing-candle-count cap (zones
  regenerated constantly per the v2 diagnosis = definitionally never
  fresh), no departure-strength filter, no retest-depth confirmation.
  H30 formalizes the rework.

## 7. ENGINE
indicators/wendell_zone_engine.pine — proximal/distal zone construction
per the exact line rules above, basing-candle-count quality score,
departure-strength score, hard freshness filter (untested-only), retest-
depth confirmation, HTF wall / LTF chair dual-timeframe overlay via
request.security. All bar-close, non-repainting (zones only confirm
after the base has fully formed and departure is complete).

---

## Audit pass — original transcript recovered from session log (2026-07-22)
Raw transcript recovered from the session log and permanently saved to
`trader_playbooks/sources/raw_transcripts/line1527_2026-07-20.txt`.
Overall faithful, but one real fabrication found and fixed:

- **Fabricated precision, corrected**: this file previously stated "7-9
  candles at the base... explicitly called 'a little long'." The
  transcript only discusses ONE worked example — a student asks about
  an 8-day base, Wendell counts it live on the chart and gets **7
  days** ("1 2 3 4 5 6 and the seventh day we finally left... that may
  be a little long"). There is no "9" anywhere in the source. The
  "7-9" range was invented by an earlier extraction pass. Should read:
  "7 (in the one worked example)," not a range.
- **Missing rule**: Wendell explicitly caps the usable timeframe floor
  — "the lowest timeframe for the zones to be tradable... I wouldn't
  usually suggest anything lower than 5 minutes" (despite saying the
  method technically works down to 1-minute charts).
- **Missing framing**: he opens the live-chart walkthrough with an
  explicit numbered rule — "Number one, I always look for trend first...
  the supply and demand tell us where to enter or exit the trend" —
  currently only implied by the walls/chairs section, not stated as his
  own first rule.

Everything else re-verified verbatim-consistent: proximal/distal line
rules, drop-base-rally/rally-base-drop terminology, freshness test
(look further left, 1st/2nd/3rd test probability decay), 50%
retest-depth logic, "don't trade in the middle" (credited to Michelle
Wulmering), walls-vs-chairs MTF analogy, news-as-delivery-mechanism
framing, hedge-fund "average cost" rationale.
