---
name: mesh
description: Execute plan-driven orchestration with CSV waves, strict coder+reducer-to-fixer-to-integrator unit gates, and budget-aware parallelism. Use for `$mesh`, parallel step execution from `update_plan`, `spawn_agents_on_csv` wave runs, CAS budget clamping, and event-only orchestration ledgers.
---

# mesh

## Overview

`$mesh` is the execution engine for implementation orchestration:

- Uses `update_plan` as the canonical ready queue.
- Slices coarse steps into atomic units.
- Builds disjoint-scope CSV waves.
- Executes waves with `spawn_agents_on_csv`.
- Enforces `coder + reducer -> fixer -> integrator` on each unit.
- Defaults coding phases to dual-author cohorts (`coder x2`, `reducer x1`) and safety cohorts (`fixer x3`, `integrator x3`) with safe degrade/restore.
- Emits an event-only orchestration ledger.

## Zig CLI Iteration Repos

When iterating on the Zig-backed `mesh` helper CLI path, use these two repos:

- `skills-zig` (`/Users/tk/workspace/tk/skills-zig`): source for the `mesh` Zig binary, build/test wiring, and release tags.
- `homebrew-tap` (`/Users/tk/workspace/tk/homebrew-tap`): Homebrew formula updates/checksum bumps for released `mesh` binaries.

## Quick Start (Zig Binary + Brew Bootstrap)

```bash
run_mesh() {
  install_mesh_direct() {
    local repo="${SKILLS_ZIG_REPO:-$HOME/workspace/tk/skills-zig}"
    if ! command -v zig >/dev/null 2>&1; then
      echo "zig not found. Install Zig from https://ziglang.org/download/ and retry." >&2
      return 1
    fi
    if [ ! -d "$repo" ]; then
      echo "skills-zig repo not found at $repo." >&2
      echo "clone it with: git clone https://github.com/tkersey/skills-zig \"$repo\"" >&2
      return 1
    fi
    if ! (cd "$repo" && zig build -Doptimize=ReleaseSafe); then
      echo "direct Zig build failed in $repo." >&2
      return 1
    fi
    if [ ! -x "$repo/zig-out/bin/mesh" ]; then
      echo "direct Zig build did not produce $repo/zig-out/bin/mesh." >&2
      return 1
    fi
    mkdir -p "$HOME/.local/bin"
    install -m 0755 "$repo/zig-out/bin/mesh" "$HOME/.local/bin/mesh"
  }

  local os="$(uname -s)"
  if command -v mesh >/dev/null 2>&1 && mesh --help 2>&1 | grep -q "mesh.zig"; then
    mesh "$@"
    return
  fi

  if [ "$os" = "Darwin" ]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "homebrew is required on macOS: https://brew.sh/" >&2
      return 1
    fi
    if ! brew install tkersey/tap/mesh; then
      echo "brew install tkersey/tap/mesh failed." >&2
      return 1
    fi
  elif ! (command -v mesh >/dev/null 2>&1 && mesh --help 2>&1 | grep -q "mesh.zig"); then
    if ! install_mesh_direct; then
      return 1
    fi
  fi

  if command -v mesh >/dev/null 2>&1 && mesh --help 2>&1 | grep -q "mesh.zig"; then
    mesh "$@"
    return
  fi
  echo "mesh binary missing or incompatible after install attempt (marker mesh.zig not found)." >&2
  if [ "$os" = "Darwin" ]; then
    echo "expected install path: brew install tkersey/tap/mesh" >&2
  else
    echo "expected direct path: SKILLS_ZIG_REPO=<skills-zig-path> zig build -Doptimize=ReleaseSafe" >&2
  fi
  return 1
}

run_mesh --help
```

## Commands

- `mesh budget`: compute active-unit clamp from 5-hour + weekly remaining budget.
- `mesh plan_sync`: summarize and normalize plan JSON payloads.
- `mesh slice`: produce atomic units from plan steps.
- `mesh wave`: emit a wave-template CSV from sliced units.
- `mesh run_csv`: validate input CSV, enforce template/output path separation, and prepare output CSV.
- `mesh ledger`: filter ledger payloads to occurred events only.
- `mesh replay`: preflight simulation of budget/wave behavior without execution.

## Final Response Ledger Rendering (Required)

When orchestration actually ran (wave spawn, retries/replacements, delivery, or budget/scaling events), include the event-only ledger in the final assistant response.

Hard gate:

