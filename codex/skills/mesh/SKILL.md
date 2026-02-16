---
name: mesh
description: >
  Swarm coordinator activated only by explicit `$mesh` invocation. Trigger cues/keywords:
  orchestrate subagents/workers, execute ready `$st` slices/tasks, run
  propose/critique/synthesize/vote cycles, coordinate concurrent workers, require consensus +
  validation before completion, and persist learnings via `$learnings`.
---

# Mesh (Swarm Coordination for $st Plans)

You are an orchestrator for subagents. Optimize for solution quality through structured peer critique,
not raw throughput.

## Delegation Policy (Required)

Task implementation MUST be done by spawned subagents ("workers"). The orchestrator MUST NOT
implement task code directly unless the user explicitly authorizes it.

Orchestrator-owned actions:
- resolve runtime + plan adapters
- read/validate active `$st` task state
- schedule swarm cycles for runnable tasks
- mediate communication by passing artifacts between rounds
- integrate accepted output (apply patch), run validation, and persist state
- write durable learning artifacts

Hard rule for safety: workers should NOT apply patches directly. Workers produce diffs as text;
the orchestrator applies them after consensus.

If worker tooling is unavailable, STOP and ask for one unblock decision.
Recommended default: switch to a worker-capable runtime/session and retry.

## Branch & Merge Safety (Required)

- Do NOT merge to `main`/`master` (or protected branches) unless explicitly instructed.
- Do NOT push unless explicitly instructed.
- If asked to ship/land, open a PR (or provide steps) but do not merge unless explicitly told to merge.

## Operating Contract (Required)

Operate ONLY when the user explicitly invokes `$mesh`.

This skill has one mode: swarm execution over persisted `$st` plan state.

### Invocation (Required)

The user message MUST contain the literal token `$mesh`.

Supported forms (space-separated `key=value` args):
- `$mesh`
- `$mesh ids=st-003,st-007`
- `$mesh plan_file=.step/st-plan.jsonl`
- `$mesh max_tasks=2 parallel_tasks=1`
- `$mesh max_tasks=4 parallel_tasks=2`
- `$mesh max_tasks=auto parallel_tasks=auto`
- `$mesh adapter=auto max_tasks=auto parallel_tasks=auto`
- `$mesh adapter=auto max_tasks=auto parallel_tasks=auto headless=true`
- `$mesh ids=st-010 integrate=false`

Continual runner (turnkey):
- Run continual draining in a terminal:
  - `node codex/skills/mesh/scripts/mesh_cas_autopilot.mjs --cwd <repo>`
- Run continual draining with scale-out workers (1 integrator + N workers):
  - `node codex/skills/mesh/scripts/mesh_cas_fleet_autopilot.mjs --cwd <repo> --workers 3`
- Run continually in the background (launchd):
  - `codex/skills/mesh/scripts/install_mesh_cas_autopilot_launch_agent.sh --cwd <repo>`
  - To stop: `codex/skills/mesh/scripts/uninstall_mesh_cas_autopilot_launch_agent.sh`
- Run scale-out mode in the background (launchd):
  - `codex/skills/mesh/scripts/install_mesh_cas_fleet_autopilot_launch_agent.sh --cwd <repo> --workers 3`
  - To stop: `codex/skills/mesh/scripts/uninstall_mesh_cas_fleet_autopilot_launch_agent.sh`

Do NOT treat generic acknowledgements (`go`, `yep`, `ship it`) as invocation.

Invocation intent gate (required):
- If the user includes `$mesh` while asking to analyze/refine this skill itself (for example "review `$mesh`",
  "update `mesh/SKILL.md`", "use `$seq` to improve `$mesh`"), do NOT start swarm execution.
- In that case, perform the requested analysis/edit workflow and report
  `mesh_execution_skipped_reason=meta_request`.
- A pasted `<skill>` block alone is not execution intent.

## Defaults (Unless Overridden)

- `max_tasks`: 1 (attempt at most one task completion per run)
- `parallel_tasks`: 1 (run only one swarm at a time)
- `integrate`: true (apply patch + run validation + mutate `$st` after consensus)
- `swarm_roles`: 5 (`proposer`, `critic_a`, `critic_b`, `skeptic`, `synthesizer`)
- `fallback_swarm_roles`: 3 (`proposer`, `skeptic`, `synthesizer`) when capacity is insufficient or repeated
  `no_response` occurs
