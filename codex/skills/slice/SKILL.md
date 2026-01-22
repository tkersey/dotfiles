---
name: slice
description: "Slice a plan into a DAG in SLICES.md; iteratively pick the next slice to expand using the select rubric."
---

# Slice

## Overview
`slice` is a plan-space workflow that combines decomposition + dependency-graph discipline with selection/scoring,
and it writes/maintains a repo-root `SLICES.md` file.

Each invocation performs **one slicing move**:
1) select the next best slice to further decompose/refine, and
2) update `SLICES.md` accordingly.

Stop condition (global): the plan is fully sliced (cannot be meaningfully decomposed further).

## Inputs
- Required: a path to a plan markdown file (explicitly passed by the user).
- Optional: scope boundaries, sequencing constraints, priority guidance, and workflow constraints.

## Defaults (override if the user says otherwise)
- Parallel-first: build a DAG, not a single linear chain.
- `blocks` only for true prerequisites; use `tracks`/`related` for soft ordering.
- Medium granularity: each leaf slice should be independently PR-able.
- Include explicit contract slices (APIs/schemas/interfaces/config formats) to decouple workstreams.
- Include checkpoint/integration slices as join points (force feedback loops).

## `SLICES.md` (repo-root workspace)
- Path: `SLICES.md` at the repository root.
- Canonical: `SLICES.md` is the source of truth for slicing state.
- `slice` only reads the plan file and `SLICES.md`, and only writes to `SLICES.md`.

### Slice record format
Each slice is represented as a section containing a single YAML object with a consistent issue-record schema.

Conventions:
- IDs: `sl-<short-hash>` (stable within `SLICES.md`).
- `priority`: integer 0..4 (0 is highest).
- `issue_type`: `task|bug|feature|epic|chore|docs|question` (or custom string).
- `status`: `open|blocked|closed|tombstone` (or custom string).
- `dependencies`: list of `{type, depends_on_id}` objects.

Minimum recommended keys per slice:
- `id`, `title`, `status`, `priority`, `issue_type`
- `description`, `acceptance_criteria`, `notes` (can be empty strings but should converge)
- `dependencies` (omit or empty list)

Recommended metadata footer (in `notes`, used by selection/scoring):
```
Workstream: <name>
Role: contract | implementation | integration | checkpoint
Parallelism impact: unlocks <n> slices
```

Example slice:
```yaml
id: sl-1a2b3c4d
title: "Backend API: auth contract"
status: open
priority: 1
issue_type: task
description: |
  Decide and document the auth API surface so frontend/integration work can proceed.
acceptance_criteria: |
  - Document endpoints (request/response) including error shapes.
  - Define token/session lifecycle.
notes: |
  Workstream: Backend API
  Role: contract
  Parallelism impact: unlocks 3 slices
dependencies:
  - type: blocks
    depends_on_id: sl-deadbeef
```

## Workflow

### 0) Invocation gate
1. Confirm explicit invocation and that a plan path was provided.
2. Read the plan file.
3. Ensure `SLICES.md` exists; if missing, create it with:
   - a link/reference to the plan path, and
   - an empty `# Slices` section.

### 1) Parse current slicing state
1. Parse `SLICES.md` into slice records.
2. Compute derived properties (best-effort):
   - Leaf vs epic (has children via `parent-child` edges or a declared parent convention).
   - Blocked-by set: any `blocks` deps to slices that are not `closed`.
   - Ready-to-slice set: `status != closed/tombstone` AND no blocking deps.
3. Define “atomic” (cannot be sliced further) as:
   - medium-granularity PR-able,
   - clear acceptance criteria,
   - at least one verification signal (command or precise manual check), and
   - no obvious internal substructure that would become multiple PRs.

### 2) If no slices exist yet: initial slicing pass
If `SLICES.md` has no slice records:
1. Extract major workstreams, milestones, risks, and implied dependencies from the plan.
2. Create epics per workstream.
3. Create contract slices that unblock parallel work (API/schema/interface decisions).
4. Create initial implementation slices and checkpoint/integration slices.
5. Wire dependencies for true prerequisites only.
6. Stop after this single move (do not fully elaborate every slice in the first pass).

### 3) Select the next slice to expand (borrowed from `select`)
Selection rubric (adapted):
- Feature-first: if any ready slices are `issue_type=feature`, evaluate all ready features first.
- Type order (fallback): `task` > `bug` > `epic` > `chore`.
- Priority: 0 > 1 > 2 > 3 > 4.
- Risk: migrations, auth/security, infra, data loss/consistency, breaking API/CLI, perf regressions, ambiguous acceptance.
- Hardness: vague scope, multiple subsystems, unknown deps, heavy verification.
- Blast radius: widely used modules, shared config, CI/build pipeline, core user paths.
- Parallelism impact (balance with risk): prefer slices that unlock more blocked slices or establish a contract/checkpoint when risk is in the same tier.
- Soft deps: if a ready slice tracks/relates another ready slice, apply a soft penalty and prefer the tracked-first item.
- Tie-break: priority -> strongest signals -> earliest in-file order.

Scoring notes (lightweight):
- Base score comes from risk/hardness/blast/priority.
- Parallelism nudges (apply only within the same risk tier):
  - Role: contract/checkpoint +2; integration +1; implementation +0.
  - Unlock count: +1 per blocked slice unlocked (cap at +3).
  - Soft deps: -2 if it tracks/relates another ready slice; 0 otherwise.

Readiness gate:
- Never expand a slice if it requires missing prerequisites.
- If the prerequisite is a decision/contract, create a new contract slice and add a `blocks` edge.
- If the dependency is uncertain and would become a `blocks` edge, ask the human before adding it.

### 4) Perform one slicing move
For the selected slice:
1. If it is too large or multi-PR:
   - Split into 2–6 child slices.
   - Rewire dependencies so children inherit only necessary prerequisites.
   - Convert the parent to an `epic` (if it isn’t already) and connect children via `parent-child` (or an equivalent documented convention).
2. If it is already the right size but underspecified:
   - Fill in missing `description`, `acceptance_criteria`, and `notes` (including verification signals).
3. If it blocks parallelism:
   - Extract a contract slice and downgrade soft ordering to `tracks`/`related`.
4. Update `SLICES.md` only in the region needed for this move; avoid rewriting the entire file.

### 5) Global review (quick)
After the move:
- Audit the local dependency subgraph for parallelism; if mostly linear, refactor toward workstreams + contracts + join points.
- Ensure `blocks` edges are only true prerequisites.
- Ensure each leaf slice is independently PR-able and has acceptance + verification.

## Output
- Print: `Sliced <id>: <short rationale>`.
- List new/updated slice IDs.
- If no ready-to-slice items exist, report why (e.g., everything is `closed`, or remaining items are `blocked`) and ask targeted questions if needed.
- If the plan is fully sliced, report: `Slicing complete: no further meaningful decomposition found.`
