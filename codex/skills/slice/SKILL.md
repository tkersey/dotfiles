---
name: slice
description: "Slice a plan into a DAG in SLICES.md; validate it; pick and mark the next ready slice to execute."
---

# Slice

## Overview
`slice` is a plan-space workflow that turns a markdown plan into a **dependency-aware DAG** of PR-able slices in
a repo-root `SLICES.md`, and then uses that file as the canonical source of truth to pick the next slice to work on.

It supports two modes:
- **Generate mode**: create/repair `SLICES.md` from a plan and (re)build a sensible DAG, including explicit
  dependencies and subtask checklists.
- **Next mode**: validate `SLICES.md`, select the next ready slice to execute, mark it `in_progress`, and return
  it to the user as the work item.

Default behavior is **auto**:
- If `SLICES.md` is missing, invalid, or has zero slice records: run Generate mode.
- If `SLICES.md` is valid: run Next mode.

Important:
- Generate mode never auto-selects a work slice in the same invocation; it only writes `SLICES.md`.
  Selecting/starting work happens on a later explicit invocation (mode=`next` or auto when valid).
- In auto mode, selecting a slice only happens when `SLICES.md` is already valid at invocation start.

## Inputs
- Plan path (optional metadata in `SLICES.md`):
  - Provide on the first run to create/repair `SLICES.md`.
  - Not required for Next mode; `SLICES.md` is portable without it.
- Mode:
  - Not required; infer it from the invocation text + `SLICES.md` state.
  - If the human wants to force generate, they can say "generate"/"rebuild"/"regenerate".
  - If the human wants to force selection, they can say "next slice"/"what should I work on".
- Assignee (orchestrator id):
  - Used in Next mode to support concurrent `in_progress` slices (one per assignee).
  - If not available from `SLICES.md` header or invocation context, ask the human once.
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

### File header
`SLICES.md` should start with minimal metadata so Next mode can run without any plan reference:

```yaml
schema_version: 1
default_assignee: opencode
```

`default_assignee` is optional; if present, Next mode uses it as the orchestrator id. `plan_path` is optional metadata only.

### Slice record format
Each slice is represented as a section containing a single YAML object with a consistent issue-record schema.

Canonical markdown layout in `SLICES.md`:

````md
# Slices

## <title> (<id>)
```yaml
id: sl-...
...
```
````

Conventions:
- IDs: `sl-<short-hash>` (stable within `SLICES.md`).
- `priority`: integer 0..4 (0 is highest).
- `issue_type`: `task|bug|feature|epic|chore|docs|question` (or custom string).
- `status`: `open|in_progress|blocked|closed|tombstone`.
- `dependencies`: list of `{type, depends_on_id}` objects.
  - Allowed dependency types: `blocks|tracks|related`.

Recommended additions:
- `subtasks`: ordered checklist (2-10 items) for the slice's internal steps.
- `verification`: at least one concrete signal (command or manual check) that proves the slice is done.
- `parent_id`: optional; if present, this slice is a child of an epic.
- `assignee`: optional string; required when `status: in_progress`.

Minimum recommended keys per slice:
- `id`, `title`, `status`, `priority`, `issue_type`
- `description`, `acceptance_criteria`, `notes` (can be empty strings but should converge)
- `dependencies` (omit or empty list)

If `status: in_progress`, `assignee` is required.

If present, `subtasks` should be a YAML list of strings.

Epic/child convention:
- Prefer `parent_id` over encoding parent/child as dependencies.
- If any slice has `parent_id: <id>`, then `<id>` is an epic.
- Epics are organizational; do not add `blocks` edges between parent and child.

Recommended metadata footer (in `notes`, used by selection/scoring):
```
Workstream: <name>
Role: contract | implementation | integration | checkpoint
Parallelism impact: unlocks <n> slices
```

Role ↔ Double Diamond (guidance):
- `contract`: Define
- `implementation`: Develop / Deliver
- `integration` / `checkpoint`: Deliver

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
verification: |
  - Docs: open the spec and confirm all endpoints + error shapes are present.
subtasks:
  - Draft endpoint list and auth model.
  - Specify request/response JSON shapes.
  - Specify error shapes and token/session lifecycle.
notes: |
  Workstream: Backend API
  Role: contract
  Parallelism impact: unlocks 3 slices
dependencies:
  - type: blocks
    depends_on_id: sl-deadbeef
```

## Workflow

### 0) Invocation gate + mode selection
1. Confirm explicit invocation.
2. Determine mode (infer; do not require explicit flags):
   - If user explicitly asks to "generate" / "(re)build" slices: mode=`generate`.
   - If user explicitly asks for "next slice" / "what should I work on": mode=`next`.
   - Otherwise mode=`auto`.
3. If mode requires a plan path and it was provided, read the plan file.

### 1) Ensure + validate `SLICES.md`
1. If `SLICES.md` does not exist:
   - If no plan path is available, ask the human for it.
   - Otherwise create `SLICES.md` with header metadata and an empty `# Slices` section.
