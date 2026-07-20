# Gann Square of Nine (voice #16)
Source: "Trading the Gann Square of Nine" (TradingFives.com, June 2003) — 57
pages, includes an appendix reproducing W.D. Gann's own 1953 typed/signed
notes on the Square of Nine / Master Square of 144 ("original works of
W.D. Gann made available for general use"). Read cover-to-appendix
(text) AND every embedded chart/diagram image (pypdf text extraction
alone would have missed the appendix — it's a scanned facsimile of
Gann's original letter, garbled to ~12 chars/page as plain text; the
rendered page images (via pymupdf) were read directly to recover it).

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
