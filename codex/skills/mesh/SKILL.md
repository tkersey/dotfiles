---
name: mesh
description: Execute plan-driven streaming orchestration with scope-gated mutating lanes, prove-selected worktree execution, and budget-aware scaling. Use for `$mesh`, parallel step execution from `update_plan`, `spawn_agents_on_csv` rolling batches, CAS budget clamping, and event-only orchestration ledgers.
---

# mesh

## Overview

`$mesh` is the execution engine for implementation orchestration:

- Uses `update_plan` as the canonical ready queue.
- Runs a streaming per-unit state machine.
- Uses `spawn_agents_on_csv` in rolling batches.
- Enforces candidate -> adjudication -> proof -> delivery gates.
- Uses coder/reducer for candidate generation, fixer for selection, prover for proof, and integrator for delivery.
- Emits event-only orchestration ledger output.

Core execution model:

- `planned -> candidates_ready -> fixer_selected -> proofs_ready -> completed`
- no global wave barrier; units progress independently once dependencies are satisfied.

## Compliance Guardrails (Fail-Closed)

- Do not claim `$mesh` orchestration if execution only used direct `spawn_agent` workers or a single-lane `coder` run without downstream lanes.
- Default lane matrix per unit is mandatory unless explicitly overridden by the user:
  - candidate cohort: `coder` + `reducer` (distinct `candidate_id`/`triplet_index`)
  - adjudication: `fixer` quorum by `risk_tier` (selects one candidate or no-op)
  - proof: `prover` runs for the fixer-selected candidate only
  - delivery/state write: `integrator`
- Collapsed path is allowed only on explicit user request; record the override in ledger output and keep unit closure criteria explicit.
- Never close a unit in `$st` without fixer accept + integrator completion evidence (or explicit collapsed-path override).

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

- `coder x1 + reducer x1`: generate 2 candidate patch artifacts per unit (prefer more units over more candidates).
- `fixer`: select one candidate (or no-op) per unit; proof runs after selection.
- `prover`: apply the selected patch in an isolated worktree and run `proof_command` with bounded retry.
- `integrator`: package/land the proven patch and write plan/ledger state.

Risk-adaptive fixer quorum:

- low: 1
- med: 2
- high: 3

## Orchestration Policy

- Source of truth: `update_plan` ready queue; keep `$st` synchronized in the same turn when active.
- Decomposition gate: run `$select` (or equivalent) before non-trivial execution.
- $select adapter (recommended): map OrchPlan `task.scope` -> unit `write_scope` and `task.validation[0]` -> unit `proof_command`.
- Dependency gate: schedule only units with satisfied `$st` deps.
- Candidate gate: require `coder x1 + reducer x1` per unit unless explicitly overridden (e.g. add a second coder only for high-risk/ambiguous units).
- Proof gate: prove only the fixer-selected candidate (do not prove-all by default).
- Floor gate (strict): when runnable units are `>= 3`, fail preflight unless the planned path can achieve effective peak `>= 3` on `spawn_agents_on_csv`.
- Scope gate: only run parallel mutating/proof work when unit `write_scope` sets are disjoint.
- Plan-write rule: workers return structured results only; only integrator writes plan state.
- Completion gate: close a unit only when (a) fixer accepted, (b) prover proof_status is pass for selected-candidate units, and (c) integrator delivery succeeded.
- Anti-pattern gate: a coder-only wave is not a valid completion path unless a collapsed-path override is explicitly requested.
- Artifact retention gate (hard): all `spawn_agents_on_csv` `csv_path` + `output_csv_path` must be durable (not repo-ephemeral) so `$seq` can postmortem. Default root: `${CODEX_MESH_ARTIFACT_ROOT:-$HOME/.codex/mesh-artifacts}/<YYYY>/<MM>/<DD>/run-<stamp>/`. Fail the handoff if `seq orchestration-concurrency` reports `csv_rows_missing>0`.
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
- `base_sha`
- `delivery_mode`
- `attempt`
- `variant`
- `budget_tier`

Required worker output fields are defined in:

- `references/output-contract.md` (Mesh Output Contract v2)

## Recommended Flow

1. Convert planning output to units (recommended):
   - If you used `$select`, write the emitted OrchPlan to a file and run:
     `mesh orchplan_to_units --orchplan /tmp/orchplan.yaml --output-json /tmp/units.json`
2. Prepare a durable CRFIP candidate batch under `${CODEX_MESH_ARTIFACT_ROOT:-$HOME/.codex/mesh-artifacts}`:
   - `mesh prepare_crfip_batch --units-json /tmp/units.json --max-active <n> --max-concurrency <m> --fail-on-floor`
