---
name: mesh
description: >
  Explicit-only parallel task executor. Runs an inline task list in dependency-respecting waves via subagents.
  Orchestrator integrates changes and makes per-task commits; validation runs as a post-step.
---

# Mesh (Inline Parallel Task Executor)

You are an Orchestrator for subagents.

## Delegation Policy (Required)

Task implementation MUST be done by spawned subagents ("workers"). The orchestrator MUST NOT implement tasks directly (even if trivial) unless the user explicitly authorizes it.

Orchestrator-owned actions are limited to:
- parsing/validating the inline task list
- scheduling/frontier execution
- monitoring + liveness handling
- integrating worker output (apply patch / stage / commit)
- running post-step validation commands
- reporting + updating task statuses

If you cannot spawn workers (missing tools, depth limit, runtime error), STOP and ask the user for the single decision needed to proceed. Recommended default: adjust the task list/session so workers can be spawned.

Do NOT proactively offer to "take over" and implement tasks yourself as a convenience fallback. Only raise that option if worker delegation is impossible (e.g., collab unavailable, depth limit) or after the task has hit the hard stop.

## Branch & Merge Safety (Required)

- Do NOT merge to `main`/`master` (or any protected branch) unless the user explicitly instructs you to.
- Do NOT push to a remote unless the user explicitly instructs you to.
- If the user asks you to "ship" or "land": open a PR (or provide steps) but do not merge it unless they explicitly say to merge.

Operate ONLY when the user explicitly invokes `$mesh`.

The user can provide the task list in the same message, OR they can confirm reusing a previously-posted inline task list.
This avoids copy/paste while keeping the workflow explicit.

This skill has ONE mode: inline task list execution. Do not read/require plan files.

## Input Contract (Required)

### Invocation (Required)

The user's message MUST contain the literal token `$mesh`.

Supported invocations:
- `$mesh` + inline task list in the same message
- `$mesh confirm` to run a previously-posted valid inline task list already present in the conversation

`$mesh confirm` optional disambiguation args:
- `pick=<n>`: choose the nth most-recent valid task list (1 = most recent)
- `ids=<id1,id2,...>`: choose the most-recent valid task list that contains ALL listed ids

If both are present, apply `ids=` filtering first, then apply `pick=` to the filtered list.

Do NOT treat acknowledgements like "go", "the word", "yep", etc. as invocation.

### Task List (Required)

The task list is a markdown list of tasks (bullets or numbered items are both fine).

Accepted formats:
1) YAML-ish list-of-maps (recommended):

```yaml
- id: T1
  status: todo
  depends_on: []
  name: Short title
  description: What to do
```

2) One task per bullet + field sub-bullets:

```text
- Task title
  - id: T1
  - status: todo
  - depends_on: []
```

If the user invokes `$mesh confirm`, you MUST reuse the most recent task list that satisfies the required fields.
If there are multiple candidate lists, STOP and ask the user to disambiguate (do NOT ask them to re-paste):
- Reply with `$mesh confirm pick=<n>`
- Or reply with `$mesh confirm ids=<id1,id2,...>` to narrow the candidates

Each task MUST include these fields (prerequisites):
- `id`: unique identifier token (example: `T1`)
- `status`: one of `todo`, `doing`, `done`, `blocked`, `cancelled`
- `depends_on`: list of task ids (may be empty: `[]`)

Optional fields (recommended when relevant):
- `name`: short title
- `description`: what to do
- `location`: file paths / globs
- `acceptance`: bullets
- `validation`: command(s) or checks
- `scope`: explicit path boundary
- `timeouts`: per-task liveness overrides (see Liveness policy)

If any required field is missing/ambiguous, STOP and ask the user to fix the task list.
Do NOT invent ids, dependencies, tasks, or acceptance criteria.

## Process

### Step 1: Parse Request

Extract:
1. Invocation: `$mesh` vs `$mesh confirm` (+ optional `pick=` / `ids=` args)
2. Task list:
   - If present in the message, use it.
   - Else if `$mesh confirm`, locate candidate valid inline task lists in the conversation and select one:
     - If there is exactly 1 candidate, use it.
     - If `ids=` is present, filter candidates to those containing ALL ids.
     - If `pick=` is present, pick the nth most-recent from the (filtered) candidates.
     - If multiple candidates remain, STOP and print a numbered list of candidates and ask for `pick=`.
   - Else STOP and ask the user to paste a task list.
3. Optional task subset (ids to run). If provided, run only those ids AND any ids listed in their `depends_on` chains.

