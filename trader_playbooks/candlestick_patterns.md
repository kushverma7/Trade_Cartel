# Candlestick Playbook — Source Rules for the Real-Time Engine

Each entry: mechanical definition → context requirement → what confirms it.
Every pattern here is implemented in `indicators/candlestick_engine.pine`
and prints + alerts in real time on bar close.

Reliability tiers (from Bulkowski's quantified testing, honest ranking):
- **A** = statistically meaningful edge with confirmation
- **B** = works only with strong context (trend + location)
- **C** = popular but near coin-flip; included for completeness, off by default

## Reversal patterns (bullish)

| Pattern | Definition (mechanical) | Context required | Tier |
|---|---|---|---|
| Hammer | lower shadow >= 2x body; upper shadow <= 25% of range; body in top third | downtrend, at/near swing low | B |
| Bullish Engulfing | bear candle then bull candle whose body engulfs prior body | downtrend | A |
| Piercing Line | bear candle, then bull candle opening below prior low, closing above prior body midpoint | downtrend | B |
| Morning Star | big bear body, small body gapping/holding lower, bull body closing into first candle's body | downtrend | A |
| Bullish Harami | big bear body, then small body inside it | downtrend | C |
| Tweezer Bottom | two candles with (near-)equal lows, second closes bullish | downtrend, at support | C |
| Three White Soldiers | three consecutive bull bodies, each closing near its high, opens within prior body | after decline | A |

## Reversal patterns (bearish)

| Pattern | Definition (mechanical) | Context required | Tier |
|---|---|---|---|
| Shooting Star | upper shadow >= 2x body; lower shadow <= 25% of range; body in bottom third | uptrend, at/near swing high | B |
| Bearish Engulfing | bull candle then bear candle whose body engulfs prior body | uptrend | A |
| Dark Cloud Cover | bull candle, then bear candle opening above prior high, closing below prior body midpoint | uptrend | B |
| Evening Star | big bull body, small body gapping/holding higher, bear body closing into first candle's body | uptrend | A |
| Bearish Harami | big bull body, then small body inside it | uptrend | C |
| Tweezer Top | two candles with (near-)equal highs, second closes bearish | uptrend, at resistance | C |
| Three Black Crows | three consecutive bear bodies, each closing near its low, opens within prior body | after advance | A |

## Indecision / warning

| Pattern | Definition | Meaning | Tier |
|---|---|---|---|
| Doji | body <= 10% of range | trend exhaustion warning at extremes only | C alone, B at swing + trend |

## Nison's context rules (implemented as filters, not suggestions)

1. **Trend prerequisite**: a reversal pattern requires a trend to reverse.
   Engine: EMA(20) slope + close position over last `trendLen` bars.
2. **Location**: patterns matter at swings. Engine: within `locAtr` x ATR of
   the highest high / lowest low of the last `swingLen` bars.
3. **Confirmation**: optional next-candle confirmation (close beyond the
   pattern's extreme) — halves the signals, roughly doubles the quality.
4. **Size matters**: engulfing/star bodies must be >= `bigBody` x average
   body to exclude noise candles.

## v2 additions — "@Thechartcornerr" chart pattern cheat sheet (2026-07-20)
Source: visual-only PDF cheat sheet (Instagram-style account), names
and pattern shapes only -- no numeric criteria extractable (images
carry the actual geometry, text layer has labels only). Public-domain
classical TA, same treatment as the original Nison-derived table above:
apply well-established mechanical definitions to the named patterns.
No new context rules; same trend/location/confirmation filters apply.

## Reversal patterns (bullish) — additions

| Pattern | Definition (mechanical) | Context required | Tier |
|---|---|---|---|
| Inverted Hammer | same shape as Shooting Star (upper shadow >= 2x body, small/no lower shadow) | downtrend, at swing low | C |
| Dragonfly Doji | doji body, upper shadow <= 10% of range, lower shadow >= 60% of range | downtrend, at swing low | C |
| Bullish Spinning Top | small body (<=30% of range), both shadows roughly equal and substantial (each >=25% of range) | downtrend, at swing low | C |
| Bullish Marubozu | body >= 90% of range (near-zero shadows), bull | works as a momentum/strength candle anywhere; stronger at a breakout | B |
| Bullish Long-Legged Doji | doji body, BOTH shadows long (each >= 35% of range) | downtrend, at swing low | C |
| Bullish Kicker | bear (or flat) candle, then a bull candle whose LOW opens above the prior candle's HIGH (zero body overlap) | any -- rare, self-confirming by the gap | A |
| Rising Three Methods | big bull body, then 3 small candles (any color) staying within that body's range, then a bull candle closing above the first candle's high | uptrend continuation (mid-trend, not at a swing extreme) | B |
| Three Inside Up | bear candle, smaller bull candle inside it (harami), then a third bull candle closing above the first candle's open | downtrend, at swing low | B |
| Three Outside Up | bear candle, bull engulfing candle, then a third bull candle closing above the engulfing candle's close | downtrend, at swing low | B |

## Reversal patterns (bearish) — additions

| Pattern | Definition (mechanical) | Context required | Tier |
|---|---|---|---|
| Hanging Man | same shape as Hammer (lower shadow >= 2x body, small/no upper shadow) | uptrend, at swing high | C |
| Gravestone Doji | doji body, lower shadow <= 10% of range, upper shadow >= 60% of range | uptrend, at swing high | C |
| Bearish Spinning Top | small body (<=30% of range), both shadows roughly equal and substantial | uptrend, at swing high | C |
| Bearish Marubozu | body >= 90% of range (near-zero shadows), bear | works anywhere; stronger at a breakdown | B |
| Bearish Long-Legged Doji | doji body, BOTH shadows long (each >= 35% of range) | uptrend, at swing high | C |
| Bearish Kicker | bull (or flat) candle, then a bear candle whose HIGH opens below the prior candle's LOW (zero body overlap) | any -- rare, self-confirming by the gap | A |
| Falling Three Methods | big bear body, then 3 small candles staying within that body's range, then a bear candle closing below the first candle's low | downtrend continuation (mid-trend) | B |
| Three Inside Down | bull candle, smaller bear candle inside it (harami), then a third bear candle closing below the first candle's open | uptrend, at swing high | B |
| Three Outside Down | bull candle, bear engulfing candle, then a third bear candle closing below the engulfing candle's close | uptrend, at swing high | B |

## Corroboration — "Everything You Wanted to Know About Candlestick Charts"
(Mark Rose, Thames Publishing/Trader's Bulletin, 2026-07-20 supplied). Covers
Doji, Marubozu, Harami (bull/bear), Hammer/Hanging Man, Inverted Hammer/
Shooting Star, Engulfing (bull/bear), Morning/Evening Star, Three White
Soldiers/Black Crows, Piercing Line/Dark Cloud Cover -- the exact same core
pattern set already built (candlestick_engine.pine), no patterns outside
what's already implemented. NOT a new voice, NOT a new file -- logged here
as corroboration per the same-subject/no-new-mechanics rule.

Two genuinely useful confirmations, not new mechanics:
- **Hammer/Shooting Star wick ratio, independently stated**: "the lower
  [upper] wick should be at least two times longer than the body" --
  matches `shadowMult` default (2.0) already used in
  candlestick_engine.pine exactly. Now corroborated by a second,
  independent source (this book + the original cheat sheet), not just an
  arbitrary default -- raises confidence in that specific threshold.
- **Harami reliability caveat, explicit**: "a harami doesn't always live
  up to its hype... often several days of tight-range consolidation will
  follow... best to look for confirmation and combine with other
  longer-term patterns" -- independent restatement of this repo's
  dominant confirmation-before-entry family (now the strongest idea in
  the register, 8+ independent sources) applied specifically to the
  Harami pattern. Consistent with `en_harami` already defaulting to
  OFF in candlestick_engine.pine (weaker tier-C pattern) -- this source
  explains WHY that default is justified, not just that it should be.

No new H-number, no engine changes -- nothing here contradicts or extends
what's built.

## Pending: material from user (book chapters, trader transcripts)

Every new scenario from supplied material gets:
1. an entry in this file (definition -> context -> confirmation)
2. a module in the engine (label + alertcondition, bar-close evaluation)

---

## CLASSIC CHART PATTERNS (multi-swing geometric patterns)
Source: same "@Thechartcornerr" cheat sheet. Distinct category from
candlesticks (single/few-bar) -- these are built from pivot-confirmed
swing sequences over many bars. Public-domain classical TA (Edwards &
Magee / Bulkowski lineage), implemented in
indicators/chart_pattern_engine.pine (new file -- distinct source/
subject from the candlestick engine, not an extension of it).

### Implemented (well-defined swing geometry)
| Pattern | Definition | Signal |
|---|---|---|
| Double Top | two pivot highs within a tolerance band, separated by a pivot low (the "neckline") | short on neckline break |
| Double Bottom | mirror: two pivot lows within tolerance, separated by a pivot high | long on neckline break |
| Triple Top | three pivot highs within tolerance | short on neckline break |
| Triple Bottom | mirror | long on neckline break |
| Head & Shoulders | three pivot highs, middle one clearly the highest, neckline connects the two troughs between them | short on neckline break |
| Inverse Head & Shoulders | mirror (middle pivot low is the lowest) | long on neckline break |
| Ascending Triangle | flat resistance (pivot highs within tolerance) + rising support (higher pivot lows) | long on resistance break |
| Descending Triangle | flat support + falling resistance (lower pivot highs) | short on support break |
| Symmetrical Triangle | converging trendlines, one rising from higher lows, one falling from lower highs | breakout direction = signal direction |
| Rising Wedge | both trendlines rising, converging (compressing range while still climbing) | typically resolves DOWN (bearish) despite the up-slope |
| Falling Wedge | both trendlines falling, converging | typically resolves UP (bullish) despite the down-slope |
| Bull/Bear Flag | sharp impulse ("pole") followed by a short, roughly-parallel counter-sloped channel | breakout continues the pole's direction |
| Bull/Bear Pennant | sharp impulse ("pole") followed by a short converging-triangle consolidation | breakout continues the pole's direction |
| Bull/Bear Rectangle | horizontal channel (flat top AND flat bottom) | breakout direction = signal direction |
| Cup & Handle | two similar-height pivot highs ("rims") separated by a wide/deep trough, then a short shallow secondary dip at the rim (the "handle") [v3] | long on rim break |
| Inverted Cup & Handle | mirror (two similar-height pivot lows under a wide/deep arch, shallow handle) [v3] | short on rim break |
| Diamond Top / Diamond Bottom | broadening (expanding highs/lows) immediately followed by a narrowing symmetrical triangle, sharing the widest point [v3] | breakout direction = signal direction |

### v3 additions — re-review of BOTH source PDFs' page IMAGES, not just
their text (2026-07-20). The original text-extraction passes for this
project's very first chart-pattern source ("@Thechartcornerr" cheat
sheet) and the Josh Trade ebook had not rendered every page image --
doing so now surfaced real content the text alone missed.

**Cup & Handle / Inverted Cup & Handle -- RECLASSIFIED from "not
implemented" to implemented.** The cheat sheet's own diagram (not
described in its text/labels, only visible in the picture) shows the
handle as a second, SHALLOWER rounded dip sitting right at the rim --
not a straight-line pullback as assumed when this was first flagged
"too subjective." This is concrete enough to build the same way every
other pattern in this file is built: width/depth minimums standing in
for "rounded," the same treatment `headMinAtr` already gives to
"prominent" on Head & Shoulders. Implemented in
indicators/chart_pattern_engine.pine v3: two rim pivots within
tolerance, separated by >= `cupMinBars` bars and >= `cupMinAtr` x ATR
of depth (distinguishes a genuine cup from a quick double-top/V-shape),
followed by a handle window (`handleMaxBars`) that doesn't give back
more than `handleMaxRetrace` of the cup's depth, then a breakout
through the rim. Still a heuristic proxy with no source-given numeric
thresholds (same caveat as every pattern here) -- test standalone.

**Diamond Top / Diamond Bottom -- RECLASSIFIED from "not implemented"
to implemented.** Same discovery: the diagram shows this explicitly as
a broadening (expanding highs/lows) formation immediately chained into
a symmetrical (contracting) triangle at its widest point -- i.e., two
already-partially-understood shapes glued together, not a genuinely
novel geometry. Implemented by chaining the engine's existing
pivot-slope classifier: the OLDER half of the tracked pivots must
broaden (each subsequent high higher, each subsequent low lower), the
NEWER half must narrow (matching the existing symmetrical-triangle
slope logic exactly), breakout direction (not the shape itself, same
as symmetrical triangle) determines Diamond Top (bearish break) vs
Diamond Bottom (bullish break). Needs 6 tracked pivots per side
(`maxPiv`, default 6) to see both the broadening and narrowing halves.

The Josh Trade ebook itself (re-reviewed in full via its own page
images, all 34 pages) does NOT contain Cup & Handle or Diamond
material at all -- confirmed absent, not missed. Its images did reveal
two other genuinely new things, folded into the v2 section below
retroactively as "v3" additions since they were found in the same
re-review pass:
- **Fixed risk:reward targets, anchored at the RETEST bar, not the
  breakout bar.** Nearly every one of the ebook's real-chart worked
  examples shows a small labeled risk box (entry to just past the
  retest bar's opposite extreme) stacked against a larger reward box,
  explicitly labeled with a ratio -- overwhelmingly **1:3** (8 of 9
  labeled examples), once **1:4** (Descending Triangle). This is a
  materially different target methodology than the v2 measured-move
  (pattern-height) projection already implemented -- added as an
  OPTIONAL alternate (`showRR`, default off, `rrMult` default 3.0) so
  the two methodologies can be A/B tested against each other rather
  than one silently replacing the other.
- **Head & Shoulders "high-probability" filter (page 25 text, precise
  and quotable)**: "The possibility of breakdown increases if the
  slope of the neckline is flat to downward sloping and the right
  shoulder is relatively smaller or equal to the left shoulder."
  Directly implementable and not previously checked by the engine
  (which only verified head prominence over both shoulders). Added as
  an `hnsHighProb` flag shown in the H&S signal's label/tooltip --
  informational tag, does not gate the signal itself, since the source
  frames it as a probability modifier, not a hard requirement.
- The previously-flagged unclear "0.382 Fibo Retracement" detail on
  the Descending Triangle page is now understood more precisely (the
  post-breakdown retest zone into former support, now resistance, sits
  around the 0.382 retracement of the down-leg) but the exact anchor
  points for the fib measurement remain ambiguous -- still not built,
  the existing ATR-based retest tolerance is judged adequate for the
  same purpose without guessing at unstated anchor points.

### v2 additions — "Josh Trade"/Suraj Saini ebook (2026-07-20)
Same 13 patterns, same public-domain classical TA -- extended the
existing engine in place rather than forking a new file. Genuinely
new detail this source adds:
- **Measured-move price targets, explicit for symmetrical triangles**:
  "price target = distance from the high and low of the earliest part
  of the pattern, applied to the breakout price point." Generalized
  to every pattern (double/triple top-bottom, H&S use extreme-to-
  neckline height; triangles/wedges/rectangles use the tracked
  boundary height; flags/pennants use the pole length) -- simplified
  from "earliest part of the pattern" to "current tracked boundary
  height" for implementation robustness, noted in-code.
- **Volume confirmation emphasized repeatedly** for breakouts
  (descending triangle, H&S, both explicitly). Added as an OPTIONAL
  filter, default OFF -- gold/forex "volume" on most feeds is tick
  count, not real traded volume, so this is a proxy at best.
- **Neckline/boundary retest behavior**: "post breakdown... there may
  be a possibility of retest to the neckline" (H&S), similarly implied
  for double top/bottom and rectangles via page diagrams. Added as
  retest tagging within a configurable window after breakout -- a
  secondary, often tighter-risk entry than chasing the breakout candle.
- One unclear detail preserved, not built: several pattern diagrams
  show "1-3" and Fibonacci-percentage labels (e.g. "0.382 Fibo
  Retracement") suggesting entries on a retracement into the pattern
  after breakout rather than at the breakout candle itself, but the
  extracted text doesn't explain the exact ratio/rule clearly enough
  to implement without guessing -- flagged per standing rule.
- "Bearish trap" noted on the bullish pennant page (a fakeout in the
  counter direction before the real breakout) -- informal corroboration
  of the already-dominant sweep-reversal family (8+ sources), not
  logged as a new H-number given how thin the source detail is.

---

## Audit pass against all three original sources (2026-07-22)
Re-read the candlestick book (Mark Rose), the PriceActionPatterns20
ebook, and the Chart Pattern Cheat Sheet PDF in full.

- **Missing — Entry/Stop/Target placement convention**: every single page
  in the cheat sheet (candlestick pages 3-10, chart-pattern pages 11-34,
  shared with the ebook) diagrams a consistent convention: Entry at the
  breakout/confirmation candle's extreme, Stop-Loss at the pattern's
  opposite extreme, Target projected beyond. This playbook's note that
  the cheat sheet has "no numeric criteria extractable" is true for wick
  ratios but overlooks that this entry/stop/target geometry IS
  consistently extractable, unlike the wick percentages — a real,
  non-trivial gap, not yet flagged as "not implemented" either.
- **Possibly misread — 0.382 Fib anchor**: the descending-triangle page's
  "0.382 Fibo Retracement" label was read as marking the post-breakdown
  retest zone. Re-checking the page, it more plausibly marks the
  pre-breakdown consolidation/triangle-support relative to the prior
  down-leg (i.e. where the triangle itself formed). Flagged as still
  ambiguous, not corrected outright.
- **Minor — Rising Wedge's dual treatment**: the ebook presents it twice —
  once as a bearish REVERSAL (uptrend, p.17), once as a bearish
  CONTINUATION (explicitly "in the downtrend," p.27). Both resolve
  bearish so the single "typically resolves DOWN" line isn't wrong, but
  the context-dependent framing (reversal vs. continuation) isn't noted.

Verified accurate: all Mark Rose book definitions and reliability
language (Morning/Evening Star tier A; harami unreliability; piercing/
dark-cloud tier B vs engulfing tier A; 2x wick ratio for hammer/shooting
star), the cheat sheet's shape/name inventory, H&S "high-probability"
quote, symmetrical-triangle measured-move quote, volume-confirmation
notes, 1:3/1:4 R:R tallies. Confirmed `indicators/chart_pattern_engine.
pine`'s own header holds no separate hidden text content. Not yet
ported to the engine.
