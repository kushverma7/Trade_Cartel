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
