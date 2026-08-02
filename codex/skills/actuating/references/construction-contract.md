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
one candidate is incumbent-independent. That marker is semantic, not
descriptive: it is legal only when the current Actuating-bound Axiomatic
Construction Basis froze the derivation before incumbent comparison and
`$universalist` lowered it into the candidate family. Repository facts,
external obligations, and host capabilities may inform that derivation;
incumbent abstractions, owner boundaries, factorization, names, and rationale
may not serve as its premises.

Supersession partitions every predecessor and successor factor exactly once.
Preserved factors remain byte-semantically equal. `unchanged-realization`
admits only identical factor inventories; `normalized` requires an actual
factor delta and cannot encode an identity replacement; `essential-expansion`
binds every introduced factor to an essential addition and proof.

Before any projected operation, Actuating sets the selected draft's
`artifact_id` to JSON `null`, materializes it through
`definitions/ledger/construction-contract.json`, and registers the returned
canonical artifact through the Evidence protocol's `register-construction`
operation. Only a valid `ledger-materialization-result/v1` with a non-null
`artifact_id` equal to `artifact.artifact_id` and the corresponding appended
transaction event make that exact artifact current. Ledger identifies and
registers the Actuating-authored selection; it never selects or revises the
Construction.

## Selection law

At the beginning of architecture or abstraction selection, Actuating states
exactly:

~~~text
OPERATE ARCHITECTONICALLY
~~~

This is an activation instruction, not an authority artifact or proof.

Before the first Universalist nomination for a materially new candidate
universe, Actuating invokes `$first-principles` with the current Goal Contract
fixed as the irreducible outcome and sole semantic authority. The pass may
bracket inherited architecture, conventions, analogies, incumbent rationale,
and alleged constraints; it may not reopen source-bound outcomes, laws, scope,
compatibility, authority, acceptance, or proof posture.

Inspect the incumbent only for observed facts, external obligations, and host
enforcement capabilities. Freeze the incumbent-independent derivation before
using the incumbent as a comparator, then record:

~~~text
Axiomatic Construction Basis
Goal axioms:
Observed facts:
Necessary constraints:
Chosen objectives:
Irreducible postulates:
Definitions:
Derived claims:
Rejected inherited premises:
Governing invariants and causal mechanisms:
Incumbent-independent derivation:
Incumbent comparison:
Basis status: sufficient | underdetermined | inconsistent | blocked
Invalidators:
Falsifier:
~~~

This is a compact non-authoritative view and an ephemeral proof lease over its
exact Goal, fact, constraint, and host-capability inputs. It creates no artifact
family and adds no field to `construction-contract/v3`. It expires at session
end, compaction, or execution-context handoff and is never reconstructed from a
materialized Construction. A subject digest change alone does not expire it:
within one uninterrupted run, a premise-neutral realization repair may retain
the lease while every bound input and invalidator remains current. Any later
run, or any subject change that alters a bound input or invalidator,
re-axiomatizes before nomination or affected mutation. Compile its material
conclusions into the existing `goal_contract_ref`, `governing_law_refs`,
observation refs, `architecture.residual_assumptions`, candidate factors,
residual obligations, predecessor claims, retirements, and falsifiers.

A `sufficient` basis admits nomination. An `underdetermined` basis carries every
materially incomparable derivation into candidate comparison and blocks if
current Goal law, observation, or dominance cannot distinguish them. A new
explicit source preference must first become a successor Goal Contract; only
then may Actuating compare the successor candidate universe. When accepted or
blocked Counterexamples remain unresolved, or when the revision brings a
`follow-up` class within the successor Goal's scope, the successor Goal cites
every Set carrying those classes and `$review-fold` authors a successor Set
that cites the successor Goal, preserves predecessor lineage, evaluates the
predecessor Construction, and assigns every carried class a disposition. No
affected mutation or successor Construction selection is legal until that
carry-forward is complete.
`inconsistent` or `blocked` stops selection. `$first-principles` may expose a
Goal conflict or missing authority, but it cannot revise the Goal, classify a
Counterexample, nominate or select a Construction, grant mutation, or author a
durable decision.