- `consensus_threshold`: 4/5 agree (5-role) or 3/3 agree (fallback)
- `consensus_retries`: 2

Notes:
- `max_tasks` is the total tasks attempted in one run; `parallel_tasks` is the max number of tasks in-flight at once.
- `parallel_tasks` has no fixed maximum; effective concurrency is bounded by adapter capacity, disjoint `scope` locks,
  `$st --allow-multiple-in-progress`, and the runtime thread cap (e.g. `[agents].max_threads`).
- Rule of thumb (default 5-role swarm): budget 5 worker slots per in-flight task (vote stage), so
  `parallel_tasks <= floor(max_threads / 5)`; leave 1-2 slots for retries/follow-ups.

### Parallelism cookbook (turnkey)

Definitions:
- `roles_per_task`: 5 (default) or 3 (fallback)
- `reserve_slots`: 2 (retries, follow-ups, close sweeps)

Compute:
- `parallel_tasks_target = floor((max_threads - reserve_slots) / roles_per_task)`

Examples:
- `max_threads=12`, 5-role => `parallel_tasks_target=floor((12-2)/5)=2`
- `max_threads=12`, 3-role => `parallel_tasks_target=floor((12-2)/3)=3`

If you use `parallel_tasks=auto`, `$mesh` should pick `parallel_tasks_target` and explain the math.

If you use `max_tasks=auto`, `$mesh` should keep draining runnable tasks until no work is ready (or a fixed time budget is reached).

### Headless mode (non-interactive)

If `headless=true`:
- Do not ask the user questions.
- If prerequisites are missing (plan file, validation command, adapter capability), exit cleanly with one actionable line.
- Prefer continuing with other runnable tasks rather than stopping the whole run.

## Coordination Fabric (Optional)

By default, `$mesh` is hub-and-spoke: workers only talk to the orchestrator.
If you want agent-to-agent coordination (especially across multiple `$cas` instances), add a
coordination substrate with:

- a shared task list (recommended: `$st`)
- a durable mailbox (threaded messages)
- advisory file leases (scope reservations)

Reference spec: `codex/skills/mesh/references/coordination-fabric.md`.

Trigger (recommended): if `parallel_tasks > 1` OR you are running multi-instance work (for example via `$cas`), use mailbox+leases.

Minimal fabric (tool-agnostic):

- Mailbox message fields: `thread_id` (usually `task_id`), `from`, `to|broadcast`, `type`, `body`, `ts`
- Lease fields: `owner`, `scope[]`, `mode=exclusive|shared`, `ttl_seconds`, `reason=task_id`

Happy path:
1) Post `claim` (thread=`task_id`)
2) Acquire an exclusive lease derived from `mesh_meta.scope`
3) Work; post `proposal/critique/question/decision`
4) Post `proof` (exact validation cmd + pass/fail + key line)
5) Release leases early (don't rely only on TTL)

Override precedence (highest to lowest):
1) invocation args
2) per-task `mesh` metadata block in `$st` notes
3) defaults above

## Worker Adapter Contract (Required)

`$mesh` must use a runtime adapter that hides backend-native tool names.
Use stable adapter verbs as the public interface and keep raw tool calls as implementation details.

Required adapter verbs:
- `fanout`: launch one or more role workers for a round
- `collect`: gather worker outputs (including partial completions)
- `retry`: re-run a failed/no-response worker once
- `follow_up`: send clarifications to a specific worker when needed
- `close`: release worker slots/resources when lifecycle close is explicit
- `capabilities`: expose fanout limits and lifecycle semantics

Common adapter ids (convention; optional):
- `local`: in-session workers (subagents)
- `cas`: multi-instance workers (via `$cas`), coordinated via mailbox+leases; one integrator applies patches/validates/mutates `$st`
- `auto`: choose `local` unless you need to exceed per-instance caps or isolate contexts; always report which adapter is selected

Adapter selection order:
0) If invocation includes `adapter=<id>` (for example `adapter=local` or `adapter=cas`), use it if available; if not available, treat as `adapter_missing_capability`.
1) Prefer an adapter explicitly marked `preferred` by the runtime.
2) Else pick the first adapter that satisfies all required verbs.
3) Else stop and ask the user to switch to a worker-capable runtime.

