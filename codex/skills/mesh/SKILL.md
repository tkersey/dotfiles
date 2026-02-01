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
- Patch-first by default: workers propose diffs; the orchestrator applies sequentially. If strict escalation triggers, the orchestrator switches to direct execution to unblock.
- Worker-first by default: the orchestrator does not start direct implementation unless an escalation gate triggers (e.g., patch draft timeout) or collab tools are unavailable.
- Audit mode (on request): show the full worker prompts + full outputs.

## Non-goals
- Do not invent tasks.
- Do not do product planning, architecture planning, or task DAG construction.
- Do not auto-run `$validate`/`$fix`/`$ship`/`$join`/`$fin` unless the user explicitly asked.

## When to use
Use `$mesh` when the user explicitly asks to parallelize tasks, e.g.:

- "Use $mesh to parallelize these tasks:" followed by a list.
- "$mesh: run these three investigations in parallel." followed by a list.

## Input contract
Mesh needs separable tasks to parallelize. A numbered/bulleted list is ideal, but not mandatory.

Accepted inputs:
- A numbered/bulleted task list (best).
- A single task (mesh treats it as a one-item list; hedging/restarts are still allowed).
- Freeform text containing multiple tasks: mesh MUST extract an interpreted task list and print it in the delegation manifest before spawning.

If separability is unclear or the interpretation is ambiguous, ask for clarification by proposing the interpreted list. Avoid pedantic refusal; do not invent new tasks.

Optional (recommended): state agent type per task.

Agent types (Codex `spawn_agent(agent_type=...)`):
- `worker` (default): implement/fix/run things.
- `explorer`: fast repo research / analysis-only by default.
- `orchestrator`: coordinate its own workers/explorers for that task, then report results upstream.

If tasks are not clearly separable, propose a best-effort interpreted list and ask the user to confirm/correct it.

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

## Codex constraints (first principles)
Mesh must operate within Codex collab tool semantics (see `references/codex-multi-agent.md` and the Codex repo).

Key constraints:
- Multi-agent tools exist only when the under-development feature flag `[features].collab = true` is enabled; spawns can fail (cap/depth/feature off). If collab tools are unavailable, mesh MUST fall back to single-agent execution.
- `wait(ids, timeout_ms)` returns only when an agent reaches a final status, or when it times out; timeout is clamped by Codex to 10s-300s.
- You cannot observe intermediate worker state while it runs.
- `send_input` is queued and delivered only after the worker finishes unless `interrupt=true` is used. Use interrupts sparingly for SLA/stall escalation.
- Agents share the same workspace; prefer patch-first and attempt-scoped artifacts to avoid clobbering.

## Recommended task phrasing (for best results)
In each task, encourage the user to include:
- The desired skill(s) (if any), explicitly (e.g. `$complexity-mitigator`, `$fix`, `$validate`).
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

Tunable thresholds (optional overrides; monitoring/enforcement remain mandatory):
- Cap: <max concurrent agents>
- Conflict budget: <max rebase roundtrips before asking for scopes>
- Tick interval: <e.g. 60s|off> (live monitoring cadence; `off` enables deadline-only monitoring; effective clamp 10s-300s due to Codex `wait` timeout)
- Checkpoint interval: <e.g. 2m> (worker must emit a checkpoint at least this often)
- Time budget (optional): <e.g. 45m> (after this, return best-effort partial results)
- Ack SLA (optional): <e.g. 30s> (worker must ack with plan + first edit, or explain why not)
- Patch draft timeout (optional): <e.g. 5m> (if no patch draft exists, auto-cancel and switch to direct execution unless explicitly overridden)
- First edit target (optional): <e.g. 10m> (make at least one minimal change, even scaffolding)
- Continue waiting (optional): <yes|no> (default no; only relevant for patch draft timeout)
- Hedge budget (optional): <e.g. 2> (max concurrent attempts per task)
- Stall threshold (optional): <e.g. 2> (consecutive ticks without progress before declaring stall)
```

## Examples

Parallel research (no code edits):

```text
Use $mesh to parallelize:
1. Use $complexity-mitigator to explain how config is loaded and list the entrypoints.
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
This workflow is strict and non-optional. It exists to prevent worker stalls paired with false "I'm monitoring" claims.

