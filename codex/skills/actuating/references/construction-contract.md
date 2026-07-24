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
  schema: construction-contract/v3
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
        owner_boundary:
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
    recompilation:
      trigger: initial | accepted-review-fold
      counterexample_set_ref:
      evaluated_class_refs: []
      candidates:
        - candidate_id:
          family: realization-preserve | admitted-domain-restriction | representation-or-owner-strengthening | ablation-normalization
          derivation: incumbent-relative | incumbent-independent
          status: selected | dominated | incomparable | obstructed
          summary:
          law_refs: []
          observation_refs: []
          factors:
            - factor_id:
              kind: law-owner | authoritative-representation | semantic-mechanism | recovery-correlation | residual-validator | bypass | compatibility-branch | illegal-state-family | resource-obligation | proof-path
              owner:
              law_refs: []
              observation_refs: []
              description:
          residual_obligations: []
          falsifier:
      selected_candidate_id:
      adjudication:
        selected_reason:
        reduction_disposition: minimal | smaller-admissible | incomparable | obstructed
        reduction_reason:
        falsifier:
    semantic_surface:
      predecessor_factors: []
      successor_factors: []
    supersession:
      disposition: initial | unchanged-realization | normalized | essential-expansion
      preserved_factor_refs: []
      retired_factor_refs: []
      introduced_factor_refs: []
      replacement_relations:
        - relation_id:
          predecessor_factor_refs: []
          successor_factor_refs: []
          rationale:
      essential_additions:
        - factor_ref:
          law_refs: []
          proof_refs: []
          rationale:
      surface_completeness_proof_ref:
    execution:
      allowed_paths: []
      owner_boundary:
      operation_effects: [inspect, edit, verify]
      completion: complete | ready-to-ship
~~~

Use canonical JSON, content-address `artifact_id`, reject unknown fields, and
treat a materialized Construction as immutable. A changed decision creates an
explicit successor. Arrays that represent sets are sorted and duplicate-free.
The four candidate families above are a v3 schema constant in that exact order,
not the incidental order of an implementation enum. Exactly one candidate is
selected, its factor inventory exactly equals `successor_factors`, and at least
one candidate is incumbent-independent.

Supersession partitions every predecessor and successor factor exactly once.
Preserved factors remain byte-semantically equal. `unchanged-realization`
admits only identical factor inventories; `normalized` requires an actual
factor delta and cannot encode an identity replacement; `essential-expansion`
binds every introduced factor to an essential addition and proof.

Before any projected operation, Actuating sets the selected draft's
`artifact_id` to JSON `null` and requests the current Ledger structural adapter
to append it. Only `actuating-append-result/v1` with a non-null top-level
`artifact_id` equal to the returned `artifact.artifact_id` and the associated
registration `event_digest` makes that exact canonical artifact current. Ledger
identifies and registers the Actuating-authored selection; it never selects or
revises the Construction.

## Selection law

Before consequential mutation, Actuating applies `$universalist` to the
affected boundary and records its nomination:

- the current context and accepted laws;
- the existing owner and host enforcement capabilities;
- the smallest repository-native candidate;
- materially distinct candidates and their falsifiers;
- the nominated construction and materially distinct alternatives;
- invalid states eliminated, residual obligations, and retirements.

Actuating then compiles exactly four comparable candidate families in canonical
order:

1. `realization-preserve`;
2. `admitted-domain-restriction`;
3. `representation-or-owner-strengthening`;
4. `ablation-normalization`.

Each candidate names its laws, observations, factors, residual obligations,
and falsifier. Repository-native specializations live within these families;
they do not replace or add a fifth family.

For each accepted Counterexample class that can lead to mutation, Actuating
also records a compact Repair Disposition while selecting this Construction:

~~~text
Law:
Owner:
Reduction: not-required | minimal | dominated | incomparable | essential-shape-gap | blocked
Route: delete | consolidate | edit | add
Why not smaller:
Falsifier:
~~~

This is a view over the existing Construction decision, not another authority
artifact. A finding authorizes the invariant, not its suggested implementation.
The selected route is the least additive route that satisfies the law; an
`add` route explains why `delete`, `consolidate`, and `edit` are insufficient.
Before selection, `$reduce` challenges any materially disputable factor by
factoring live obligations, testing congruent quotients or ablations, and
checking recomposition. The order is `nominate -> challenge once -> adjudicate
-> one Construction`: Universalist, Reduce, then Actuating. The compact challenge
is sufficient in Actuating composition; an independently useful Reduction
Certificate may appear only in `supporting_refs`. Neither supporting surface
selects the Construction or Repair Disposition.

A challenge is required when the nominee adds or preserves an independent
semantic owner, parallel representation, bypass, compatibility branch,
semantic mechanism, or apparently dominated residue. `dominated` requires the
smaller admissible candidate. `minimal` permits the nominee. `incomparable`,
`essential-shape-gap`, or `blocked` returns to Actuating for adjudication or
obstruction; it never starts recursive Universalist/Reduce competition.

