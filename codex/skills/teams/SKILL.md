---
name: teams
description: "Coordinate agent teams (multi-session) as the native Codex delegation workflow for composite work: decompose, challenge, and parallelize the full ready wave with `update_plan`, `spawn_agent`, and built-in `explorer`/`worker` roles. Hand only homogeneous leaf batches to `$mesh`."
---

# teams

## Intent

Use `$teams` when a task is still composite and parallelism helps, but keep the workflow aligned with how Codex actually works:

- `update_plan` tracks the shared checklist.
- `spawn_agent` handles heterogeneous delegation.
- `send_input`, `resume_agent`, `wait`, and `close_agent` manage running agents.
- `explorer` answers specific codebase questions.
- `worker` owns bounded execution with explicit ownership.
- Custom roles from `codex/agents/` are specialist edges only: `selector`, `coder`, `fixer`, `prover`, `integrator`, and peripheral `joiner`.
- Deprecated shims (`reducer`, `mentor`, `locksmith`, `applier`) are compatibility-only and should not receive new work.

Canonical name: use `$teams` in policy text and examples.

Plan first, execute second: use `$teams` to shape or challenge the work, then delegate bounded leaf tasks.

## Composite vs Leaf Fit

Use `$teams` for composite work:

- the task still needs decomposition, comparison, sequencing, or shared judgment
- you want parallel research, review, challenge, or design before choosing a path
- you have several bounded sidecar tasks or disjoint core branches that are not one repeated row template

Do not reach for `$teams` just because multiple tools exist. If the work is already one repeated row template, use `$mesh` instead.

## When To Use `$teams`

Use `$teams` when:

- The user explicitly asks for teammates, an agent team, or a parallel approach.
- You have multiple independent questions that explorers can answer in parallel.
- You have bounded, file-disjoint implementation slices that workers can own.
- You want parallel review, comparison, or challenge before choosing a direction.
- You need help turning a composite task into a set of leaf tasks.

Stay local instead when:

- There is only one ready branch and no second independent branch worth spawning yet.
- The work is tiny, tightly coupled, or not decomposed yet.
- Multiple agents would need to mutate the same files.

Use `$mesh` instead when:

- The user explicitly asks for `$mesh`.
- The workload is homogeneous and row-shaped: one file, row, or item per worker.
- `spawn_agents_on_csv` is a better fit than long-lived teammates.

## Native Architecture Fit

- Codex is thread-centric: public integrations use `thread/start`, `thread/resume`, `thread/fork`, and `turn/start`.
- Collaboration activity appears as `collabToolCall` items, not as a separate public teams protocol.
- `$teams` should therefore stay close to the native collab tools and roles instead of inventing a second orchestration stack.

## Recommended Workflow

1. Make a short local plan with `update_plan` and identify the current ready set, not just the next critical-path step.
2. Identify the composite parts and reshape them into bounded leaf tasks.
3. Keep synthesis, integration, and overlapping-write work local; dispatch every dependency-independent ready branch before the first blocking `wait`.
4. Pick the right role:
   - `explorer` for specific repository questions
   - `worker` for bounded edits or verification with explicit ownership
   - `selector` only for explicit `$select`-class source shaping
   - `coder` only for parse-first author/judge orchestration when specialist output is actually needed
   - `fixer` for mandatory winner review/repair when you would otherwise chain reviewer + mentor behavior
   - `prover` for apply-plus-proof in a temp worktree
   - `integrator` for scoped delivery packaging after proof
   - `joiner` only for GH-only PR routing workflows
5. Give every teammate a concrete deliverable and, for code changes, a disjoint write scope.
6. While teammates run, continue non-overlapping integration prep, review, or another ready local task.
7. Use `wait` only when you are actually blocked, prefer longer waits over polling, and do not immediately wait after the first spawn if more ready branches remain.
8. Reuse context with `send_input` or `resume_agent` when follow-up belongs with the same teammate.
9. Review, integrate, and close agents when they are no longer needed.

## Concrete Examples

### Example 1: Parallel repo research

Request:

> Compare the thread API with the collab tool surface. Have one teammate inspect docs and another inspect runtime code, then recommend the native path.

