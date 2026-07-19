# Ship Record

```yaml
ship_record:
  record_version: SHIP-v1
  source: direct | actuation
  branch:
  base_branch:
  head_sha:
  existing_pr:
    exists:
    url:
    draft:
  validation:
    build:
    lint:
    tests:
    language_specific:
    acceptance:
  pr_readiness:
    mode: ready | draft | update-existing | promote-draft | blocked
    reason:
    draft_allowed_reason:
  action:
    command:
    result:
    pr_url:
  actuation_binding:
    actuation_run_id:
    state_fingerprint:
```

`pr_readiness.mode` is a compatibility projection from the internal two-axis
`pr_decision`:

```yaml
pr_decision:
  operation: create | update | update-and-promote | blocked
  final_state: ready | draft | preserve
  compatibility_mode: ready | draft | update-existing | promote-draft | blocked
```

- `create` + `ready` -> `ready`;
- `create` + `draft` -> `draft`;
- `update` + `preserve` -> `update-existing`;
- `update-and-promote` + `ready` -> `promote-draft`;
- invalid or ambiguous state -> `blocked`.

`action.command` may record an ordered sequence: body update, optional promotion,
and live readback. `created`, `updated`, or `promoted` is valid only after the
live PR matches the intended repository, base ref and SHA, head ref and SHA,
open/draft state, and managed proof block. A successful mutation command with a
failed readback must report `blocked` plus the observed partial side effect.

`actuation_binding` is required when `source=actuation` and the readiness mode
is ready, update-existing, or promote-draft. It is omitted for direct shipping.
The exact two-field binding is copied verbatim from the actuation input and
treated as opaque by Ship. For `artifact-kernel-v1`, Actuating produces the
transient compatibility projection
`closure_receipt.receipt_id -> actuation_run_id` and
`closure_receipt.subject_digest -> state_fingerprint`. Ship requires that exact
match against the supplied closure receipt, copies it, and never synthesizes or
relabels it. It must not be reconstructed from PR text, extended with review
fields, or rewritten with later review-closeout evidence.

`SHIP-v1` remains immutable evidence for one publication epoch. For
`artifact-kernel-v1`, Ship returns the complete receipt to `$actuating`; the
current `publication_observed` Evidence Ledger event binds Ship's owner-issued
receipt reference to the deterministic closure receipt identity, Construction,
and subject after live readback. Ship does not append the event or interpret
the receipt as architecture, review, or closure authority.

For `legacy-actuating-v1`, preserve the existing implementation-checkpoint and
`review.ship_receipt` handback. A proved review edit produces a fresh `SHIP-v1`
for the retained PR. That replacement reports `updated` / `update-existing`,
retains `existing_pr.exists: true`, and uses the exact prior receipt's PR URL.
