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

`actuation_binding` is required when `source=actuation` and the readiness mode
is ready, update-existing, or promote-draft. It is omitted for direct shipping.
The exact two-field binding is copied from the current implementation or
review-repair `closure-decision/v1`: run ID and state fingerprint are preserved.
It must not be reconstructed from PR text, extended with review fields, or
relabeled with later review-closeout evidence. SHIP-v1 is immutable evidence for
one publication epoch. The ordered actuation lifecycle embeds the complete
receipt unchanged as `review.ship_receipt` before publication-bearing
review-closeout admission, then replaces that field with a fresh SHIP-v1 after
any proved review edit returns `ready-to-ship`.
That replacement reports `updated` / `update-existing`, retains
`existing_pr.exists: true`, and uses the exact prior receipt's PR URL.
