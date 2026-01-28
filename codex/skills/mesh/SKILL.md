---
name: mesh
description: Parallelize a user-provided task list across workers, then integrate results patch-first. Explicit-only; no planning.
---

# Mesh

## Intent
Run multiple Codex workers in parallel for a user-provided list of tasks, then integrate their results safely.

Key properties (by design):
- Explicit-only: do not decide which other skills to invoke; do only what the user asked.
- No planning: do not create a plan/DAG; treat the user's task list as the plan.
- Max parallel: run as many workers as allowed; queue the rest.
- Two topologies: orchestrate workers (default) or orchestrate sub-orchestrators (explicit).
- Patch-first: workers propose diffs; the orchestrator applies/merges sequentially.
- Audit mode (on request): show the full worker prompts + full outputs.

## Non-goals
- Do not invent tasks.
- Do not do product planning, architecture planning, or task DAG construction.
- Do not auto-run `$validate`/`$fix`/`$ship`/`$join`/`$fin` unless the user explicitly asked.

## When to use
Use `$mesh` when the user explicitly asks to parallelize tasks, e.g.:

- "Use $mesh to parallelize these tasks:" followed by a list.
- "$mesh: run these three investigations in parallel." followed by a list.

## Input contract (required)
To parallelize, the user must provide a clearly separable task list:
- A numbered list or bullet list is ideal.
- Each task should be independently executable; if not, state dependencies or required integration order.

Optional (recommended): state agent type per task.

Agent types (Codex `spawn_agent(agent_type=...)`):
- `worker` (default): implement/fix/run things.
- `explorer`: fast repo research / analysis-only by default.
- `orchestrator`: coordinate its own workers/explorers for that task, then report results upstream.

If tasks are not clearly separable, ask for a numbered list (do not guess).

## Prereqs (Codex CLI)
Multi-agent orchestration requires the Collab feature flag.

- Enable `collab` in `~/.codex/config.toml` (global or profile-scoped):
  ```toml
  [features]
  collab = true
  ```
- Optional: raise concurrency via `agents.max_threads`:
  ```toml
  [agents]
  max_threads = 8
  ```

## Recommended task phrasing (for best results)
In each task, encourage the user to include:
- The desired skill(s) (if any), explicitly (e.g. `$trace`, `$fix`, `$validate`).
- Whether the task is analysis-only vs a code change.
- Any path constraints or ownership boundaries.
- Any ordering constraints (default integration order is list order).

This is not planning: it is just making the task boundary explicit so workers do not drift.

## Suggested task style (synthesized)
Prefer tasks that make the worker contract explicit without adding a separate planning step.

Recommended pattern:
- Start with a verb and a concrete object.
- Name the skill(s) to use (or explicitly say "no skills").
- State whether edits are allowed (default is patch-first).
- State the expected deliverable.

Template:
```text
N. <Verb> <concrete object>.
   - Agent: worker | explorer | orchestrator
   - Skills: <explicit list, or "none">
   - Mode: analysis-only | patch-first | direct edit ok
   - Scope: <paths/globs or "unconstrained">
   - Done when: <signal, file, or user-visible behavior>

Optional (execution controls):
- Cap: <max concurrent agents>
- Conflict budget: <max rebase roundtrips before asking for scopes>
```

## Examples

Parallel research (no code edits):

```text
Use $mesh to parallelize:
1. Use $trace to explain how config is loaded and list the entrypoints.
2. Search the repo for where auth tokens are parsed and summarize risks.
3. Read CI logs for the latest failing run and summarize root cause candidates.
```

Parallel code work (patch-first):

```text
Use $mesh to parallelize (patch-first):
1. Implement formula: mol-mesh-run (persistent orchestration session).
2. Implement formula: mol-mesh-arm (ephemeral per-agent arm).
3. Implement script: mesh-workspace (bd worktree create/remove wrapper).
4. Implement script: mesh-merge-slot (acquire/release wrapper).
5. Implement script: mesh-gates (gate discover/check wrappers).
```

Orchestrating orchestrators (explicit):