2. Validate `SLICES.md` (structural + semantic). Treat failures as:
   - Hard invalid (must repair before Next mode can proceed).
   - Warning (can proceed, but print warnings).

   Hard invalid checks:
   - Header: has `schema_version`.
   - Parseability: every slice section contains exactly one valid YAML object (mapping).
   - Required keys: each slice has at least `id,title,status,priority,issue_type`.
   - Priority sanity: `priority` is an int in 0..4.
   - Uniqueness: slice IDs are unique.
   - Status sanity: statuses are in the allowed set.
   - Dependency type sanity: dependency `type` is one of `blocks|tracks|related`.
   - Referentials: every `dependencies[*].depends_on_id` refers to an existing slice.
   - Epic referentials: if `parent_id` is present, it refers to an existing slice.
   - In-progress assignee: every `status: in_progress` slice has non-empty `assignee`.
   - In-progress uniqueness: at most one slice has `status: in_progress` per `assignee`.
   - In-progress readiness: an `in_progress` slice has no unmet `blocks` deps.
   - Dependency sanity: `blocks` edges are acyclic (toposort/DFS; if uncertain, ask).

   Warning checks:
   - `status: blocked` but no unmet `blocks` deps (auto flip to `open`).
   - `status: open` but has unmet `blocks` deps (recommend switching to `blocked`).
   - `status: closed` but has unmet `blocks` deps (probable bookkeeping bug).
   - Leaf slice missing `verification` or meaningful acceptance criteria.

   Normalization + auto-remediation (overlap with `$select`):
   - Apply deterministic normalization before hard-failing:
     1. ID normalization + aliasing: trim/lowercase IDs and `depends_on_id`, drop a leading `#`, and map unique numeric suffix aliases when unambiguous.
     2. Status token normalization: treat `in progress`, `in-progress`, and `in_progress` as equivalent; write back canonical `in_progress`.
     3. Safe status drift fix: keep auto-flip `blocked` -> `open` when no unmet `blocks` deps remain.
   - After normalization, unresolved unknown dependency IDs remain hard invalid.
   - Record applied fixes as `auto_fix` keys for Next-mode output.

   Ambiguity guardrails:
   - If validation failure requires human intent (e.g., missing `assignee` on an `in_progress` slice, or multiple
     `in_progress` slices for the same `assignee`), ask the human how to resolve before repairing.
3. If validation fails:
   - Switch to mode=`generate` (auto-repair) and (re)read the plan if available.
   - Stop after writing the repaired `SLICES.md`; do not select/mark any slice `in_progress`.

4. If mode=`auto` and `SLICES.md` contains zero slice records:
   - Switch to mode=`generate` and read the plan if provided.
   - Stop after writing `SLICES.md`.

Derived sets (best-effort):
- Leaf vs epic: epic if `issue_type=epic` OR any slice has `parent_id` pointing at it.
- Blocked-by set: any `blocks` deps to slices that are not `closed`.
- Ready-to-work set: `status in {open}` AND no blocking deps AND not epic.
- Ready-to-execute set: Ready-to-work AND meets the PR-able leaf criteria below.
- Unblocker candidates: blocked leaf slices ranked by highest unlock impact within the same risk tier.

Define “PR-able leaf” as:
- small enough for a single PR,
- clear acceptance criteria,
- `verification` (or an explicit verification signal inside `acceptance_criteria`),
- includes `subtasks` (checklist) OR is obviously single-step.

### 2) Generate mode: create/repair the DAG
Generate mode either creates the initial DAG or repairs an invalid DAG.

If `SLICES.md` has no slice records (or is being rebuilt):
1. Extract major workstreams, milestones, risks, and implied prerequisites from the plan.
2. Create epics per workstream.
3. Create contract slices that unblock parallel work (API/schema/interface decisions).
4. Create implementation slices and at least one checkpoint/integration slice per workstream.
5. For each slice, add `subtasks` (2-10 items) and at least one `verification` signal.
6. Wire dependencies:
   - `blocks`: hard prerequisites only (a consuming slice cannot be started safely without it).
   - `tracks`: soft ordering / "do this first if possible".
   - `related`: informational relationship only.
7. Stop after producing a usable DAG (do not exhaustively elaborate every slice in the first pass).

Generate mode does not mark any slice `in_progress`.

Dependency identification heuristics:
- Contracts block implementations that consume them (API/schema/CLI/interface decisions).
- Data model/migrations block anything that reads/writes the affected data.
- Infra/provisioning (env vars, secrets, DB setup, CI plumbing) blocks runtime/integration slices.
- Checkpoints/integration slices usually `track` multiple implementations; they rarely `block` them.
- If a dependency is uncertain and would become a `blocks` edge, ask the human before adding it.

### 3) Next mode: select the next slice to execute
If there are zero slice records:
- Report: `No slices found; run slice in generate mode with a plan path.`

Determine `self_assignee` (orchestrator id):
- Prefer `default_assignee` from the `SLICES.md` header if present.
- Otherwise infer from invocation context; if unknown, ask the human.

