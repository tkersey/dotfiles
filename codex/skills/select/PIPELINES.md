# Pipelines for driving planning artifacts

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