```text
Use $mesh to orchestrate orchestrators (patch-first at boundaries):
1. Formula workstream (Agent: orchestrator)
   - Subtasks:
     - Implement formula: mol-mesh-run.
     - Implement formula: mol-mesh-arm.
2. Scripts workstream (Agent: orchestrator)
   - Subtasks:
     - Implement script: mesh-workspace.
     - Implement script: mesh-merge-slot.
     - Implement script: mesh-gates.
```

## Workflow (orchestrator algorithm)
1. Extract the user-provided task list (do not invent subtasks).
2. Decide the agent type per task:
- Default `worker`.
- Prefer `explorer` for tasks explicitly marked analysis-only.
- Use `orchestrator` only when the user explicitly requested it (per task or globally).
3. Run tasks in waves (max parallel, queue the rest):
   - Spawn as many agents as allowed (optionally respect a user-provided cap and/or `agents.max_threads`).
   - Use `spawn_agent` (not a custom command).
   - If a spawn fails (agent/thread limit, collab unavailable, or spawn-depth limit), do not thrash; `wait`, integrate, `close_agent`, then continue.
4. Wait + integrate incrementally:
   - `wait(ids=[...])` returns when *any* agent reaches a final status (not when all finish).
   - Use the completed agent status' embedded final message as the worker output (patch, commands, etc.).
   - Loop: `wait` -> integrate finished agent(s) -> `close_agent` -> repeat until the wave drains.
   - Avoid tight polling: use the default timeout or longer timeouts (minutes). (Codex clamps `timeout_ms` to a minimum.)
5. Validate outputs:
   - If an agent did not follow the output contract, use `send_input` to request a re-emit in the contract format.
6. Integrate patch-first:
   - Apply each proposed patch sequentially in the user-provided task order.
   - If a patch no longer applies (conflict/drift), ask that same agent for a rebased patch against current HEAD.
7. `close_agent` after integrating an agent's results to release slots.
8. Repeat waves until all tasks are processed.
9. Report results and residual risks.

## Patch application protocol (parent orchestrator)
When integrating a worker/sub-orchestrator patch:
- Apply the unified diff as-is; avoid manual edits unless explicitly necessary.
- If the patch applies but looks suspicious, request audit mode artifacts (prompt/output) rather than guessing intent.
- If the patch does not apply cleanly:
   - Ask the authoring agent for a rebased patch against current HEAD.
   - Include the failure mode ("patch failed to apply", conflicting files) so it can rebase precisely.

Rebase request template (parent -> agent):
```text
Your patch did not apply cleanly.

Please rebase/regenerate your patch against the current workspace state and resend a single unified diff.

Failure details:
- Conflicting files: <paths>
- Error summary: <what failed>

Constraints:
- Keep patch-first.
- Do not broaden scope.
```

## Conflict handling (default)
- Default behavior is "max parallel, resolve later": accept that patches may conflict and do the integration work.
- Prefer rebase roundtrips over manual conflict surgery; it preserves intent attribution.

## Conflict budget (optional, recommended for large swarms)
If you hit repeated conflicts or churn, stop and ask the user for one of:
- Explicit per-task scope boundaries (paths/globs) so work can be partitioned.
- A smaller concurrency cap (run fewer agents at once).
- Switch to orchestrator-of-orchestrators with explicit workstream scopes.

## Worker policy (defaults)
- Workers may do anything Codex can do, but default to patch-first to avoid clobbering a shared workspace.
- Workers MUST NOT spawn sub-agents unless explicitly told.
- Workers SHOULD avoid duplicating repo-wide research; the orchestrator should pass filepaths and constraints.
- Workers SHOULD ask questions only when blocked; otherwise pick a reasonable default and state it.

## Explorer policy (defaults)
- Explorers are best for repo-wide search/reading and returning pointers (paths, commands, key snippets).
- Default them to analysis-only unless the user explicitly asked for patches.
- Explorers MUST NOT spawn sub-agents unless explicitly told.

## Sub-orchestrator policy (explicit-only)
Sub-orchestrators are coordination-only agents. Use them only when the user asked for orchestrator-of-orchestrators.

Default constraints:
- Patch-first at the boundary: the sub-orchestrator should not directly edit shared files.
- It may spawn workers and collect their patches.

