---
name: select
description: "Swarm-ready work selector: pick a source, refine into atomic tasks, and emit an OrchPlan (waves + delegation) plus optional pipelines. Plan-only; no writeback; orchestration-agnostic."
---

# Select

## Intent
Pick a task source, refine it into dependency-aware atomic tasks, schedule parallel waves when safe, and emit an **orchestration plan**.

This skill is **plan-only**:
- It does not implement changes (no code edits; no running workers).
- It does not mutate the task source (no `bd update`, no `SLICES.md` writes, no `plan-N.md` writes); instead it emits explicit manual writeback steps when needed (e.g., "mark <id> as in_progress").
- It is orchestration-agnostic: the output is a neutral plan schema (not tied to a specific executor).

It may also emit a small pipeline for driving planning artifacts into execution (manual steps; optionally loopable).

## Swarm-ready planning
`$select` is optimized for parallel multi-agent execution, so it prefers plans that are explicit, decomposed, and lock-safe.

- **Explore the codebase (read-only)** when needed to ground tasks in real paths/components and to set tight `scope` locks.
- **Ask clarifying questions** when multiple reasonable approaches exist; include a recommended default.
- **Atomic tasks**: each task should be independently executable by a single worker.
- **Workstream shaping**: identify major workstreams first, then map atomic tasks into those workstreams.
- **Role-aware shaping**: use role labels when useful (`contract`, `implementation`, `integration`, `checkpoint`) to improve sequencing and review quality.
- **Explicit dependencies**: prefer explicit edges over relying on implicit serialization via overlapping `scope`.
- **Delegation metadata**: include `scope` (required for safe parallelism), plus `location` and `validation` whenever possible.
- **Review before yielding**: run a separate reviewer-mode pass for missing deps/order/lock overlaps/validation gaps.

## Decomposition heuristics (parallelism quality)
When the selected source is coarse or linear, refine task structure before scheduling waves:

- Identify workstreams and keep task descriptions scoped to one workstream where possible.
- Create explicit `contract` tasks for API/schema/interface/config decisions that unblock multiple downstream tasks.
- Create explicit `checkpoint`/`integration` tasks as join points after parallel branches.
- Keep medium granularity: each task should be independently PR-able.
- Prefer explicit dependency edges to document true prerequisites and avoid accidental serialization.

## Dependency semantics (hard vs soft)
Use two dependency channels with distinct meaning:

- `depends_on`: hard prerequisite; contributes to DAG readiness and wave scheduling.
- `related_to`: soft ordering/context edge; never gates readiness or wave eligibility.

If ordering is uncertain or advisory ("nice first", "reduces rework"), prefer `related_to` over `depends_on`.

## Invocation directives (optional)
If present, interpret these directives from the invocation text:

- `mode`: `both|triage|new`
  - `both` (default): triage `in_progress` first; then select new work.
  - `triage`: only triage `in_progress` and recommend close/reopen/continue.
  - `new`: skip triage and select new work (still warn about `in_progress`).
- `max_tasks`: `auto|<int>`
  - If omitted: default `1` for queue sources (`slices`, `beads`); otherwise `auto`.
  - Applies after triage decisions.
- `review`: `required|auto|off`
  - `required` (default): run a reviewer pass and iterate until it passes (or stop+ask if blocked).
  - `auto`: run one reviewer pass; fix what you can; proceed with remaining warnings.
  - `off`: skip the reviewer pass.

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
   - Canonicalize ids/depends_on/related_to (trim, lowercase, drop leading `#`).
   - If a `depends_on` is unknown, try to map it to a **unique** known id via a numeric suffix alias (e.g., `1` -> `t-1`, `sl-1`) or an exact canonical match.
   - If resolved, replace the dep with the canonical id and suppress the unknown-dep warning.
2. **Scope normalization (safe)**:
   - Normalize each `scope` entry: trim whitespace; drop a leading `./` (normalize `./` to `.`); collapse repeated `/`; remove a trailing `/` (except `/`).
   - Record as `auto_fix: scope_normalize` if any scope entry changed.
