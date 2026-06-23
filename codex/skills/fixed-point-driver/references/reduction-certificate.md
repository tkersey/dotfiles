# Reduction Certificate (RC-v1)

The Reduction Certificate separates structural operators from the preservation relation.

```text
FACTORING -> QUOTIENTING -> ABLATIVE -> NORMALIZING
```

Preservation relations:

```text
isomorphic
observationally-equivalent
refinement-preserving
intentional-contract-change
```

Use `refinement-preserving` as the default technical-debt relation.

Never claim isomorphism merely because tests remain green.

Required areas:

```yaml
reduction_certificate:
  certificate_version: RC-v1
  artifact_state_id:
  live_contract:
  factorization:
  quotient:
    equivalence_relation:
    equivalence_classes: []
    congruence_checks: []
    retained_distinctions: []
  ablation:
    removed_factors: []
    retained_with_warrant: []
  normal_form:
    retained_factors: []
    canonical_owners: []
    orphan_surfaces: []
  preservation:
    relation:
    observation_set: []
    proof_refs: []
  recomposition:
    live_obligations: []
    covered_obligations: []
    lost_obligations: []
    orphan_retained_surfaces: []
    result:
  gate:
    every_live_obligation_covered:
    every_removed_factor_accounted:
    every_retained_distinction_witnessed:
    quotient_is_congruent:
    recomposition_proved:
    no_orphan_surface:
    reduction_allowed:
```

Laws:

1. No quotient without congruence.
2. No retained distinction without a witness.
3. No ablation without obligation discharge.
4. No normal form without recomposition.
5. No preservation overclaim.
