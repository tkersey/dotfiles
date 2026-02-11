---
name: mesh
description: >
  Swarm coordinator for requests that explicitly invoke `$mesh`. Executes ready items from a
  persisted `$st` plan using propose/critique/synthesize/vote, gates completion on consensus +
  validation, and captures durable learnings via `$learnings`.
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

Do NOT treat generic acknowledgements (`go`, `yep`, `ship it`) as invocation.

## Defaults (Unless Overridden)

- `max_tasks`: 1 (attempt at most one task completion per run)
- `parallel_tasks`: 1 (run only one swarm at a time)
- `swarm_roles`: 5 (`proposer`, `critic_a`, `critic_b`, `skeptic`, `synthesizer`)
- `fallback_swarm_roles`: 3 (`proposer`, `skeptic`, `synthesizer`) when capacity is insufficient
- `consensus_threshold`: 4/5 agree (5-role) or 3/3 agree (fallback)
- `consensus_retries`: 2

Override precedence (highest to lowest):
1) invocation args
2) per-task `mesh` metadata block in `$st` notes
3) defaults above

## Runtime Adapter (Required)

`$mesh` must pick a worker transport that exists in the current runtime.

Supported transports:

1) OpenCode Task-tool transport (preferred here)
- Spawn workers with `functions.task`.
- Use `multi_tool_use.parallel` to run independent role calls concurrently.
- Communication is orchestrator-mediated: each round's prompts include prior round artifacts.
- Liveness: a `functions.task` call is the unit of work; if output is unusable or missing, count it
  as `no_response` and retry by spawning a replacement once.

Capacity rule:
- If you cannot run a 5-role swarm for a task (thread cap, spawn failure, or resource limits),
  fall back to the 3-role swarm (`proposer`, `skeptic`, `synthesizer`) for that task.

2) Codex collab transport (optional, if available)
- Use the runtime's multi-agent tools (see `references/codex-multi-agent.md`).
- You MAY reuse live workers for the vote step via follow-up messaging if supported.

If no transport is available, STOP and ask the user to switch runtimes.

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

### Step 0: Hydrate Metadata (If Needed)

If required task metadata is missing:
1) Spawn proposer with `step=hydrate_meta` to generate the `mesh` block.
2) Persist via `$st set-notes`.
3) Reload task meta and proceed.

### Round A: Proposal

Spawn proposer with:
- task id + step
- current `mesh` meta
- current code context (paths listed in `scope`)

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

If your runtime provides a plan UI tool (for example Codex `update_plan` or OpenCode `todowrite`),
mirror `$st` state after each `$st` mutation. Treat the UI as a mirror only.

## Reporting

Return:
- tasks attempted and their final states (`completed`, `blocked`, `pending`)
- consensus telemetry (attempt count, vote tallies)
- validation commands and outcomes
- `$st` mutations performed (ids + statuses)
- learning capture evidence (records appended)

Never fabricate timestamps, tool events, or command outputs.

## Error Handling

- Missing `$mesh` token: do nothing under this skill.
- Plan file missing: stop with the exact `$st init` command.
- Both `.codex/st-plan.jsonl` and `.step/st-plan.jsonl` exist: ask user to pick `plan_file=`.
- No runnable tasks: report ready/blocked/completed counts and exit cleanly.
- Consensus failure after retries: set `blocked` + comment `no_consensus`.
- Worker non-response/unusable output: retry once, then set `blocked` + comment `no_response`.

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
