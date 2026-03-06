---
name: teams
description: "Coordinate agent teams (multi-session) as the native Codex delegation workflow for composite work: decompose, challenge, and parallelize with `update_plan`, `spawn_agent`, and built-in `explorer`/`worker` roles. Hand only homogeneous leaf batches to `$mesh`."
---

# teams

## Intent

Use `$teams` when a task is still composite and parallelism helps, but keep the workflow aligned with how Codex actually works:

- `update_plan` tracks the shared checklist.
- `spawn_agent` handles heterogeneous delegation.
- `send_input`, `resume_agent`, `wait`, and `close_agent` manage running agents.
- `explorer` answers specific codebase questions.
- `worker` owns bounded execution with explicit ownership.

Canonical name: use `$teams` in policy text and examples; treat `$team` as a user alias.

Plan first, execute second: use `$teams` to shape or challenge the work, then delegate bounded leaf tasks.

## Composite vs Leaf Fit

Use `$teams` for composite work:

- the task still needs decomposition, comparison, sequencing, or shared judgment
- you want parallel research, review, challenge, or design before choosing a path
- you have several bounded sidecar tasks that are not one repeated row template

Do not reach for `$teams` just because multiple tools exist. If the work is already one repeated row template, use `$mesh` instead.

## When To Use `$teams`

Use `$teams` when:

- The user explicitly asks for teammates, an agent team, or a parallel approach.
- You have multiple independent questions that explorers can answer in parallel.
- You have bounded, file-disjoint implementation slices that workers can own.
- You want parallel review, comparison, or challenge before choosing a direction.
- You need help turning a composite task into a set of leaf tasks.

Stay local instead when:

- The next critical-path step is urgent and blocked on one task you can do directly.
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

1. Make a short local plan with `update_plan` and decide the immediate critical-path step.
2. Identify the composite parts and reshape them into bounded leaf tasks.
3. Keep the blocking next step local; delegate only sidecar work that can run in parallel.
4. Pick the right role:
   - `explorer` for specific repository questions
   - `worker` for bounded edits or verification with explicit ownership
5. Give every teammate a concrete deliverable and, for code changes, a disjoint write scope.
6. While teammates run, continue non-overlapping local work.
7. Use `wait` only when you are actually blocked, and prefer longer waits over polling.
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

> Add a new CLI flag, update the docs, and add focused validation. Use teammates where helpful.

Good `$teams` execution:

- keep the parser or core behavior change local because it is on the critical path
- spawn one `worker` to update the docs in a disjoint file
- spawn one `worker` to add or adjust a focused test in a disjoint test file
- integrate both results locally and close the agents

Why `$teams`:

- the sidecar tasks are bounded and file-disjoint
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
- If a child task would need to negotiate scope with another child, it is not a leaf yet.
- If the remaining leaf tasks become a uniform row batch, hand that subset to `$mesh`.

## Forking And Ownership

- Default `fork_context: false` for fresh-eyes research or review.
- Use `fork_context: true` only when the child truly needs the same history, constraints, or diff.
- Tell `worker` agents they are not alone in the repo and must not revert other edits.
- Keep write scopes disjoint; one worker should own each mutating scope.
- Remember that `thread/fork` branches a conversation; it is not a substitute for worker delegation.

## Guardrails

- Do not delegate the immediate next blocking step if you can do it locally.
- Do not spawn agents for vague goals; narrow each ask to the artifact or answer you need next.
- Do not duplicate work between the lead and teammates.
- Do not treat `$teams` as a hidden batch engine; once the work is a uniform row job, hand it to `$mesh`.
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
