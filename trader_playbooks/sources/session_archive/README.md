# Session Archive — recovered 2026-07-29

## Why this exists

The user asked whether I had the data from every session. I did not. This is
everything that was still recoverable, extracted before the container holding
it was reclaimed.

**What existed on the machine at recovery time**

| Source | Coverage |
|---|---|
| Raw main transcript | one file, **2026-07-22 → 2026-07-29** (7 days) |
| Subagent logs | 32 files, same window |
| Git history | 127 commits, first **2026-07-13** (16 days) |
| claude-mem database | **absent** — never existed on this box |

Everything before 2026-07-13 is unrecoverable from my side. The user's own
chat history is the only remaining route to it; exports dropped into
`trader_playbooks/sources/` can be archived the same way the 21 raw
transcripts were.

**The container is ephemeral.** `/root/.claude/` does not survive session
reclamation. Only what is committed to git persists. That is why this
extraction happened when it did.

## Files

| File | What it is |
|---|---|
| `00_prior_sessions_summary_2026-07-22.md` | Context-compaction summary written when an earlier conversation ran out of context. **The sessions it describes have no surviving transcript — this is the only record of them.** 38k chars. |
| `01_prior_sessions_summary_2026-07-28.md` | Same, for the 22–28 July stretch. 16k chars. |
| `02_user_turns_verbatim.md` | All 31 genuine user instructions in the recovered window, verbatim, timestamped. Screenshots marked but image data unrecoverable. |
| `03_source_audit_reports.md` | 26 subagent audit reports, 286k chars — each one a full audit of a source PDF/transcript against the playbook distilled from it. These produced the corrections logged in the source-audit session but were never saved in full. |
| `04_recovered_facts_gap_analysis.md` | The facts found here that were **not** in MEMORY.md / PLAYBOOK.md / BELIEF_REGISTER.md, and what was done about each. |

## Standing lesson

Prose in a registry did not stop BUG-012 recurring, and a memory MCP that
was never populated meant four months of continuity rested entirely on
hand-written markdown. Anything that matters gets committed, in git, in the
session it happens — not summarised later.


---

## 2026-08-16 session (added 2026-08-17)

- `05_session_2026-08-16_full.jsonl.gz` — the raw session JSONL, verbatim,
  388 records, 2026-08-16T00:24:56Z .. 2026-08-17T01:55Z.
- `06_user_turns_verbatim_2026-08-16.md` — the 13 user turns from it, unedited.

**KNOWN GAP, stated rather than papered over.** This session was compacted
before the archived range begins. Everything that happened BEFORE
2026-08-16T00:24:56Z — the delivery of the 10 AM Body Break strategy that
turned out to be BUG-039, the corpus PDF builds, the quarters-theory
extraction, the four-trader hybrid work — survives ONLY as the compaction
summary, which is Turn 1 of the verbatim file. The raw exchange for that
portion is not on disk and cannot be recovered.

**Images are not recoverable.** The two handwritten note photos and every
chart screenshot were referenced by upload id, and the uploads directory was
cleared when the container recycled mid-session. The archive marks them
`[IMAGE ATTACHED]` and my transcriptions of the two note pages are preserved in
the assistant turns of the full JSONL, but the images themselves are gone.

**Why this file now exists.** The user asked whether every conversation was
saved. It was not: distilled knowledge was committed continuously, but the
conversation itself lived only on ephemeral container disk. Archiving the
session transcript is now part of the learning-capture rule, not an
afterthought.


---

## 2026-08-17 recovery sweep

The user pushed back that nothing should have been lost. A full sweep of
container-local disk found material that had never been archived:

- `07_subagent_runs_2026-07-13_to_08-11.md` — 39 subagent runs across roughly a
  month of prior sessions, each with the task it was given and the result it
  returned, verbatim. 272 KB.
- `raw/subagents_2026-07-13_to_08-11.jsonl.xz` — all 1,284 raw records from
  those 39 transcripts. 68 MB of JSONL compressed to 1.3 MB; every record is
  present, only base64 image payloads were replaced with a marker.
- `05_session_2026-08-16_full.jsonl.gz` re-generated at full current length.

Checked and found to contain NO conversation data: `/root/.claude/backups/*`
(feature flags and account state only), `/root/.claude/sessions/` (key
material), tool-results directory (empty).

### What is still genuinely unrecoverable

1. **The pre-compaction portion of the 2026-08-16 session.** The main thread
   JSONL begins at the compaction point. Everything before it survives only as
   the compaction summary, preserved as Turn 1 of
   `06_user_turns_verbatim_2026-08-16.md`. The raw exchange is not on disk in
   any form.
2. **Uploaded files attached before 2026-08-16 13:30.** The uploads directory
   was recreated empty at the first container recycle. Price CSVs survived only
   because copies had been committed to `data/`. The AU200 1-minute file was
   never committed and is gone. All images — the two handwritten note pages and
   every chart screenshot — are gone; only my transcriptions of them, in the
   assistant turns, remain.

Neither gap is recoverable by any means available inside the container. Both
are consequences of nothing being pushed to git at the time, which is the
failure the standing rule in CLAUDE.md now prevents.
