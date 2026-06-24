# RB-v1 — Review Batch

Review is batched before mutation.

```yaml
review_batch:
  batch_version: RB-v1
  batch_id:
  campaign_id:
  review_mode:
    discovery |
    kernel_review |
    conformance |
    terminal_holdout

  artifact_state:
    base:
    head:
    dirty_fingerprint:

  contract:
    contract_id:
    contract_fingerprint:
    horizon_fingerprint:

  state:
    open |
    sealed |
    invalidated

  apertures: []
  reviewer_receipts: []
  counterexample_refs: []

  classification:
    claims_total:
    confirmed:
    refuted_or_stale:
    in_horizon:
    outside_horizon:
    contract_invalidating:
    unknown:
    new_classes:
    existing_class_witnesses:
    duplicates:

  mutation_events_while_open: []

  gate:
    apertures_complete:
    receipts_terminal:
    every_claim_classified:
    no_unknown_intent_relation:
    no_mutation_while_open:
    counterexamples_valid:
    batch_allowed_to_seal:
```

## Mode rules

### Discovery

One broad review is allowed before kernel synthesis.

### Kernel review

Apertures target AC/CEB/MBK/RC structure. No delivery code.

### Conformance

Every aperture names laws, owners, transitions, proof, and excluded scope.

Generic whole-diff review is invalid.

### Terminal holdout

One broad final review is allowed. Its findings still have no direct mutation authority.

## Mutation barrier

Any delivery mutation timestamp between `open` and `sealed` is a hard failure.

The realization worktree is also frozen while a conformance or holdout batch is open.
