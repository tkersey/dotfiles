---
name: select
description: "Source-agnostic work selector: emit an OrchPlan (waves + delegation) plus PLANS/SLICES pipelines. Plan-only; no writeback; orchestration-agnostic."
---

# Select

## Intent
Pick a task source, schedule parallel waves when safe, and emit an **orchestration plan**.

This skill is **plan-only**:
- It does not execute work (no agent spawning).
- It does not mutate the task source (no `bd update`, no `SLICES.md` writes, no `plan-N.md` writes).
- It is orchestration-agnostic: the output is a neutral plan schema (not tied to `$mesh`).

It also emits a pipeline for driving **PLANS -> SLICES -> execution** (manual steps, plus an optional `$loop` form).

## Source precedence
When multiple sources exist, pick exactly one using this precedence:
1. Explicit user-provided task list in the invocation text.
2. `SLICES.md` (if present and parseable).
3. `bd` issues (if `.beads/` exists and `bd` works).
4. `plan-N.md` (highest N, repo root).

If the highest-precedence source exists but has **no viable tasks**, stop and ask whether to fall back to the next source.

## Source detection + preflight (how)
Detect sources without mutating them:

1. Invocation task list:
   - A numbered/bulleted list that follows an explicit phrase like "Use $select" / "$select:".
   - If present, treat it as the source and do not look elsewhere.
2. `SLICES.md`:
   - Exists at repo root (`SLICES.md`).
   - Parseable (each slice section contains exactly one YAML mapping).
3. `bd`:
   - Run `rg --files -g '.beads/**' --hidden --no-ignore`.
   - If any paths exist, `bd` is an available source.
4. `plan-N.md`:
   - Find files matching `plan-(\d+).md` in the repo root and pick the highest `N`.

Preflight (best-effort):
- For the chosen source, collect candidate tasks + dependency edges.
- If any dependency refers to an unknown task ID, stop and ask.
- If the dependency graph is cyclic/unschedulable, stop and ask.
- If the source is present but unparseable/empty, stop and ask before falling back.

## Input: task list (recommended)
If the user provides an explicit list, treat it as the canonical source.

Recommended per-task metadata (all optional, but required to unlock safe parallelism):
- `id`: stable identifier (string; default is a generated `t-<n>`).
- `agent`: `worker|orchestrator`.
- `scope`: list of path prefixes/globs (see parallelism rules).
- `depends_on`: list of task IDs.
- `subtasks`: only when `agent=orchestrator`; a list of tasks in the same format.

Example input:
```text
Use $select to plan:
1. Implement mol-mesh-run.
   - id: run
   - agent: worker
   - scope: ["codex/formulas/mol-mesh-run/**"]
2. Scripts workstream.
   - id: scripts
   - agent: orchestrator
   - scope: ["codex/scripts/mesh-*"]
   - subtasks:
     - Implement mesh-workspace.
       - id: ws
       - agent: worker
       - scope: ["codex/scripts/mesh-workspace"]
     - Implement mesh-gates.
       - id: gates
       - agent: worker
       - scope: ["codex/scripts/mesh-gates"]
```

## Parallelism rules (safety-first)
Parallelism is only scheduled when tasks provide enough metadata to make it defensible.

- A task is eligible for parallel waves only if it has a non-empty `scope` list.
- Two tasks may share a wave only if their `scope` sets do not overlap.
  - Treat `scope` entries as **exclusive locks**.
  - Recommended lock style: directory roots or tight file globs.
  - Conservative overlap check: if any lock is equal OR one lock is a path-prefix of another, treat as overlap.
- Tasks missing `scope` are treated as overlapping everything and therefore scheduled alone; include a warning explaining which metadata would unlock parallelism.

## Orchestration-of-orchestration
Tasks may be delegated to an `agent: orchestrator` only when the user provided `subtasks`.
If `agent: orchestrator` is set but `subtasks` is empty/missing, downgrade to `agent: worker` and warn.

## Output: OrchPlan v1
Emit one YAML block with the canonical plan.

Schema (YAML; best-effort, omit unknown keys):
```yaml
schema_version: 1
kind: OrchPlan

created_at: "<rfc3339>"

source:
  kind: list|slices|beads|plan
  locator: "<freeform; e.g. 'invocation', 'SLICES.md', 'bd ready', 'plan-3.md'>"

# Optional. If omitted, treat as "auto" (unbounded by cap; waves are dependency/lock driven).
cap: auto

tasks:
  - id: t-1
    title: "..."
    agent: worker|orchestrator
    scope: ["path/**"]
    depends_on: []
    subtasks: []

waves:
  - id: w1
    tasks: [t-1, t-2]
  - id: w2
    tasks: [t-3]

integration:
  boundary: patch-first
  order: [t-1, t-2, t-3]
  conflict_policy: rebase-author

warnings:
  - "..."
```

### Example 1: simple worker wave
```yaml
schema_version: 1
kind: OrchPlan
created_at: "2026-01-26T00:00:00Z"
source:
  kind: list
  locator: "invocation"
cap: auto
tasks:
  - id: run
    title: "Implement mol-mesh-run"
    agent: worker
    scope: ["codex/formulas/mol-mesh-run/**"]
    depends_on: []
  - id: arm
    title: "Implement mol-mesh-arm"
    agent: worker
    scope: ["codex/formulas/mol-mesh-arm/**"]
    depends_on: []
waves:
  - id: w1
    tasks: [run, arm]
integration:
  boundary: patch-first
  order: [run, arm]
  conflict_policy: rebase-author
warnings: []
```

