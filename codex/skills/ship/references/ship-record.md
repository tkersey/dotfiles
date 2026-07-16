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
The exact two-field binding is copied from the current implementation or
review-repair `closure-decision/v1`: kernel run ID and state fingerprint are
preserved. It must not be reconstructed from PR text, extended with review
fields, or relabeled with later review-closeout evidence. SHIP-v1 is immutable
evidence for one publication epoch. The ordered actuation lifecycle binds that
receipt into the GoalContract digest of a new review generation under the same
goal ID. A proved review edit closes another `ready-to-ship` generation and
produces a fresh SHIP-v1 for the retained PR. That replacement reports
`updated` / `update-existing`, retains `existing_pr.exists: true`, and uses the
exact prior receipt's PR URL.
