# SKILL REGISTRY
Index of reusable, code-reviewed Pine patterns, per
SKILL_EXPANSION_FRAMEWORK.md Part I. Reference by name; do not rewrite.

**Honest validation note:** the framework's validation bar is "works on
3+ assets, 3+ timeframes." None of these patterns has had that formal
cross-asset test run yet — status below says exactly what each has
actually survived (code review, live XAUUSD 5m chart use, or a caught
bug that shaped it). Upgrading a status requires actual test evidence,
same as every other claim in this repo.

| Skill | File | Purpose | Validation Status | Used By | Related Bugs |
|-------|------|---------|-------------------|---------|--------------|
| Responsive Swing / BOS | swing_detection.pine | Real-time break of prior N-bar high/low, no pivot lag | Code-reviewed; born from BUG-008 fix; live XAUUSD 5m use pending re-test | amdm engines | BUG-008 |
| Safe Array Loop | safe_arrays.pine | Empty-array guard + bounds-checked access | Survived 2 real bug fixes (BUG-001); in use across 5+ engines | hima_reddy, spaceman_yotov, others | BUG-001 |
| Anti-Repaint Idioms | anti_repaint.pine | Confirmed-bar signals, HTF security refs, top-level ta.* calls | In use across all engines this project ships | all engines | BUG-004 |
| Cooldown State Machine | (inline pattern, see anti_repaint.pine §3) | One-signal-per-N-bars + price-distance re-arm | Live-tested through 3 iterations on XAUUSD 5m (see BUG-006) | topbottom, amdm | BUG-006 |
| Sweep-Stop Placement | (inline pattern, see swing_detection.pine §2) | Stop beyond the sweep bar's actual wick extreme + ATR buffer | Live-tested: fixing this took PF-analog 0 -> non-zero (BUG-005) | spaceman_daye, amdm, topbottom | BUG-005 |
| Rolling Volume Profile | (lives in trader_dale_volume_profile_engine.pine + amdm engines) | VAH/VAL/POC from a rolling window, ~O(window) per bar | In live use in 3 engines; perf claim of "toxic" reviewed and rejected (see PLAYBOOK round-2 entry) | trader_dale, amdm | — |
| TP1/TP2/SL Hit Tracker | (inline pattern, standard across engines) | Signal-anchored TP/SL lines + never-same-bar hit counters + PF-analog | In live use across 6+ engines; the project's standard results dashboard | most engines | — |

## How to add a skill
Follow SKILL_EXPANSION_FRAMEWORK.md Part I steps 1-4. A skill enters
this table with its REAL validation status — "extracted, untested" is
an acceptable status; an inflated one is not.
