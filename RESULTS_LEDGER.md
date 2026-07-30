# RESULTS LEDGER

**Every backtest result on record, in one table.** Built 2026-07-29 by
extracting every result mention from `trader_playbooks/PLAYBOOK.md` and the
recovered session archive.

## Why this file exists

Before it, results lived as prose scattered across 1,097 lines of PLAYBOOK.md
— 19 separate PF mentions, of which only ~12 recorded a trade count and only
5 recorded the date range tested. There was no way to answer "what did engine
X score, on what sample, with what settings" without re-reading the whole
file. That is a large part of why 17 engines got built and none got validated:
the comparison was never actually available.

**Rules for this file**
1. Every row records the sample, not just the headline. A PF with no trade
   count and no date range is not a result.
2. `Unknown` means unknown. Do not infer, do not backfill from memory.
3. Nothing gets a `VALID` status without an out-of-sample test. As of this
   file's creation, **no row qualifies** — that is the finding.
4. New results are appended here in the session they are produced.

---

## The ledger

| # | Date | Engine | Sym / TF | Window | Trades | WR | PF | Net | Max DD | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ~07-15 | Reversal Sniper v2 (auto S/D zones) | XAUUSD 5m | Unknown | Unknown | Unknown | **0.731** | Unknown | Unknown | RETIRED — mechanism blamed & banned |
| 2 | 07-20 | Session Trendline Breakout | XAUUSD 5m | ~2 months | 117 | Unknown | **3.656** | Unknown | Unknown | **RETRACTED** — sample too small (free-plan data cap) |
| 3 | 07-20 | Top/Bottom engine, run 1 | XAUUSD 5m | Unknown | Unknown | Unknown | 0.90 (analog) | Unknown | Unknown | superseded |
| 4 | 07-20 | Top/Bottom engine, run 2 | XAUUSD 5m | Unknown | Unknown | Unknown | 0.67 (analog) | Unknown | Unknown | regression, diagnosed |
| 5 | 07-20 | Top/Bottom engine, run 3 | XAUUSD 5m | Unknown | Unknown | Unknown | 0.85 (analog) | Unknown | Unknown | superseded |
| 6 | 07-20 | **Top/Bottom engine, run 4** | XAUUSD 5m | Unknown | **112** | 35.7% | **1.11** (analog) | Unknown | Unknown | first >1; settings recovered 07-29 (see below) |
| 7 | 07-20 | Spaceman + Daye Quarters | XAUUSD 5m | Unknown | 12 | 0% | **0** | Unknown | Unknown | broken — 12/12 losses, root-caused |
| 8 | 07-20 | Spaceman + Daye, re-test | XAUUSD 5m | Unknown | 8 | 12.5% | **0.14** | Unknown | Unknown | abandoned |
| 9 | 07-27 | OMNIBUS four-model | XAUUSD 5m | Jun–Jul | 298 | 40.6% | **0.843** | −13.01% | Unknown | plateau |
| 10 | 07-27 | Key-to-Key | XAUUSD 5m | Jun–Jul | ~245 | 26.1% | **0.886** | −10.87% | 23.15% | plateau |
| 11 | 07-27 | Trendline × Key Levels v1 | XAUUSD 5m | Jun–Jul | 382 | 40.8% | **0.882** | −11.72% | 20.68% | plateau |
| 12 | 07-27 | Trendline × Key Levels v2 (+HTF bias) | XAUUSD 5m | Jun–Jul | ~380 | Unknown | **0.819** | −13.34% | 15.69% | REVERTED — filter made it worse |
| 13 | 07-28 | **Multi-Voice Confluence** | XAUUSD **15m** | Feb 2 – Jul 28 2026 | **521** | 44.15% | **1.093** | +15.25% | 11.90% | best on record; in-sample only, confounded |
| 14 | 07-28 | Multi-Voice + level-to-level exits | XAUUSD 15m | Feb 2 – Jul 28 2026 | 461 | 34.06% | **0.892** | −14.19% | 25.47% | REVERTED — see H74 |
| 15 | 07-29 | Key Levels (Spaceman Edition) v1.0 | XAUUSD 30m | Jan 2025 – Jul 2026 | 22 | 63.64% | **1.783** | +7.70% | 7.01% | **VOID** — order-rejection artifact (BUG-012) |
| 16 | — | Key Levels (Spaceman Edition) v1.1 | XAUUSD 30m | — | — | — | — | — | — | superseded by v1.2, never run |
| 17 | — | Key Levels (Spaceman Edition) v1.2 | XAUUSD 30m | — | — | — | — | — | — | fixes + level scorecard, NOT YET RUN |

## What the ledger says when you read it as one table

- **16 runs. Zero out-of-sample tests. Zero valid rows.**
- Two of the three results above PF 1.0 are already dead: #2 retracted for
  sample size, #15 void as an execution artifact. Only #13 survives, and it
  is one in-sample window with a confound (logic and timeframe both changed).
- Rows 9–12 are the plateau: four different architectures, same Jun–Jul 5m
  window, PF 0.819–0.886. Four distinct entry mechanisms converging on the
  same losing number is evidence about the **timeframe**, not the mechanisms.
- Rows 1–8 mostly lack trade counts and date ranges entirely. They cannot be
  compared to anything. Roughly half the project's recorded history is
  unusable as evidence.
- Every window ≤ 07-27 is Jun–Jul only — a ~2-month sample, because of the
  free-plan data cap. Row 13 was the first time a real sample was tested.

## Settings for the results that had them recorded

**#6 Top/Bottom, PF-analog 1.11** (recovered 2026-07-29 from the session
archive — these existed nowhere in the repo before):
```
useTestFail  = false      closePosPct = 0.2       rsiOb = 72
rsiOs        = 31         useTrendVeto = false    cooldown = 20
minReArmAtr  = 1.5
```
User confirmation, verbatim: *"oversold is 31 rest is as told"*.

**#13 Multi-Voice, PF 1.093:** `minScore = 6`, `weightHigh = true`, all 20
voters on, defaults elsewhere. Group ⑤/⑥ did not exist yet.

## Standing conclusions the table supports

1. **Trend / HTF filters have failed three times.** #12 (HTF bias MA, 0.882 →
   0.819), the ADX veto, and `useTrendVeto` on #6. Three strikes.
2. **A suspiciously low trade count is an execution symptom.** #15 looked
   like a 1.783 edge and was rejected orders. #7 looked like a strategy
   failure and was also plumbing.
3. **The plateau is the finding.** Rows 9–12 say XAUUSD 5m does not support
   these mechanisms after costs. Kronos was acquired to test that directly
   and is still blocked on HuggingFace being firewalled.