### Example 2: orchestrator-of-orchestrators
```yaml
schema_version: 1
kind: OrchPlan
created_at: "2026-01-26T00:00:00Z"
source:
  kind: list
  locator: "invocation"
cap: auto
tasks:
  - id: scripts
    title: "Scripts workstream"
    agent: orchestrator
    scope: ["codex/scripts/mesh-*"]
    depends_on: []
    subtasks:
      - id: ws
        title: "Implement mesh-workspace"
        agent: worker
        scope: ["codex/scripts/mesh-workspace"]
        depends_on: []
      - id: gates
        title: "Implement mesh-gates"
        agent: worker
        scope: ["codex/scripts/mesh-gates"]
        depends_on: []
  - id: docs
    title: "Docs updates"
    agent: worker
    scope: ["codex/skills/mesh/**"]
    depends_on: []
waves:
  - id: w1
    tasks: [scripts, docs]
integration:
  boundary: patch-first
  order: [scripts, docs]
  conflict_policy: rebase-author
warnings: []
```

## Workflow
1. Confirm explicit invocation; if unclear, ask.
2. Source detection (pick exactly one; do not merge sources):
   - Task list in invocation text (preferred).
   - Else `SLICES.md` if present.
   - Else `bd` if `.beads/` exists.
   - Else latest `plan-N.md`.
3. Extract tasks from the chosen source.
4. Normalize tasks:
   - Ensure each task has an `id`.
   - Validate `depends_on` references; if unknown IDs exist, ask.
   - Enforce orchestrator rule: only `agent=orchestrator` when `subtasks` is provided.
5. Schedule waves (see algorithm below).
6. Emit OrchPlan v1 YAML.
7. Emit pipelines (PLANS + SLICES) as applicable.

## Scheduling algorithm (parallelism-first)
Build waves using dependency readiness and `scope` locks:

1. Build a DAG from `depends_on` edges.
2. Maintain `ready` = unscheduled tasks whose deps are all scheduled.
3. While tasks remain:
   - Treat missing `scope` as overlapping everything (i.e. it can only be scheduled alone).
   - Pick a maximal subset of `ready` whose `scope` locks do not overlap (greedy is fine).
   - If `cap` is a number, limit the wave to `cap` tasks.
   - Remove scheduled tasks from the pool; proceed to next wave.

When you must choose between conflicting tasks (overlapping scope or cap pressure), use tie-breaks:
1. Priority (if present): 0/P0 first.
2. Kind order (if present): task > bug > feature > chore > epic > docs > question.
3. Role (if present): contract/checkpoint > integration > implementation.
4. Unlock count: tasks that unblock more other tasks in this plan.
5. Risk/hardness/blast (if present): prefer lower risk, smaller blast radius, and clearer scope.
6. Stable order: preserve the source order.

Always emit warnings when:
- Parallelism was reduced due to missing `scope`.
- A `depends_on` points at an unknown ID.
- A task declared `agent=orchestrator` without `subtasks`.

## Source adapters (extraction only)

### A) `SLICES.md`
- Parse each slice YAML record.
- Candidates: leaf slices with `status: open` and no unmet `blocks` deps.
- Do not rewrite `SLICES.md` (plan-only).
- If slices do not provide `scope`, expect sequential scheduling and warn.

### B) `bd` (beads)
`bd` is an optional source when `.beads/` exists.

Read-only commands:
- Active work: `bd list --status in_progress --limit 50`
- Ready work: `bd ready`
- Inspect: `bd show <id>`

Extraction notes:
- Treat `blocks` deps as `depends_on`.
- Treat `tracks`/`related` as soft ordering (tie-break only).
- Never run `bd update`, `bd comments add`, `bd dep add`, or `bd close` from `$select`.

### C) `plan-N.md`
`plan-N.md` is treated as planning context, not a task source.
If no better source is available, emit a PLANS/SLICES pipeline (below) and an empty OrchPlan (with warnings).

## Pipelines
`$select` may emit these pipelines alongside the OrchPlan to drive planning artifacts.

### PLANS pipeline (manual)
Goal: iterate `plan-N.md` until `$gen-plan` says `Plan is ready.`

1. If no `plan-N.md` exists: run `$gen-plan` (it will ask clarifying questions, then create `plan-1.md`).
2. Re-run `$gen-plan` to create `plan-(N+1).md` until it replies exactly `Plan is ready.`

### SLICES pipeline (manual)
Goal: keep iterating until **all slices are `status: closed`**.

1. Run `$slice` to create/repair `SLICES.md` (generate mode).
2. Repeat until all slices are closed:
   - Run `$slice` (next mode) to choose the next slice.
   - Implement that slice.
   - Update `SLICES.md`: set the slice `status: closed` and record its verification.

### Optional `$loop` form
These are convenience drivers for repetition; they are optional.

PLANS (loop-ready):
```text
- $gen-plan
Stop when: The assistant replies exactly "Plan is ready."
```

SLICES (loop-ready; serial execution):
```text
- $slice (next)
- Implement the selected slice; update SLICES.md to mark it closed with verification.
Stop when: All slices in SLICES.md have status: closed.
```

## Output
- Always emit OrchPlan v1 (or an empty plan + warnings if no actionable tasks exist).
- If the chosen source is empty/non-viable and a fallback source exists, stop and ask before falling back.
