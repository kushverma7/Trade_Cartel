# Blind-chart methodology audit
Run at chart 069 of 120, mid-experiment. **Touches no classification.**

## Why this audit does not cover the recorded answers

The classifications in `MANUAL_RESPONSES.md` are the USER's, entered chart by
chart. Claude has classified nothing in this experiment. There is no prior
Claude classification to re-audit, and no ChatGPT classifications have been
supplied in the conversation.

Auditing the user's answers mid-run would also break the experiment: the design
is zero feedback until all 120 are locked, and the user's own instruction was
"do not analyse patterns in my decisions while the test is running". Telling the
participant which answers look wrong, or reporting the L3/S3 distribution, is
feedback. It would bias charts 069-120 and permit revision of 001-068, which
destroys the pre-registration.

## Technical checks — all pass

| check | result |
|---|---|
| Last drawn bar equals the Logic A entry candle | 0 failures / 120 |
| Renderer can receive a post-decision bar | impossible by construction: filter is `CTX_START <= m <= entry_m` |
| 09:50 open and 10:00 body recomputed from raw bars | 0 mismatches / 120 |
| Body definition | `max/min(open, close)` of the 10:00 candle; wicks unused, as specified |
| Timezone | per-bar UTC to `zoneinfo` Australia/Melbourne; AEDT and AEST both observed in the sample; no fixed offset |
| Y-axis scaling | limits from drawn bars only; no future range can influence the scale |
| Era leak | axis is points from the 09:50 open, so the absolute index level is hidden |
| Answer key isolation | `touch20`, `mfe`, `mae`, `date` never passed to the renderer |

## One residual, disclosed rather than fixed

Chart width varies with entry time (10:05 to 14:40), so a wide chart reveals a
late entry. This is information available AT the decision point - how long the
setup took to trigger - not future information. Standardising the width would
require padding, which would itself be a visual artefact. Left as is, recorded
here.

## The classification scale

No formal L1/L2/L3 rubric was ever defined in this project, deliberately. The
scale is direction plus the participant's own confidence, and the experiment
tests that unaided judgement. Imposing a rubric now would change what is being
measured, mid-measurement.

## Items 8-10, completed

**8. OHLC integrity — PASS.** 947 drawn 5-minute bars rebuilt independently from
the raw 1-minute Dukascopy file and compared to the bars actually rendered.
Zero mismatches.

**9. Sample selection — PASS.** 120 drawn uniformly, seed 20260819, from 1,232
eligible Logic A days. Against the 1,112 not drawn: 10:00 body size p=0.412,
10:00 range p=0.504, entry time p=0.758, all representative. Year spread
chi-square 4.87 on 7 df, no year over-represented. Per-year counts and the
direction balance are deliberately withheld while the test runs, since either
could steer the remaining answers.

**10. Response file — PASS.** 68 rows, ids strictly increasing, zero duplicates,
no gaps in 001-068, zero malformed rows. Next chart 069. Answer values not
printed.

**1. Source books.** Not part of this experiment's methodology, and that is
deliberate. The MANUAL VISUAL TEST measures unaided visual judgement; no book
rule is applied, encoded or shown. The candlestick playbook was used only in the
earlier, separate classifier experiment, whose answers are excluded here.

## Verdict

No data or methodology flaw found. The blind-test infrastructure passes.