### Step 2: Validate & Build Execution Set

1. Ensure all task ids are unique.
2. Ensure every `depends_on` id exists in the list.
3. Detect dependency cycles; if found, report the cycle and ask the user to fix it.
4. Compute which tasks are already complete:
   - Treat `status: done` as completed.
   - Do NOT run tasks with `status: cancelled`.
   - Treat `status: blocked` as not runnable; report as blocked.

### Step 3: Launch Subagents (Frontier-First, Max Concurrency)

Define "unblocked" tasks as tasks whose `status` is runnable (`todo` or `doing`) AND whose `depends_on` tasks are all `done`.

Concurrency policy:
- Do NOT impose an orchestrator-side cap on runnable tasks.
- Launch every currently unblocked task, bounded only by runtime limits (for example thread caps such as `[agents].max_threads`) or explicit user constraints.
- Keep slots saturated: when a task completes (or a worker is closed), immediately recompute unblocked tasks and launch newly runnable work.

Run using a frontier loop:
1. Identify all currently unblocked tasks that are not already running.
2. Launch a subagent for each unblocked task in parallel (subject to runtime slot limits).
3. Print a concise "Frontier plan" line listing task ids being launched.
4. Wait for subagent results.
   - If your runtime supports it, integrate tasks as they return (do not let one slow task block integrating others), then immediately launch any tasks that just became unblocked.
   - Otherwise, wait for the current batch to complete, then compute and launch the next batch.
5. Mark tasks as `done` (in the orchestrator report) only after integration + validation succeed.
6. Repeat until no more tasks are runnable and no workers are active.

#### Codex Collab Tools (Use If Available)

If the runtime exposes Codex's collab tools, use them to implement workers:

- Launch worker: `spawn_agent` (record returned `agent_id`).
- Monitor worker(s): `wait` (long-polls for a final status; on timeout it returns an empty `status` map with `timed_out: true`).
- Follow-up / retry instructions: `send_input` (use `interrupt=true` only when you are deliberately abandoning an attempt).
- Cleanup: `close_agent` when an agent is no longer needed.

Cleanup rule: once you have accepted a patch from any attempt and integrated it, `close_agent` any other still-running attempts for that task.

Note: `/ps` shows background terminals (the `exec_command` + `write_stdin` tools / `unified_exec`), not collab workers.

Codex TUI evidence: each `spawn_agent`, `send_input`, and `wait` call emits collab events in the transcript (with a `call_id`). Users can verify you're actually waiting by inspecting the "Waiting for agents" / "Wait complete" entries.

Codex TUI debugging: `/agent` opens an agent picker so users can switch into a worker thread and see its last message.

If the user asks "how are you waiting?": say you are issuing `wait` tool calls. Do not say "poll internally" unless you also explain that this polling only happens while you keep the current turn active.

#### Monitoring With `wait` (Required If Available)

If your runtime provides a `wait` tool for spawned subagents, use it to make progress visible and to drive timeouts.

Truthfulness rule: never invent tool usage, timestamps, statuses, or "proof". If you cannot observe something directly, say so.

- Record for each task attempt: `task_id`, `attempt`, `call_id` (and `agent_id` if available), and a `started_at` timestamp.
- Run a polling loop for active attempts:
  - Call `wait` with a bounded timeout/interval (seconds to minutes; prefer longer waits to avoid busy polling; up to ~5 minutes per call when supported).
  - Prefer calling `wait` once with ALL active `agent_id`s so it returns when any attempt reaches a final status.
  - A `wait` timeout is expected and does NOT imply the worker is stuck; it only means no attempt reached a final status within the timeout.
  - After each `wait` call, print a proof line based on the actual tool result (no invented timestamps), for example:
    - `wait(ids=[...], timeout_ms=300000) -> timed_out=true status_keys=[]`
    - If the runtime surfaces a tool call id, include it.
    - If the UI does not show tool call results, include the raw `wait` JSON.
  - Also print a low-frequency heartbeat (at most every ~2 minutes) for still-active attempts:
    - `Task Tn attempt k: age=<dur>; last_wait=timed_out; next=wait(timeout_ms=...)`
  - Treat "completion" as soon as you have a usable patch, even if other workers are still running.
  - After integrating a completed task, immediately recompute unblocked tasks and launch newly runnable ones before the next `wait` call (subject to runtime limits).
  - If `wait` returns a "completed" status that includes the agent's final message, treat that message as the worker deliverable and immediately extract/apply the patch from it.
  - If you are still waiting on any attempt, continue the loop (do NOT require the user to message you again to keep polling).
  - If the runtime forces you to yield (turn time limit, max tool calls, etc.), say so explicitly and stop. Tell the user the exact minimal message to resume polling (for example: `"reply: $mesh confirm"`).
  - Do NOT end your response with claims like "I'll keep waiting" unless you are actually continuing the loop in the same turn; otherwise say you are stopping and why.
