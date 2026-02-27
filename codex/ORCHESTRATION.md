# Orchestration Runbook

This document is the detailed companion to `codex/AGENTS.md`.

Policy stays in `codex/AGENTS.md` (thin, mandatory gates). Execution details live here.

## Goals

- Correctness first: every unit has an explicit proof signal.
- Speed via parallelism: maximize safe parallelism with disjoint write scopes.
- Auditability: every accept/reject has a concrete evidence anchor.

## Core Invariants

- Single-writer: only the integrator applies patches/creates commits; parallel workers are read-only.
- Durable DAG: dependency edges live in `.step/st-plan.jsonl` ($st). `update_plan` is a derived ready queue.
- Strict outputs: when machine output is required, the machine block wins over narrative text.

## Pipeline Roles (Coder -> Fixer -> Integrator)

- Coder: produce the smallest patch that satisfies acceptance criteria; report `result` with
  `decision` + `proof_status` (+ optional `patch`).
- Fixer: adversarial review for safety/regression/invariant breaks; flip `decision` to `reject`
  with a concrete `failure_code` when needed.
- Integrator: apply accepted patches, run `proof_command`, package delivery (`commit_first` or
  `patch_first`), and update plan/ledger/learnings.

## Recommended Flow (Wave Mode)

1. Adopt `$st` for any plan with dependencies or multi-turn execution.
2. Keep `update_plan` synced from `$st` after each mutation.
3. Slice ready plan items into atomic units:
   - one objective
   - one `unit_scope`
   - one `proof_command`
4. Build a CSV wave: only disjoint `unit_scope` values run in parallel.
5. Execute `coder -> fixer -> integrator` per unit.
6. Emit an event-only ledger (waves, scopes, counts, budget snapshot, retries, delivery artifacts).

Practical note:

- In shared-workspace wave mode, the safest default is read-only workers that propose patches and
  report `proof_status: skipped`, with the integrator applying patches and running proofs.
- If you need worker-executed proofs, use Worktree Mode so each unit runs in an isolated checkout.

## Context Engineering: Plan Task -> Mesh Unit

Mesh units are rows with these key fields:

- `objective`: task ID/name + why + acceptance criteria (short, testable).
- `unit_scope`: explicit paths (files/dirs) and boundaries; keep it small and disjoint.
- `constraints`: hard rules and "do not touch" areas.
- `invariants`: must-not-break statements that make review mechanical.
- `proof_command`: one command that supports the claim (prefer `fail -> pass`).
- `delivery_mode`: `commit_first` (default) or `patch_first`.
- `attempt`: start at `1`, increment on retry/replacement.
- `variant`: execution strategy tag (example: `wave`, `fleet`, `worktree`, `test_first`).
- `budget_tier`: concurrency policy tag (example: `aware`, `tight`, `all_out`).

## Agent Jobs: `spawn_agents_on_csv` (Upstream Codex)

Mesh wave execution typically uses Codex agent jobs:

- `spawn_agents_on_csv`: spawns one worker sub-agent per CSV row.
- `report_agent_job_result`: worker-only tool to report a per-row JSON result.

Key mechanics (from `openai/codex`):

- Tools are available only when collaboration tools + sqlite are enabled.
- Job spawning enforces `agent_max_depth`; deep subagents may be unable to spawn more workers.

- The `instruction` string is a template; `{column_name}` placeholders expand per row.
- Use `{{` and `}}` to emit literal braces; to show a placeholder literally write `{{column}}`.
- If `id_column` is provided, that column becomes `item_id`; duplicates are suffixed (`foo`, `foo-2`).
- Concurrency defaults to 16, caps at 64, and is additionally capped by configured `max_threads`.
- Each worker has a max runtime (default 1800s) after which the item is failed.
- Workers MUST call `report_agent_job_result` exactly once; missing reports are failures.
- Workers may cancel remaining pending items by passing `stop: true` to `report_agent_job_result`.

Role note:

- `spawn_agents_on_csv` spawns generic agent-job workers (no configured `agent_role`). If you want
  coder/fixer semantics, encode the lane in the CSV (example: `lane=coder|fixer`) and include it
  in the instruction template, or run separate jobs per lane.

Export behavior:

- Output CSV includes the original input columns plus job metadata columns including `job_id`,
  `item_id`, `status`, `attempt_count`, `last_error`, and `result_json`.

Example tool call (shape only):

```json
{
  "csv_path": "/abs/path/to/wave.csv",
  "instruction": "Lane: {lane}\nImplement unit {id}\nObjective: {objective}\nScope: {unit_scope}\nProof: {proof_command}\n\nIf lane=coder: propose a patch and set proof_status=skipped.\nIf lane=fixer: review proposed patch and set decision=accept|reject.",
  "id_column": "id",
  "output_csv_path": "/abs/path/to/wave.out.csv",
  "max_concurrency": 8,
  "max_runtime_seconds": 1800,
  "output_schema": {
    "type": "object",
    "required": ["id", "decision", "proof_status"]
  }
}
```

For mesh strict result keys and early-stop semantics, see `codex/skills/mesh/references/output-contract.md`.

## Machine Output Precedence

When an executor expects machine-readable output (CSV cells, JSONL, explicit result blocks):

- Put the machine block last.
- If both machine output and narrative exist, parsers MUST prefer the machine output.
- If the machine block is missing/invalid, fail closed and classify as `invalid_output_schema`.

For `spawn_agents_on_csv`, the machine output is the `report_agent_job_result` tool call and the
exported `result_json` column in the output CSV.

## Optional Integration Modes

### Fleet Mode (Super Swarm, Safe)

Goal: high parallelism without write collisions.

- Use `$cas` to run N worker instances.
- Workers run read-only and only propose diffs/patches + structured result blocks.
- Integrator applies patches sequentially, runs `proof_command`, and produces the delivery artifact.

### Worktree Mode (Isolation First)

Goal: remove filesystem overlap at the cost of more setup.

- Create one git worktree per unit.
- Run `coder -> fixer` in the worktree.
- Integrator merges/applies into the main worktree, then runs proof and delivers.

### Test-First Lane

Goal: make correctness cheap by pinning proof signals early.

- Add an initial wave of "tests only" units that create failing tests and define `proof_command`.
- Implementation units follow and must make those proofs pass.

## Handoff Checklist

- Capture the proof command and its outcome in the ledger.
- Persist any new rule/footgun in `.learnings.jsonl` (prefer 1 record).
- For cross-agent handoffs, dual-write key outcomes to both memory and `.learnings.jsonl`.