3. **Scope inference (conservative)**:
   - If `scope` is missing, scan `id`/`title`/`subtasks` for explicit path or glob tokens (contain `/`, `**`, or a file extension).
   - Only adopt tokens that are existing paths or obvious globs; prefer the narrowest non-overlapping set.
   - If inferred, set `scope` and suppress the missing-scope warning.
4. **Orchestrator downgrade**:
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
  - Conservative overlap check: compare **lock roots**, not raw strings.
    - For each `scope` entry: normalize it (drop leading `./`; collapse `/`), drop a trailing `/**` or `/**/*`, then take the prefix up to the first glob metachar (`*`, `?`, `[`).
    - Treat overlap if any lock root is equal OR one lock root is a path-prefix of another.
- Tasks missing `scope` are treated as overlapping everything and therefore scheduled alone.
  - Warn `missing_scope` only when it affects this plan's wave packing.
  - Hint: add a narrow `scope` list (paths/globs) to unlock parallel waves.
- Tasks with overly-broad `scope` are treated as overlapping everything and therefore scheduled alone.
  - Broad examples: `""`, `.`, `./`, `/`, `*`, `**`, `**/*`.
  - Warn `broad_scope` only when it affects this plan's wave packing.
- If tasks must be serialized due to overlapping lock roots, prefer an explicit `depends_on` edge to make the order intentional.
  - Warn `implicit_order` only when lock roots are nested (strict prefix), the tasks are otherwise dependency-independent (no DAG path), and the order was chosen by tie-breaks/stable order.

## Delegation readiness (recommended)
Parallel waves are only useful if each task is independently executable by a worker.

- Prefer tasks that include:
  - `location`: where to work (paths/globs; navigation only; does not affect scheduling)
  - `validation`: how to prove done (commands/checks; does not affect scheduling)
- If emitting any wave with 2+ tasks and that wave contains at least one task with `validation`, warn `missing_validation` for tasks in that wave that lack `validation`.

## Claiming selected work (required)
When `$select` selects work to *start now* (i.e., the tasks in the first scheduled wave `waves[0]`), it must also emit a **claim** so other planners/executors do not pick the same work concurrently.

- If the chosen source supports status, the claim is: set the selected tasks to an in-progress status using the source's spelling.
  - Canonical token: `in_progress`
  - Accept common variants as equivalent when reading/triaging: `in progress`, `in-progress`, `in_progress`
  - When emitting a claim, prefer the token already used by the source; otherwise default to `in_progress`.
- If the source is `list` or `plan`, emit `claim: none`.

This is still plan-only: `$select` does not perform the writeback; it spells out what to change.

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

# Optional. Human/worker context only (does not affect scheduling).
prereqs: []
risks: []

tasks:
  - id: t-1
    title: "..."
    description: "..."          # optional
    workstream: "..."           # optional
    role: contract|implementation|integration|checkpoint  # optional
    parallelism_impact: "unlocks <n> tasks"  # optional best-effort
    agent: worker|orchestrator
    scope: ["path/**"]
    location: ["path/file"]     # optional
    validation: ["..."]         # optional
    depends_on: []
    related_to: []              # optional non-gating links
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
- `claim`: `mark <in_progress token> <id,...>` OR `already <in_progress token> <id>` OR `none`
- `counts`: totals for the chosen source (at minimum: leaf, ready, blocked, in_progress)
- `pick`: selected task id + 3-10 word reason
- `next2`: next two candidates (or `none`) + 3-10 word reason each
- `waves`: (recommended when tasks were scheduled) `N` + a compact wave listing (e.g. `w1[t-1,t-2]; w2[t-3]`)
- `review`: `pass|warn|skipped|blocked` + 0-6 word note
- `warnings`: list count + top 1-3 keys (e.g. `unknown_deps`, `status_drift`, `cycle`, `broad_scope`, `implicit_order`, `missing_validation`, `linear_graph`, `missing_role`, `missing_checkpoint`)
- `auto_fix`: list count + top 1-3 keys (e.g. `dep_alias`, `scope_normalize`, `scope_infer`)

