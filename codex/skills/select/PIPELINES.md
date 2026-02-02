# Pipelines for driving planning artifacts

## ORCHPLAN execution (manual; wave-based)
Goal: execute an OrchPlan safely with parallel workers.

1. For each wave `wN` in order:
   - Dispatch each task in `wN` to a worker.
   - Each worker should operate within `task.scope` (exclusive lock) and use `task.location` to navigate.
   - Each worker should return a patch-first diff plus a proof signal from `task.validation` (or explain what validation is missing).
2. Integrate patches in `integration.order`.
3. Resolve conflicts per `integration.conflict_policy`.
4. Re-run relevant validations; proceed to the next wave only when green.

## PLANS pipeline (manual)
Goal: iterate `plan-N.md` until `$gen-plan` says `Plan is ready.`

1. If no `plan-N.md` exists: run `$gen-plan` (it will ask clarifying questions, then create `plan-1.md`).
2. Re-run `$gen-plan` to create `plan-(N+1).md` until it replies exactly `Plan is ready.`

## SLICES pipeline (manual)
Goal: keep iterating until all slices are `status: closed`.

1. Run `$slice` to create/repair `SLICES.md` (generate mode).
2. Repeat:
   - Run `$slice` (next mode) to choose the next slice.
   - Implement that slice.
   - Update `SLICES.md`: set the slice `status: closed` and record its verification.

## Optional `$loop` form
PLANS (loop-ready):
```text
- $gen-plan
Stop when: The assistant replies exactly "Plan is ready."
```

SLICES (loop-ready; serial execution):
```text
- $slice (next)
- Implement the selected slice; update SLICES.md to mark it closed with verification.
Stop when: All slices in SLICES.md have status: closed.
```
