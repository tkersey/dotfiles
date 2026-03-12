# Pipelines for driving planning artifacts

## ORCHPLAN execution (manual; wave-based)
Goal: execute an OrchPlan safely with parallel workers.

1. For each wave `wN` in order:
    - If durable execution is in play, run `st import-orchplan --input <orchplan>` once, then `st claim --ids <wave task ids> --executor teams|mesh --wave wN` before any worker starts.
    - If the task source supports status and no durable ledger is being used, claim the tasks in `wN` first by marking them in-progress (use the source token; default `in_progress`).
    - Treat `depends_on` as mandatory ordering and `related_to` as advisory ordering/context only.
    - Prefer executing `role: contract` tasks early when they unlock multiple downstream tasks.
    - Dispatch each task in `wN` to a worker.
    - Each worker should operate within `task.scope` using the lock-root contract in `codex/skills/select/references/lock-roots.md` and use `task.location` to navigate.
    - Each worker should return a patch-first diff plus a proof signal from `task.validation` (or explain what validation is missing).
2. Integrate patches in `integration.order`.
3. If the plan includes `role: checkpoint` or `role: integration` tasks, run their validations as explicit join gates before advancing.
4. Resolve conflicts per `integration.conflict_policy`.
5. Re-run relevant validations; proceed to the next wave only when green.

## ORCHPLAN -> $mesh (streaming; substantive-unit fanout)
Goal: execute an OrchPlan as a streaming run with maximum safe parallelism over substantive units.

1. Ensure each selected task has a tight `scope` list (exclusive lock roots) and at least one `validation` command.
2. Map each task into one primary mesh row per substantive unit:
   - `task_id`: task id
   - `objective`: task title
   - `write_scope`: task `scope`
   - `proof_command`: first `validation` command
   - `risk_tier`: default `med` unless the task is clearly `low|high`
3. Set `id_column=task_id` and `max_concurrency` to the safe row count unless a lower explicit cap is required.
4. Only create secondary review/reduce/fix/prove/integrate rows for units that reported a concrete blocker, a non-trivial diff requiring reduction, or a failed proof.
5. Do not multiply rows just to create lane evidence; a clean primary row is already sufficient evidence for that unit.
6. Artifact retention gate (required): store wave CSVs under `${CODEX_MESH_ARTIFACT_ROOT:-$HOME/.codex/mesh-artifacts}` and fail the handoff if `$seq` reports `csv_rows_missing>0`.
7. If `$st` is the durable source of truth, reconcile the output CSV with `st import-mesh-results --input <output.csv>` before advancing the wave.

## PLANS pipeline (manual)
Goal: iterate `plan-N.md` until the plan is stable and implementation-ready.

1. If no `plan-N.md` exists: create `plan-1.md` (draft).
2. Revise by creating `plan-(N+1).md` until a review pass finds no actionable gaps.
3. Use an explicit stop phrase (recommended): end the run by replying exactly `Plan is ready.`

## SLICES pipeline (manual)
Goal: keep iterating until all slices are `status: closed`, using wave-based execution whenever scopes allow.

1. Create/repair `SLICES.md` by converting the current plan/tasks into slices.
2. Repeat:
    - Run `$select` to claim the next safe wave of ready slices (deps satisfied; not closed).
    - Update `SLICES.md`: set every selected slice in that wave to the in-progress token (prefer the token already used in `SLICES.md`; default `in_progress`).
    - Implement the selected wave in parallel where scopes remain disjoint; if the wave width is `1`, run serially.
    - Integrate the wave and run wave-level verification.
    - Update `SLICES.md`: set each completed slice `status: closed` and record its verification.

## Optional loop form
PLANS (loop-ready):
```text
- Create the next plan revision (plan-(N+1).md)
Stop when: The assistant replies exactly "Plan is ready."
```

SLICES (loop-ready; wave-based):
```text
- Select the next safe wave of ready slices
- Mark the selected wave in_progress in SLICES.md
- Implement and verify the selected wave; update each completed slice to closed with verification.
Stop when: All slices in SLICES.md have status: closed.
```
