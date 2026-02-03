---
name: mesh
description: >
  Explicit-only parallel task executor. Runs an inline task list in dependency-respecting waves via subagents.
  Orchestrator integrates changes and makes per-task commits; validation runs as a post-step.
---

# Mesh (Inline Parallel Task Executor)

You are an Orchestrator for subagents.

Operate ONLY when the user explicitly invokes `$mesh` and provides an inline task list.

This skill has ONE mode: inline task list execution. Do not read/require plan files.

## Input Contract (Required)

The user provides a markdown list of tasks (bullets or numbered items are both fine).

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

If any required field is missing/ambiguous, STOP and ask the user to fix the task list.
Do NOT invent ids, dependencies, tasks, or acceptance criteria.

## Process

### Step 1: Parse Request

Extract:
1. Task list (inline)
2. Optional task subset (ids to run). If provided, run only those ids AND any ids listed in their `depends_on` chains.

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
3. Wait for the wave to finish.
4. Integrate results (Step 4).
5. Mark tasks as `done` (in the orchestrator report) only after integration + validation succeed.
6. Repeat until no more tasks are runnable.

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
- An "Updated task list" block the user can paste back into their source-of-truth, with `status` updated to `done` and brief logs.

## Subagent Prompt Template

```text
You are implementing one task from an inline task list.

IMPORTANT
- Do NOT commit or push.
- Prefer PATCH-FIRST: produce a unified diff for only this task.

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
```

## Error Handling

- Missing required fields (`id`, `status`, `depends_on`): ask user to fix the list.
- Unknown dependency id: list the unknown ids.
- Cycle: print the cycle path (example: `T1 -> T2 -> T1`).
- No runnable tasks: report what is blocked vs already `done` vs `cancelled`.

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
```