## Procedure (high-level)
1. Resolve invocation directives (mode/max_tasks/cap).
2. Source detection (pick exactly one; do not merge sources).
3. Read the corresponding adapter spec (above) and extract tasks.
4. If tasks are too coarse or missing metadata required for safe parallelism, refine them:
   - Decompose into atomic tasks with explicit `depends_on`.
   - Identify workstreams and annotate `workstream` where useful.
   - Insert `contract` tasks when they can unlock parallel implementation branches.
   - Insert `checkpoint`/`integration` tasks as explicit join points across branches.
   - Encode soft ordering/context in `related_to` instead of `depends_on`.
   - Populate `scope` locks (tight paths/globs), plus `location` and `validation` where possible.
   - Keep each task independently PR-able (medium granularity).
   - Explore the repo (read-only) and consult authoritative docs when needed.
   - Stop and ask targeted questions if blocked by ambiguity.
5. Normalize tasks: ensure `id`; apply orchestrator rule; treat unknown deps as blocked (pending auto-remediation).
6. Run warning auto-remediation (above); finalize warnings.
7. Schedule waves using `depends_on` + `scope` locks.
7.5. If selecting new work, compute `claim` from `waves[0]` and emit instructions to mark those tasks in-progress in the source (when the source supports status).
8. Reviewer pass (per `review`): check deps/order/locks/validation/delegation gaps; revise as needed.
   - Detect unnecessary linear chains and downgrade advisory edges from `depends_on` to `related_to` when safe.
   - Require explicit roles/workstreams in multi-wave plans when inference is feasible.
   - Require checkpoint/integration joins when multiple parallel implementation branches converge.
   - In reviewer mode: do not expand scope; do not redesign; only close gaps and reduce risk.
   - If `review=required`: iterate until `review: pass` OR stop+ask if blocked.
9. Emit OrchPlan v1 YAML (always) + Decision Trace (required). Add pipelines only when useful.

## Scheduling algorithm (parallelism-first)
Build waves using dependency readiness and `scope` locks:

1. Build a DAG from `depends_on` edges only (`related_to` is non-gating and excluded from DAG readiness).
2. Maintain `ready` = unscheduled tasks whose deps are all scheduled.
3. While tasks remain:
    - Treat missing `scope` as overlapping everything (i.e. it can only be scheduled alone).
    - Treat overly-broad `scope` locks (`""`, `.`, `./`, `/`, `*`, `**`, `**/*`) as overlapping everything.
    - Pick a maximal subset of `ready` whose `scope` lock roots do not overlap (greedy is fine).
    - If `cap` is a number, limit the wave to `cap` tasks.
    - Remove scheduled tasks from the pool; proceed to next wave.

When you must choose between conflicting tasks (overlapping scope or cap pressure), use tie-breaks:
1. Priority (if present): 0/P0 first.
2. Kind order (if present): task > bug > feature > chore > epic > docs > question.
3. Role (if present): contract/checkpoint > integration > implementation.
4. Unlock count: tasks that unblock more other tasks in this plan.
5. Delegation readiness: prefer tighter `scope` and explicit `validation`.
6. Risk/hardness/blast (if present): prefer lower risk, smaller blast radius, and clearer scope.
7. Stable order: preserve the source order.

