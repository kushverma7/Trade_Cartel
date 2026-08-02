# Recovery Push Prompt — save the work before the container is reclaimed

For any session that has done real work which may not be pushed. Two AU200
research efforts have already been lost this way: built, committed locally,
push failed or was never attempted, container reclaimed, gone.

**Order matters. This prompt pushes first and asks questions second**, because
a container can be reclaimed between the question and the answer.

---

## PROMPT — COPY FROM HERE

Before you answer anything, before you summarise, before you clean anything
up: **push whatever is on disk.**

This container is ephemeral. Local commits are not saved work. Only pushed
git objects survive. Two research efforts in this project have already been
lost exactly here — committed locally, push failed, container reclaimed. Do
not let this session be the third.

### Step 1 — push now, messy is fine

```
git config user.email noreply@anthropic.com
git config user.name Claude
git status --porcelain -uall | head -50
git add -A
git commit -m "WIP: checkpoint before review"
git push -u origin HEAD
```

Do not tidy first. Do not rename files, do not split commits, do not remove
debug scripts. A messy pushed commit can be cleaned later; an elegant
unpushed one cannot be recovered. If you are on a detached HEAD or an unnamed
branch, create a branch and push that.

**If the push fails**, this is now the only thing you are working on. Report
the exact error immediately. A 403 at the proxy is the known failure here —
see `/root/.ccr/README.md` and run
`curl -sS "$HTTPS_PROXY/__agentproxy/status"`. Do not disable TLS
verification and do not unset `HTTPS_PROXY`. If it cannot be fixed, say so
loudly and paste the critical file contents into the chat as a last resort,
because chat outlives the container and the disk does not.

**One exception, and only one:** do not push credentials. If an API key,
token or password is in a file you are about to add, move it to a gitignored
`.env` (mode 600) first. Git history is permanent and cannot be cleaned
without a rewrite. Everything else goes in, including work you think is
worthless.

### Step 2 — find what the first push missed

`git add -A` does not catch everything. Check each of these:

```
git log --oneline @{upstream}..HEAD          # commits never pushed
git stash list                                # stashed work
git branch -a --no-merged                     # other local branches
git worktree list                             # other worktrees
cat .gitignore                                # is real work being ignored?
ls -la /tmp /tmp/claude-* ~ 2>/dev/null       # files written outside the repo
```

The `.gitignore` check matters most. Sessions routinely write results to
paths like `*.json`, `*.csv`, `output/` or `scratch/` that a broad ignore
rule silently excludes. If real output is being ignored, force-add it:
`git add -f <path>`. Then push again.

### Step 3 — save what is not on disk at all

The most valuable thing in a research session is usually not a file. It is
the numbers that only ever appeared in chat, and the reasoning behind them.
Those die with the container.

Create `SESSION_NOTES_<date>.md`, write the following into it, and push:

1. **Every measured number produced in this session**, each with its trade
   count, date range, timeframe, instrument, slippage and commission, and the
   exact settings. A profit factor with no sample size and no window is not a
   result and should be recorded as "unverified claim", not as a number.
2. **Which numbers are measured and which are estimates.** Be explicit. An
   estimate presented alongside measured runs has already caused a problem in
   this project.
3. **Which file produced which number.** If the file no longer exists, say
   so — that is the single most important fact about that number.
4. **What was tried and rejected, with its numbers.** This is worth as much
   as the successes; it stops the next session re-running dead ends.
5. **Open questions and the next action**, written for someone with no
   memory of this conversation.

### Step 4 — then, and only then, report

Reply with:

- the branch name and commit SHA you pushed
- what is now safe
- what was found in Step 2 that the first push missed
- what could NOT be saved and is therefore gone
- any number you produced whose code no longer exists — flagged clearly as
  unreproducible

Do not restate results tables as if they were validated. In this repo a
result requires trade count, date range, cost model, and an out-of-sample
test; see `RESEARCH_PROTOCOL_PROMPT.md` and `RESULTS_LEDGER.md`. A table
whose code was never pushed is a rumour, not a finding.

### Step 5 — from now on, in this session

Push at every checkpoint, not at the end. After each meaningful piece of work:

```
git add -A && git commit -m "<what changed>" && git push
```

If you are about to run something long, push before you run it, not after.

## PROMPT — COPY TO HERE

---

Written 2026-08-02, after the second AU200 research loss in three days. The
matching standing rule is in `MEMORY.md` — verify the push path works at
session start, before doing the work.
