# Supplied Pine originals, archived verbatim

These are the scripts **as supplied**, kept unedited so every audit in this
branch can be re-run against the exact text it examined. Do not "fix" them here
— corrections live as separate files.

| file | audited in | verdict |
|---|---|---|
| `gold_10am_quarter_matrix_v1_AS_SUPPLIED.pine` | PR #7 Phase 7 | **BUG-047** — `tradedToday` set inside the entry block, so the quarter filter is a search. 117 trades at PF 1.321 against the documented rule's 60 at 1.638. Corrected version committed as `strategies/gold_10am_quarter_matrix_v2.pine`. |
| `../../microq3/pine/micro_q3_smoother_v1.pine` | PR #7 Phase 13 | **BUG-047 again**, independently. 45 trades at PF 2.149 against the reference's 34 at 2.869. Audit: `research/microq3/PINE_SMOOTHER_AUDIT.md`. |

Recovered from the session transcript on 2026-08-23 — v1 had been superseded by
the committed v2 without the original ever being archived, so the Phase 7 audit
could not be reproduced against its own subject.