Defaults (unless the user explicitly overrides):
- Tick interval: 60s (effective clamp 10s-300s due to Codex `wait` timeout). Set to `off` for deadline-only monitoring.
- Ack SLA: 30s
- Patch draft timeout: 5m (no patch draft -> auto-cancel + direct execution; worker-first until this triggers)
- First edit target: 10m (at least one minimal change, even scaffolding)
- Missing-artifact strikes: 1 (second miss triggers restart)
- Stall detection: same status twice OR no patch progress in two consecutive ticks

1. Extract tasks from the user input (do not invent subtasks):
   - If the user provided a list, use it verbatim.
   - Otherwise, extract an interpreted list (best-effort) and print it in the delegation manifest before spawning.
2. Decide the agent type per task:
   - Default `worker`.
   - Prefer `explorer` for tasks explicitly marked analysis-only.
   - Use `orchestrator` only when the user explicitly requested it (per task or globally).
3. Assign a `run_id` and create `.mesh/runs/<run_id>/`.
4. Emit a delegation manifest:
   - Print (and write to `.mesh/runs/<run_id>/manifest.md`) the task list, per-task agent type/mode/scope, caps/budgets/timeouts, and integration order (list order).
5. Spawn tasks in waves (max parallel, queue the rest):
   - Spawn as many agents as allowed (respect Cap if provided).
   - Use `spawn_agent` (not a custom command).
   - Record per-attempt metadata: `spawned_at`, `last_tick_at`, `last_status`, `last_patch_stat`, `unreliable_strikes`.
   - Enforce Ack SLA: at `spawned_at + Ack SLA` (default 30s), verify the checkpoint exists on disk and matches the required checkpoint format. If missing/invalid, restart once.
6. Monitoring loop (non-optional):
   - Use `wait(..., timeout_ms=...)` as the scheduler tick; treat `wait` timeouts as ticks (not failures).
   - Tick scheduling:
     - If Tick interval is set, run a tick at that cadence.
     - If Tick interval is `off`, run ticks at enforcement deadlines (Ack SLA, Patch draft timeout, checkpoint interval) and at the Codex `wait` clamp boundary (<= 300s).
   - On each tick, perform artifact verification + enforcement, then print:
     - `last tick: <timestamp>`
     - Live status dashboard
     - Monitoring log (tick entries + verified artifact paths)
   - A "monitoring" claim is only allowed if a tick was executed since the prior user-visible message.
   - Never stop ticking while any task has an active agent or any enforcement deadline is pending.
7. Progress enforcement (non-optional):
   - Stall: same status twice OR no patch progress in two consecutive ticks -> print `STALL DETECTED` + action.
   - Checkpoint integrity: verify claimed artifacts exist before acknowledging.
   - If patch draft still missing at Patch draft timeout -> auto-cancel + switch to direct execution unless the user opted to keep waiting.
   - If worker misses Ack SLA -> restart. Continue restarting/hedging until Patch draft timeout; do not take over before Patch draft timeout unless collab tools are unavailable or the user explicitly requests take over.
8. Validate outputs (strict gates):
   - If a worker output violates the contract, request a re-emit.
   - Do not mark a task done until its gates pass.
9. Integrate patch-first:
   - Apply each proposed patch sequentially in user-provided task order.
   - If a patch does not apply, request a rebased patch from the same agent.
10. `close_agent` after integrating or cancelling to free slots.
11. Repeat waves until all tasks are processed.
12. Report results and residual risks.

## Monitoring ticks (mandatory)
Definitions:
- A "tick" is an explicit monitoring+enforcement action executed by the orchestrator.
- A "monitoring" claim is only allowed if at least one tick was executed since the previous user-visible message.