If there is already a slice with `status: in_progress` and `assignee: <self_assignee>`:
- Return that slice (do not pick a new one).

Otherwise, select the next slice from the Ready-to-execute set using the rubric below.

If Ready-to-execute is empty but Ready-to-work is non-empty, report that slices exist but are underspecified
(missing `verification` / acceptance) and recommend running Generate mode to enrich them.

If Ready-to-execute is empty and blocked leaf slices exist, return the top unblocker recommendation (do not mark it
`in_progress`) and identify the missing prerequisite slice(s) that must close first.

Selection rubric (adapted from `select`):
- Feature-first: if any ready slices are `issue_type=feature`, evaluate all ready features first.
- Type order (fallback): `task` > `bug` > `feature` > `chore` > `epic` > `docs` > `question`.
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
- Never select a slice for execution if it has missing prerequisites.
- Next mode is non-creative: do not add new slices or dependencies while selecting.
- If selection surfaces a missing decision/contract or an ambiguous prerequisite, switch to Generate mode to
  update the DAG and stop after writing `SLICES.md` (do not mark anything `in_progress`).

### 4) Update `SLICES.md`
If mode=`next` (or auto-selected next):
1. Mark the chosen slice `status: in_progress`.
2. Set `assignee: <self_assignee>` (required for `in_progress`).
3. Do not rewrite unrelated slices; apply the smallest possible edit.

If any safe normalization edits were identified during validation (e.g., auto flipping `blocked` -> `open` when
no `blocks` deps remain), apply them with minimal diff.

If mode=`generate` (or auto-selected generate):
1. If an existing slice is too large or multi-PR, split into 2-6 child slices.
2. Ensure each leaf slice has `subtasks` and `verification`.
3. Update `SLICES.md` with minimal diff when possible; if the file was invalid/unparseable, regenerate the
   `# Slices` section and preserve any unknown content in an `# Appendix (legacy)` section.

### 5) Global review (quick)
After any write:
- Audit the local dependency subgraph for parallelism; if mostly linear, refactor toward workstreams + contracts + join points.
- Ensure `blocks` edges are only true prerequisites.
- Ensure each leaf slice is independently PR-able and has acceptance + verification (+ subtasks when useful).
- Run a reviewer pass for overlap gaps from `$select`: unresolved unknown deps, cycle risk, and missing verification on likely near-term leaf work.

## Output
- If mode=`generate`: print `Generated slices: <n>` and list new/updated slice IDs.
- If mode=`generate` (including auto-repair): instruct the human to review `SLICES.md` and re-run `slice` later to pick work.
- If mode=`next`: print `Next slice: <id> - <title>` and include the selected slice YAML in full.
- If mode=`next`: include a compact `Selection Trace` with `counts`, `pick`, `next2`, `warnings`, and `auto_fix`.
- If no ready-to-work items exist, report why (everything `closed`, or remaining items are `blocked`) and ask targeted questions if needed.
- If no ready-to-work items exist but blocked leaf slices remain, also print `Top unblocker: <id> - <title>` with prerequisite IDs.

## Examples

Minimal `SLICES.md` skeleton (portable; no plan reference required):

````md
---
schema_version: 1
---

# Slices

## Backend Workstream (sl-0a1b2c3d)
```yaml
id: sl-0a1b2c3d
title: "Backend Workstream"
status: open
priority: 2
issue_type: epic
description: |
  Organizational epic for backend work.
acceptance_criteria: |
  - All child slices are closed.
verification: |
  - Review: all children of sl-0a1b2c3d are closed.
subtasks: []
notes: |
  Workstream: Backend
  Role: checkpoint
dependencies: []
```

## Backend API: auth contract (sl-1a2b3c4d)
```yaml
id: sl-1a2b3c4d
parent_id: sl-0a1b2c3d
title: "Backend API: auth contract"
status: open
priority: 1
issue_type: task
description: |
  Decide and document the auth API surface so other work can proceed.
acceptance_criteria: |
  - Document endpoints (request/response) including error shapes.
  - Define token/session lifecycle.
verification: |
  - Docs: open the spec and confirm endpoints + error shapes are present.
subtasks:
  - Draft endpoint list and auth model.
  - Specify request/response JSON shapes.
  - Specify error shapes and token/session lifecycle.
notes: |
  Workstream: Backend API
  Role: contract
dependencies: []
```

## Backend: implement auth endpoints (sl-2b3c4d5e)
```yaml
id: sl-2b3c4d5e
parent_id: sl-0a1b2c3d
title: "Backend: implement auth endpoints"
status: open
priority: 2
issue_type: feature
description: |
  Implement auth endpoints per the contract.
acceptance_criteria: |
  - Endpoints implemented and return expected responses.
verification: |
  - Run: <test command>
subtasks:
  - Implement routes + handlers.
  - Add tests.
notes: |
  Workstream: Backend
  Role: implementation
dependencies:
  - type: blocks
    depends_on_id: sl-1a2b3c4d
```
````