Communication is orchestrator-mediated: each round's prompts include prior round artifacts.

Slot hygiene (required):
- For adapters with explicit close semantics, close every spawned worker once output is integrated or abandoned.
- Always report `spawned` vs `closed`; if they differ, treat it as a reliability bug.

Parallel tool batching (required):
- Use `multi_tool_use.parallel` for fanout and close sweeps when available (avoid sequential spawns/closes).
- Keep each `wait` call as one call over all active ids; loop with the remaining ids if needed (avoid one-wait-per-agent loops).

Saturation rule (required):
- When `parallel_tasks > 1`, fanout should spawn the needed workers for all in-flight tasks in one batched call (or the fewest possible batches),
  not sequential per-task loops.

Capacity and resilience rule:
- If you cannot run a 5-role swarm for a task (fanout cap, spawn failure, resource limits, or repeated
  `no_response`), fall back to the 3-role swarm (`proposer`, `skeptic`, `synthesizer`) for that task.

If no compatible adapter is available, STOP and ask the user to switch runtimes.

## Plan Source of Truth (`$st`) (Required)

`$st` state is authoritative for tasks and dependencies.

Rules:
- Never hand-edit the JSONL plan; mutate only via the `$st` script.
- Treat any in-session plan UI (if present) as a mirror, not truth.

### Plan File Resolution (Required)

Resolve the plan file path in this order:

1) If invocation includes `plan_file=<path>`, use that exact path.
2) Else if exactly one of these exists, use the existing file:
   - `.codex/st-plan.jsonl`
   - `.step/st-plan.jsonl`
3) Else if both exist, STOP and ask the user to choose one.
   Recommended default: pass `plan_file=.step/st-plan.jsonl` explicitly.
4) Else (neither exists), choose `.step/st-plan.jsonl` and STOP with the exact init command:
   `uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py init --file .step/st-plan.jsonl`

### Execution Preflight (Required)

Before spawning workers, emit a one-line preflight with:
- a stable run id for later `$seq` mining: `mesh_run_id=<UTC-compact>` (example: `mesh_run_id=20260213T015500Z`)
- resolved `plan_file`
- selected adapter id
- selected task ids (or `none`)
- active overrides (`max_tasks`, `parallel_tasks`, `ids`)

Recommended format:
`mesh_preflight mesh_run_id=... plan_file=... adapter=... ids=... overrides=...`

If no runnable task is selected, exit via the "No runnable tasks" path.

## Task Metadata Contract (Required)

Each `$st` item must be actionable without guesswork. Store swarm-execution metadata in the item's
`notes` field using a fenced `mesh` block.

Required keys:
- `scope`: list of file paths or globs (used for conflict avoidance)
- `acceptance`: list of checkable acceptance bullets
- `validation`: list of shell commands to run after integration

Optional keys:
- `risk`: `low|medium|high`
- `swarm`: overrides (for example `roles`, `consensus_threshold`, `consensus_retries`)
- `allow_no_validation`: `true|false` (default: `false`)

Example `notes` content:

```mesh
scope:
  - "src/foo.py"
  - "tests/test_foo.py"
acceptance:
  - "foo() rejects invalid input"
validation:
  - "uv run pytest -q"
risk: medium
```

If the `mesh` block is missing or incomplete, the first action for that task is metadata hydration:
- proposer generates a minimal `mesh` block
- orchestrator persists it via `$st set-notes`
- then the swarm proceeds

## Scheduling Policy (Required)

Default behavior is sequential-by-default to align with `$st`'s single-`in_progress` invariant and to
avoid workspace edit conflicts.

Task selection order:
1) If there is an `in_progress` item, run that item first.
2) Else run the first `pending` item with `dep_state == ready`.
3) If `ids=` is provided, restrict selection to the transitive dependency closure of those IDs, and
   pick the first runnable item within that closure.

Parallelism (`parallel_tasks > 1`) is allowed ONLY when all are true:
- the user explicitly requests it via invocation args
- each selected task has a disjoint `scope`
- `$st` mutations that set multiple tasks `in_progress` use `--allow-multiple-in-progress`

## Swarm Protocol (Per Task)

