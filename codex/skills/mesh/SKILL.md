---
name: mesh
description: >
  Explicit-only parallel task executor. Runs an inline task list in dependency-respecting waves via subagents.
  Orchestrator integrates changes and makes per-task commits; validation runs as a post-step.
---

# Mesh (Inline Parallel Task Executor)

You are an Orchestrator for subagents.

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

### Step 3: Launch Subagents (Waves)

Define "unblocked" tasks as tasks whose `status` is runnable (`todo` or `doing`) AND whose `depends_on` tasks are all `done`.

Run in waves:
1. Identify all currently unblocked tasks.
2. Launch a subagent for each unblocked task in parallel.
3. Print a concise "Wave plan" line listing task ids being launched.
4. Wait for subagent results.
   - If your runtime supports it, integrate tasks as they return (do not let one slow task block integrating others).
   - Otherwise, wait for the wave to complete.
5. Integrate results (Step 4).
6. Mark tasks as `done` (in the orchestrator report) only after integration + validation succeed.
7. Repeat until no more tasks are runnable.

#### Monitoring With `wait` (Required If Available)

If your runtime provides a `wait` tool for spawned subagents, use it to make progress visible and to drive timeouts.

- Record for each task attempt: `task_id`, `attempt`, `call_id` (and `agent_id` if available), and a `started_at` timestamp.
- Run a polling loop for active attempts:
  - Call `wait` with a short timeout/interval (if supported).
  - Track `last_status` per attempt and log only state transitions (e.g., `pending_init -> running -> completed`).
  - Also print a low-frequency heartbeat (at most every ~2 minutes) for still-active attempts:
    - `Task Tn attempt k: status=<status> age=<dur>; next=<timeout action>`
    - This is how you demonstrate monitoring even when there are no transitions.
  - As soon as an attempt finishes and returns a usable patch, integrate it immediately.
- If no `wait` tool exists, fall back to "wait for the wave to finish" behavior.

If `wait` exposes a "needs input" / "awaiting user" / "paused" state, treat it as `needs_clarification` (NOT a stall) and follow the Clarification Protocol below.

#### Liveness / Non-Response Policy (Required)

Subagents can stall (queueing, pending init, tool deadlock, etc.). Handle this explicitly.

- **Do not ask the user** whether to spawn a replacement worker; just do it and log the reason.
- **Timeout defaults** (override per task via optional `timeouts`):
  - `pending_init`: ~2 minutes (time stuck in `pending_init`)
  - `soft`: ~10 minutes (time since attempt spawn without a usable patch)
  - `hard`: ~30 minutes (give up on the task after exhausting attempts)
- **Give up / respawn rules**:
  - If `wait` shows `pending_init` longer than `pending_init`, spawn a replacement attempt.
  - Else if there is no usable patch by `soft`:
    - If `wait` indicates the attempt is actively running (e.g., `running`), assume it is working and DO NOT spawn a replacement yet; continue waiting until `hard`.
    - Otherwise (no `wait`, unknown status, or non-active status), spawn a replacement attempt.
  - "Usable patch" means a fenced unified diff that is scoped to the task.
- **Replacement**: spawn at most ONE replacement worker per task (attempt 2). Keep attempt 1 running (do not try to cancel unless your runtime supports it).
- **Race**: accept the first usable patch; ignore later results and note it in the final report.
- **Max attempts / hard stop**:
  - If neither attempt returns a usable patch by `hard`, mark the task `blocked` with reason `no_response` and continue with other runnable tasks.
- **Observability**: when you spawn a worker, print `Task Tn attempt k spawned` (include agent/call ids if your runtime surfaces them). When using `wait`, also print status transitions.

#### Clarification Protocol (Required)

Workers must not "hold" indefinitely on unanswered questions.

- **Worker rule**: if a task is blocked by missing information, the worker MUST NOT wait for a reply. They must either:
  - Make a reasonable default decision and proceed (document the assumption), OR
  - Stop quickly and return `HUMAN INPUT REQUIRED` in Notes (one question + recommended default + what changes based on the answer).
- **Orchestrator rule**: if a worker returns `HUMAN INPUT REQUIRED`, ask the user that one question (include the recommended default). Do NOT spawn a replacement attempt until the user answers.
- **If you only observe a `needs_clarification` state via `wait` but do not have the question text**, treat the attempt as stalled and spawn the single replacement attempt with an instruction to follow the Worker rule above.

### Step 4: Integrate & Commit (Orchestrator-Owned)

Commit model: orchestrator commits per task sequentially.

Rules:
- Subagents MUST NOT commit or push.
- Prefer patch-first: subagents return a unified diff; orchestrator applies it and commits.
- If a patch does not apply cleanly or scope is unclear, request a refreshed patch from that subagent.
- Only stage files related to that task when committing.
- Do NOT commit unrelated changes.

### Step 5: Post-Step Validation (Orchestrator-Owned)

Validation runs after integrating a task (and before marking it `done`).

Defaults:
- If a task provides `validation`, run it as the post-step for that task.
- If no validation is provided, do not invent one.
- If a validation fails, do not mark the task `done`; report the failure and either retry (by delegating a fix task) or ask the user.

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
