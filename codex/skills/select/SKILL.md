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

## Invocation directives (optional)
If present, interpret these directives from the invocation text:

- `mode`: `both|triage|new`
  - `both` (default): triage `in_progress` first; then select new work.
  - `triage`: only triage `in_progress` and recommend close/reopen/continue.
  - `new`: skip triage and select new work (still warn about `in_progress`).
- `max_tasks`: `auto|<int>`
  - If omitted: default `1` for queue sources (`slices`, `beads`); otherwise `auto`.
  - Applies after triage decisions.

## Source precedence
When multiple sources exist, pick exactly one using this precedence:
1. Explicit user-provided task list in the invocation text.
2. `SLICES.md` (if present and parseable).
3. `bd` issues (if `.beads/` exists and `bd` works).
4. `plan-N.md` (highest N, repo root).

If the highest-precedence source exists but has **no viable tasks**, do not default to an empty plan.
- First try to select an **unblocker** (a blocked leaf task that would unlock future ready work).
- Only stop+ask about falling back if the source is empty/unparseable, or if *everything* is closed/unschedulable.

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
- If a dependency refers to an unknown task ID, treat the referencing task as **blocked**; warn only after auto-remediation fails.
- If the dependency graph is cyclic/unschedulable, schedule any work outside the cycle (if possible) and emit a warning.
- If the source is present but unparseable/empty, stop and ask before falling back.

## Warning auto-remediation (read-only)
Before emitting warnings, attempt safe, deterministic fixes that do not mutate sources.

Order (stop when resolved):
1. **ID normalization + aliasing**:
   - Canonicalize ids/depends_on (trim, lowercase, drop leading `#`).
   - If a `depends_on` is unknown, try to map it to a **unique** known id via a numeric suffix alias (e.g., `1` -> `t-1`, `sl-1`) or an exact canonical match.
   - If resolved, replace the dep with the canonical id and suppress the unknown-dep warning.
2. **Scope inference (conservative)**:
   - If `scope` is missing, scan `id`/`title`/`subtasks` for explicit path or glob tokens (contain `/`, `**`, or a file extension).
   - Only adopt tokens that are existing paths or obvious globs; prefer the narrowest non-overlapping set.
   - If inferred, set `scope` and suppress the missing-scope warning.
3. **Orchestrator downgrade**:
   - If `agent: orchestrator` lacks `subtasks`, downgrade to `worker`.
   - This is a semantic change; still emit a warning even after the fix.

Record auto-fixes in the Decision Trace (`auto_fix`) and keep `warnings` for unresolved issues.

## Source adapters (read one; do not improvise)
After you choose the source kind, read and apply exactly one adapter spec:
- list: `codex/skills/select/ADAPTER_LIST.md`
- slices: `codex/skills/select/ADAPTER_SLICES.md`
- beads: `codex/skills/select/ADAPTER_BEADS.md`
- plan: `codex/skills/select/ADAPTER_PLAN.md`

Regression fixtures live in `codex/skills/select/FIXTURES.md`.

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
If `agent: orchestrator` is set but `subtasks` is empty/missing, downgrade to `agent: worker`, record an auto-fix, and warn.

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

## Decision Trace (required)
After the OrchPlan YAML, emit a short plaintext trace (tight and structured):

- `source`: chosen source kind + locator
- `mode`: resolved `mode` + resolved `max_tasks`
- `triage`: if any `in_progress` was seen, state: `continue <id>` OR `recommend close <id>` OR `recommend reopen <id>` OR `none`
- `counts`: totals for the chosen source (at minimum: leaf, ready, blocked, in_progress)
- `pick`: selected task id + 3-10 word reason
- `next2`: next two candidates (or `none`) + 3-10 word reason each
- `warnings`: list count + top 1-3 keys (e.g. `unknown_deps`, `status_drift`, `cycle`)
- `auto_fix`: list count + top 1-3 keys (e.g. `dep_alias`, `scope_infer`, `orchestrator_downgrade`)

## Procedure (high-level)
1. Resolve invocation directives (mode/max_tasks/cap).
2. Source detection (pick exactly one; do not merge sources).
3. Read the corresponding adapter spec (above) and extract tasks.
4. Normalize tasks: ensure `id`; apply orchestrator rule; treat unknown deps as blocked (pending auto-remediation).
5. Run warning auto-remediation (above); finalize warnings.
6. Schedule waves using `depends_on` + `scope` locks.
7. Emit OrchPlan v1 YAML (always) + Decision Trace (required). Add pipelines only when useful.

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

Emit warnings when unresolved:
- Parallelism was reduced due to missing `scope`.
- A `depends_on` points at an unknown ID.
- A task declared `agent=orchestrator` without `subtasks`.
If a warning is auto-remediated, omit it from `warnings` and list it under `auto_fix` (except orchestrator downgrade, which must still warn).

## Source adapters (extraction only)
Adapter specs live in:
- `codex/skills/select/ADAPTER_LIST.md`
- `codex/skills/select/ADAPTER_SLICES.md`
- `codex/skills/select/ADAPTER_BEADS.md`
- `codex/skills/select/ADAPTER_PLAN.md`

## Pipelines
Pipelines live in `codex/skills/select/PIPELINES.md`.

## Output
- Always emit OrchPlan v1 YAML, then Decision Trace.
- If no actionable source tasks exist, prefer selecting an unblocker; only then emit an empty plan + warnings.
- If the chosen source is empty/non-viable and a fallback source exists, stop and ask before falling back.