Required handoff packet (the thing the parent integrates):
- Workstream summary.
- Delegation table (subtask -> worker).
- Patch bundle (prefer a single combined patch; otherwise one patch per subtask).
- Recommended integration order.
- Conflicts discovered inside the workstream (if any) + how to resolve.
- Risks / follow-ups.
- Questions/blockers.

Scope discipline (recommended):
- Prefer giving each sub-orchestrator an explicit scope (paths/globs).
- If two workstreams overlap heavily, expect conflict churn; ask the user to re-scope or run those tasks sequentially.

Escalation path:
- If the parent cannot apply a patch cleanly, send the failure details back to the owning sub-orchestrator and ask it to rebase/regenerate the patch bundle against current HEAD.

## Direct-edit override (explicit-only)
If the user explicitly instructs a task to do direct edits ("direct edit ok"), workers may edit files directly.
Default remains patch-first.

## Prompt template (orchestrator -> worker)
Paste and fill this template per task:

```text
You are a worker operating in a shared workspace.

Default mode: PATCH-FIRST.
- Do NOT directly edit files unless explicitly instructed.
- If you need to run commands, do so and report exact outputs.
- Do NOT spawn subagents unless explicitly instructed.

Task:
- <one sentence>

Context (provided; do not re-discover unless needed):
- Files/paths: <...>
- Commands/entrypoints: <...>

Constraints:
- Only invoke other skills if explicitly named here: <...>

Deliverable (required format):
1) Summary (1-3 bullets)
2) Intended files touched
3) Patch (unified diff in a fenced block)
4) Commands run + results
5) Risks / follow-ups
6) Questions (if blocked)
```

## Prompt template (orchestrator -> explorer)
Use for analysis-only / repo-understanding tasks.

```text
You are an explorer operating in a shared workspace.

Default mode: ANALYSIS-ONLY.
- Do NOT directly edit files unless explicitly instructed.
- Do NOT spawn subagents unless explicitly instructed.

Task:
- <one sentence>

Context (provided; do not re-discover unless needed):
- Files/paths: <...>
- Commands/entrypoints: <...>

Deliverable (required format):
1) Summary (1-3 bullets)
2) Findings (with file paths and minimal snippets if needed)
3) Commands run + results
4) Risks / follow-ups
5) Questions (if blocked)
```

## Prompt template (orchestrator -> sub-orchestrator)
Use this only when the user explicitly requested orchestrator-of-orchestrators.

```text
You are a sub-orchestrator. You coordinate; you do not do the substantive work yourself.

Default mode: PATCH-FIRST AT THE BOUNDARY.
- Do NOT directly edit shared workspace files.
- You MAY spawn workers.
- You MUST NOT spawn additional sub-orchestrators unless explicitly instructed.

Workstream:
- <one sentence>

Workstream scope (if provided):
- <paths/globs or "unconstrained">

User-provided subtasks (do not invent more tasks):
<paste the subtask list verbatim>

Constraints:
- Only invoke other skills if explicitly named here: <...>
- Audit mode: <on|off>. If on, include the full prompts you sent to workers and their full outputs.
- Worker cap (optional): <max workers to run at once>
- Boundary mode: patch-first at the boundary (you return patches; parent integrates).

Deliverable (required format):
1) Workstream summary (1-3 bullets)
2) Delegation (subtask -> worker)
3) Worker outputs (including patches)
4) Patch bundle (prefer one combined patch when safe; otherwise one patch per subtask)
5) Recommended integration order
6) Risks / follow-ups
7) Questions/blockers
```

## Orchestrator output contract
- Topology: worker vs orchestrator per task.
- Delegation: task -> agent.
- Waves: how many waves ran + any concurrency cap used.
- Integration: patches applied (or failed) + conflict handling/rebase roundtrips.
- Commands/signals: what ran and what it showed (only if explicitly requested).
- Residual risks / next actions.

## Audit mode (on request)
If the user asks for auditability ("audit mode", "show worker prompts", "show worker outputs"):
- Print the full prompt you sent to each worker.
- Print the full raw output from each worker.
- If output is truncated by the UI, ask the worker to write its patch/output to a file and return the path.

## Resources
- `references/codex-multi-agent.md`: tool semantics for `spawn_agent` / `send_input` / `wait` / `close_agent`.