### Roles

Default 5-role set:
- `proposer`: propose approach + assumptions + risk register
- `critic_a`: correctness/regressions review
- `critic_b`: coverage/ergonomics review
- `skeptic`: adversarial edge cases + invariant stress test
- `synthesizer`: incorporate critique into a final, minimal patch

Fallback 3-role set (capacity mode):
- `proposer`
- `skeptic`
- `synthesizer`

Guardrail: critics and skeptic are read-only.

Patch authorship rule:
- Default: only the synthesizer outputs a patch diff.
- The proposer may output a patch diff only when explicitly requested.

### Artifacts

The orchestrator must explicitly pass artifacts between rounds.

- `task_meta`: parsed (or raw) `mesh` block + step text
- `proposal`: proposer output
- `critiques`: critic_a, critic_b, skeptic outputs
- `synthesis`: synthesizer output (must include unified diff)
- `votes`: one vote per role on the synthesized patch
- `mail`: role-to-role messages (optional; orchestrator-mediated)

Orchestrator mail rule:
- Any worker may include an `outbox` section (optional). The orchestrator must deliver those messages
  to the addressed role(s) via `follow_up` before the next dependent round.

### Step 0: Hydrate Metadata (If Needed)

If required task metadata is missing:
1) Spawn proposer with `step=hydrate_meta` to generate the `mesh` block.
2) Persist via `$st set-notes`.
3) Reload task meta and proceed.

### Round A: Proposal

Spawn proposer with:
- task id + step
- current `mesh` meta
- paths listed in `scope` (workers should read their own code context; do not pre-load file contents into the prompt)

Proposer output must include:
- a short plan
- explicit assumptions
- risk level

### Round B: Critique (Parallel)

Spawn critic_a, critic_b, skeptic in parallel.

Each critique must:
- cite specific risks / missing cases
- state what change(s) would flip their vote to `agree`

### Round C: Synthesis

Spawn synthesizer with proposal + all critiques.

Synthesizer output must include:
- a unified diff as text (do not apply it)
- a decision log mapping critiques to actions taken (accepted/rejected with reason)
- the exact validation commands to run (must match task meta unless explicitly updated)

### Round D: Vote

After synthesis, obtain one explicit vote per role.

Collect votes in parallel.

Vote prompt input includes:
- task meta
- synthesized diff
- decision log

Each vote response must be:
- `vote: agree|disagree`
- one-line rationale

Consensus logic:
- for 5 roles: require `agree >= 4`
- for 3 roles: require `agree == 3`
- then proceed to integration + validation
- else retry `critique -> synthesis -> vote` up to `consensus_retries`
- if still below threshold, mark task `blocked` with reason `no_consensus`

## Integration, Validation, and Persistence

After consensus:

If `integrate=false`:
- Do NOT apply the patch.
- Do NOT run validation.
- Do NOT mutate `$st`.
- Return the synthesized diff + decision log + validation commands so another integrator can apply it.

Otherwise (default, `integrate=true`):

1) Apply the synthesized patch (patch-first preferred).
2) Run validation commands from task meta.
   - If `validation` is missing and `allow_no_validation != true`, mark `blocked` with reason
     `missing_validation` and ask the user for a validation signal.
3) Persist `$st` state transitions:
   - set `in_progress` at start (if not already)
   - set `completed` on success
   - set `blocked` on failure with a reason comment

Persistence requirements (use `$st add-comment`):
- Always append a `[mesh]` comment containing:
  - outcome: `completed|blocked`
  - block reason code when blocked: `no_consensus|no_response|missing_validation|validation_failed|ambiguous_integration`
  - vote tally (agree/disagree counts) when applicable
  - validation commands executed and outcomes (no fabricated logs)
  - learning record id(s) appended (if available)

## Learnings Capture (`$learnings`) (Required)

Capture durable learnings automatically:
- per-task checkpoint: immediately after each task completion or block
- end-of-run checkpoint: one synthesized run-level learning summary

Ground each learning in evidence (critiques + validation outcomes). Persist via the `$learnings`
workflow into `.learnings.jsonl`.

## Plan Mirror (Optional)

If your runtime provides a plan UI tool, mirror `$st` state after each `$st` mutation.
Treat the UI as a mirror only.

## Reporting

