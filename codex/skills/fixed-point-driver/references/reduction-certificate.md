# Reduction Certificate (RC-v1)

The Reduction Certificate separates **reduction operators** from the **preservation relation**.

Reduction operators answer what changes structurally:

```text
FACTORING -> QUOTIENTING -> ABLATIVE -> NORMALIZING
```

The preservation relation answers what must remain true:

- `isomorphic`: a reversible structure-preserving correspondence is required.
- `observationally-equivalent`: selected external observations remain equal.
- `refinement-preserving`: all required behavior remains, while invalid, obsolete, duplicated, or unrequired behavior may disappear.
- `intentional-contract-change`: behavior changes under explicit authority.

Use `refinement-preserving` as the default for technical-debt reduction. Do not claim `isomorphic` merely because tests stay green.

```yaml
reduction_certificate:
  certificate_version: RC-v1
  artifact_state_id: "branch=<name> head=<sha-or-id> diff=<digest-or-path-set>"

  live_contract:
    required_observations: []
    permitted_contractions: []
    forbidden_changes: []
    external_obligations: []

  factorization:
    whole: "..."
    factors:
      - id: "F1"
        obligation: "..."
        owner: "..."
        inputs: []
        outputs: []
        dependencies: []
        observations: []
        recomposition_role: "..."
    irreducible_core: []
    recomposition_rule: "..."

  quotient:
    equivalence_relation: "..."
    equivalence_classes: []
    congruence_checks:
      - operation_or_transition: "..."
        result: pass | fail | unknown
        proof_ref: "..."
    merged_factors: []
    retained_distinctions:
      - distinction: "..."
        witness: "..."
    unresolved_distinctions: []

  ablation:
    removed_factors:
      - factor_id: "F..."
        obligation_status: expired | moved | duplicated | invalid | unrequired
        replacement_owner: "..."
        evidence_ref: "..."
    retained_with_warrant:
      - factor_id: "F..."
        warrant: "..."
        expiry_or_recheck: "..."

  normal_form:
    retained_factors: []
    canonical_owners: []
    orphan_surfaces: []
    target_shape: "..."

  preservation:
    relation: isomorphic | observationally-equivalent | refinement-preserving | intentional-contract-change
    observation_set: []
    proof_refs: []
    known_contractions: []
    approved_semantic_changes: []

  recomposition:
    live_obligations: []
    covered_obligations: []
    lost_obligations: []
    preserved_observations: []
    orphan_retained_surfaces: []
    result: pass | validate-first | fail | blocked

  gate:
    every_live_obligation_covered: pass | fail
    every_removed_factor_accounted: pass | fail
    every_retained_distinction_witnessed: pass | fail
    quotient_is_congruent: pass | fail | not-applicable
    recomposition_proved: pass | fail
    no_orphan_surface: pass | fail
    reduction_allowed: yes | no
```

## Laws

1. **No quotient without congruence.** Every accepted operation, transition, and observation must respect the proposed equivalence classes.
2. **No retained distinction without a witness.** A distinction survives only when an accepted observation can detect it.
3. **No ablation without discharge.** Every removed factor must have an expired, moved, duplicated, invalid, or explicitly unrequired obligation.
4. **No normal form without recomposition.** The retained factors must still cover the live contract.
5. **No preservation overclaim.** Use the weakest accurate relation; never label a refinement-preserving contraction as isomorphic.