Emit warnings when unresolved (noise-controlled; warn only when it affects this OrchPlan):
- `missing_scope`: a task missing `scope` prevented adding at least one other ready task to the same wave.
- `broad_scope`: a task with overly-broad `scope` prevented adding at least one other ready task to the same wave.
- `implicit_order`: two dependency-independent tasks had nested lock roots and were concurrently ready; order chosen by tie-breaks/stable order.
- `missing_validation`: a parallel wave mixed tasks with and without `validation`.
- `unknown_deps`: a `depends_on` points at an unknown ID.
- `orchestrator_without_subtasks`: a task declared `agent=orchestrator` without `subtasks`.
- `linear_graph`: the dependency graph is mostly chain-like and a safe split into workstreams/contracts/checkpoints appears possible.
- `missing_role`: multi-wave plan lacks role annotations where they are needed for reasoning/review.
- `missing_checkpoint`: multiple parallel implementation branches have no explicit integration/checkpoint join.
If a warning is auto-remediated, omit it from `warnings` and list it under `auto_fix` (except orchestrator downgrade, which must still warn).

## Examples (synthesized)

### Example A: clean parallel wave (list source)
```yaml
schema_version: 1
kind: OrchPlan

created_at: "2026-02-02T00:00:00Z"

source:
  kind: list
  locator: "invocation"

cap: auto

tasks:
  - id: cfg
    title: "Add config loader"
    agent: worker
    scope: ["src/config/**"]
    location: ["src/config/loader.ts", "src/config/index.ts"]
    validation: ["npm test -w config"]
    depends_on: []
    subtasks: []
  - id: ui
    title: "Update settings UI"
    agent: worker
    scope: ["src/ui/**"]
    location: ["src/ui/Settings.tsx"]
    validation: ["npm test -w ui"]
    depends_on: []
    subtasks: []
  - id: wire
    title: "Wire config into UI"
    agent: worker
    scope: ["src/app/**"]
    location: ["src/app/bootstrap.ts"]
    validation: ["npm test"]
    depends_on: [cfg, ui]
    subtasks: []

waves:
  - id: w1
    tasks: [cfg, ui]
  - id: w2
    tasks: [wire]

integration:
  boundary: patch-first
  order: [cfg, ui, wire]
  conflict_policy: rebase-author

warnings: []
```

Decision Trace:
- source: list (invocation)
- mode: both; max_tasks=auto
- triage: none
- claim: none
- counts: leaf=3 ready=2 blocked=1 in_progress=0
- pick: cfg; unblocks wire; parallel-safe scope
- next2: ui; parallel-ready; disjoint scope
- waves: 2 w1[cfg,ui]; w2[wire]
- review: pass
- warnings: 0
- auto_fix: 0

### Example B: parallel wave with mixed validation + broad scope
```yaml
schema_version: 1
kind: OrchPlan

created_at: "2026-02-02T00:00:00Z"

source:
  kind: list
  locator: "invocation"

cap: auto

tasks:
  - id: api
    title: "Add /health endpoint"
    agent: worker
    scope: ["src/api/**"]
    location: ["src/api/health.ts", "src/api/router.ts"]
    validation: ["npm test -w api"]
    depends_on: []
    subtasks: []
  - id: docs
    title: "Document /health endpoint"
    agent: worker
    scope: ["docs/**"]
    location: ["docs/api.md"]
    depends_on: []
    subtasks: []
  - id: big
    title: "Repo-wide rename OldName -> NewName"
    agent: worker
    scope: ["**"]
    location: ["."]
    validation: ["rg -n \"OldName\" . || true"]
    depends_on: []
    subtasks: []

waves:
  - id: w1
    tasks: [api, docs]
  - id: w2
    tasks: [big]

integration:
  boundary: patch-first
  order: [api, docs, big]
  conflict_policy: rebase-author

warnings:
  - "missing_validation: [docs]"
  - "broad_scope: [big]"
```

Decision Trace:
- source: list (invocation)
- mode: both; max_tasks=auto
- triage: none
- claim: none
- counts: leaf=3 ready=3 blocked=0 in_progress=0
- pick: api; explicit validation; tight scope
- next2: docs; parallel-ready; missing validation
- waves: 2 w1[api,docs]; w2[big]
- review: warn missing_validation,broad_scope
- warnings: 2 missing_validation,broad_scope
- auto_fix: 0

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
