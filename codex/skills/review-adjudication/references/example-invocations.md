# Example invocations

## Surface-Budgeted v6 review adjudication

```md
Use $review-adjudication in Surface-Budgeted v6 mode.

Goal: determine which current PR review comments should change code before any
implementation.

Inputs:
- raw PR review comments with id/thread/reviewer/location/excerpt
- current branch vs main
- branch/head/diff/comment-set identity if available
- PR description / intended change
- current tests and CI status
- relevant files

Rules:
- preserve raw comment identity and input inventory
- bind the adjudication to artifact_state_id
- treat each comment as a claim, not an obligation
- construct the strongest no-change countercase for every comment
- separate concern validity from proposed-fix validity
- use evidence grade + evidence ref for every action
- emit Resolve Selection, Resolve Countercases, Adversarial Action Matrix,
  Resolution Warrants, and Surface Budget Ledger
- do not implement fixes
- do not hand off implementation unless the Adjudication Gate passes and the
  selected action has adversarial clearance
```

## Handoff-agenda consistency check

```md
Use $review-adjudication in Surface-Budgeted v6 mode.

After the Comment Ledger, Resolve Selection, Adversarial Action Matrix, and
Resolution Warrants, produce a Handoff Agenda whose buckets are exact projections:

- items selected for implementation = all and only `address` rows with active
  `mutate-code` warrants and adversarial clearance
- validation-only items = all and only `validate-only` rows
- proof-only thread-resolution items = all and only `resolve-thread-only` rows
- items not selected = all and only `do-not-address` rows
- blocked items = all and only `blocked` rows

Do not use "all". Use explicit comment IDs.
```
