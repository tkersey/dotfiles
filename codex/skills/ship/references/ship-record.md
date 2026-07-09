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
  actuation_review:
    actuation_run_id:
    state_fingerprint:
    review_contract_fingerprint:
    selected_lenses: []
    resolution_ref:
    resolution_digest: # null when actuation review was not required
    cas_rer_record_ids: []
```

`actuation_review` is required when `source=actuation` and the readiness mode
is ready, update-existing, or promote-draft. It is omitted for direct shipping.
The binding is copied from a current `closure-decision/v1` and its inputs; it
must not be reconstructed from PR text.
