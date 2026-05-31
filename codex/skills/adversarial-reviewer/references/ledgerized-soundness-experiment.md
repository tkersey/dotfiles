# Ledgerized Soundness Experiment

Turn type-theoretic language into concrete review rows.

## Required row kinds

- `unwitnessed-guarantee`: the code or review claims a guarantee without a concrete witness.
- `illegal-inhabitant`: a representation admits a state the domain says should be impossible.
- `partial-handler`: a consumer/eliminator does not handle the intended domain totality.
- `non-canonical-witness`: proof points at a shadow owner, stale artifact, or duplicate truth surface.
- `broken-preservation`: a transition can violate the invariant it should preserve.
- `stuck-progress`: a valid state can no longer make legal progress.

## Row schema

```text
id:
kind:
claim_or_guarantee:
constructor_or_producer:
eliminator_or_consumer:
missing_or_current_witness:
evidence_ref:
minimum_acceptable_fix_or_validation:
status: open | closed | downgraded | not-found
```
