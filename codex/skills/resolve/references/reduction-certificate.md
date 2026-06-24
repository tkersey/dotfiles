# RC-v1 — Reduction Certificate

```yaml
reduction_certificate:
  certificate_version: RC-v1
  campaign_id:
  contract_fingerprint:
  basis_ref:

  factorization:
    whole:
    factors: []
    recomposition_roles: []

  quotient:
    relation:
    classes: []
    congruence_witnesses: []
    unresolved: []

  retained_distinctions:
    - distinction:
      witness_cex_refs: []

  ablation:
    removed_factors:
      - factor:
        status:
          expired |
          moved |
          duplicated |
          invalid |
          unrequired
        evidence_refs: []
        replacement_owner:

  normal_form:
    canonical_owners: []
    retained_factors: []
    surfaces_to_retire: []

  preservation:
    relation:
      refinement-preserving |
      observationally-equivalent |
      isomorphic |
      intentional-contract-change
    observation_set: []
    proof_refs: []

  recomposition:
    live_obligations: []
    covered_obligations: []
    lost_obligations: []
    result:

  gate:
    quotient_congruent:
    every_retained_distinction_witnessed:
    every_removed_factor_discharged:
    recomposition_proved:
    no_orphan_surface:
    realization_allowed:
```

Default to `refinement-preserving`.

No deletion without discharge.

No normal form without recomposition.
