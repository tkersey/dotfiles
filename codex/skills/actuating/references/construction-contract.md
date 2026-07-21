# Construction Contract

The Construction Contract is Actuating's sole architecture-selection artifact
for one material construction. It answers:

> What structure makes the Goal laws true, excludes accepted Counterexamples,
> preserves valid behavior, and retires the construction it dominates?

It never grants mutation by itself.

Every accepted defect compiles through one law-level route:

~~~text
witnessed Counterexample -> intended law -> canonical owner -> selected Construction
-> strongest feasible proof -> executable obligation -> retirement -> independent review
~~~

Passing only the witnessed example is insufficient unless the Construction
proves that the class is genuinely instance-specific.

## Shape

~~~yaml
artifact:
  schema: construction-contract/v1
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
    falsified_predecessor_claims: []
    preserved_predecessor_claims: []
    invalid_states_eliminated: []
    counterexample_class_refs: []
    preserved_observations: []
    proof_obligations:
      - obligation_id:
        law_ref:
        statement:
        proof_mode: representation | total-transition | exhaustive-model | static-refinement | property-law | differential | example-regression
        adequacy_reason:
        verifier: {argv: []}
        falsifier: {argv: []}
        proof_kind: implementation | review | acceptance | ship
    retirements:
      - retirement_id:
        dominated_construct:
        disposition: collapse | delegate | retire | replace
        replacement_ref:
        verifier: {argv: []}
    execution:
      allowed_paths: []
      owner_boundary:
      operation_effects: [inspect, edit, verify]
      completion: complete | ready-to-ship
~~~

Use canonical JSON, content-address `artifact_id`, reject unknown fields, and
treat a materialized Construction as immutable. A changed decision creates an
explicit successor.

Before any projected operation, Actuating sets the selected draft's
`artifact_id` to JSON `null` and requests the current Ledger structural adapter
to append it. Only `actuating-append-result/v1` with a non-null top-level
`artifact_id` equal to the returned `artifact.artifact_id` and the associated
registration `event_digest` makes that exact canonical artifact current. Ledger
identifies and registers the Actuating-authored selection; it never selects or
revises the Construction.

## Selection law

Before consequential mutation, Actuating applies `$universalist` to the
affected boundary and records:

- the current context and accepted laws;
- the existing owner and host enforcement capabilities;
- the smallest repository-native candidate;
- materially distinct candidates and their falsifiers;
- the selected non-dominated construction;
- invalid states eliminated, residual obligations, and retirements.

For each accepted Counterexample class that can lead to mutation, Actuating
also records a compact Repair Disposition while selecting this Construction:

~~~text
Law:
Owner:
Route: delete | consolidate | edit | add
Why not smaller:
Falsifier:
~~~

This is a view over the existing Construction decision, not another authority
artifact. A finding authorizes the invariant, not its suggested implementation.
The selected route is the least additive route that satisfies the law; an
`add` route explains why `delete`, `consolidate`, and `edit` are insufficient.

One Construction selects the canonical owner, representation or machine,
interpreter or handler, proof strategy, scope, and retirements. Executors,
review coordinators, Ship, and Ledger project that selection; none may
reconsider it.

A Counterexample class's `owner_boundary` records where its predecessor was
falsified; it does not force the successor's `canonical_owner` to be identical.
One successor may compose classes from multiple witnessed owners when its laws
and obligations prove the join. Otherwise Actuating proves `separate-laws` and
splits the construction or blocks. Ledger validates references, not semantic
owner adequacy.

A candidate `A` dominates candidate `B` only when `A` is no worse in every
ACT-AK dimension:

- satisfies every required law satisfied by `B`;
- preserves every required observation preserved by `B`;
- excludes every Counterexample excluded by `B`;
- has no more independent law owners;
- has no more parallel semantic representations;
- has no more bypasses;
- introduces no more semantic mechanisms;
- leaves no more dominated residue; and
- requires no greater resource burden.