Tick actions (non-optional; do this on every tick for every active agent):
1. Verify artifacts on disk (per attempt; these are the monitoring surface):
   - checkpoint: `.mesh/runs/<run_id>/checkpoints/<task-slug>--a<attempt>.md`
   - patch draft (patch-first): `.mesh/runs/<run_id>/patches/<task-slug>--a<attempt>.diff`
2. Record patch progress signals:
   - patch draft exists?
   - patch draft mtime/size changed since last tick?
3. Request a checkpoint/status from the worker if needed:
   - NOTE: Codex cannot show intermediate state from a running worker; `send_input` is queued unless `interrupt=true`.
   - Do NOT spam `send_input` on every tick.
   - Use `send_input(interrupt=true)` only when you need an immediate response (SLA miss, stall escalation, missing artifact re-checkpoint).

Required output while work is in progress:
- Include `last tick: <timestamp>` in every message.
- Include a "Monitoring log" section (see below).

## Live status dashboard (mandatory)
The orchestrator must print a live dashboard on each tick.

Required dashboard columns (ASCII-only):
- `task`: index + task identifier/slug
- `agent`: agent id
- `att`: attempt number for that task
- `unrel`: unreliable strike count
- `state`: queued | spawned | acked | running | waiting_checkpoint | stalled | restarting | taking_over | needs_reemit | needs_rebase | applying_patch | integrated | done | failed
- `last_seen`: time since last agent message
- `last_tick`: timestamp of most recent tick
- `gates`: compact gate status
- `next`: next orchestrator action

Gates (required set):
- `A` (ack): initial checkpoint exists by Ack SLA and matches required checkpoint format
- `C` (checkpoint): checkpoint continues to exist and is being updated when required
- `O` (output): final message follows the deliverable contract sections
- `D` (draft): patch draft exists and is a unified diff (contains at least one `diff --git` line)
- `P` (patch): unified diff applies cleanly to current workspace state
- `S` (scope): if scope constraints were provided, touched files are within scope
- `V` (verification): only when explicitly requested in the user task/done-when; required commands ran and results are reported

Gate formatting example: `A=ok C=ok O=-- D=ok P=-- S=? V=--`

## Checkpoint file format (required)
Workers/explorers MUST write checkpoints in a machine-parseable, stable format so stall detection is deterministic.

Checkpoint path (per attempt):
- `.mesh/runs/<run_id>/checkpoints/<task-slug>--a<attempt>.md`

Required fields (exact keys; ASCII-only):
- `status_code: <one token>`
- `status_detail: <one line>`
- `plan:` (exactly 5 bullets)
- `intended_files:` (0+ bullets)
- `blockers:` (0+ bullets; use `- none` if none)
- `artifacts:` (0+ bullets; include checkpoint + patch paths)

Recommended `status_code` values:
- `started`
- `discovering`
- `drafting_patch`
- `waiting_for_feedback`
- `blocked`
- `done`

Patch draft path (patch-first):
- `.mesh/runs/<run_id>/patches/<task-slug>--a<attempt>.diff`

Patch draft requirements:
- Must be a unified diff (start with `diff --git ...`).
- If you truly cannot propose a diff yet, do not create a placeholder diff. Leave the patch draft absent and explain why in the checkpoint.

## Monitoring log (mandatory)
Every orchestrator message while work is in progress MUST include a short "Monitoring log" section.

Minimum required fields:
- `last tick: <timestamp>`
- `tick interval: <duration|off>`
- Recent tick entries (at least the most recent tick):
  - time
  - which agents were ticked
  - last known status per agent (1 line)
  - checkpoint path + verified existence
  - patch draft path + verified existence + mtime/size (for patch-first)

## Strict gate mode (mandatory)
"Strict gate" means the orchestrator does not treat a task as complete until objective criteria are met.

Gate profiles:
- Analysis-only task: require `A` + `O` (and `V` only if explicitly requested).
- Patch-first task: require `A` + `O` + `D` + `P` (and `S` if scoped; and `V` only if explicitly requested).

If a gate fails, the orchestrator MUST take a recovery action (request re-emit, request rebase, restart, hedge, or take over) rather than silently declaring success.