One Construction selects the canonical owner, representation or machine,
interpreter or handler, proof strategy, scope, and retirements. Executors,
review coordinators, Ship, and Ledger project that selection; none may
reconsider it.

A Counterexample class's `owner_boundary` records where its predecessor was
falsified; it does not force the successor's `canonical_owner` to be identical.
Each v3 proof obligation carries `owner_boundary` and covers an accepted class
only when both `law_ref` and `owner_boundary` match. One successor may compose
multiple witnessed owners when matching obligations prove the join; otherwise
Actuating proves `separate-laws` and splits or blocks. Ledger validates exact
declared owner binding, not semantic owner adequacy.

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

## Implementation reclassification

Before fresh review, compare the realized production delta with the challenged
candidate. Diff size is evidence to inspect, not a reduction trigger. Run one
new challenge only when implementation introduces or materially changes a
disputable semantic factor. That challenge belongs to the successor candidate;
the same candidate and evidence never repeat recursively. Otherwise retain the
pre-mutation challenge. Fresh review evaluates the adjudicated result or the
recorded obstruction.

## Causal recurrence gate

Before another affected mutation, Actuating folds current and predecessor
Counterexample Sets against current and predecessor Constructions for the same
Goal. The gate triggers when one accepted class recurs after repair or when two
accepted classes across subject revisions share an evidenced missing
observation, authority, correlation, or Construction factor. Similar prose,
files, or line counts are not sufficient evidence of shared cause.

Actuating compares the four ordinary v3 candidate families before
adjudication: realization preservation, admitted-domain restriction,
representation or owner strengthening, and ablation or normalization.

The candidate universe may contain a more specific repository-native
equivalent, but it may not omit one of these semantic alternatives. The Reduce
challenge tests the continued existence of the repair or validation mechanism,
not only whether its latest implementation is locally minimal.

Record one composed, non-authoritative view:

~~~text
Causal Recurrence Disposition
Evidence and class refs:
Shared cause:
Current Construction factor:
Candidate comparison:
Disposition: instance-specific | architecture-repair | ablation-repair | blocked
Why another local repair is sufficient or forbidden:
Proof:
Falsifier:
~~~

The current `construction-contract/v3` remains sufficient:

- `counterexample_class_refs` contains the complete causal cluster;
- `falsified_predecessor_claims` names the shared cause and the predecessor
  belief it invalidates;
- `mode` records `architecture-repair` or `ablation-repair`, unless an
  instance-specific `realization-repair` is proved;
- `proof_obligations` carries the separating or structural proof; and
- `retirements` removes dominated validators, correlations, caches, bypasses,
  compatibility branches, or path-dependent recovery.

Instance-specific proof must be non-example evidence that separates the
cluster and establishes the current representation as sufficient. Without that
proof, Actuating must select an architecture or ablation successor or block.
It must not select another local validator that reconstructs information the
representation repeatedly forgets. This rule adds no artifact family and gives
Ledger no causal-classification or Construction-selection authority.

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

A weaker mode requires an adequacy reason. High or Critical authority, state-machine, identity, persistence,
or concurrency defects require more than an example unless the accepted source explicitly owns the residual risk and a compensating invariant proof exists.

For every accepted Counterexample class, v3 requires a law-matched
`implementation` obligation; aggregate `acceptance` is not a substitute.
Recurrent, High, and Critical classes require non-`example-regression`
implementation proof. Ledger 0.13.0 and later reject Construction v1, v2, and
mixed stores with `LegacyConstructionUnsupported`. There is no migration:
start a fresh goal-local Evidence store and ignore the legacy data.

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

Every implementation or acceptance obligation names an exact verifier and an independent falsifier. Review and Ship
obligations remain projections of their external owners; their argv is not executable repository authority. Every `law_ref`
names a current Goal law. Each `argv` is an ordered, nonempty string sequence; repeated token values remain valid positional arguments.

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

An accepted Review Fold uses `accepted-review-fold`, names the latest
Counterexample Set, and records the exact current accepted-class set in both
`counterexample_class_refs` and `evaluated_class_refs`. The Set must evaluate
the predecessor Construction on the exact current subject. An empty
review-driven successor is legal only when it clears a nonempty predecessor
debt set without an intervening subject change.

Proof references are artifact-relative. Predecessor-factor observation refs
resolve only through the predecessor Construction's proof obligations.
Candidate, successor-factor, essential-addition, and surface-completeness refs
resolve only through the successor. Reusing a local proof id cannot silently
change the predecessor witness.

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

For Git, invoke `scripts/subject_observation.py` with the accepted repository,
`--allow`, and `--prohibit` scope; never substitute HEAD-only or diff-only identity.

## Ablation

A replacement is incomplete while a dominated predecessor, duplicate owner,
bypass, representation, validator, adapter, flag, or proof path remains live.
Every retirement names an absence verifier and must be independently observed
before closure.
