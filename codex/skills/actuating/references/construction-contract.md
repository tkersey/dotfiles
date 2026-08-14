# Construction Contract v6

The Construction Contract is Actuating's sole architecture-selection artifact
for one material construction. It answers:

> Given the current Goal, complete applicable Counterexample Theory, and exact
> predecessor subject, what typed semantic model and proof-carrying realization
> relation should exist?

It never grants mutation by itself.

v6 deliberately has no `mode`, `change_kind`, `repair_class`,
`semantic_model_disposition`, or supersession disposition. A Construction
describes the predecessor and successor objects and their relation; admission
derives obligations from their actual differences.

## Shape

```yaml
artifact:
  schema: construction-contract/v6
  artifact_id:
  goal_id:
  semantic_author: actuating
  created_at:
  predecessor_refs: []        # zero or one Construction
  supporting_refs: []

  payload:
    goal_contract_ref:

    subject:
      repository:
      base_artifact_digest:   # exact predecessor Git subject

    boundary:
      boundary_key:
      source_worlds: []
      target_worlds: []
      admitted_domain:
      carrier_element_refs: []
      operation_element_refs: []
      observation_element_refs: []
      compatibility_constraints: []

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
      generator_class_refs: []
      instance_specific_class_refs: []

      instance_specific_classes:
        - class_ref:
          separated_from_generator_ref:
          separation_proof_ref:
          non_example_falsifier_ref:

      causal_generators:
        - generator_id:
          class_refs: []
          law_ref:
          required_element_ref:
          carrier_claim_ref:
          proof_family:
          falsifier:

    semantic_model:
      kind: algorithm | data-refinement | effect-system | protocol |
        structural | transition-system
      element_refs: []
      elements:
        - element_id:
          kind: owner | state-dimension | event | transition | effect |
            custody | observation | terminality | illegal-state |
            equivalence-or-normalization
          owner:
          statement:
          law_refs: []
          observation_refs: []
      equations: []

    carrier_claim_refs: []
    carrier_claims:
      - claim_id:
        element_ref:
        disposition: closed-existing | open-existing | absent | unresolved
        predecessor_construction_ref:
        predecessor_subject_digest:
        predecessor_factor_refs: []
        presence_obligation_ref:
        closure_obligation_ref:
        negative_obligation_ref:
        presence_receipt_ref:
        closure_receipt_ref:
        negative_receipt_ref:
        structural_resolution_refs: []

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
        verifier_argv_digest: sha256:...
        falsifier: {argv: []}
        proof_kind: implementation | review | acceptance | ship

    recompilation:
      counterexample_set_ref:
      evaluated_class_refs: []
      candidates:
        - candidate_id:
          derivation: incumbent-relative | incumbent-independent
          status: selected | dominated | incomparable | obstructed
          summary:
          boundary: {}
          architecture: {}
          semantic_model: {}
          factor_refs: []
          factors: []
          law_refs: []
          observation_refs: []
          residual_obligations: []
          falsifier:
      selected_candidate_id:
      adjudication:
        selected_reason:
        reduction_disposition: minimal | smaller-admissible |
          incomparable | obstructed
        reduction_reason:
        falsifier:

    normal_form:
      mandatory_obligation_refs: []
      causal_generator_refs: []
      arrival_order_invariance_falsifier:
      disposition: normal | incomparable | obstructed
      incomparable_candidate_refs: []

    semantic_surface:
      predecessor_factor_refs: []
      predecessor_factors: []
      successor_factor_refs: []
      successor_factors: []

    realization:
      element_bindings:
        - element_ref:
          factor_ref:
          owner_boundary:
          constructor_or_representation:
          realization_paths: []
          proof_refs: []
          closure_obligation_ref:
      proof_bindings:
        - obligation_ref:
          proof_paths: []
      unmapped_production_surface: []
      unmapped_proof_surface: []
      retirement_witness_refs: []

    supersession:
      preserved_factor_refs: []
      retired_factor_refs: []
      introduced_factor_refs: []
      replacement_relations: []
      essential_additions: []
      surface_completeness_proof_ref:

    retirements:
      - retirement_id:
        retired_factor_ref:
        disposition: collapse | delegate | replace | retire
        replacement_ref:
        verifier: {argv: []}

    execution:
      allowed_paths: []
      owner_boundary:
      operation_effects: [inspect, edit, verify]
      completion: complete | ready-to-ship
```

Use canonical JSON, content-address `artifact_id`, reject unknown fields, and
treat a materialized Construction as immutable. A changed decision creates a
successor.

## Typed semantic identity

The semantic model is no longer a collection of unconstrained prose arrays.
Every selected semantic constructor has one stable element identity and a type.
The model's `element_refs` exactly name its `elements`.

The element vocabulary is intentionally semantic rather than language-specific.
A repository-native type, field, state variant, transition function, schema
constraint, handler, or interpreter may realize an element; the element remains
stable while realization paths change.

Boundary carriers, operations, and observations reference typed element
identities. Candidate and factor observations reference observation elements.
A string description may explain an element, but it cannot serve as its
identity.

## Carrier claims

Every semantic element has exactly one predecessor carrier claim.
Claim identity does not weaken that function: two distinct claim IDs may not
name the same `element_ref`.

### `closed-existing`

The carrier exists in the exact predecessor and construction is controlled by
one owner without an unchecked bypass. Require:

- one or more exact predecessor factor refs;
- a presence obligation and successful predecessor-presence receipt;
- a closure obligation and successful predecessor-closure receipt.

A closed carrier may still be deliberately replaced. If so,
`structural_resolution_refs` names the concrete factor delta.

Every predecessor factor ref resolves in `semantic_surface.predecessor_factor_refs`.
Every structural resolution ref resolves to an introduced factor, retired
factor, or replacement-relation ID in the same Construction.

### `open-existing`

The carrier exists, but a bypass, parallel representation, direct write,
alternate constructor, or competing owner defeats closure. Require:

- exact predecessor factor refs;
- a presence receipt;
- an independent negative receipt witnessing openness;
- at least one introduced factor, retired factor, or replacement relation that
  resolves it.

### `absent`

A bounded nonexistence witness establishes that the predecessor lacks the required carrier.
Require:

- no predecessor factor ref;
- an negative or nonexistence obligation and successful predecessor-nonexistence receipt;
- at least one introduced factor or replacement relation that creates the
  carrier.

Failure to find a carrier is not proof of absence. The falsifier must state why
its inspected surface is complete.

### `unresolved`

Evidence establishes neither presence nor absence. The claim carries no receipt
or structural resolution. A Construction containing any unresolved claim may be
materialized as a remediation proposal but cannot authorize an edit.

## Total correspondence

The contract mechanically enforces two total functions:

```text
semantic element -> carrier claim
semantic element -> selected successor factor
```

The second function is carried by `realization.element_bindings`. Every binding
also names the owner-controlled constructor or representation, bounded paths,
implementation proofs, and current-subject closure obligation.

Every selected factor must be the target of at least one semantic element.
Consequently, factor granularity is not assessed through another prose gate. A
factor that cannot support one coherent owner and bounded construction surface
cannot receive a valid binding and must split.

## Counterexample Theory

`counterexample_class_refs` is the complete currently applicable accepted class
set. The contract totally partitions it into:

```text
generator_class_refs
instance_specific_class_refs
```

Every generator class occurs in one causal generator. Every instance-specific
class has a separation proof and independent non-example falsifier explaining
why it does not instantiate the named generator.

Each causal generator references:

- one required typed semantic element;
- the unique carrier claim for that element;
- the governing law, proof family, and falsifier.

Duplicate witnesses and finding order do not alter the theory.

## Recurrence law

A generator with at least two accepted classes cannot preserve a pointwise
correction. Its carrier claim must name at least one concrete structural
resolution:

```text
introduced factor
retired factor
replacement relation
```

The only alternative is a valid separation that removes the class from the
generator and moves it into the instance-specific partition. A stronger
regression test alone is not a structural resolution.

## Concrete candidates

Candidates no longer carry free transformation axes such as
`representation: replace` or `ownership: preserve`. Each candidate carries the
actual boundary, architecture, semantic model, and factor set being compared.

Exactly one candidate is selected and at least one is incumbent-independent.
The selected candidate's complete objects exact-match the top-level boundary,
architecture, semantic model, and successor factors.

`normal_form` is a projection of the candidate adjudication, not an independent
claim. `minimal` and `smaller-admissible` yield `normal`; `obstructed` yields
`obstructed`; and `incomparable` yields `incomparable` with the exact
incomparable candidate refs. Only the first two dispositions can authorize an
edit.

A candidate dominates another only when it preserves the complete mandatory
obligation core and is no worse in every required law, observation,
Counterexample exclusion, authority, representation, semantic mechanism,
residue, proof, compatibility, and resource dimension, while strictly improving
at least one. Incomparable minima remain explicit.

## Difference-triggered admission

No classifier grants permission. Differences imply obligations directly:

```text
new element or absent carrier
  -> introduced/replacement factor and implementation proof

open carrier
  -> concrete structural resolution and closure proof

changed factor
  -> retirement, introduction, or replacement relation

introduced factor
  -> essential-addition law and proof coverage

retired factor
  -> retirement record and absence verifier

preserved factor
  -> exact value equality

changed boundary, owner, representation, or admitted domain
  -> corresponding factor delta and observation-preservation proof
```

A full implementation rewrite may preserve the complete relation. Conversely,
an unchanged abstract semantic model does not authorize a representation or
ownership replacement without a factor delta.

## Supersession and retirement

`predecessor-successor` partitions every predecessor and successor factor through
the explicit preserved, retired, introduced, and replacement sets. There is no
supersession disposition summarizing those sets.

Every introduced factor has an essential-addition record binding current laws
and proof. Every retired factor has a retirement record and absence verifier.
Replacement relations map exact predecessor and successor factors but do not
substitute for deletion proof.

## Two-sided evidence

Predecessor receipts are part of the Construction registration packet and bind:

```text
Goal
predecessor Construction; initial registration has no predecessor receipt packet
exact predecessor subject
claim
obligation
purpose
exact verifier argv
canonical verifier argv digest
exit status
output digests
```

They prove the selected relation was admissible before mutation.

Successor receipts are produced after realization and bind the v5 Construction
and exact current subject. They prove every element binding, closed owner, proof,
and retirement actually holds. They are cited by operation evidence and the
closure receipt, not embedded in the immutable Construction.

## Version law

v5 supersedes v4 for new selection and mutation. Do not reinterpret v1-v4
bytes. The v5 Evidence definition uses a separate goal-local store path so
historical logs remain inspectable without weakening replay.