- If orchestration events occurred, a missing ledger block is an invalid completion; do not finalize until the ledger is present.
- Treat any `spawn_agents_on_csv` run with started/completed/timed_out/replaced items as orchestration activity requiring the ledger block.

Rendering rules:

- Heading: `Orchestration Ledger`
- Body: formatted prose only (no fenced JSON block and no inline JSON).
- Use deterministic line order and omit lines for non-events: `Skills used`, `Wave summary`, `Subagents`, `Budget and scaling`, `CAS instances`, `Retry/replacement events`, `Delivery/join status`.
- Include lane fanout target/effective and degrade/restore events in `Wave summary` whenever dual-author lanes were active.
- If orchestration did not run, omit the `Orchestration Ledger` section entirely.

Template:

````markdown
Orchestration Ledger
- Skills used: st, mesh, spawn_agents_on_csv
- Wave summary: 2 waves (wave1: U00,U10; wave2: U01); fanout target coder/reducer/fixer/integrator=2/1/3/3, effective=2/1/3/2, degraded once (budget_low)
- Subagents: spawned 12, completed 12, timed out 0, replaced 1
- Budget and scaling: tier aware, single-instance clamp at max-active 3
- CAS instances: used false, count 0
- Retry/replacement events: U10 fixer rejected once; replacement succeeded on attempt 2
````

## Orchestration Policy

- Source of truth: `update_plan` queue.
- `$st` sync: when `.step/st-plan.jsonl` is active, keep `$st` and `update_plan` aligned in the same turn.
- Decomposition gate: before spawning non-trivial waves, run `$select` (or equivalent decomposition) so units are atomic and carry explicit scope + proof metadata.
- Claim gate: apply first-wave `$select` `in_progress` claims in `$st` before spawning workers.
- Dependency discipline: run only units whose `$st deps` are satisfied. Treat dependency metadata as advisory only when explicitly requested by the user and all participating `unit_scope` sets are disjoint.
- Unit pipeline (hard gate): `coder + reducer -> fixer -> integrator` as explicit lanes/jobs unless user intent requires a collapsed path.
- Dual-author default (coding phase): run lane cohorts as `coder x2`, `reducer x1`, `fixer x3`, and `integrator x3` per active unit.
- Author adversarial gate: require coder/reducer peer challenge findings before fixer intake.
- Fixer quorum gate: require at least 2 accepts and no blocker reject to promote.
- Integrator trio gate: run one writer and two shadows; close only when writer passes and both shadows accept.
- Delivery default: `patch_first`; use `commit_first` only when explicitly requested.
- Commit materialization gate: if accepted patches are converted to commits, integrator must use `git am` only (no `git apply`-then-commit path).
- Plan-write rule: workers return structured results only; they do not edit plan docs, `.step/st-plan.jsonl`, or ledger artifacts directly.
- Scope quality gate: missing/unknown/overly broad scopes are not parallel-safe; block or serialize those units until scope is narrowed.
- Budget clamp uses strictest remaining window (`min(remaining_5h, remaining_weekly)`):
  - `> 33%`: no budget-based clamp.
  - `10%..33%`: linear clamp.
  - `<= 10%`: single active unit, sequential single-agent execution.
- Concurrency authority: derive one active-unit target during preflight and keep it aligned across `mesh wave --max-active`, `spawn_agents_on_csv.max_concurrency`, and orchestration ledger counts.
- Scale-out gate: only allow CAS multi-instance fanout when backlog/saturation warrants it and strict remaining budget is `> 25%`.
- Lane fanout (safe degrade):
  - `remaining > 15%` and no instability: keep dual-author fanout at `coder x2 + reducer x1` and safety lanes at width `3`.
  - `10% < remaining <= 15%` or prior-wave instability: degrade to width `2`.
  - `remaining <= 10%` or two consecutive unstable waves: degrade to width `1`.
  - Restore by one level after two consecutive clean waves and `remaining > 20%`.
- Failure backpressure: if a wave reports `reject`, timeout, `invalid_output_schema`, lifecycle mismatch, or user `turn_aborted`, set next-wave concurrency to `max(1, floor(previous/2))` and serialize overlapping scopes until a clean wave passes.
- Reject/proof closure gate: never close units with `decision=reject` or `proof_status=fail`; require explicit replacement/re-run evidence first.
- Wave closeout ledger gate: emit/refresh an event-only ledger after each completed wave, not only at final handoff.
- Dirty working tree is not a reason to disable orchestration by itself; continue with disjoint `unit_scope`, read-only workers, and integrator-only writes.