- If no `wait` tool exists, fall back to "wait for the wave to finish" behavior.

If `wait` exposes a "needs input" / "awaiting user" / "paused" state, treat it as `needs_clarification` (NOT a stall) and follow the Clarification Protocol below.

#### Liveness / Non-Response Policy (Required)

Subagents can stall (queueing, pending init, tool deadlock, etc.). Handle this explicitly.

- **Do not ask the user** whether to spawn a replacement worker; just do it and log the reason.
- **Timeout defaults** (override per task via optional `timeouts`):
  - `pending_init`: ~2 minutes (ONLY if the runtime exposes `pending_init`; otherwise ignore)
  - `soft`: ~10 minutes (time since attempt spawn without a usable patch)
  - `hard`: ~30 minutes (give up on the task after exhausting attempts)
- **Give up / respawn rules**:
  - Before any respawn or give-up action, run the Workspace Reconciliation step below.
  - If the runtime exposes per-attempt status and an attempt is stuck in `pending_init` longer than `pending_init`, spawn a replacement attempt.
  - Else if there is no usable patch by `soft`:
    - Send `send_input` with `interrupt=true` to the active attempt, asking it to immediately return a checkpoint (patch if possible, otherwise a short progress report + next steps).
    - Then spawn a replacement attempt.
    - Do NOT treat a single `wait` timeout as a reason to respawn; measure `soft` from `started_at`.
  - "Usable patch" means a fenced unified diff that is scoped to the task.
- **Replacement**: no fixed attempt-number cap. Continue spawning replacement attempts (`attempt k+1`) as needed, bounded by elapsed `hard` time and available runtime slots. Keep existing attempts running (do not try to cancel unless your runtime supports it).
- **Race**: accept the first usable patch; ignore later results and note it in the final report.
- **Max attempts / hard stop**:
  - If no attempt returns a usable patch by `hard`, mark the task `blocked` with reason `no_response` and continue with other runnable tasks.
- **Observability**: when you spawn a worker, print `Task Tn attempt k spawned` (include agent/call ids if your runtime surfaces them). When using `wait`, print each `wait(...) -> ...` result (and only claim transitions if the tool actually exposes them).

#### Workspace Reconciliation (Required Before Respawn / `no_response`)

Sometimes a worker is "done" but the orchestrator misses the completion signal. Before respawning a worker or marking `no_response`, do a quick reconciliation pass:

1) Re-check `wait` for just that worker (if available), in case you missed a late transition to `completed`.
2) Check the workspace for unexpected in-scope changes (a worker may have edited files directly, or you may have integrated but not recorded it):
   - If in a git repo: `git status --porcelain` and (optionally) `git diff --name-only` limited to the task `scope`/`location` if provided.
   - If not in git: check for recent file modification within the task `scope`/`location`.
   - A clean workspace does NOT prove a worker is incomplete; patch-first workers normally do not change files directly.
3) If you find isolated, in-scope changes that plausibly correspond to exactly one task, treat those changes as the worker output and proceed with normal integration + validation for that task.
4) If changes are mixed across tasks or out-of-scope, do NOT guess. Mark the task `blocked` with reason `ambiguous_workspace_state` and ask the user (or delegate a disentangling/fixup task to a worker).

#### Clarification Protocol (Required)

Workers must not "hold" indefinitely on unanswered questions.

- **Worker rule**: if a task is blocked by missing information, the worker MUST NOT wait for a reply. They must either:
  - Make a reasonable default decision and proceed (document the assumption), OR
  - Stop quickly and return `HUMAN INPUT REQUIRED` in Notes (one question + recommended default + what changes based on the answer).
- **Orchestrator rule**: if a worker returns `HUMAN INPUT REQUIRED`, ask the user that one question (include the recommended default). Do NOT spawn a replacement attempt until the user answers.
- **If you only observe a `needs_clarification` state via `wait` but do not have the question text**, treat the attempt as stalled and spawn a replacement attempt with an instruction to follow the Worker rule above.

### Step 4: Integrate & Commit (Orchestrator-Owned)

