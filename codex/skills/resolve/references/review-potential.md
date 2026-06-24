# PHI-v1 — Monotone Review Potential

PHI makes convergence a controller invariant.

```yaml
review_potential:
  potential_version: PHI-v1
  potential_id:
  campaign_id:
  cycle_id:
  contract_fingerprint:
  kernel_fingerprint:
  artifact_state_before:
  artifact_state_after:

  before:
    unclassified_in_horizon_counterexamples:
    unsatisfied_laws:
    open_counterexample_classes:
    orphan_realization_constructs:
    hard_semantic_surface:
      truth_owners:
      public_symbols:
      state_variants:
      protocol_cases:
      fallback_or_compatibility_paths:
      control_flow_branches:
      helpers_or_wrappers:
      test_families:
    proof_debt:
      missing_law_proofs:
      unmapped_proof_actions:
      wound_specific_tests:

  after: {}

  comparison:
    primary_before: []
    primary_after: []
    primary_lexicographic_decrease:
    hard_surface_componentwise_nonincreasing:
    proof_debt_nonincreasing:
    contract_rebase_ref:
    strict_progress:

  evidence_refs: []
```

## Gate

Without an AC rebase:

```text
(U,L,C,O)_after <lex (U,L,C,O)_before
S_after <=componentwise S_before
P_after <= P_before
```

An AC rebase may change the horizon, but invalidates the old cycle and requires a new baseline.

## Interpretation

```text
comment no longer appears
  not sufficient

accepted class closed with no earlier debt increase
  progress

same class recurs after patch
  realization invalid

new helper/test but no new accepted class
  surface regression
```