## Core Invariants

- Single-writer: only the integrator applies patches/creates commits; parallel workers are read-only.
- State-writer ownership: only the integrator mutates plan state (`.step/st-plan.jsonl`), task status logs, and orchestration ledger fields.
- Durable DAG: dependency edges live in `.step/st-plan.jsonl` (`$st`). `update_plan` is a derived ready queue.
- Strict outputs: when machine output is required, machine blocks win over narrative text.

## Pipeline Roles (`coder + reducer -> fixer -> integrator`, Dual-Author First)

- `coder`: two candidates per unit; each reports `decision` + `proof_status` + peer `challenge_findings`.
- `reducer`: one candidate per unit; invokes `$reduce`, emits a `Reduce Record`, and may propose a lower-indirection patch.
- `fixer`: three adversarial reviews per promoted candidate; quorum is `>=2 accepts` with no blocker reject.
- `integrator`: one writer plus two shadows; writer applies accepted patch and runs proof, shadows validate scope/proof, and closure requires writer pass + both shadow accepts. Commit materialization from patches uses `git am` only.

## Lane Expansion (Safe Fanout)

For parallel waves, prefer explicit per-unit dual-author plus safety lanes to maximize safe subagent usage:

- Emit `u-<id>-coder-{1..2}`, `u-<id>-reducer-1`, `u-<id>-fixer-{1..3}`, and `u-<id>-integrator-{1..3}` rows/jobs per unit.
- Keep lane dependency order strict (`coder + reducer -> fixer -> integrator`) per unit id.
- Because `spawn_agents_on_csv` does not enforce dependencies, run lanes as separate waves/spawns (coder/reducer first, then fixer, then integrator).
- Integrator index `1` is writer; integrator indexes `2` and `3` are shadow reviewers.
- If you intentionally collapse lanes (for trivial or serialized units), record the reason in notes/ledger.

## Integration Modes

### Fleet Mode (Super Swarm, Safe)

Goal: high parallelism without write collisions.

- Use `$cas` to run N worker instances.
- Workers run read-only and only propose diffs/patches plus structured result blocks.
- Integrator applies patches sequentially, runs `proof_command`, and produces the delivery artifact.

### Worktree Mode (Isolation First)

Goal: remove filesystem overlap at the cost of setup overhead.

- Create one git worktree per unit.
- Run `coder -> fixer` in each worktree.
- Integrator merges/applies into the main worktree, then runs proof and delivers.

### Test-First Lane

Goal: make correctness cheap by pinning proof signals early.

- Add an initial wave of test-only units that create failing tests and define `proof_command`.
- Implementation units follow and must make those proofs pass.

## CSV-Wave Contract (`spawn_agents_on_csv`)

Required input headers:

- `id`
- `objective`
- `unit_scope`
- `constraints`
- `invariants`
- `proof_command`
- `delivery_mode`
- `attempt`
- `variant`
- `budget_tier`
- `cohort_id`
- `triplet_index` (legacy key name; use as lane index: coder `1..2`, reducer `1`, fixer/integrator `1..3`)
- `candidate_id`
- `role_in_lane`
- `challenge_targets`
- `quorum_rule`

Notes:

- Additional columns are allowed and can be referenced as `{column_name}` placeholders in the
  `instruction` template. A common extension is `lane` (example: `coder|reducer|fixer`).
- Optional dependency columns: `depends_on` and `dep_policy` (`strict` default, `advisory` only by explicit user request).
- Optional state column: `plan_write` (`integrator_only` recommended default).

### `spawn_agents_on_csv` Tool Arguments (Upstream Codex)

`spawn_agents_on_csv` takes:

- `csv_path` (required): path to the input CSV
- `instruction` (required): template string; `{column_name}` placeholders expand per row
- `id_column` (optional): which column to use as stable `item_id` (duplicates are suffixed)
- `output_csv_path` (optional): exported CSV path (default is derived from input filename)
- `max_concurrency` (optional): max parallel workers (default 16; capped by config; max 64)
- `max_workers` (optional): alias for `max_concurrency`
- `max_runtime_seconds` (optional): per-worker runtime timeout (default 1800)
- `output_schema` (optional): JSON shown to workers as the expected schema (not runtime-validated)

Agent-job mechanics:

- Collaboration tools + sqlite must be enabled for agent jobs.
- Job spawning is subject to `agent_max_depth`; deep fanout may be blocked.
- Workers must call `report_agent_job_result` exactly once; missing reports are failures.
- Workers may cancel remaining pending items by setting `stop: true` in `report_agent_job_result`.

Role note:

- `spawn_agents_on_csv` spawns generic agent-job workers (no configured `agent_role`). If lane semantics are needed, encode lane (for example `coder|reducer|fixer`) in CSV/instruction, or run separate lane jobs.

Placeholder escaping:

- Use `{{` and `}}` to emit literal braces in the rendered instruction.
- To show a placeholder literally (without expansion), write `{{column_name}}`.

### Canonical CSV Example (Fully Filled)

This is a minimal, parseable example row that maps a plan task into one atomic unit.

```csv
id,objective,unit_scope,constraints,invariants,proof_command,delivery_mode,attempt,variant,budget_tier
u-001,"Fix flaky parser: treat trailing commas as invalid","src/parser.py; tests/test_parser.py","Do not change public API; keep diff minimal; no git push","No new allocations in hot path; reject invalid input at boundary","uv run pytest tests/test_parser.py::test_reject_trailing_comma","patch_first",1,"wave","aware"
```

Field mapping from a typical subagent task template:

- Plan/Goals/Task/Acceptance -> `objective`
- Location/File paths -> `unit_scope`
- Constraints/Risks/"do not touch" -> `constraints`
- Invariants/"must never" rules -> `invariants`
- Validation command -> `proof_command`
- Commit vs patch delivery choice -> `delivery_mode` (if materializing commit(s) from patches, use `git am` only)

Required worker output fields:

- `id`
- `candidate_id`
- `triplet_index` (legacy key name; lane index semantics)
- `decision`
- `proof_status`

These fields are expected inside the worker's `report_agent_job_result.result` object (exported in
the `result_json` column). See `references/output-contract.md`.

### Machine Output Precedence (Strict Mode)

When using Codex agent jobs, the machine output is the `report_agent_job_result` tool call.
Prefer the recorded `result_json` over any narrative text.
If `result_json` is missing or cannot be parsed, classify the unit as `invalid_output_schema`.

Recommended strict-mode contract: `references/output-contract.md`.

Optional output fields:

- `failure_code`
- `patch`
- `notes`

Export note:

- `spawn_agents_on_csv` exports an output CSV that includes the original input columns plus job
  metadata columns like `job_id`, `item_id`, `status`, `attempt_count`, `last_error`, and
  `result_json`.

Important:

- Keep `csv_path` and `output_csv_path` distinct per run.
- `output_schema` metadata is not runtime-enforced by `spawn_agents_on_csv`; mesh must enforce strict output parsing before integration.

## Recommended Flow

1. `mesh budget --remaining-five-hour <pct> --remaining-weekly <pct> --max-threads 12`
2. `mesh plan_sync --input-json <plan.json>`
3. `mesh slice --input-json <plan.json> --output-json <units.json>`
4. `mesh wave --units-json <units.json> --csv-path <run-wave.csv> --max-active <n>`
5. `mesh run_csv --csv-path <run-wave.csv> --output-csv-path <run-output.csv>` for preflight/contract checks.
6. Run `spawn_agents_on_csv` against `<run-wave.csv>` with a distinct output CSV path.
   - Recommended: set `id_column: "id"`, pass an `output_schema` matching `references/output-contract.md`, and clamp `max_concurrency` to your current safe parallelism.
7. `mesh ledger --input-json <ledger.json>` to emit event-only final ledger payload.

## Preflight Checklist (Required Before Wave Spawn)

Treat this as a hard gate. If any check fails, do not spawn workers for that wave.

1. Decomposition gate (`$select`/equivalent completed).
   - Ensure candidate units are atomic and include explicit `unit_scope`, constraints/invariants, and proof commands.
   - Avoid manual wave CSV authoring from coarse tasks unless the user explicitly requests it.
2. Claim gate.
   - If `$select` emitted first-wave claims, apply those `in_progress` updates in `$st` before spawn.
3. Runnable-unit gate (`$st deps` satisfied).
   - Exclude units with unresolved dependencies from the candidate wave.
   - If zero runnable units remain, emit no-runnable preflight and stop.
4. Scope quality gate.
   - Treat missing/unknown/overly broad scopes as unsafe for parallelism.
   - Block the wave or serialize those units until scope is narrowed.
