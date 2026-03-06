# Local Codex orchestration guidance

Keep multi-agent work aligned with native Codex primitives.

## Native model

- Codex is thread-centric: public work centers on `thread/start`, `thread/resume`, `thread/fork`, and `turn/start`.
- Collaboration appears as `collabToolCall` items; there is no separate public teams protocol.
- `update_plan` is the main user-visible planning surface.
- Do not invent a second orchestration stack when the runtime already provides the primitive you need.

## Composite vs leaf tasks

- Treat a composite task as work that still needs decomposition, comparison, sequencing, or shared judgment.
- Treat a leaf task as one bounded answer or artifact with clear inputs, outputs, and ownership.
- Plan and decompose first; execute second.
- Borrow the tree-to-leaf mindset when it helps, but keep execution on native Codex tools rather than importing an external runtime.

## Routing

Apply these in order:

1. Explicit `$mesh`, CSV fanout, or an obvious row-batch workload -> use `$mesh`.
2. Explicit `$team` or `$teams` -> use `$teams`.
3. Multiple independent questions or file-disjoint sidecar tasks -> use `$teams`.
4. Otherwise stay local and execute directly.
5. Escalate to hybrid only when `$teams` discovers that the remaining work is a homogeneous leaf batch suitable for `$mesh`.

## Quick routing examples

- Choose `$team` / `$teams`: "Compare the thread API with the collab tool surface, then recommend the native path." The work still needs parallel research plus shared judgment.
- Choose `$team` / `$teams`: "Add a CLI flag while one teammate updates docs and another adds a focused test." The work has disjoint sidecar tasks, not one repeated row template.
- Choose `$mesh`: "Audit each file in this CSV for missing frontmatter and export one result row per file." The same bounded instruction runs independently per row.
- Choose `$mesh`: "Classify each support ticket in this CSV by area and urgency." The inputs are row-shaped and the outputs are structured per row.
- Borderline rule: if you still need to decide the rule, CSV columns, or output fields, start with `$team` / `$teams`; switch to `$mesh` only after planning is complete.

## `$teams`

- `$teams` is the native heterogeneous orchestration path.
- Use `update_plan`, `spawn_agent`, `send_input`, `resume_agent`, `wait`, and `close_agent`.
- Use built-in roles intentionally: `explorer` for focused questions, `worker` for bounded execution.
- Keep the immediate blocking step local when the next action depends on it.
- Delegate concrete sidecar work with explicit deliverables and disjoint write scopes.
- Default `fork_context: false`; use `true` only when the child truly needs the parent's exact context.
- While subagents run, continue non-overlapping local work.
- Close agents once their contribution is integrated.

## `$mesh`

- `$mesh` is the narrow homogeneous batch path over `spawn_agents_on_csv`.
- Use it only for already-shaped leaf rows that can run independently.
- Each worker must call `report_agent_job_result` exactly once.
- Planning and decomposition do not happen inside `$mesh`; they happen before the batch starts.
- Prefer structured outputs, optionally constrained with `output_schema`, then review the exported CSV locally or with `$teams`.
- If rows share mutable state, depend on each other, or need debate or design, stop and use `$teams` or local execution instead.

## Wait semantics

- `wait` is not a join; it returns when any agent reaches a final state.
- Avoid tight polling loops; wait only when you are actually blocked on the remaining agents.

## Reporting

- When orchestration actually ran, include a short `Orchestration Ledger` in prose.
- Keep it factual and event-only: `Skills used`, `Subagents`, `Artifacts produced`, `Cleanup status`.
- Omit the ledger when no orchestration ran.
