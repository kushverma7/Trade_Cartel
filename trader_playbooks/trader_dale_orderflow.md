# TRADER DALE — ORDER FLOW & VOLUME PROFILE TRADING SETUPS
# Source: "Order Flow Trading Setups" ebook, Trader Dale (full-time
# trader since 2008, states finance degree + portfolio manager,
# investment manager, and financial derivatives certifications),
# supplied 2026-07-20. INDEPENDENT voice #14.
# Credibility tier: MEDIUM — unusually explicit formal credentials
# for this register (most sources are anonymous or self-taught), but
# still zero independently verified backtested track record; the book
# is also a funnel for paid software/courses, so treat marketing
# framing ("this is my favorite setup") skeptically even where the
# mechanics are sound.
#
# CRITICAL DATA CONSTRAINT: this entire book is built on true
# footprint/DOM data -- per-price-level Bid vs Ask volume, individual
# order/lot sizes, real auction completion at each price. Standard
# TradingView OHLCV feeds for gold/forex do NOT provide this (no
# Bid/Ask split, no per-trade size, often tick-count "volume" not
# real traded volume). This document is valuable primarily because it
# explains, in detail, the EXACT real data our existing CVD-from-
# candle-direction and absorption-from-volume+wick proxies (Valentini
# school, voice #5) were built to approximate. Read section 6 before
# assuming any concept here is directly implementable.

## 1. VOLUME PROFILE (buildable with OHLCV + volume)
- Definition: a histogram of volume traded AT EACH PRICE (not over
  time, like standard volume indicators) -- shows WHERE big players
  were active, not just WHEN.
- POC (Point of Control, implied though not the term used here): the
  price level with the most volume in the window.
- **Four repeating shapes**, each with a claimed regime meaning:
  - **D-shaped**: balanced/symmetric, POC near the middle of the
    range -- temporary balance, institutions building positions,
    getting ready for a move.
  - **P-shaped**: heavy volume concentrated toward the TOP of the
    range -- uptrend or the end of a downtrend (aggressive buyers
    pushed up, then a rotation built volume near the highs).
  - **b-shaped**: mirror of P -- heavy volume toward the BOTTOM --
    downtrend or the end of an uptrend.
  - **Thin/I-shaped**: volume spread thin and even, with small
    "bumps" (Volume Clusters) -- strong trend, little time to
    accumulate positions except in brief pauses.
- Directly buildable: bin volume by price over a rolling/session
  window, find the max-volume bin (POC), classify shape by POC
  position relative to the range (top third / bottom third / middle)
  and by how concentrated vs. spread-out the histogram is.

## 2. VOLUME CLUSTERS / HVN (High Volume Node) — the core setup family
- An HVN is a price level (or narrow price band) with disproportionate
  volume relative to its surroundings -- a "fingerprint" of heavy
  institutional activity.
- **Multiple/Double/Triple Node**: when 2+ consecutive candles/
  footprints share an HVN at the same price, the level is graded
  stronger (more repetitions = stronger).