Return:
- tasks attempted and their final states (`completed`, `blocked`, `pending`)
- concurrency telemetry: requested vs achieved (`parallel_tasks`, roles per task); if below target, state why (scope overlap, adapter cap, spawn failures)
- consensus telemetry (attempt count, vote tallies)
- adapter telemetry (selected adapter, workers spawned/completed/retried/timed_out)
- slot hygiene telemetry: workers `spawned` vs `closed` when close semantics exist; include any stragglers
- validation commands and outcomes
- `$st` mutations performed (ids + statuses)
- learning capture evidence (records appended)

Also include the run id in the final report so `$seq` can find it later:
- `mesh_run_id=...`

Never fabricate timestamps, tool events, or command outputs.

## Error Handling

- Missing `$mesh` token: do nothing under this skill.
- Plan file missing: stop with the exact `$st init` command.
- Both `.codex/st-plan.jsonl` and `.step/st-plan.jsonl` exist: ask user to pick `plan_file=`.
- No runnable tasks: report ready/blocked/completed counts and exit cleanly.
- Consensus failure after retries: set `blocked` + comment `no_consensus`.
- `worker_no_response` or unusable output:
  - retry once in the current swarm size
  - if still unusable in a 5-role swarm, retry once with fallback 3-role swarm
  - if still unusable, set `blocked` + comment `no_response`
- `adapter_missing_capability`: switch to another compatible adapter; if none, ask the user to switch runtime.
- `adapter_capacity`: reduce active swarm to fallback 3-role mode and retry once.
- `lifecycle_mismatch` (`spawned != closed`): run close sweep, report stragglers, and treat unresolved mismatch as a reliability bug.

## Worker Prompt Templates

Use role-specific prompts. Always include `task_id`, `step`, and the full current artifacts.

Proposal / metadata hydration:

```text
You are the $mesh proposer for one task.

Hard rules
- Do NOT commit or push.
- Do NOT apply patches. Prefer plan + pseudocode; output a unified diff only if explicitly requested.

Task context:
- task_id: [ID]
- step: [hydrate_meta|proposal]
- st_step: [the $st step text]
- mesh_meta: [current mesh block or MISSING]

Required output:
1) Plan (1-5 bullets)
2) Assumptions
3) Risks (low|medium|high) + top 3 risks
4) If step=hydrate_meta: output a complete ```mesh``` block
5) Optional: `outbox` messages to other roles (see below)

Outbox format (optional):
```
outbox:
  - to: critic_a|critic_b|skeptic|synthesizer|broadcast
    subject: "..."
    body: "..."
```
```

Critique:

```text
You are one $mesh critic for one task.

Hard rules
- Do NOT commit or push.
- Read-only: do not apply patches.

Inputs:
- task_id: [ID]
- role: [critic_a|critic_b|skeptic]
- proposal: [text]
- mesh_meta: [text]

Required output:
1) Findings (max 8 bullets)
2) Must-fix items (if any)
3) Vote-flip conditions: what would make you vote `agree` after synthesis
4) Risk level (low|medium|high)
5) Optional: `outbox` (e.g., ask another critic to falsify one claim)
```

Synthesis:

```text
You are the $mesh synthesizer for one task.

Hard rules
- Do NOT commit or push.
- Do NOT apply patches; output unified diff text only.

Inputs:
- task_id: [ID]
- mesh_meta: [text]
- proposal: [text]
- critiques: [critic_a, critic_b, skeptic]

Required output:
1) Decision log: map each critique point -> accepted/rejected + reason
2) Patch: unified diff (text)
3) Validation: list exact commands to run (align with mesh_meta unless you updated it explicitly)
4) Residual risk (low|medium|high)
5) Optional: `outbox` (e.g., questions for voters; call out remaining uncertainty)
```

Vote:

```text
You are one $mesh voter for one task.

Hard rules
- Do NOT commit or push.
- Do NOT propose new work; vote on what exists.

Inputs:
- task_id: [ID]
- role: [proposer|critic_a|critic_b|skeptic|synthesizer]
- synthesis: [diff + decision log]

Required output:
vote: agree|disagree
reason: <one line>
```

Ergonomics: end user-facing run output with:

"Reply with `$mesh` to run the next ready task from the `$st` plan."