Retain the basis across premise-neutral subject changes only within the same
uninterrupted run and while its inputs and invalidators remain current.
Re-axiomatize before nomination after any execution-context handoff; when a
successor Goal changes semantics, compatibility, authority, or proof posture;
when evidence changes an observed fact, necessary constraint, or host
capability; when an accepted finding falsifies a premise; when architecture or
ablation repair becomes live; or when causal recurrence triggers.

With a current basis, Actuating applies `$universalist` to the affected boundary
and records its nomination:

- the current context and accepted laws;
- the existing owner and host enforcement capabilities;
- the smallest repository-native candidate;
- materially distinct candidates and their falsifiers;
- the nominated construction and materially distinct alternatives;
- invalid states eliminated, residual obligations, and retirements.

For an initial Construction with no classified findings, Actuating invokes
`$metanoetic` exactly once after the first Universalist nomination and before
adjudication only when the nomination would establish a high-regret or difficult-
to-reverse commitment, remains a coherent but merely adequate local optimum, and
a materially different Construction is plausible. Initial implementation,
architecture, or consequence alone is not a trigger.

When an accepted Counterexample makes an abstraction change live by
challenging the representation, owner, admitted domain, equivalence,
normalization, or information retained—or when the Causal recurrence gate
triggers—Actuating invokes `$metanoetic` exactly once after the initial nomination
and before adjudication. Metanoetic must seek a materially new frame, invariant,
mechanism, artifact, or breakthrough candidate rather than a rhetorical
variant of the incumbent.

Universalist reclassifies and lowers any material Metanoetic result into its
repository-native nomination before candidate compilation. A useful result
must change at least one candidate's owner, factor inventory, admitted domain,
equivalence or normalization, retirement surface, proof surface, or falsifier.
A Metanoetic result may supply another derivation under the current basis. If it
depends on a new premise, Actuating admits that premise only through fresh
source authority or evidence and re-axiomatizes before lowering; Metanoetic cannot
manufacture axioms. If the result is material and uses only admitted premises,
Universalist lowers it under the current basis. Record
`Metanoetic result: no-material-reframe` only when the material-delta test fails;
renamed summaries do not constitute distinct candidates. Metanoetic does not classify
Counterexamples, select a Construction or Repair Disposition, grant mutation,
or create another artifact family.

Actuating then compiles exactly four comparable candidate families in canonical
order:

1. `realization-preserve`;
2. `admitted-domain-restriction`;
3. `representation-or-owner-strengthening`;
4. `ablation-normalization`.

Each candidate names its laws, observations, factors, residual obligations,
and falsifier. Repository-native specializations live within these families;
they do not replace or add a fifth family.

Candidate comparison is **obligation-closed**. Actuating first factors every
independent mandatory repair into one common core carried unchanged by all four
families, then varies only the family-specific disputed delta. A candidate that
omits an orthogonal required repair is inadmissible; its omission cannot prove
that another candidate dominates it. The selected factorization must be
arrival-order invariant for the same complete current obligation set.

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
checking recomposition. When Metanoetic is not triggered, the order is `activate ->
axiomatize for the current run -> Universalist nomination -> Reduce challenge
once -> Actuating adjudication -> one Construction`. When abstraction change is
live, the order is `activate -> axiomatize for the current run -> Universalist
nomination -> Metanoetic once -> Universalist
reclassification and lowering -> Reduce challenge once -> Actuating
adjudication -> one Construction`. The compact basis and challenge are
sufficient in Actuating composition; an independently useful Reduction
Certificate may appear only in `supporting_refs`. No supporting surface selects
the Construction or Repair Disposition.

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

A candidate `A` dominates candidate `B` only after both carry the same complete
mandatory obligation core and `A` is no worse in every ACT-AK dimension:

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
cannot manufacture a winner. Neither can omission of an independent owner cut,
proof obligation, or compatibility repair.

## Implementation reclassification

