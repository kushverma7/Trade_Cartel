# Intermarket Lead-Lag Trading (voice #17)
Source: "The Big Secret of Intermarket Trading" — a short (7-page) free
PDF, unattributed author, hosted as a lead-gen funnel for an external
"learn-forex" site (footer: "to learn the best methods... I highly
recommend reading the following book: http://learn-forex.awardspace.us").

**Credibility tier: LOW.** Explicit "100% profitable trading
opportunities" and "100% winning trades" language — a hard red flag
phrase this project treats as disqualifying for any claim taken at
face value. Zero track record, zero statistics, and every "example"
in the PDF is a static screenshot with SELL/BUY arrows and cyan boxes
drawn AFTER the move already happened — hindsight annotation, not a
demonstrated forward rule. The text labels describing which two
instruments are being compared don't even reliably match the
screenshots underneath them (page 4's text says "S&P500 leading
gold," the actual image is SPX500 vs. "US Dollar Index" — likely a
templated document with copy-pasted captions, not carefully
proofread). Treat this source as "gestures at a real, known technique
without ever specifying one" rather than as a usable method in itself.

## The underlying idea (real, just not rigorously presented here)
Cross-asset lead-lag correlation trading is a legitimate, well-known
technique (classical intermarket analysis, e.g. John Murphy's work):
when two instruments are reliably correlated (or anti-correlated) but
one tends to move first, a lag/discrepancy opens up where the
"leading" instrument has already moved and the "lagging" one hasn't
caught up yet. The source's claimed examples: USD/JPY leads
NASDAQ100/crude oil (lag ~1-3h), DXY leads S&P500 (lag ~1h), S&P500
leads gold (lag 1-2h, negative correlation), gold vs. FTSE (lag ~20h,
negative correlation). None of these specific lag durations are
independently verified here — they're asserted, not measured, and are
presented on 1H forex-broker demo charts from what appears to be a
single week in May of an unstated year.

## What's built — our own operationalization, not the source's method
The source gives NO actual trigger rule (just "overlay the charts and
wait until a lag occurs," then retroactively boxes examples). Rather
than encode that non-method, this engine builds the sober version of
the same underlying idea, with a safeguard the source itself never
uses:
1. **Rolling correlation gate**: compute `ta.correlation()` between
   XAUUSD's returns and a reference asset's returns (default DXY,
   inverse — matches the source's own claimed gold/dollar-index
   negative correlation and is the most liquid, always-available
   reference). Only consider a "lag" real when the rolling correlation
   magnitude is currently above a threshold (default 0.5) — i.e., the
   relationship must be ACTUALLY HOLDING right now, not just claimed
   to generally exist. The source never checks this; every one of its
   "examples" could equally be cherry-picked periods where the
   correlation happened to be strong that week.
2. **ATR-normalized catch-up gap**: over a lag window (default 6
   bars), measure how many ATRs the reference has moved vs. how many
   ATRs gold has moved. When the reference has moved further than gold
   (after adjusting for the inverse relationship) by more than a
   threshold, AND the correlation gate is active, flag a "catch-up"
   signal in the direction the reference implies gold should still
   move.
3. This is DELIBERATELY a confluence/observation signal, same as
   everything else in this repo — not a standalone trigger, and
   explicitly not carrying the source's "100%" framing anywhere into
   the implementation.

## What's NOT built
- No attempt to reproduce the source's specific claimed lag durations
  (1h, 3h, 20h, etc.) as fixed parameters — they're asserted from a
  handful of hindsight screenshots, not measured, and hard-coding them
  would be fabricating precision the source doesn't actually have.
  `lagWindow` is a user input instead, default a round number.
  Optional TODO(measure): once this project has functioning historical
  backtesting on this engine, empirically measure XAUUSD's own typical
  lag vs. DXY/SPX rather than trusting the source's numbers.
- No multi-reference version (source claims USD/JPY, NASDAQ100, DXY,
  crude oil, S&P500, FTSE all have cross-lag relationships with each
  other) — only one reference asset at a time is implemented, keep
  the mechanic legible rather than building a 6x6 correlation matrix
  on a single pass through unverified source material.
- The "100% winning" framing itself is not preserved anywhere except
  as a documented fact about the source (i.e., "the source claims
  this," not "this is true").

## Register impact
Genuinely new mechanism — nothing else in this repo does rolling
cross-asset correlation-gated lag detection. Closest existing concept
is SMT divergence (Quarterly Theory, quarterly_theory_engine.pine):
SMT checks whether a correlated asset FAILS TO CONFIRM a sweep at a
specific moment (a snapshot comparison); this is a CONTINUOUS
rolling-correlation + magnitude-gap comparison instead, structurally
different even though both compare gold against a reference asset.
Not corroboration of SMT, not a duplicate — a different mechanism
answering a related but distinct question.

## Engine
indicators/intermarket_lag_engine.pine — rolling correlation gate
(`ta.correlation`) between gold and a reference symbol (default DXY,
inverse), ATR-normalized catch-up gap detector over a configurable
lag window, catch-up long/short signal + alerts. Bar-close,
non-repainting (uses `request.security` with default lookahead
behavior on already-closed reference-symbol bars, consistent with the
SMT reference pattern already used in quarterly_theory_engine.pine).
