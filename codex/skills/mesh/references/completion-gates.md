# Mesh Completion Gates

This document defines fail-closed gates for task promotion.

## GateResult v1

Use this shape for each task before status moves to `completed`:

```json
{
  "task_id": "st-123",
  "proof_pass": true,
  "rubric_pass": true,
  "adjudication_resolved": true,
  "scope_lock_clean": true,
  "decision": "promote"
}
```

## Required checks

1. `proof_pass`
   - At least one executable validation command ran.
   - Result is pass and evidence line is recorded.
2. `rubric_pass`
   - Rubric average is at or above threshold.
   - No dimension falls below minimum floor.
3. `adjudication_resolved`
   - Any disagreement has a recorded final authority decision.
4. `scope_lock_clean`
   - No overlapping exclusive scopes remained unresolved at integration time.

## Decision rule

- Promote only when all four checks are `true`.
- Otherwise set `decision` to `rework` or `block`, attach failure code from `failure-taxonomy.md`, and persist evidence.

## Evidence contract

Record these fields in task comments:

1. validation command(s) run
2. pass/fail output key line(s)
3. rubric score breakdown
4. adjudication record ID (if applicable)
5. selected failure code (or `none`)