- **The one repeating trading pattern underlying FIVE of this book's
  named setups** (Volume Clusters in a trend, Volume Clusters in a
  rejection, Multiple Nodes, Volume Accumulation, VP Trend Setup, VP
  Rejection Setup -- all listed separately in the source but
  mechanically identical):
  1. Find a heavy-volume price zone (in a trend leg, in a strong
     rejection, or in a pre-trend accumulation rotation).
  2. Require price to move AWAY from that zone by at least ~1-2 full
     bars' worth of range on a higher timeframe (30m in source) --
     confirms the zone was actually left, not just touched.
  3. Wait for a PULLBACK/retest of the zone.
  4. Enter in the direction the zone was originally defended
     (uptrend accumulation -> long; downtrend/rejection of highs ->
     short), **trading only the FIRST test** -- second+ tests of the
     same level are explicitly lower probability.
  5. Two-factor rationale (source's own explanation, matches every
     other "leftover orders" logic already in this register): (a) the
     original accumulators defend their position by re-entering
     aggressively, (b) traders on the other side don't want to fight
     them and close out, and closing itself adds pressure the SAME
     direction as the defenders. Same underlying mechanism as
     Wendell's zones (voice #10) and PBD's value area (voice #3),
     now independently re-derived a fourth time with volume weighting
     specifically as the selection criterion instead of price
     structure or close-clustering.

## 3. TAKE PROFIT / STOP LOSS RULES (directly portable, buildable)
- **Volume-based TP**: take profit AT or slightly BEFORE the next
  heavy-volume zone in the trade's direction -- don't wait to test it
  fully, since price often reacts just ahead of the zone. If the
  nearest HVN is too close for a decent R:R, either skip the trade or
  hold through to the NEXT HVN instead.
- **Three SL placement methods** (explicit, portable):
  1. Fixed SL (simplest, doesn't adapt to conditions).
  2. High/low of the S/R zone being traded.
  3. **Low-volume-area SL** (their preferred systematic method): place
     the stop in a LOW-volume pocket just beyond the nearest HVN --
     if price actually reaches a low-volume area, that itself signals
     real momentum against the trade, not just noise.
  - **SL width guard**: whichever method, keep the stop within
    roughly 10-20% of the instrument's average daily range (ADR).
    Outside that band (too tight or too wide) -- skip the trade or
    fall back to a fixed SL in that range. Directly compatible with
    the ADR-based sizing framework already used elsewhere in this
    project (Steve/MMM4x, voice #8).
- **Trailing TP**: only trail a winning position while seeing signs
  the SAME side remains aggressive (their Imbalance/Delta signals,
  which need true footprint data -- see section 6). Stop trailing the
  moment a confirmation setup fires AGAINST the position, especially
  near an S/R zone or heavy-volume area.

## 4. "UNFINISHED BUSINESS" (Failed Auction) — proxy needed
- A properly formed high should show ZERO trading still happening on
  the Ask at the very top tick (nobody still buying at the extreme);
  a properly formed low should show zero on the Bid. If the market
  turns without that -- if there was still real two-sided activity
  right at the extreme -- the auction "failed," and that price level
  becomes a magnet the market tends to revisit and "fix."
- Uses: stretch a take-profit toward it if already close (with the
  explicit caution that price won't reliably travel a LONG distance
  just to test it), avoid placing a stop just short of it (price will
  likely blow through to test it), use it as trend-continuation
  confirmation (a countertrend move that stops right at an Unfinished
  Business level from the ORIGINAL move is more likely a pullback than
  a real reversal), and as a warning against entering trades with
  Unfinished Business sitting against the position.
- **Our proxy** (true per-price Bid/Ask completion data unavailable):
  a swing extreme candle with a NEGLIGIBLE opposing wick (price closed
  very near its own extreme, an abrupt turn with no visible two-sided
  fight at the top/bottom) is flagged as a candidate "unfinished"
  level; a swing extreme WITH a proper opposing wick (clear rejection
  tail) is flagged "finished." This is an approximation of the
  underlying idea, not the real thing -- explicitly caveated in-code.

## 5. WHAT WE ALREADY HAVE THAT THIS BOOK VALIDATES
- **Cumulative Delta divergence at S/R** (price makes a new extreme,
  cumulative delta doesn't confirm) is this book's Confirmation Setup
  #4 -- the SAME underlying idea already implemented as the CVD-
  divergence veto in trade_cartel_master_engine.pine (CVD approximated
  from candle direction since we lack true Bid/Ask split). This book
  independently corroborates that proxy's design intent.
- **Absorption** (heavy two-sided volume without price progress) is
  this book's Confirmation Setup #2 -- the same concept already
  implemented via volume+wick geometry in effort_result_engine.pine
  (Valentini, voice #5). Now 2 independent sources on absorption
  specifically.
- **PBD's value area** (voice #3, close-cluster proxy) and this book's
  Volume Profile are conceptually the same tool (find where the
  market spent the most "time/activity" to define S/R) built from
  different available data (close-count vs. real volume). This book's
  approach is more faithful to the real concept where volume data is
  usable at all -- worth treating the volume-weighted version as the
  PREFERRED implementation over the close-count proxy where both are
  available, and A/B testing which one performs better on gold.

## 6. NOT BUILDABLE — requires true footprint/DOM data we don't have
- **Imbalances / Stacked Imbalances**: require per-price-level Bid vs
  Ask volume SPLIT (e.g. Ask 300%+ of Bid at a specific price) --
  standard OHLCV feeds give one aggregate volume number per bar, no
  price-level Bid/Ask breakdown at all. Not approximable without
  fabricating a split that doesn't exist in the data.
- **Big Limit Orders confirmation**: requires visibility into
  passive/pending order size at specific prices (DOM/Level 1 depth
  data) -- not available.
- **Trades Filter** (track only trades above N lots): requires
  individual trade/order size data (tick-by-tick with size) -- not
  available on standard chart feeds.
- **True Aggressive Orders confirmation**: requires real Bid vs Ask
  execution split; our existing CVD-from-candle-direction proxy
  (already built) is the best available substitute, not a true
  replacement.
- **True Unfinished Business**: requires per-price auction-completion
  data at the exact extreme tick; see section 4 for the wick-based
  proxy used instead.
None of these are guessed at or faked -- flagged and left undone per
standing rule, preserved here for a future source with real footprint
data access to potentially unlock.

## 6a. Re-upload verification (2026-07-20)
The same book was re-supplied in full (3,453 lines, vs. a shorter/
partial extract the first time around). Read start to finish this
pass to check for anything the first pass missed. Confirmed
identical mechanics throughout, including the three named "Volume
Profile Setups" (Accumulation, Trend, Rejection) -- all three are the
exact same zone-then-pullback-then-defend logic already captured as
"the one repeating pattern underlying five setups" in section 2, no
new mechanic. No changes made to this playbook or the engine as a
result -- logged here only so a future session doesn't re-process
the same file a third time.

## 7. ENGINE
indicators/trader_dale_volume_profile_engine.pine — rolling volume-
weighted price histogram with POC and D/P/b/Thin shape classification,
generalized HVN/Volume-Cluster detector with first-test-only retest
entries (the one pattern underlying five of the book's named setups),
volume-based TP target + low-volume-area SL placement with ADR-width
guard, and the wick-based Unfinished-Business proxy. All bar-close,
non-repainting.