5. Scope isolation gate (`unit_scope` disjointness).
   - Keep overlapping write scopes out of the same wave.
   - If overlap cannot be separated safely, serialize that scope (`max_active=1` for that lane).
6. Concurrency authority gate (single active-unit target).
   - Compute one active-unit target from budget preflight.
   - Use the same number in `mesh wave --max-active`, `spawn_agents_on_csv.max_concurrency`, and ledger reporting.
7. CSV hygiene gate.
   - Require distinct `csv_path` and `output_csv_path`.
   - Run `mesh run_csv` before spawn to validate headers/shape and output path separation.
8. Strict output gate.
   - Require worker `result_json` fields `id`, `candidate_id`, `triplet_index`, `decision`, and `proof_status`.
   - If strict parsing fails, classify as `invalid_output_schema` and block integration for that unit.
9. Reject/proof closure gate.
   - Do not close units with `decision=reject` or `proof_status=fail`.
   - Require explicit replacement/re-run evidence before closure.
10. State-writer ownership gate.
   - Workers must return structured results only.
   - Integrator alone mutates `.step/st-plan.jsonl`, plan/task status logs, and ledger fields.
11. Launch gate.
   - Spawn only after all gates pass for the wave.
   - Keep `id_column: "id"` and use the preflight concurrency authority value.
12. Backpressure gate for next wave.
   - On `reject`, timeout, lifecycle mismatch, `invalid_output_schema`, or `turn_aborted`, reduce next-wave concurrency to `max(1, floor(previous/2))`.
   - Serialize overlapping scopes until a clean wave passes.

### Preflight Command Skeleton (Copy/Paste)

```bash
# Inputs (set these per run)
PLAN_JSON=/tmp/plan.json
UNITS_JSON=/tmp/units.json
WAVE_CSV=/tmp/mesh_wave.csv
WAVE_OUT_CSV=/tmp/mesh_wave.out.csv
REMAINING_5H=40
REMAINING_WEEKLY=28
MAX_THREADS=12

# 1) Budget -> choose one active-unit target (ACTIVE_UNITS) and reuse it everywhere.
mesh budget --remaining-five-hour "$REMAINING_5H" --remaining-weekly "$REMAINING_WEEKLY" --max-threads "$MAX_THREADS"

# 2) Normalize plan and slice runnable units.
mesh plan_sync --input-json "$PLAN_JSON"
mesh slice --input-json "$PLAN_JSON" --output-json "$UNITS_JSON"

# 3) Build wave with the single concurrency authority value.
mesh wave --units-json "$UNITS_JSON" --csv-path "$WAVE_CSV" --max-active <ACTIVE_UNITS>

# 4) Preflight CSV contract and path separation before spawning workers.
mesh run_csv --csv-path "$WAVE_CSV" --output-csv-path "$WAVE_OUT_CSV"
```

Then run `spawn_agents_on_csv` with:

- `csv_path: <WAVE_CSV>`
- `output_csv_path: <WAVE_OUT_CSV>` (must be different from input)
- `id_column: "id"`
- `max_concurrency: <ACTIVE_UNITS>` (same value used in `mesh wave --max-active`)
- `output_schema` aligned to `references/output-contract.md`

## Replay Mode

Use `mesh replay` to simulate orchestration before spending budget:

```bash
mesh replay --remaining-five-hour 62 --remaining-weekly 41 --max-threads 12 --ready-units 19
```

Replay returns predicted active-unit clamp, wave count, and per-wave unit counts.

## Validation

```bash
mesh --help
mesh budget --remaining-five-hour 40 --remaining-weekly 28 --max-threads 12
mesh replay --remaining-five-hour 72 --remaining-weekly 55 --max-threads 12 --ready-units 24
mesh run_csv --csv-path /tmp/mesh_wave.csv --output-csv-path /tmp/mesh_wave.out.csv
```

## References

- `references/failure-taxonomy.md`
- `references/coder-rubric.md`
- `references/output-contract.md`
- `references/orchestration-anti-patterns.md`

## Handoff Checklist

- Capture the proof command and outcome in the orchestration ledger.
- Final-response gate: if orchestration activity occurred, include the `Orchestration Ledger` formatted prose block in the final response before handoff.
- Persist reusable orchestration footguns/rules in `.learnings.jsonl` (prefer one record).
- For cross-agent handoffs, dual-write key outcomes to both memory and `.learnings.jsonl`.
