---
name: mesh
description: Execute plan-driven orchestration with CSV waves, strict coder->fixer->integrator unit gates, and budget-aware parallelism. Use for `$mesh`, parallel step execution from `update_plan`, `spawn_agents_on_csv` wave runs, CAS budget clamping, and event-only orchestration ledgers.
---

# mesh

## Overview

`$mesh` is the execution engine for implementation orchestration:

- Uses `update_plan` as the canonical ready queue.
- Slices coarse steps into atomic units.
- Builds disjoint-scope CSV waves.
- Executes waves with `spawn_agents_on_csv`.
- Enforces `coder -> fixer -> integrator` on each unit.
- Emits an event-only orchestration ledger.

## Quick Start (Zig Binary + Brew Bootstrap)

```bash
run_mesh() {
  if command -v mesh >/dev/null 2>&1 && mesh --help 2>&1 | grep -q "mesh.zig"; then
    mesh "$@"
    return
  fi
  if [ "$(uname -s)" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
    if ! brew install tkersey/tap/mesh; then
      echo "brew install tkersey/tap/mesh failed; refusing fallback." >&2
      return 1
    fi
    if command -v mesh >/dev/null 2>&1 && mesh --help 2>&1 | grep -q "mesh.zig"; then
      mesh "$@"
      return
    fi
    echo "brew install tkersey/tap/mesh did not produce a compatible mesh binary." >&2
    return 1
  fi
  echo "mesh binary missing or incompatible (marker mesh.zig not found)." >&2
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

## Orchestration Policy

- Source of truth: `update_plan` queue.
- `$st` sync: when `.step/st-plan.jsonl` is active, keep `$st` and `update_plan` aligned in the same turn.
- Unit pipeline (hard gate): `coder -> fixer -> integrator`.
- Delivery default: `commit_first`; use `patch_first` only when explicitly requested.
- Budget clamp uses strictest remaining window (`min(remaining_5h, remaining_weekly)`):
  - `> 33%`: no budget-based clamp.
  - `10%..33%`: linear clamp.
  - `<= 10%`: single active unit, sequential single-agent execution.
- Scale-out gate: only allow CAS multi-instance fanout when backlog/saturation warrants it and strict remaining budget is `> 25%`.

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

Required worker output fields:

- `id`
- `decision`
- `proof_status`

Optional output fields:

- `failure_code`
- `patch_ref`
- `commit_ref`
- `notes`

Important:

- Keep `csv_path` and `output_csv_path` distinct per run.
- `output_schema` metadata is not runtime-enforced by `spawn_agents_on_csv`; mesh must enforce strict output parsing before integration.

## Recommended Flow

1. `mesh budget --remaining-five-hour <pct> --remaining-weekly <pct> --max-threads 12`
2. `mesh plan_sync --input-json <plan.json>`
3. `mesh slice --input-json <plan.json> --output-json <units.json>`
4. `mesh wave --units-json <units.json> --csv-path <run-wave.csv> --max-active <n>`
5. Run `spawn_agents_on_csv` against `<run-wave.csv>` with a distinct output CSV path.
6. `mesh run_csv --csv-path <run-wave.csv> --output-csv-path <run-output.csv>` for preflight/contract checks.
7. `mesh ledger --input-json <ledger.json>` to emit event-only final ledger payload.

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