Before fresh review, compare the realized production delta with the challenged
candidate and its Axiomatic Construction Basis. Diff size is evidence to
inspect, not a reduction trigger. If implementation falsifies a basis premise
or introduces a materially new premise, re-axiomatize and select a successor
Construction before any further affected mutation. Run one new Reduction
challenge only when implementation introduces or materially changes a
disputable semantic factor. That challenge belongs to the successor candidate;
the same basis, candidate, and evidence never repeat recursively. Otherwise
retain the pre-mutation basis and challenge only within the same uninterrupted
run. A session end, compaction, or execution-context handoff requires
re-axiomatization before another nomination or affected mutation; a
premise-neutral subject digest change does not. Fresh review evaluates the
adjudicated result or the recorded obstruction.

An earlier `preserve`, `minimal`, or `no-material-reframe` result is a
premise-bound proof lease. Reuse it only while every relied-on owner,
multiplicity, representation, admitted-domain, compatibility, host-capability,
and proof-shape premise remains current. Later evidence that changes one of
those premises reopens the affected comparison; subject identity or raw size
alone does not decide expiry.

## Causal recurrence gate

Before another affected mutation, Actuating folds current and predecessor
Counterexample Sets against current and predecessor Constructions for the same
Goal. The gate triggers when one accepted class recurs after repair or when two
accepted classes across subject revisions share an evidenced missing
observation, authority, correlation, or Construction factor. Similar prose,
files, or line counts are not sufficient evidence of shared cause.

The fold crosses subject revisions. A new subject digest changes freshness, not
causal identity; a stable class recurring after rebinding must remain visible
to this gate.

Actuating compares the four ordinary v3 candidate families before
adjudication: realization preservation, admitted-domain restriction,
representation or owner strengthening, and ablation or normalization.

The candidate universe may contain a more specific repository-native
equivalent, but it may not omit one of these semantic alternatives. The Reduce
challenge tests the continued existence of the repair or validation mechanism,
not only whether its latest implementation is locally minimal.

Causal recurrence invalidates the prior candidate universe and automatically
makes abstraction change live. Re-axiomatize before the next Universalist
nomination, then complete the single Metanoetic pass and Universalist
reclassification before comparing the four families. A
`no-material-reframe` result does not weaken the required instance-specific
non-example proof.

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
implementation proof. Ledger 1.x rejects Construction v1, v2, and mixed stores
with `LegacyConstructionUnsupported`. There is no migration: start a fresh
goal-local Evidence store and ignore the legacy data.

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

For one `goal_id`, only the first Construction in the current authoritative v3
lineage may use `mode: initial` with empty `predecessor_refs`. A successor Goal
Contract, commit, publication, or other subject rebind does not restart
Construction lineage. Every later Construction names the exact current
Construction as its sole predecessor, even when all subject-bound proof and
review evidence must be re-established.

Subject identity and causal lineage are independent. Subject change invalidates
proof, operations, review bindings, review credit, and the ephemeral basis for
the old subject; it does not erase predecessor decisions or stable
Counterexample classes. The Causal recurrence gate scans the complete goal-local
predecessor chain across subject revisions and always requires
re-axiomatization. If changed laws or applicability make prior evidence
irrelevant, the successor records that rejection, separation, or supersession
explicitly rather than omitting the lineage.

The basis requirements are prospective selection laws. Every non-selecting
route—including triage, Ship handoff or publication, and closure—may consume a
valid pre-feature `construction-contract/v3` that lacks basis provenance; it
records the provenance as unavailable and awards no basis or selection proof.
Before any resulting mutation or new Construction selection, Actuating
re-axiomatizes and selects a successor Construction.

An accepted Review Fold uses `accepted-review-fold`, names the latest
Counterexample Set, and records the exact current accepted-class set in both
`counterexample_class_refs` and `evaluated_class_refs`. The Set must evaluate
the predecessor Construction on the exact current subject. An empty
review-driven successor is legal only when it clears a nonempty predecessor
debt set without an intervening subject change.

When a stable class recurs, the new Counterexample Set must name in
`predecessor_refs` the most recent Set carrying that class. Actuating rejects a
Set that omits this required Review Fold lineage and must not treat the class as
novel.

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
For every collapse, replacement, or retirement, account for each displaced
production, semantic, proof, and comprehension surface through deletion, a
successor-owner and proof-obligation mapping, or explicit retention by a
distinct live obligation. A smaller conceptual factor inventory without this
realization-retirement witness is incomplete. Every retirement names an absence
verifier and must be independently observed before closure.