`A` must also be strictly better in at least one dimension. If two or more
non-dominated minima remain incomparable, prove `separate-laws` from distinct
accepted laws or block; preference, familiarity, and implementation momentum
cannot manufacture a winner.

## Review-repair reduction

Before fresh review, classify the repair's production delta. A new algorithm,
compatibility branch, semantic helper family, or more than 50 net production
lines triggers exactly one proof-preserving reduction pass. The pass may
collapse duplicate paths, return semantics to the canonical owner, or retire
dominated residue. When no reduction preserves the Goal laws and observations,
record the specific compatibility or representation obstruction instead.

The trigger is not a hard line budget, does not force deletion, and does not
repeat recursively for the same delta. Fresh review evaluates the reduced
result or the recorded obstruction.

## Correct-by-construction proof

For each law, select the strongest feasible proof mode:

~~~text
representation
> total transition
> exhaustive finite model
> static or refinement proof
> property or algebraic law
> differential proof
> example or regression proof
~~~

A weaker mode requires an adequacy reason. High or Critical authority,
state-machine, identity, persistence, or concurrency defects require more than
an example unless the accepted source explicitly owns the residual risk and a
compensating invariant proof exists.

Expected minimums by law family are:

| Law family | Expected minimum |
|---|---|
| State machine or lifecycle | representation and total-transition; bounded exhaustive model when feasible |
| Authority, capability, or replay | representation or static contract plus adversarial transitions |
| Identity or canonicalization | property law and corpus; differential proof when available |
| Parser, serializer, or codec | round-trip property and malformed-input corpus |
| Persistence or event fold | integrity replay and model or property proof |
| Idempotency, ordering, or quotienting | repeated-operation or permutation property law |
| Compatibility or migration | golden corpus and before/after differential proof |
| Concurrency | explicit state and ownership model plus stress or model check |
| Pure algorithm | property or differential proof |
| Public API or CLI affordance | contract fixtures and footgun review |

Every implementation or acceptance obligation names an exact verifier and an
independent falsifier. Review and Ship obligations remain projections of their
external owners; their argv is not executable repository authority. Every
`law_ref` names a current Goal law. Each `argv` is an ordered, nonempty string
sequence; repeated token values remain valid positional arguments.

## Successors

Every material implementation has one current Construction. A successor must
state:

- exactly one `predecessor_refs` entry naming the current Construction;
- which predecessor claims were falsified and preserved;
- which accepted Counterexample classes it excludes;
- whether the defect is realization, architecture, or ablation;
- what structure changes or remains;
- which valid observations remain;
- what proof becomes stronger;
- what dominated residue must disappear.

`realization-repair` preserves the architecture and corrects an implementation
or bypass. `architecture-repair` changes the architecture. `ablation-repair`
preserves the selected replacement while completing retirements.

Every `preserved_observations` entry names an `obligation_id` in the same
Construction. It is not free prose and cannot claim preservation without a
corresponding executable proof obligation.

## Operation projection

`execution.allowed_paths` is a duplicate-free canonical literal repository
path set. `.` is valid Goal scope but never executable Construction or
operation scope. The `.git` root and the Artifact Kernel control store,
including slash descendants and any ancestor that contains them, are reserved
under ASCII case-folding. A broader Goal scope does not authorize them.

Actuating, not Ledger, selects the next exact operation from the current Goal,
Construction, live subject, and evidence. The executor applies only that
operation and reports observations. An operation envelope or structural
validator pass supplies no mutation authority.

Every selected operation carries the exact current `expected_subject_digest`.
Immediately before the effect, the executor recomputes the live subject through
the exact repository-native procedure selected and supplied by Actuating for
that operation and must abort without effect on mismatch. The procedure is
transient execution policy, not a fifth authoritative artifact field. Ledger
stores and compares the opaque identity but never selects the procedure,
derives the digest, or invokes Git.

## Ablation

A replacement is incomplete while a dominated predecessor, duplicate owner,
bypass, representation, validator, adapter, flag, or proof path remains live.
Every retirement names an absence verifier and must be independently observed
before closure.