## Progress enforcement (mandatory)
Stall detection rules (non-optional):
- Same status twice: if the worker's checkpoint `status_code` + `status_detail` are identical in two consecutive ticks, treat as stalled.
- No patch progress twice: if patch draft exists but mtime/size does not change across two consecutive ticks, treat as stalled.

Stall policy (non-optional):
- Emit `STALL DETECTED: <reason>` in the orchestrator output.
- Take exactly one action immediately:
  - Restart the worker, OR
  - Switch to direct execution in the orchestrator ("take over").

Default action policy (unless the user explicitly overrides):
- On stall before Patch draft timeout: restart (and hedge if capacity allows).
- Take over only after Patch draft timeout, unless collab tools are unavailable or the user explicitly requests take over.

Timeout escalation (non-optional):
- After Patch draft timeout (default 5m) with no patch draft file, auto-cancel and switch to direct execution unless the user explicitly opted to continue waiting.

Worker SLA (non-optional):
- Workers must satisfy Ack SLA by writing the required checkpoint format within 30s.
- If they can propose a real diff quickly, they should also write an initial patch draft; otherwise, record blockers (do not write placeholder diffs).
- If no ACK, restart and keep attempting/hedging until Patch draft timeout, then take over (unless user opted to keep waiting).

## Checkpoint integrity (mandatory)
If a worker claims it created/updated a checkpoint or patch, the orchestrator MUST verify the file exists on disk before acknowledging progress.

Rules:
- Missing file after a claim: request a re-checkpoint and mark the worker unreliable (one strike).
- Second missing-artifact incident for that worker: restart immediately.

## Checkpoint protocol (mandatory)
Codex multi-agent runs can hit UI/tool timeouts even when work is still progressing.
To make mesh durable (recoverable) and elastic (less sensitive to timeout semantics), require periodic checkpoints.

Orchestrator policy:
- Track `last_seen` and `last_tick` per active agent.
- Execute monitoring ticks on the configured tick schedule.
- On each tick:
  - verify checkpoint/patch artifacts on disk
  - request a checkpoint/status if needed
  - print dashboard + monitoring log
- If an agent misses 2 checkpoint intervals in a row, request a "minimal checkpoint" (status + artifact paths) using `send_input(interrupt=true)`.
- Never treat a `wait` timeout as a reason to `close_agent`.

Worker/explorer policy:
- Maintain durable artifacts in the workspace so the parent can recover even if chat output is lost:
  - Progress log: `.mesh/runs/<run_id>/checkpoints/<task-slug>--a<attempt>.md`
  - Patch draft (if patch-first): `.mesh/runs/<run_id>/patches/<task-slug>--a<attempt>.diff`
- Create `.mesh/runs/<run_id>/checkpoints/` and `.mesh/runs/<run_id>/patches/` if needed.
- Every checkpoint interval (or at each milestone), update the progress log and (if applicable) refresh the patch draft.
- On any tick/checkpoint request, respond quickly with:
  1) Current status (1-3 bullets)
  2) Paths to artifacts
  3) Any blocker

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
- Workers MUST satisfy the SLA requirements in the prompt (checkpoint + patch draft early; first edit target).
- Workers MUST treat `.mesh/` artifacts as the source of truth; do not claim artifacts exist unless they exist on disk.
- Workers SHOULD avoid duplicating repo-wide research; the orchestrator should pass filepaths and constraints.
- Workers SHOULD ask questions only when blocked; otherwise pick a reasonable default and state it.
- Workers SHOULD avoid "looks hung" failures: no pagers, no interactive prompts, prefer long-running command logs written to files under `.mesh/`.

## Explorer policy (defaults)
- Explorers are best for repo-wide search/reading and returning pointers (paths, commands, key snippets).
- Default them to analysis-only unless the user explicitly asked for patches.
- Explorers MUST NOT spawn sub-agents unless explicitly told.
- Explorers MUST satisfy the SLA requirements in the prompt (checkpoint early, updated on cadence).
- Explorers SHOULD follow the checkpoint protocol for long-running searches/reads.

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

