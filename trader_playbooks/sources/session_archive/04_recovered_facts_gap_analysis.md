# Gap analysis — what the recovery found that the repo had lost

Method: every concrete claim in the recovered summaries and user turns was
grepped against `MEMORY.md`, `PLAYBOOK.md` and `BELIEF_REGISTER.md`.

## 1. The exact configuration of the repo's first PF>1 result — WAS MISSING

`trade_cartel_topbottom_engine.pine` reached **PF-analog 1.11**, the first
above-1 result before the multi-voice engine. The settings that produced it
were described in the recovered summary but existed **nowhere in the repo**:

```
useTestFail   = false     (sweep-only; the Hima test-failure path OFF)
closePosPct   = 0.2       (tightened from 0.35)
rsiOb         = 72        (tightened from 66)
rsiOs         = 31        (tightened from 34)
useTrendVeto  = false     (input label warns: made PF worse on the last run)
cooldown      = 20
minReArmAtr   = 1.5
```

User confirmation of these, verbatim: *"oversold is 31 rest is as told"*.

This matters beyond bookkeeping. Two independent results now say a trend
veto HURTS (`useTrendVeto` here, the HTF bias MA on the trendline engine:
PF 0.882 → 0.819), and a third (ADX veto) said the same. Three strikes on
the same class of filter is a finding, and it was scattered across three
places instead of stated once. → now recorded in MEMORY.md.

## 2. Two standing user corrections that were never written down

- *"i never told you to create supertrend or similar settings, i dont you
  to make sure it only presents signals like the screenshot."*
  → **A screenshot of a chart is a request to restyle an existing engine's
  display, not a spec for a new algorithm.** I built a whole SuperTrend off
  a screenshot and had to throw it away.

- *"i never restricted you to any settings. i told you to find me the best
  and accurate signal printing."*
  → **Do not treat a number visible in a screenshot as a constraint.** I
  copied `lookback 5` off an image and then defended it for three
  iterations.

Both are the same failure in different clothes: reading a picture as a
specification. → now a standing rule in MEMORY.md.

## 3. An unanswered question left dangling since before 22 July

The summary records that after the SuperTrend correction I asked **which
engine the user wanted restyled** and *"that question has not been answered
yet."* It was never revisited — it fell off when the context compacted.
→ now listed as an open thread in MEMORY.md.

## 4. The 26 source-audit reports

The audit session found roughly 105 omissions and 2 fabrications across the
21 voices. The *corrections* were applied to the playbooks, but the reports
themselves — the full per-source audit, 286k chars of it — were never saved.
They are now in `03_source_audit_reports.md`. Anyone re-checking a playbook
against its source can start from the audit rather than redo it.

## 5. Confirmed already captured (no action needed)

- PF 0.731 Reversal Sniper v2 failure and the auto-regenerating-zone lesson
- PF 3.656 retraction (117 trades, free-plan data limit)
- User platform constraints: no TradingView Premium, ~2 months of 5m history,
  also uses London Strategic Edge / Brue
- The 21-voice register and the fabricated-Tendler correction

## 6. What is gone for good

Everything before **2026-07-13**. No transcript, no summary, no commit. If
the user still has those chats, exporting them into
`trader_playbooks/sources/` is the only way to recover that period.