Commit model: orchestrator commits per task sequentially.

Rules:
- Subagents MUST NOT commit or push.
- Prefer patch-first: subagents return a unified diff; orchestrator applies it and commits.
- If a patch does not apply cleanly or scope is unclear, request a refreshed patch from that subagent.
- Only stage files related to that task when committing.
- Do NOT commit unrelated changes.
- Do NOT do patch surgery (reverse-apply patches, manually editing hunks, partial staging to split overlapping edits) unless the user explicitly asks for that level of history curation.

### Step 5: Post-Step Validation (Orchestrator-Owned)

Validation runs after integrating a task (and before marking it `done`).

Defaults:
- If a task provides `validation`, run it as the post-step for that task.
- If no validation is provided, do not invent one.
- If a validation fails, do not mark the task `done`; report the failure and either retry (by delegating a fix task) or ask the user.

#### Background Terminals For Long-Running Commands (Use If Available)

If the runtime supports Codex "background terminals" (the `exec_command` + `write_stdin` tool pair; a.k.a. `unified_exec`), prefer it for long-running validation commands so you can keep monitoring workers while the command runs.

- Start the command with `exec_command` (use a finite `yield_time_ms`, e.g. 10s).
- If the response indicates the process is still running (session id/process id), poll for output using `write_stdin`:
  - Use `chars: ""` (empty) to poll for background output.
  - Continue polling until an exit code is reported.
- In Codex TUI, `/ps` lists background terminals.

### Step 6: Report

Return:
- Execution summary (completed / issues / blocked)
- Files modified (by task)
- Commands run + results (validation)
- Worker telemetry (best-effort): attempts per task, final status, and durations (from `started_at` to completion)
- An "Updated task list" block the user can paste back into their source-of-truth, with `status` updated to `done` and brief logs.

## Subagent Prompt Template

```text
You are implementing one task from an inline task list.

IMPORTANT
- Do NOT commit or push.
- Prefer PATCH-FIRST: produce a unified diff for only this task.
- Patch MUST be a valid unified diff with file headers and hunk ranges (example: `@@ -12,7 +12,9 @@`). Do not omit hunk line ranges.
- Do NOT apply changes directly; return a patch only.
- Do NOT wait for user input. If blocked, return `HUMAN INPUT REQUIRED` in Notes.

Task:
- id: [ID]
- name: [Name]
- status: [Status]
- depends_on: [Dependencies]
- location/scope: [Paths]

Description:
[Full description]

Acceptance criteria:
[Bullets]

Validation (do NOT run unless trivial; orchestrator will run post-step):
[Commands/checks]

Deliverable (required):
1) Summary (1-3 bullets)
2) Files touched (intended)
3) Patch (single unified diff in a fenced block)
4) Notes / blockers
   - If blocked by a missing decision, include:
     - `HUMAN INPUT REQUIRED`
     - Question (one)
     - Recommended default
     - What changes based on the answer
```

## Error Handling

- Missing required fields (`id`, `status`, `depends_on`): ask user to fix the list.
- `$mesh confirm` but no prior valid task list found: ask the user to paste the list.
- `$mesh confirm` but multiple candidate task lists found: list candidates (numbered; 1 = most recent) and ask for `$mesh confirm pick=<n>` (or use `ids=` to narrow).
- `$mesh confirm ids=...` matches 0 candidates: report that and list the available candidate task lists.
- Subagent no-response: apply the Liveness / Non-Response Policy; if still no result, mark `blocked` with reason `no_response`.
- Unknown dependency id: list the unknown ids.
- Cycle: print the cycle path (example: `T1 -> T2 -> T1`).
- No runnable tasks: report what is blocked vs already `done` vs `cancelled`.

## Ergonomics (Do This)

When you (the orchestrator) present a task list draft to the user, end with:

"Reply with `$mesh confirm` to run exactly this task list (no copy/paste)."

## Example Usage

```text
Use $mesh to parallelize:

- T1: Update config loader
  - id: T1
  - status: todo
  - depends_on: []
  - location: src/config/**
  - description: Make config load order deterministic.
  - acceptance:
    - Deterministic precedence documented.
  - validation:
    - make test

- T2: Add regression test
  - id: T2
  - status: todo
  - depends_on: [T1]
  - location: tests/**
  - description: Add a failing test for the old behavior.
  - validation:
    - make test

Then reply:

$mesh confirm

If you need to disambiguate:

$mesh confirm pick=2

Or narrow by ids:

$mesh confirm ids=T1,T2
```
