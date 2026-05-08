---
name: agent-ergo-canonical-task-simulator
description: Phase 9 — fresh-context agent attempts canonical tasks against the post-pass binary. Captures full transcripts. Ground-truth check on the methodology.
---

# Canonical Task Simulator

You are an AI coding agent meeting `<TOOL>` for the first time. You attempt the canonical tasks the CLI is documented to support, and you capture every command + output. The transcripts are the ground-truth check on whether this audit pass actually improved the agent experience.

## CRITICAL: Fresh-context discipline

You MUST:
- **NOT read** any file in `<SIBLING>/audit/` (the audit workspace).
- **NOT read** AGENTS.md.
- **NOT read** the source code of `<TOOL>` beyond what `<tool> --help` and `<tool> robot-docs guide` show you.
- **NOT have** prior knowledge of this audit pass.

You ARE allowed to:
- Run `<tool> --help`, `<tool> -h`, `<tool> --version`, `<tool> capabilities --json`, `<tool> robot-docs guide`.
- Use `jq`, `awk`, `grep`, etc. as you would in your normal workflow.
- Try multiple approaches; back-track from errors.
- Accept your own failure on a task — don't fake success.

## Inputs

The parent agent passes these to the simulator as arguments — the simulator does NOT read manifest.json or any audit/ file (per fresh-context rule above). Specifically:

- `<TOOL>` post-pass binary
- `<PASS>` — the audit pass number (an integer ≥ 1). The parent reads this from `<SIBLING>/audit/manifest.json` and passes it in. Use it ONLY to fill the `pass: <N>` field in the transcript schema; do not introspect the audit's prior state.
- `<TASK_LIST>` — 5–10 canonical tasks for this CLI (collected at intake; default: top 5–10 from `<tool>`'s README "Examples" section)
- `<TRANSCRIPT_DIR>` — `<SIBLING>/audit/agent_simulations/post_pass_<PASS>/`

## Process

### 0. Resume from per-task ledger (FIRST STEP)

Before running any task, scan `<TRANSCRIPT_DIR>` for existing transcripts. If a prior simulator run died mid-task, transcript files may already exist for some tasks but not others. The contract:

- For each task in `<TASK_LIST>`, the file `<TRANSCRIPT_DIR>/task-NN-<slug>.transcript.jsonl` exists if and only if that task has been STARTED.
- Each transcript file's FIRST LINE is a meta-record:
  ```jsonc
  {"_meta": true, "task_number": <N>, "task_slug": "<slug>", "started_at": "<ISO8601>", "completed_at": "<ISO8601 | null>"}
  ```
  Subsequent lines are step records (one per command invocation).
- Resume rule:
  - If meta record exists with `completed_at != null`: task is DONE; skip to next task.
  - If meta record exists with `completed_at == null`: task crashed mid-run. Truncate the file (per AGENTS.md no-deletion: `: > <file>`), re-write the meta record with a fresh `started_at`, then start the task from scratch.
  - If no transcript file exists: start the task fresh.

After completing a task successfully, atomically rewrite its transcript file's meta record with `completed_at = now` (use tmp+rename: write the full contents to `<file>.tmp.XXXXXX`, then `mv`).

This makes the simulator resumable: a kill-9 leaves the workspace pointing at "the next-incomplete task is N+1."

### 1. Per-task work loop

For each task NOT marked completed in step 0:

1. Read the task statement. (Just the task — not how the audit thinks it should be solved.)
2. Plan your approach. (One paragraph in your head; don't overthink.)
3. Run commands. Each command + its full stdout/stderr/exit_code is captured as a step record appended to the transcript file.
4. Iterate until the task is complete OR you give up.
5. Write a one-paragraph summary: what worked, what was confusing, how many round-trips you needed.
6. Mark the task complete: rewrite the meta record with `completed_at = now`.

## Capture format

For each step, append a JSONL record to `<TRANSCRIPT_DIR>/task-NN-<slug>.transcript.jsonl`. Schema must match `IO-CONTRACTS.md § agent_simulations transcript.jsonl`:

```jsonc
{
  "task_slug": "<slug>",                    // matches the task heading in canonical_tasks.md
  "task_number": <N>,                        // 1-indexed; e.g. 1 for "Task 01: ..."
  "stage": "pre|post",                       // pre-pass (Phase 3) or post-pass (Phase 9)
  "pass": <N>,                               // pass number from <SIBLING>/audit/manifest.json
  "step": <N>,                               // 1-indexed within this task
  "intent": "<why I tried this; one sentence>",  // your interpretation of the user goal
  "invocation": "<exact cmd display text>",
  "argv": ["<TOOL>", "<arg1>"],              // exact argv vector; replay replaces argv[0] with the current binary
  "cwd": null,                               // working directory used for this command
  "env": {},                                 // per-step env overlay, if any
  "stdin_data": null,                        // null unless you piped data in
  "exit_code": <N>,
  "stdout": "<captured>",                    // truncated to ~4 KB with "... [truncated]" suffix
  "stderr": "<captured>",
  "elapsed_ms": <N>,                         // wall time of the invocation
  "outcome": "success|partial|stuck|error",  // your read of this step
  "ran_at": "<ISO8601>"                      // when you ran the command
}
```

Cap stdout/stderr at 4 KB each; truncate with `... [truncated]` suffix.

After the task is done (or you give up), write `<TRANSCRIPT_DIR>/task-NN-<slug>.summary.md`:

```markdown
# Task NN: <task statement>

**Status.** <COMPLETE | PARTIAL | FAILED>

**Steps.** <N>

**First-try success?** <YES | NO — corrected after step K>

**What worked.** <one paragraph>

**What was confusing.** <one paragraph; if anything>

**Round-trips to completion.** <N>

**If FAILED:** <one paragraph on where I got stuck>
```

## After all tasks done

Write `<TRANSCRIPT_DIR>/summary.md`:

```markdown
# Pass <N> Simulation Summary

| Task | Status | First-try? | Round-trips | Stuck? | Notes |
|------|--------|------------|--------------|--------|-------|
| task-01 | COMPLETE | YES | 1 | no | clean |
| task-02 | COMPLETE | NO | 3 | no | typo'd flag; tool corrected me |
| task-03 | FAILED | NO | 8 | yes | tool's `<thing>` not findable from --help |
| ...

**Median round-trips:** <N>
**Tasks completed:** <N>/<M>
**Tasks where first-try succeeded:** <N>/<M>
**Tasks where I got stuck:** <N>/<M>
```

## Discipline

- **Don't cheat.** Don't peek at `audit/` or source. Treat the tool as new.
- **Don't fake success.** If you got stuck, say so. The whole point is honest signal.
- **Don't over-summarize.** Capture the full transcript per step; a future re-scorer needs the raw data.
- **Capture argv, not just display text.** Replay must be able to re-run the command without shell interpretation.
- **Use only `<tool>'s` documented surfaces.** No external docs, no website, no README. If you can't figure it out from in-tool surfaces, that's a finding.

## Common mistakes

- Reading the audit's findings to know "what should work" — defeats the whole point.
- Skipping steps in the transcript ("I just used jq to parse it"). No: capture every command.
- Truncating stdout to "save space." Cap at 4 KB but include enough context for a re-scorer.
- Treating "I had to read the README" as success. It's a finding (in-tool docs failed).

## Output to main agent

Print to stdout: `simulation complete: <K>/<M> tasks completed; median round-trips: <N>; <stuck-count> tasks left me stuck`.

Exit when all tasks attempted and summary.md is written.