3. `mesh budget --remaining-five-hour <pct> --remaining-weekly <pct> --max-threads <n>`
4. (Optional) `mesh plan_sync --input-json <plan.json>`
5. (Optional) `mesh slice --input-json <plan.json> --output-json <units.json>`
6. (Optional) Build a ready batch CSV (`mesh wave ...`) only when you are intentionally using legacy lane shapes.
7. (Optional) `mesh run_csv --csv-path <batch.csv> --output-csv-path <batch.out.csv>`
8. Spawn candidate cohort rows per unit (`coder x1 + reducer x1`) via `spawn_agents_on_csv`.
9. Spawn fixer lanes and enforce risk-tier quorum (`low=1`, `med=2`, `high=3`).
10. Spawn prover lanes for fixer-selected candidates only (apply patch in isolated worktree + run `proof_command`).
11. Spawn integrator lane for proven candidates, then write plan state and artifact output.
12. Repeat on next ready units immediately (streaming), rather than waiting for a global barrier.

## Preflight Checklist (Required)

Treat this as a hard gate before each batch spawn.

1. `$select` decomposition completed for non-trivial units.
2. `$st` dependency state allows runnable units.
3. Unit scopes are explicit and not over-broad.
4. Write scopes are explicit and reservation-safe.
5. One active-unit concurrency target is computed and reused.
6. Input/output CSV paths are distinct.
7. CSV artifacts are durable (default `${CODEX_MESH_ARTIFACT_ROOT:-$HOME/.codex/mesh-artifacts}`; avoid repo-ephemeral `.mesh/` and `.step/`). Prefer `mesh prepare_crfip_batch`.
8. Worker output parser is configured for contract v2.
9. Retry/backpressure settings are set for this batch.
10. Ledger event sink is enabled for occurred-event reporting.
11. Batch CSV header set includes `base_sha` (required by current `mesh run_csv` preflight).
12. Candidate cohort wave has `coder x1 + reducer x1` rows per unit (or an explicit override is recorded).
13. Mesh-truth precheck passes by running: `seq orchestration-concurrency --path <session_jsonl> --fail-on-mesh-truth --format table`.
14. Deadlock lint passes for dependency CSV (`id,depends_on,interactive_lead`) before batch spawn when interactive lead tasks are present.

## Validation

```bash
mesh --help
mesh budget --remaining-five-hour 40 --remaining-weekly 28 --max-threads 12
mesh replay --remaining-five-hour 72 --remaining-weekly 55 --max-threads 12 --ready-units 24
mesh prepare_crfip_batch --units-json /tmp/units.json --max-active 6 --max-concurrency 12 --fail-on-floor
mesh run_csv --csv-path /tmp/mesh_batch.csv --output-csv-path /tmp/mesh_batch.out.csv
mesh run_csv --csv-path /tmp/mesh_batch.csv --output-csv-path /tmp/mesh_batch.out.csv --max-concurrency 6 --runnable-units 6 --floor-threshold 3 --fail-on-floor
mesh contract_drift_lint
seq orchestration-concurrency --path /absolute/path/to/rollout.jsonl --fail-on-mesh-truth --format table
mesh lane_completeness_lint --check candidate_crfip /tmp/mesh_batch.csv
mesh lane_completeness_lint --check crfip --require-spawn-substrate .mesh/*.exec.out.csv
mesh lane_completeness_lint --check crfip --deps-csv /tmp/mesh_deps.csv .mesh/*.exec.out.csv
mesh doctor --rollout-jsonl /absolute/path/to/rollout.jsonl --expect-mesh-truth --require-artifacts --lane-check crfip --require-spawn-substrate
```

## References

- `references/output-contract.md`
- `references/streaming-cutover-phases.md`
- `references/orchestration-anti-patterns.md`
- `references/failure-taxonomy.md`

## Handoff Checklist

- Capture proof evidence for accepted candidates.
- Capture retry/backpressure events when they occur.
- Before claiming `$mesh`, run mesh-truth preflight and fail closed on mismatch: `seq orchestration-concurrency --path <session_jsonl> --fail-on-mesh-truth --format table`.
- Before claiming `$mesh`, fail if artifacts are missing (must be analyzable later): run `seq orchestration-concurrency --path <session_jsonl> --format json` and ensure `csv_rows_missing==0`.
- Optional one-shot: run `mesh doctor --rollout-jsonl <session_jsonl> --expect-mesh-truth --require-artifacts --require-archived-paths --lane-check crfip --require-spawn-substrate`.
- Before claiming `$mesh`, run lane completeness lint on outputs: `mesh lane_completeness_lint --check crfip --require-spawn-substrate .mesh/*.exec.out.csv`.
- When dependency metadata is available, run deadlock hooks in the same gate: `mesh lane_completeness_lint --check crfip --deps-csv /tmp/mesh_deps.csv .mesh/*.exec.out.csv`.
- Include `Orchestration Ledger` in final response only when orchestration actually ran.
- Append one reusable learning to `.learnings.jsonl` when appropriate.
