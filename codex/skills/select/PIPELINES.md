# Pipelines for driving planning artifacts

## ORCHPLAN execution (manual; wave-based)
Goal: execute an OrchPlan safely with parallel workers.

1. For each wave `wN` in order:
    - If the task source supports status, claim the tasks in `wN` first by marking them in-progress (use the source token; default `in_progress`).
    - Treat `depends_on` as mandatory ordering and `related_to` as advisory ordering/context only.
    - Prefer executing `role: contract` tasks early when they unlock multiple downstream tasks.
    - Dispatch each task in `wN` to a worker.
    - Each worker should operate within `task.scope` (exclusive lock) and use `task.location` to navigate.
    - Each worker should return a patch-first diff plus a proof signal from `task.validation` (or explain what validation is missing).
2. Integrate patches in `integration.order`.
3. If the plan includes `role: checkpoint` or `role: integration` tasks, run their validations as explicit join gates before advancing.
4. Resolve conflicts per `integration.conflict_policy`.
5. Re-run relevant validations; proceed to the next wave only when green.

## PLANS pipeline (manual)
Goal: iterate `plan-N.md` until the plan is stable and implementation-ready.

1. If no `plan-N.md` exists: create `plan-1.md` (draft).
2. Revise by creating `plan-(N+1).md` until a review pass finds no actionable gaps.
3. Use an explicit stop phrase (recommended): end the run by replying exactly `Plan is ready.`

## SLICES pipeline (manual)
Goal: keep iterating until all slices are `status: closed`.

1. Create/repair `SLICES.md` by converting the current plan/tasks into slices.
2. Repeat:
    - Select the next ready slice (deps satisfied; not closed).
    - Update `SLICES.md`: set the selected slice `status` to the in-progress token (prefer the token already used in `SLICES.md`; default `in_progress`).
    - Implement that slice.
    - Update `SLICES.md`: set the slice `status: closed` and record its verification.

## Optional loop form
PLANS (loop-ready):
```text
- Create the next plan revision (plan-(N+1).md)
Stop when: The assistant replies exactly "Plan is ready."
```

SLICES (loop-ready; serial execution):
```text
- Select the next ready slice
- Mark the selected slice in_progress in SLICES.md
- Implement the selected slice; update SLICES.md to mark it closed with verification.
Stop when: All slices in SLICES.md have status: closed.
```
