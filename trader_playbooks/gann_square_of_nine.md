# Gann Square of Nine (voice #16)
Source: "Trading the Gann Square of Nine" (TradingFives.com, June 2003) — 57
pages, includes an appendix reproducing W.D. Gann's own 1953 typed/signed
notes on the Square of Nine / Master Square of 144 ("original works of
W.D. Gann made available for general use"). Read cover-to-appendix
(text) AND every embedded chart/diagram image (pypdf text extraction
alone would have missed the appendix — it's a scanned facsimile of
Gann's original letter, garbled to ~12 chars/page as plain text; the
rendered page images (via pymupdf) were read directly to recover it).

**v2 addition (2026-07-20): "The W.D. Gann Master Commodities Course"**
— Gann's own original grain/cotton/egg/soybean/coffee trading courses,
16,230 lines / ~815KB plain text, read in full (7 sequential chunks).
SAME lineage/voice as the TradingFives book above (this is literally
Gann's own writing, the TradingFives book quotes and interprets him) —
extended in place per the one-brain-per-voice standing rule, not forked.
This course covers the ONE thing the TradingFives book explicitly said
it does NOT: "we make absolutely no claims that the channel lines on
the Square of Nine Roadmap charts accurately represent any particular
Gann Angle... W.D. Gann made all his charts by hand." Section 11 below
covers what this course adds. Everything in sections 1-10 (original
v1 content) is unchanged.

**Credibility tier: LOW-MEDIUM.** W.D. Gann's own claimed trading record
is famous but has never been independently verified and is widely
disputed among historians of technical analysis — treat every "Gann
said X works" claim as folklore, not evidence. The modern author
(TradingFives, self-published ebook, 2003) shows worked historical
examples (SPX, DJX, DELL, AOL, NHB, wheat/beans) but these are
retrospective illustrations picked to demonstrate the technique, not a
forward-tested track record — same caution as every other unverified
source in this register. The technique itself (squaring price and time
via a spiral of natural numbers) is real, well-documented, and widely
used by other technicians independent of Gann folklore (e.g., the
formula is explicitly credited to Carl Futia, not Gann). Treat as
**observation-layer confluence only**, same as every other engine here
— never a standalone trigger.

## Core mechanic: the Square of Nine
Arrange the natural numbers in a clockwise (or counterclockwise) spiral
starting at 1 in the center. Numbers on the same 45°/90°/180° angle from
the center have a fixed mathematical relationship via their square
roots. This gives two formulas:

1. **Price/time rotation formula** — move to a new price level a given
   number of degrees around the spiral from a base price N:
   `(SQRT(N) + factor)^2` where `factor = degrees / 180`
   (Degrees→Factor: 45°=.25, 90°=.50, 135°=.75, 180°=1.00, 225°=1.25,
   270°=1.50, 315°=1.75, 360°=2.00). For rotations BELOW a base (e.g.
   descending from a swing high), subtract the factor instead of adding.

2. **Number→degrees formula** (attributed to Carl Futia, not Gann):
   `degrees = MOD((SQRT(N) * 180) - 225, 360)`
   Converts any price, price range, or bar/day count to its position (in
   degrees) on the circle. Two numbers "square" when their degree
   values are equal or 90/180/270 degrees apart (within a few degrees —
   Gann's own "lost motion" caveat: exact-to-two-decimals accuracy is
   not expected or required).

3. **Reverse formula** (degrees → all numbers that live on that angle):
   `(((2*n) + (2*x/360) + 1.25))^2` where n = rotation count (1,2,3...),
   x = angle of interest. Used to forecast a grid of future bar-counts
   or price levels that WILL square with a known reference, before they
   happen.

## The "three digit controversy"
All these formulas are scale-sensitive — sqrt(84.26) behaves very
differently from sqrt(842.6). The source's rule of thumb: before doing
the math, convert the base price to have **three significant digits**
(multiply/divide by a power of 10), do the calculation, then convert
back. No universal rule for exactly when to convert — "experiment until
the channel looks like a normal trend line." For XAUUSD specifically
(price ~$2,000-$5,000, i.e. 4 digits) this means our engine auto-divides
by 10 before the sqrt step by default — **untested assumption**, flagged
because the source's own examples are all equity indices in the
1,000-4,000 range or single/double-digit stocks, never a 4-digit
commodity price. This is the single biggest transferability risk in this
whole engine — log as an open question, not a settled rule.

## The Square of Nine "Roadmap Chart"
The book's core actionable construct, built off ONE major pivot
(source uses all-time-high/low, 52-week H/L, contract H/L — genuinely
*major* swings, not every local pivot):
- **Horizontal grid lines**: successive rotations of a chosen angle
  (source defaults to 180°, i.e. `factor=1,2,3...`) from the anchor
  price, going up (from a swing low) or down (from a swing high).
- **Vertical time grid lines**: spaced `round(SQRT(3-digit anchor
  price))` bars apart — constant spacing regardless of chart timeframe
  (same day-count, whether the bars are hourly, daily, or weekly).
- **Diagonal channel lines**: 3 parallel lines, same slope, anchored at
  (a) the pivot itself, (b) the first horizontal level directly above/
  below the pivot's own time position, (c) one rotation higher/lower
  again. Price is expected to "vibrate" inside this channel for the
  life of the trend; a 2-consecutive-close penetration of the OUTER
  channel bound is the book's explicit trend-invalidation signal — not
  a single wick, and not a single close.
- 90° angle and its multiples (180/270/360) are called out repeatedly
  as the most important; 45° next; some bond traders reportedly favor
  60°-multiples. No claim of importance for arbitrary angles.

## Squaring price with time (5 named variants, all same core math)
The source lists five ways price and time can "square":
1. Current price vs. time elapsed since the prior change in trend (CIT)
2. Time in the prior trend vs. price range of the current trend
3. Price range in the prior trend vs. time in the current trend
4. Price that ended the prior trend vs. time in the current trend
5. Price range of the current trend vs. time in the current trend

All five reduce to the same operation: convert two quantities (a price,
a price range, or a bar/day count) to degrees via the Futia formula and
check whether they land within a few degrees of a 90° multiple of each
other. The source is explicit that **most trend changes coincide with
SOME squaring, but not every squaring produces a trend change** — this
is confluence, not a standalone trigger, consistent with every other
signal in this repo.

## Gann's own appendix material (1953 letter, "Master Square of 144")
Recovered from the scanned facsimile images, not the garbled text
extraction:
- **Master Numbers**: 3, 5, 7, 9, 12 — explicitly tied to numerology/
  Biblical references by Gann himself ("Jesus selected 12 disciples").
  Flagged as folklore, not mechanics — **not implemented**, preserved
  here verbatim per the "never discard" standing rule.
- **Table of 64ths of the circle** (Gann's own Sept 29, 1953 signed
  note): dividing the circle into 64ths (5⅝° increments) instead of the
  usual 8ths/16ths, with the important levels falling every 4th entry
  (22½°, 45°, 67½°, 90°...) — same underlying 45°/90° framework as the
  rest of the book, just finer-grained. Not separately implemented
  (redundant with the existing degree-factor math at finer resolution).
- **Squares 1-19 watch-list**: Gann's own list of "important" squares —
  1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225, 256,
  289, 324, 361 — explicitly called out as bar/day/week/month counts to
  watch for a change in trend. This IS directly implementable as a
  simple bar-count watchlist and is the one piece of the appendix folded
  into the engine (see below), independent of the numerology framing.
- **Gravity center / halfway point**: the midpoint of a price range or
  of the Master Square of 144 (72, for that specific square) is called
  out as a location where countertrend moves tend to start/end — same
  underlying idea as an 50%-equilibrium marker already built elsewhere
  in this repo (Pure PA/SMC engine, H44) — logged as **weak
  corroboration** of that existing idea from a totally independent
  90-year-old source, not a new voice-count.

## What's built (`indicators/gann_square_of_nine_engine.pine`)
- Major-pivot anchor: auto (most recent extreme of a rolling lookback,
  either the swing high or swing low, whichever is more recent) OR a
  manually-typed anchor price/bars-ago/direction — auto mode is our own
  convenience shortcut, NOT what the source does (source always
  hand-picks a genuinely major, often all-time, pivot).
- Optional 3-digit price normalization (default ON for gold).
- Roadmap chart: horizontal rotation levels (default 180°, selectable
  45/90/135/180), optional 90°-midpoint lines, vertical time grid at
  `round(sqrt(3-digit anchor price))` bar spacing, 3-line diagonal
  channel with 2-consecutive-close outer-channel-breach alert.
- Price/time squaring detector at each new confirmed swing pivot
  (`ta.pivothigh`/`ta.pivotlow`): converts the price range and the bar
  count since the prior pivot to degrees, flags a hit within a
  user-set tolerance of a 90° multiple.
- Gann's own squares-1-to-19 bar-count watchlist: flags when bars-since-
  anchor lands on 16/25/36/49/64/81/100/121/144/169/196/225/256/289/
  324/361.
- Status table + alertconditions for all three signal types.

## What's explicitly NOT built
- The Master Square of 144 / Master Numbers numerology (3,5,7,9,12,
  Biblical references, "Great Yearly Time Cycle" of 56 years 9 months)
  — no falsifiable mechanic, preserved verbatim above per standing rule.
- Celestial-longitude-based conversions ("the school that uses degrees
  of longitude of the celestial bodies") — explicitly mentioned by the
  source itself as a whole separate method it does not cover; we don't
  have the data or the method to build it either.
- Bond-trader 60°-multiple angles — mentioned only as a rumor by the
  source about a different market; not applied to gold.
- Hand-picking genuinely major (all-time/52-week/contract) pivots is
  NOT automated with any real judgment — the "Auto" anchor mode is a
  crude rolling-extreme proxy, flagged as the weakest part of this
  engine's fidelity to the source.

## Open questions (for our own backtest, not adjudicated here)
- Does the 3-digit-normalization convention (built for equity indices
  in the hundreds/low-thousands) transfer sensibly to XAUUSD's
  4-digit price level? Untested. Toggle exists to turn it off.
- Does "bars elapsed" on a 5m gold chart behave anything like "trading
  days elapsed" on the daily equity charts every worked example in the
  source uses? The source itself only validates hourly/daily/weekly —
  never anything close to 5-minute. This is a bigger timeframe jump
  than any other source folded into this repo so far.

---

## 11. Master Commodities Course — what's built, what's not

### 11a. Built: Gann Angle Fan (1x1/2x1/4x1/8x1 + mirrors)
The classic geometric angle fan from Chapter 5A/5B (grains, ~1940 and
1951 revisions) and Chapter 10 (cotton, same method rescaled). Full
construction, quoted/paraphrased from the source:

- Angles are straight lines from a pivot moving a FIXED price-per-
  time-unit (day/week/month, whatever the chart's timeframe is).
- Named angles in order of steepness: 1x8 (7.5°) < 1x4 (15°) < 1x2
  (26.25°) < **1x1/45° ("the death angle" — always the most important)**
  < 2x1 (63.75°) < 4x1 (75°) < 8x1 (82.5°). Each step doubles (or
  halves) the price-per-time-unit rate of the previous one.
- **"The rule of all angles" (verbatim, repeated near-identically
  across the grain, cotton, and egg chapters)**: "No matter what angle
  the option breaks under, it indicates a decline to the next angle
  below it." Symmetric on the way up.
- Position relative to the angle stack reads as a trend-strength
  ladder: holding above 8x1 = strongest possible position; below 1x1
  = weakest, "in a Bear Market."
- Stop-loss doctrine tied directly to the 45°: buy on rests at the
  angle with a stop 1-3¢ under it (grain scale) — "never use a
  stop-loss order more than 3¢ [or 5¢, the two chapter versions
  disagree] away."
- Gann also draws a SECOND 45° from "0" (price zero) starting on the
  same date as the actual pivot — not implemented, see "not built"
  below.

**Implemented** in `gann_square_of_nine_engine.pine` v2: draws the
1x1/2x1/4x1/8x1 fan (plus the 1x2/1x4/1x8 mirror on the weak side)
from the same major-pivot anchor already used for the Roadmap chart.
Rate for the 1x1 line is **our own convention, not source-given**:
default `ATR(14) x 0.25`, adjustable, or a manual override — Gann's
own instruction was explicitly discretionary ("pick a scale where the
45° looks right against the chart"), so an ATR-based default is in
the same spirit, not a literal transcription. A status readout shows
which angle band price currently holds above/below, and an alert
fires on the 1x1 ("death angle") being crossed.

**Not implemented from this section**: the "angle from zero" technique
(a second reference angle starting the same date but from price=0,
used to "prove Time and Price are balancing") — cheap to add later if
useful, skipped for now to keep the first pass scoped; the "3x1"/"16x1"
angles mentioned only in the 1951 revision as rare/fast-market-only
extras; drawing angles from EVERY higher-bottom/lower-top (not just
the single major anchor) — would require tracking a fan per swing
pivot rather than one fan per major anchor, a bigger redesign.

### 11b. Built: Signal Day
Quoted near-verbatim across grain/cotton/egg chapters, one of the most
repeated single-bar rules in the whole course: a bar that makes a new
extreme (new N-bar high in an advance, new N-bar low in a decline) but
closes in the WEAK half of its own range — or beyond the open — is
read as an immediate reversal cue, no confirmation bar required.
**Implemented**: `signalLookback`-bar new-extreme check (default 5)
combined with a close-in-weak-half-or-beyond-open test. Cheap, single-
bar, matches the source's own framing of it as a standalone signal
rather than requiring the next bar to confirm — distinct from most of
this repo's confirmation-before-entry discipline, flagged as such (see
H63 below).

### 11c. Built: minor time-rule bar-count watchlist
Distinct from the existing squares-1-to-19 watchlist (which is tied to
the MAJOR anchor and comes from Gann's own 1953 letter). This is a
different, source-quoted list of "minor" day-counts tied to the most
recent swing pivot: **7, 10, 14, 20-21, 28, 30 days** ("a minor change
occurs every..."), plus **45, 49 days** ("seven weeks or 49 days
usually marks the culmination of a rapid move... the 'seventh' period
from the beginning of anything is the most fatal"), plus **63, 66, 70,
84, 90** (from the Law-of-12 duration-of-moves list and the 7-to-10-week
cotton culmination rule). Implemented as a second bar-count watchlist,
tied to `lastPivotBar` (the swing tracker already used for the price/
time squaring detector) rather than the major anchor, matching the
source's own "from the beginning of ANY move" framing more closely
than the major-anchor-tied squares list does.

### 11d. NOT built — numbered trading/pyramiding/money-management rules
The course is dominated by numbered rule lists (Rules 1-8, the 29-rule
"Mechanical Method and Trend Indicator," the "Four/Five Rules" for
culminations, Rules for Eggs, 2-Day Chart Rules 1-8, the Cotton
16-point closing checklist, "Nine Mathematical Points"). These are
almost entirely **swing-chart-structure rules** (Trend Line / 2-Day
Chart / 3-Day Chart construction, double/triple top-bottom stop
placement, pyramiding triggers, breakaway points, sections-of-a-move)
— and this repo already has a substantial, independently-sourced
swing/structure-break family (IDM-gated BOS in the Alchemist engine,
strong/weak structural points in Pure PA/SMC, Dave's swing-maturity
count, MM Cycle's 3-tap fade). Gann's specific numeric thresholds
("10, 20, or 30 points," "5¢ a bushel," "$250 profit per pyramid add")
are commodity-and-decade-specific (1940s-50s grain/cotton/egg dollar
scales) and do not translate literally to XAUUSD in 2026 — logged as
**corroboration of the existing swing/structure-break family**, not
built as new code, per the same-mechanism-different-selection-criteria
treatment already used for that family. The STRUCTURE of a few of
these rules is genuinely distinct enough to flag on its own (see H62,
H64 below) even though the numeric thresholds aren't reusable:
- **"4th time at the same level" rule**: double/triple-tap fade logic
  already exists in this repo (MM Cycle, PBD, Wendell) but ALL of them
  treat the 3rd tap as the strongest signal; Gann's course explicitly
  says the reverse — "when an option reaches the same price level the
  FOURTH time, it nearly always goes thru and goes higher" — a 4th tap
  is read as breakout confirmation, not another fade opportunity. Flag
  as an open tension (H64), not adjudicated.
- **Half-way point (50% retracement) as the single most important
  support/resistance level**, ranked above 1/4, 1/3, 5/8, 3/4 points —
  corroborates the existing 50%-equilibrium marker (Pure PA/SMC, H44;
  also weakly corroborated by Gann's own 1953-letter "gravity center"
  note already logged) — third independent construction now.
- **Sections of a move**: campaigns run 3-4 "sections" (advance, halt,
  advance, halt, often culminating at the END of the 3rd section) —
  a specific, quotable version of the general "moves don't run forever,
  count the legs" idea; not separately built, logged as a documented
  but uncoded observation.
- Money-management sizing ("never risk more than 10% of capital on one
  trade," reduce size after consecutive losses) — already the stricter
  standard elsewhere in this repo (1-2% risk/trade per Pure PA/SMC and
  Forex James); Gann's 10% figure is looser than what's already adopted
  and is NOT a reason to loosen it — logged for completeness, not acted
  on.

### 11e. NOT built — time cycles and seasonal/anniversary dates
Extensive: Great Time Cycles (90/84/60/49-50/45/30/20-year), Minor
Time Cycles (13/10/7/5/3/1-year), the Law of 12 duration-of-moves
table (culminations cluster at multiples of 12 months), and detailed
COMMODITY-SPECIFIC seasonal calendars:
- Grains: Dec 21, Feb 5, [Mar 21], May 5, Jun 21, Aug 5, Sep 21, Nov 8
  (8 roughly-45-day divisions of the year) — "the most important
  changes in Grains occur during FEBRUARY, MAY, AUGUST and NOVEMBER."
- Cotton: planting (Mar-May, esp. Apr 6-17/May 5-10), maturity
  (Aug-Sep), harvest (Aug-Dec) — "**September 6-20 is the most
  important change of trend in the year**... December 10-15 MOST
  IMPORTANT" (final crop estimate/seasonal low).
- A 13-year cycle singled out as unusually reliable for cotton/wheat
  specifically because of multi-year crop-cycle effects.

None of this is built. Reasoning: this entire category is explicitly
agricultural-commodity seasonal behavior (planting/harvest/crop-report
timing) with NO mechanical analogue for a 24/7-traded, non-seasonal
metal like gold, and the year/decade-scale cycles are far too coarse
for 5m scalping in any case. Preserved verbatim here per the
never-discard standing rule in case a future source ties any of this
to gold-specific seasonality (which does exist — e.g. gold's own
central-bank-buying and jewelry-demand seasonal patterns — but this
source doesn't address gold at all, so applying its grain/cotton
calendar to gold would be pure fabrication).

### 11f. NOT built — Hexagon Chart, Master 12/144 charts, custom-modulus squares
The course describes THREE further distinct geometric constructions
beyond the spiral Square of Nine already in section 1-10 above, all
genuinely new relative to the TradingFives book:
- **The Master "12" Chart (Square of 144)**: a flat grid 1-144 (then
  145-288, 289-432...), with explicit strongest/weakest resistance
  number lists (major centers 66/67/78/79; minor centers 14/17/20/23/
  50/53/56/59/86/89/92/95/122/125/128/131) and diagonal 45°-angle
  number sequences.
- **The Hexagon Chart**: concentric numbered rings around a center
  "1," each ring gaining a larger increment than the last (6, 12, 18,
  24...), producing ring-boundary numbers 1, 7, 19, 37, 61, 91, 127,
  169, 217, 271, 331, 397. 127 = "the first Hexagon" (10yr 7mo); 397 =
  a full "cube." A 20-year cycle is mapped onto the hexagon's 6 faces
  at 60°/5-year intervals.
- **Custom "commodity's-own-number" squares**: build a square/circle
  modulus out of a commodity's OWN historic extreme price (Square of
  44 and 67 for soybeans off its own all-time lows; Square of 28 for
  wheat off its 1852 low) — and, more idiosyncratically, off a
  **letter-count of the security's NAME** (Square of 289 = 17² for
  "United States Steel," 17 letters; Square of 49 or 441 for "America"/
  "United States of America," 7 or 21 letters). The letter-count
  technique in particular has no defensible mechanism and is preserved
  here purely as a documented Gann idiosyncrasy, not a candidate for
  implementation under any circumstance.

None of these are built. All three are far more elaborate than the
already-implemented spiral rotation formula, require substantial new
Pine geometry work for uncertain payoff (numerology-heavy, no
falsifiable trigger clearly distinguishable from the existing squares-
1-19 watchlist's spirit), and the letter-count technique specifically
fails this project's "no fabricated mechanics" bar outright. Flagged
for reconsideration only if a future source gives a cleaner,
falsifiable trigger built on one of these constructions.

### 11g. NOT built — astrological forecasting content
Chapter 8 (Soy Beans) and Chapter 20 (May Coffee) contain extended
Heliocentric/Geocentric planetary-longitude calculations (Jupiter,
Saturn, Uranus, Neptune, Mars, Pluto positions converted to price via
various points-per-degree scales) presented by Gann as part of his
forecasting method. Authentic Gann material, not garbled — but
astrological rather than technical/chart-based, no falsifiable
mechanism, and outside this project's scope regardless of source
credibility. Preserved as a documented fact about the source (Gann
genuinely used this) but explicitly not evaluated or built.

### 11h. Confirmed / corroborated, no change needed
- The "5 ways price squares with time" already documented (section 4
  above) is corroborated, with Chapter 14's own separate "3 ways to
  square or balance time and price" list being a narrower, later
  (1955) restatement — not a contradiction, just a shorter enumeration
  from a different chapter/date. No change to the existing 5-way list.
- The squares-1-to-19 watchlist (section on Gann's 1953 letter) is
  independently repeated in this course almost verbatim ("1-4-9-16-25-
  36-49-64-81-100-121-144-169-196-225-256-289-324-361") — same list,
  now doubly source-confirmed within Gann's own writing.
- The Cardinal Cross (90/180/270/360°) / Fixed Cross (45/135/225/315°)
  terminology and strength-ranking is Gann's own coinage, used
  identically across multiple chapters of this course — already
  implicitly present in the existing engine's degree-factor logic, now
  given its proper name and explicit ranking (90 > 180 > 270 > 360 >
  120/240 > 45/135/225/315 > 22.5/67.5/78.75°). Documentation-only
  update, no code change (the engine doesn't rank angle importance by
  degree currently, and doesn't need to for its current scope).

## Belief-register hypotheses from this section: H62-H64 (see
BELIEF_REGISTER.md).

---

## Audit pass against both original sources (2026-07-22)
Re-read the full 57-page PDF (including the scanned 1953 appendix) plus
targeted spot-checks of the Master Commodities Course text file. Core
formulas (rotation, Futia degrees, reverse formula, degrees-to-factor
table down to 45 deg) all verified correct. Seven gaps, all omissions —
no wrong formulas or fabricated numbers found:

- **Missing — 22.5 deg = .125 base entry** in the degrees-to-factor table.
- **Missing pivot categories**: major-pivot list only keeps all-time/
  52-week/contract highs-lows; source's 10-year and 5-year high/low
  categories were dropped.
- **Missing chapter — "Squaring Price with Price"**: an entire static,
  time-free support/resistance method off major pivots is absent.
- **Missing practice — dual pivot calculation**: source says to calculate
  every major pivot TWICE (extreme vs. close) and to maintain both a
  high/low chart and a close chart in parallel; not captured.
- **Missing — alternate time-grid methods**: only one vertical time-grid
  method is implemented; source describes two further "more precise"
  time-spacing variants.
- **Missing — numeric "lost motion" tolerances**: source gives specific
  cutoffs (1-2 bar near-miss for time; 2-3 deg hit / 4-5 deg near-miss for
  price-time squaring) that got compressed into vague language.
- **Overgeneralized — the "2-consecutive-close" channel-breach rule**:
  presented in this playbook as the book's general standard, but the
  source only applies it in one specific worked hourly example; the
  book's actual general rule carries no fixed bar-count.

Verified accurate: 5-ways-price-squares-time list, Gann Angle Fan
mechanics, Signal Day, Square of 44/67/28, Hexagon, and the "United
States Steel" letter-count square (all cross-checked against the Master
Commodities Course text). Not yet ported to the engine.
