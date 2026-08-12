# Construction Contract v4

The Construction Contract is Actuating's sole architecture-selection artifact
for one material construction. It answers:

> Given the current Goal and the complete applicable Counterexample Theory,
> what semantic model and normalized realization should exist?

It never grants mutation by itself.

## Shape

```yaml
artifact:
  schema: construction-contract/v4
  artifact_id:
  goal_id:
  semantic_author: actuating
  created_at:
  predecessor_refs: []
  supporting_refs: []

  payload:
    goal_contract_ref:
    mode: initial | realization-repair | architecture-repair | ablation-repair

    subject:
      repository:
      base_artifact_digest:

    boundary:
      boundary_key:
      source_worlds: []
      target_worlds: []
      carriers: []
      operations: []
      observations: []

    architecture:
      governing_law_refs: []
      canonical_owner:
      selected_construction:
      representation_or_machine:
      interpreter_or_handler:
      residual_assumptions: []

    counterexample_class_refs: []

    counterexample_theory:
      set_refs: []
      instance_specific_class_refs: []
      causal_generators:
        - generator_id:
          class_refs: []
          law_ref:
          missing_semantic_element:
          proof_family: representation | total-transition | exhaustive-model |
            static-refinement | property-law | differential | example-regression
          falsifier:

    semantic_model:
      kind: structural | transition-system | protocol | effect-system |
        data-refinement | algorithm
      owners: []
      state_dimensions: []
      events: []
      transitions: []
      effects: []
      custody: []
      observations: []
      terminality: []
      illegal_states: []
      equivalence_and_normalization: []

    falsified_predecessor_claims: []
    preserved_predecessor_claims: []
    invalid_states_eliminated: []
    preserved_observations: []

    proof_obligations:
      - obligation_id:
        law_ref:
        owner_boundary:
        statement:
        proof_mode: representation | total-transition | exhaustive-model |
          static-refinement | property-law | differential | example-regression
        adequacy_reason:
        verifier: {argv: []}
        falsifier: {argv: []}
        proof_kind: implementation | review | acceptance | ship

    recompilation:
      trigger: initial | accepted-review-fold
      counterexample_set_ref:
      evaluated_class_refs: []

      candidates:
        - candidate_id:
          derivation: incumbent-relative | incumbent-independent
          status: selected | dominated | incomparable | obstructed
          summary:

          semantic_model: {}

          transformation:
            admitted_domain: preserve | restrict | expand-authorized
            representation: preserve | replace | introduce
            ownership: preserve | centralize | split
            realization: preserve | edit | rewrite
            residue: preserve | ablate
            proof: preserve | recompose | strengthen

          law_refs: []
          observation_refs: []
          factors: []
          residual_obligations: []
          falsifier:

      selected_candidate_id:

      adjudication:
        selected_reason:
        reduction_disposition: minimal | smaller-admissible | incomparable | obstructed
        reduction_reason:
        falsifier:

    normal_form:
      semantic_model_disposition: initial | unchanged | changed
      mandatory_obligation_refs: []
      causal_generator_refs: []
      arrival_order_invariance_falsifier:
      disposition: normal | incomparable | obstructed
      incomparable_candidate_refs: []

    semantic_surface:
      predecessor_factors: []
      successor_factors: []

    realization:
      factor_bindings:
        - factor_ref:
          realization_paths: []
          proof_refs: []
      proof_bindings:
        - obligation_ref:
          proof_paths: []
      unmapped_production_surface: []
      unmapped_proof_surface: []
      retirement_witness_refs: []

    supersession:
      disposition: initial | unchanged-realization | normalized | essential-expansion
      preserved_factor_refs: []
      retired_factor_refs: []
      introduced_factor_refs: []
      replacement_relations: []
      essential_additions: []
      surface_completeness_proof_ref:

    retirements: []

    execution:
      allowed_paths: []
      owner_boundary:
      operation_effects: [inspect, edit, verify]
      completion: complete | ready-to-ship
```

Use canonical JSON, content-address `artifact_id`, reject unknown fields, and
treat a materialized Construction as immutable. A changed semantic decision
creates a successor.

## Counterexample Theory

`counterexample_class_refs` is the complete set of currently applicable accepted
stable classes across the Goal lineage, not merely the latest review wave.
`recompilation.evaluated_class_refs` equals it.

Ordinary Counterexample Sets are source-local deltas. Actuating obtains the
complete class domain from the retained Evidence register rather than requiring
each Set to restate untouched classes. `counterexample_theory.set_refs` names
the Sets needed to prove the cumulative accepted class set.

Each accepted class appears in exactly one current causal generator or in
`instance_specific_class_refs`.

A causal generator is an Actuating-authored quotient over classified classes. It
does not revise finding truth. It states the common semantic element whose
absence or falsity explains the classes and selects a law-level proof family.

Duplicate witnesses and finding order do not alter the Theory.

## Closed-world semantic model

The selected `semantic_model` is a closed-world claim. It explicitly names the
semantic alphabet and equations that the realization may use.

A `realization-repair` is legal only when the required behavior is already
represented and no new semantic constructor is introduced. Constructors include
state dimensions, events, transitions, authority/custody transfers, freshness
or correlation rules, failure modes, effect/observation paths, compatibility
modes, independent validators, and proof families.

