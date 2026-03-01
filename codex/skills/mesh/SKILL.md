---
name: mesh
description: Execute plan-driven streaming orchestration with reservation-gated mutating lanes, prove-all worktree execution, and budget-aware scaling. Use for `$mesh`, parallel step execution from `update_plan`, `spawn_agents_on_csv` rolling batches, CAS budget clamping, and event-only orchestration ledgers.
---

# mesh

## Overview

`$mesh` is the execution engine for implementation orchestration:

- Uses `update_plan` as the canonical ready queue.
- Runs a streaming per-unit state machine.
- Uses `spawn_agents_on_csv` in rolling batches.
- Enforces candidate -> proof -> adjudication -> delivery gates.
- Uses coder/reducer for candidate generation, then locksmith/applier/prover for mutating/proof stages.
- Emits event-only orchestration ledger output.

Core execution model:

- `planned -> candidates_ready -> proofs_ready -> fixer_accept -> completed`
- no global wave barrier; units progress independently once dependencies are satisfied.

## Zig CLI Iteration Repos

When iterating on the Zig-backed `mesh` helper CLI path, use these repos:

- `skills-zig` (`/Users/tk/workspace/tk/skills-zig`)
- `homebrew-tap` (`/Users/tk/workspace/tk/homebrew-tap`)

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
  return 1
}

run_mesh --help
```

## Commands

- `mesh budget`: compute active-unit clamp from 5-hour + weekly remaining budget.
- `mesh plan_sync`: normalize plan JSON payloads.
- `mesh slice`: produce atomic units from plan steps.
- `mesh wave`: emit a CSV batch for currently ready units.
- `mesh run_csv`: validate CSV shape and enforce input/output path separation.
- `mesh ledger`: filter ledger payloads to occurred events only.
- `mesh replay`: preflight simulation of budget and batch behavior.

## Pipeline Roles

Default roles and responsibilities:

- `coder x2 + reducer x1`: generate 2-3 candidate patch artifacts per unit.
- `locksmith -> applier -> prover`: mutating and proof pipeline for every candidate.
- `fixer`: risk-adaptive quorum selection among proven candidates.
- `integrator`: package accepted artifact and write plan/ledger state.

Risk-adaptive fixer quorum:

- low: 1
- med: 2
- high: 3

## Orchestration Policy

- Source of truth: `update_plan` ready queue; keep `$st` synchronized in the same turn when active.
- Decomposition gate: run `$select` (or equivalent) before non-trivial execution.
- Dependency gate: schedule only units with satisfied `$st` deps.
- Candidate gate: require 2-3 candidates per unit unless explicitly overridden.
- Proof gate: prove all candidates in isolated worktrees with max one retry.
- Reservation gate: mutating phases require write_scope lease grants.
- Plan-write rule: workers return structured results only; only integrator writes plan state.
- Completion gate: close a unit only when fixer accepted and proof status is pass.
- Concurrency authority: compute one active-unit target and reuse it across mesh/batch/ledger reporting.
- Scale-out gate: enable CAS multi-instance only when saturation justifies it and remaining budget is above clamp thresholds.
- Backpressure gate: on reject/timeout/schema failures/turn abort, reduce next-batch concurrency and serialize overlapping scopes.
- Output schema caveat: `spawn_agents_on_csv.output_schema` is advisory; mesh parser enforcement is mandatory.

Budget policy:

- strict remaining budget = `min(remaining_5h, remaining_weekly)`
- `remaining > 33%`: no budget-based clamp
- `10% < remaining <= 33%`: linear clamp
- `remaining <= 10%`: single active unit and sequential execution

## Final Response Ledger Rendering (Required)

When orchestration actually ran, include an `Orchestration Ledger` section.

Rules:

- Format as prose only (no JSON block).
- Omit lines for non-events.
- Deterministic line order:
  - `Skills used`
  - `Wave summary`
  - `Subagents`
  - `Budget and scaling`
  - `CAS instances`
  - `Retry/replacement events`
  - `Delivery/join status`
- If orchestration did not run, omit the section entirely.

## CSV Contract (Streaming Batches)

Required input headers:

- `id`
- `objective`
- `unit_scope`
- `write_scope`
- `constraints`
- `invariants`
- `proof_command`
- `risk_tier`
- `candidate_id`
- `triplet_index`
- `lane`
- `delivery_mode`
- `attempt`
- `variant`
- `budget_tier`

Required worker output fields are defined in:

- `references/output-contract.md` (Mesh Output Contract v2)

## Recommended Flow

1. `mesh budget --remaining-five-hour <pct> --remaining-weekly <pct> --max-threads <n>`
2. `mesh plan_sync --input-json <plan.json>`
3. `mesh slice --input-json <plan.json> --output-json <units.json>`
4. Build a ready batch CSV (`mesh wave ...`) for currently unblocked units.
5. `mesh run_csv --csv-path <batch.csv> --output-csv-path <batch.out.csv>`
6. Spawn candidate lanes (`coder/reducer`) via `spawn_agents_on_csv`.
7. Spawn reservation/proof lanes (`locksmith -> applier -> prover`) for all candidate rows.
8. Spawn fixer lanes; enforce risk-tier quorum.
9. Spawn integrator lane for accepted candidates; write plan state and artifact output.
10. Repeat on next ready units immediately (streaming), rather than waiting for a global barrier.

## Preflight Checklist (Required)

Treat this as a hard gate before each batch spawn.

1. `$select` decomposition completed for non-trivial units.
2. `$st` dependency state allows runnable units.
3. Unit scopes are explicit and not over-broad.
4. Write scopes are explicit and reservation-safe.
5. One active-unit concurrency target is computed and reused.
6. Input/output CSV paths are distinct.
7. Worker output parser is configured for contract v2.
8. Retry/backpressure settings are set for this batch.
9. Ledger event sink is enabled for occurred-event reporting.

## Validation

```bash
mesh --help
mesh budget --remaining-five-hour 40 --remaining-weekly 28 --max-threads 12
mesh replay --remaining-five-hour 72 --remaining-weekly 55 --max-threads 12 --ready-units 24
mesh run_csv --csv-path /tmp/mesh_batch.csv --output-csv-path /tmp/mesh_batch.out.csv
uv run codex/skills/mesh/references/contract_drift_lint.py
```

## References

- `references/output-contract.md`
- `references/streaming-cutover-phases.md`
- `references/orchestration-anti-patterns.md`
- `references/failure-taxonomy.md`

## Handoff Checklist

- Capture proof evidence for accepted candidates.
- Capture lease and retry events when they occur.
- Include `Orchestration Ledger` in final response only when orchestration actually ran.
- Append one reusable learning to `.learnings.jsonl` when appropriate.
