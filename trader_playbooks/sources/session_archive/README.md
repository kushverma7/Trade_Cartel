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