If implementation needs an absent constructor, the current Construction is
falsified and a successor is required before mutation. `realization-repair` and
`ablation-repair` require `semantic_model_disposition: unchanged`; only
`architecture-repair` may declare `changed`. Evidence registration exact-compares
the complete predecessor and successor semantic models for realization and
ablation routes. A differing model cannot be admitted under either local route.

For lifecycle, concurrency, persistence, asynchronous effects, custody, or
authority-sensitive work, `semantic_model.kind` cannot be merely descriptive.
The model must enumerate the relevant states/events/transitions/ownership and
receive representation plus total-transition proof, with a bounded exhaustive
model when feasible.

## Candidate law

Candidates are concrete semantic models. Transformation fields are orthogonal
axes, not mutually exclusive candidate families.

Every candidate carries the same mandatory obligation core:

```text
Goal laws
+ complete applicable Counterexample Theory
+ required observations
+ compatibility
+ resources
+ host constraints
+ proof obligations
```

A candidate omitting an independent obligation is inadmissible and cannot
establish dominance.

At least one candidate is genuinely incumbent-independent. Exactly one is
selected. The selected candidate's factors equal `successor_factors`, and its
semantic model equals the top-level selected semantic model.

A candidate dominates another only when it is no worse in every required law,
observation, Counterexample exclusion, authority, representation, semantic
mechanism, residue, proof, compatibility, and resource dimension, and strictly
better in at least one. Incomparable minima remain explicit.

Reordering the same complete Counterexample Theory must produce an equivalent
selected normal form or the same incomparable set. The falsifier in
`normal_form.arrival_order_invariance_falsifier` must be executable or
decisively inspectable.

## Architectonic composition

Before candidate selection, perform the comparison:

```text
First Principles incumbent-independent basis
-> Universalist concrete model nomination
-> one bounded Metanoetic pass when triggered
-> Universalist lowering
-> Reduce challenge for disputable factors
-> Actuating adjudication
```

`OPERATE ARCHITECTONICALLY` may be used as a mnemonic, but uttering or recording
the phrase is not compliance evidence and cannot substitute for the comparison
encoded in the Construction.

Metanoetic may change the hypothesis space but cannot manufacture authority.
Universalist nominates but does not select. Reduce challenges but does not grant
mutation. Actuating alone materializes the Construction.

## Realization exactness

`realization.factor_bindings` maps every selected factor to its intended
production paths and proof obligations. `proof_bindings` maps every obligation
to its proof paths.

`unmapped_production_surface` and `unmapped_proof_surface` are always empty in a
valid v4 Construction. Existing residue belongs in explicit retirements, not in
an unowned exception list.

Before Ship or fresh review, Actuating verifies:

```text
every live production mechanism -> one selected factor
every live proof mechanism -> one current proof obligation
every superseded mechanism -> deletion, successor mapping, or distinct obligation
```

The `surface_completeness_proof_ref` proves the mark-and-sweep result over the
complete selected scope.

A bounded operation is an effect boundary only. Actuating may execute it
directly or delegate it; executor identity is not part of the theorem. Multiple
operations may realize one Construction. Closure-grade review begins only after
the complete Construction, proof, and retirements are realized on one exact
clean commit.

## Proof normalization

Each accepted class receives a law-matched implementation obligation. Passing
only the witnessed example is insufficient unless the class is proved
instance-specific.

When multiple classes share a causal generator, `example-regression` cannot be
the governing proof mode. Recompose proof around the generator and retain only
genuinely distinct minimal witnesses.

Expected minimums:

| Law family | Expected minimum |
|---|---|
| State machine or lifecycle | representation and total-transition; bounded exhaustive model when feasible |
| Concurrency | explicit state/ownership model plus stress or model check |
| Authority, capability, or replay | representation/static contract plus adversarial transitions |
| Identity or canonicalization | property law and corpus; differential proof when available |
| Parser, serializer, or codec | round-trip property and malformed-input corpus |
| Persistence or event fold | integrity replay plus model/property proof |
| Idempotency, ordering, or quotienting | repeated-operation or permutation property |
| Compatibility or migration | golden corpus and before/after differential proof |
| Pure algorithm | property or differential proof |
| Public API or CLI | contract fixtures and footgun review |

Every obligation names an exact verifier and independent falsifier.

## Supersession and retirement

Every predecessor and successor factor is partitioned exactly once.
`unchanged-realization` admits identical factor inventories.
`normalized` changes the factor inventory without essential addition.
`essential-expansion` binds every introduced factor to current laws and proof.

A label such as `collapse`, `replace`, or `retire` is not evidence. Each displaced
production and proof surface maps to deletion with an absence verifier, a
successor owner and proof, or a distinct current obligation.

## Review law

Review evidence never maps directly to edits. A canonical review wave produces a
Counterexample Set. Actuating recomputes the complete Theory from the retained
class register and selects one Construction for the whole theory before
mutation.

The static 1+4 topology and five consecutive standard-clean theorem remain
unchanged. Any material successor or normalization resets all credit. Repeated
stochastic review is a required falsification capability.

## Version law

v4 supersedes v3 for new selection and mutation. Do not reinterpret v3 bytes.
A v3 artifact may be historical evidence; the first affected mutation requires a
v4 Construction and a structurally lawful v4 Evidence store.