SLA requirements (non-negotiable):
- Within 30 seconds:
  - Create/update `.mesh/runs/<run_id>/checkpoints/<task-slug>--a<attempt>.md` with the required checkpoint format:
    - `status_code:`
    - `status_detail:`
    - `plan:` (exactly 5 bullets)
    - `intended_files:`
    - `blockers:`
    - `artifacts:` (include the checkpoint + patch paths)
  - If you can propose any real diff, create/update `.mesh/runs/<run_id>/patches/<task-slug>--a<attempt>.diff` as a unified diff.
  - If you cannot propose a real diff yet, do NOT create a placeholder diff; explain why in `blockers:`.
- First commit target: within 10 minutes, the patch draft must show real progress (mtime/size change + meaningful diff).

Durability requirements (checkpoint protocol):
- Maintain artifacts:
  - Progress log: `.mesh/runs/<run_id>/checkpoints/<task-slug>--a<attempt>.md`
  - Patch draft: `.mesh/runs/<run_id>/patches/<task-slug>--a<attempt>.diff`
- Update the checkpoint and patch draft at least every checkpoint interval.
- On any tick/checkpoint request, respond quickly with current status + artifact paths.
- Do not claim an artifact exists unless it exists on disk.

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

SLA requirements (non-negotiable):
- Within 30 seconds:
  - Create/update `.mesh/runs/<run_id>/checkpoints/<task-slug>--a<attempt>.md` with the required checkpoint format:
    - `status_code:`
    - `status_detail:`
    - `plan:` (exactly 5 bullets)
    - `intended_files:` (areas/files you will inspect first)
    - `blockers:`
    - `artifacts:` (include the checkpoint path)

Durability requirements (checkpoint protocol):
- Maintain a progress log at `.mesh/runs/<run_id>/checkpoints/<task-slug>--a<attempt>.md`.
- Update the checkpoint at least every checkpoint interval.
- On any tick/checkpoint request, respond quickly with current status + checkpoint path.

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
- Dashboard: enough per-task state/gate information that a reader can tell if delegation, monitoring ticks, and recovery behaved correctly.
- Monitoring log: list of ticks (with timestamps), last known status, and last artifact paths with verified existence.
- Stall events: each stall must be explicitly reported with `STALL DETECTED: ...` + action taken (restart or take over).
- Timeout escalation: if Patch draft timeout triggers, report it and the switch to direct execution (unless user opted to keep waiting).
- Residual risks / next actions.

## Example flow: worker stall -> enforced recovery
Illustrative output (timestamps are examples).

```text
last tick: 2026-01-31T19:22:00Z (tick interval: 60s)

Dashboard
task  agent   att  unrel  state    last_seen  last_tick  gates                       next
1     a1b2..  1    0      running  00:55      19:22:00   A=ok C=ok O=-- D=-- P=--     tick

Monitoring log
 - 19:22:00 ticked a1b2.. status="discovery done" checkpoint=OK patch=DNE

last tick: 2026-01-31T19:23:00Z (tick interval: 60s)
Monitoring log
 - 19:23:00 ticked a1b2.. status="discovery done" checkpoint=OK patch=DNE

STALL DETECTED: same status twice and no patch draft
Action: restart task 1 (close a1b2.., spawn attempt 2)

last tick: 2026-01-31T19:27:00Z (tick interval: 60s)
Monitoring log
 - 19:27:00 ticked c3d4.. status="working" checkpoint=OK patch=DNE

TIMEOUT ESCALATION: no patch draft after 5m (default)
Action: cancel worker and switch to direct execution in orchestrator
```

## Audit mode (on request)
If the user asks for auditability ("audit mode", "show worker prompts", "show worker outputs"):
- Print the full prompt you sent to each worker.
- Print the full raw output from each worker.
- If output is truncated by the UI, ask the worker to write its patch/output to a file and return the path.

## Resources
- `references/codex-multi-agent.md`: tool semantics for `spawn_agent` / `send_input` / `wait` / `close_agent`.