Good `$teams` execution:

- keep the recommendation and final synthesis local
- spawn one `explorer` to inspect API docs and examples
- spawn one `explorer` to inspect runtime handlers and tool specs
- wait only when blocked, then combine both findings into one recommendation

Why `$teams`:

- the work is parallel and heterogeneous
- the answer still needs shared judgment before execution

### Example 2: Scoped implementation with disjoint ownership

Request:

> Add a new config-backed CLI flag that touches parser wiring, config loading, help/completion output, and focused validation. Use teammates where helpful.

Good `$teams` execution:

- keep final synthesis and any overlapping edits local
- spawn one `worker` for parser/flag wiring in a disjoint CLI scope
- spawn one `worker` for config loading changes in a disjoint config scope
- spawn one `worker` for help/completion output in a disjoint shell/help scope
- spawn one `worker` for focused validation in a disjoint test scope
- wait only after the full ready wave is in flight, then integrate and close the agents

Why `$teams`:

- the first ready wave has multiple disjoint core branches, not just sidecars
- the work is not one repeated row template, so `$mesh` would be the wrong tool

### Example 3: Handoff from `$teams` to `$mesh`

Request:

> Audit 300 markdown files for missing frontmatter and export one result row per file.

Good split:

- use `$teams` or local work first to decide the audit rule, CSV columns, and output fields
- once planning is complete, hand the file list to `$mesh`
- let `$mesh` run one audit per row and review the output CSV locally

Why the handoff:

- the shaping work is composite
- the remaining execution is a homogeneous leaf batch

## Decomposition Rules

- Separate planning from execution: do the shaping work before you fan out.
- Prefer leaf tasks with a single artifact, answer, or bounded edit scope.
- When two or more ready leaf tasks are dependency-independent, prefer launching them together and use later checkpoint or integration tasks to join them.
- If a child task would need to negotiate scope with another child, it is not a leaf yet.
- If the remaining leaf tasks become a uniform row batch, hand that subset to `$mesh`.

## Forking And Ownership

- Default `fork_context: false` for fresh-eyes research or review.
- For parse-first author cohorts, run `$parse` once in the parent, freeze the worker packet, and keep `fork_context=false` unless a specific child truly needs the same history, constraints, or diff.
- Use `fork_context: true` only when the child truly needs the same history, constraints, or diff.
- Tell `worker` agents they are not alone in the repo and must not revert other edits.
- Keep write scopes disjoint; one worker should own each mutating scope.
- Remember that `thread/fork` branches a conversation; it is not a substitute for worker delegation.

## Guardrails

- Do not keep core ready branches local just because they feel central; keep only synthesis, integration, or overlapping-write work local.
- Do not spawn agents for vague goals; narrow each ask to the artifact or answer you need next.
- Do not wait immediately after the first spawn when additional ready branches remain.
- Do not duplicate work between the lead and teammates.
- Do not treat `$teams` as a hidden batch engine; once the work is a uniform row job, hand it to `$mesh`.
- Do not spawn deprecated shims for fresh work; replace `reducer` with `coder approach=reduce`, `mentor` with `fixer`, `applier` with `prover`, and keep write coordination local instead of using `locksmith`.
- Do not leave agents running after their contribution has been integrated unless the user explicitly wants them kept alive.

## Completion Criteria

Close a `$teams` run only when:

- each spawned agent produced the requested artifact or answer
- the lead synthesized the results into one decision, patch, or recommendation
- unneeded agents were closed

If you cannot meet one of these, report what is missing.

## Final Response

When teams actually ran, include a short `Orchestration Ledger` section in prose.

Use concise event-only lines such as:

- `Skills used`
- `Subagents`
- `Artifacts produced`
- `Cleanup status`

Omit the section entirely when no team orchestration ran.

## Handoff To `$mesh`

If teams discovers that the remaining work is a uniform batch job, hand off narrowly:

- state that planning is complete and the remaining work is leaf execution
- state why the work is row-shaped and independent
- provide the row schema or CSV columns
- provide the instruction template
- specify the expected output fields

Do not invent extra lane, quorum, or state-machine protocols unless the runtime actually provides them.
