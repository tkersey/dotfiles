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
materialized Construction. A clean committed subject change alone does not
expire it within one uninterrupted run when every premise and invalidator
remains current. Any later run, or any subject change that alters a premise or
invalidator, re-axiomatizes before nomination or affected mutation.

A `sufficient` basis admits nomination. An `underdetermined` basis carries every
materially incomparable derivation into candidate comparison and blocks if
current Goal law, observation, or dominance cannot distinguish them. A new
source preference must first become a successor Goal Contract. `inconsistent`
or `blocked` stops selection. `$first-principles` may expose a Goal conflict or
missing authority, but it cannot revise the Goal, classify a Counterexample,
nominate or select a Construction, grant mutation, or author a durable decision.

With a current basis, Actuating applies `$universalist` to the affected boundary
and records its nomination:

- the current context and accepted laws;
- the existing owner and host enforcement capabilities;
- the smallest repository-native candidate;
- materially distinct candidates and their falsifiers;
- invalid states eliminated, residual obligations, and retirements.

For an initial Construction with no classified findings, Actuating invokes
`$metanoetic` exactly once after the first Universalist nomination and before
adjudication only when the nomination would establish a high-regret or
difficult-to-reverse commitment, remains a coherent but merely adequate local
optimum, and a materially different Construction is plausible. Initial
implementation, architecture, or consequence alone is not a trigger.

When an accepted Counterexample challenges the representation, owner, admitted
domain, equivalence, normalization, or information retained—or when causal
recurrence or review-path accretion makes abstraction change live—Actuating
invokes `$metanoetic` exactly once after the initial nomination and before
adjudication. Universalist reclassifies and lowers every material result before
candidate compilation. Metanoetic cannot manufacture a premise, classify a
finding, select a Construction, grant mutation, or create another artifact
family.

Actuating then compiles exactly four comparable candidate families in canonical
order:

1. `realization-preserve`;
2. `admitted-domain-restriction`;
3. `representation-or-owner-strengthening`;
4. `ablation-normalization`.

Each candidate names its laws, observations, factors, residual obligations,
and falsifier. Candidate comparison is **obligation-closed**: every independent
mandatory repair is factored into one common core carried unchanged by all four
families, and only the family-specific disputed delta varies. Omission of an
orthogonal repair makes a candidate inadmissible; it cannot establish dominance.
The selected factorization must be arrival-order invariant for the same complete
obligation set.

For each accepted Counterexample class that can lead to mutation, Actuating
records this compact view while selecting the Construction:

~~~text
Repair Disposition
Law:
Owner:
Reduction: not-required | minimal | dominated | incomparable | essential-shape-gap | blocked
Route: delete | consolidate | edit | add
Why not smaller:
Falsifier:
~~~

A finding authorizes the invariant, not its suggested implementation. The route
is the least additive route satisfying the law; `add` explains why `delete`,
`consolidate`, and `edit` are insufficient.

Before selection, `$reduce` challenges every materially disputable factor by
factoring live obligations, testing congruent quotients or ablations, and
checking recomposition. A challenge is required when the nominee adds or
preserves an independent semantic owner, parallel representation, bypass,
compatibility branch, semantic mechanism, or apparently dominated residue.
`dominated` requires the smaller admissible candidate. `minimal` permits the
nominee. `incomparable`, `essential-shape-gap`, or `blocked` returns to
Actuating for adjudication or obstruction; it never starts recursive
Universalist/Reduce competition.

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

`A` must be strictly better in at least one dimension. If non-dominated minima
remain incomparable, prove `separate-laws` from distinct accepted laws or block.
Preference, familiarity, implementation momentum, or an omitted obligation
cannot manufacture a winner.

## Implementation reclassification

Before fresh review, compare the realized committed production delta with the
challenged candidate and current Axiomatic Construction Basis. Diff size is an
inspection signal, not a reduction trigger. If implementation falsifies a
basis premise or introduces a new premise, re-axiomatize and select a successor
Construction before another affected mutation. Run another Reduction challenge
only when implementation introduces or materially changes a disputable semantic
factor. Otherwise retain the current-run basis and challenge.

An earlier `preserve`, `minimal`, or `no-material-reframe` result is a
premise-bound proof lease. Reuse it only while every relied-on owner,
multiplicity, representation, admitted-domain, compatibility, host-capability,
and proof-shape premise remains current. Subject identity or raw diff size alone
does not decide expiry.

## Causal recurrence gate

Before another affected mutation, Actuating folds current and predecessor
Counterexample Sets against current and predecessor Constructions for the same
Goal. The gate triggers when one accepted class recurs after repair or when two
accepted classes across subject revisions share an evidenced missing
observation, authority, correlation, or Construction factor. Similar prose,
files, or line counts are not sufficient evidence of shared cause.

The fold crosses clean committed subject revisions. A new commit changes
freshness, not causal identity; a stable class recurring after rebinding remains
visible. Causal recurrence invalidates the prior candidate universe and makes
abstraction change live. Re-axiomatize, complete the single Metanoetic pass and
Universalist lowering, compare all four candidate families, then adjudicate.

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

Instance-specific proof must be non-example evidence that separates the cluster
and establishes the current representation as sufficient. Without it,
Actuating selects an architecture or ablation successor or blocks. It must not
add another local validator that reconstructs information the representation
repeatedly forgets.

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
an example unless accepted source authority explicitly owns the residual risk
and a compensating invariant proof exists.

For every accepted Counterexample class, v3 requires a law-matched
`implementation` obligation; aggregate `acceptance` is not a substitute.
Recurrent, High, and Critical classes require non-`example-regression`
implementation proof.

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

Every material implementation has one current Construction. A successor states:

- exactly one predecessor naming the current Construction;
- which predecessor claims were falsified and preserved;
- which accepted Counterexample classes it excludes;
- whether the defect is realization, architecture, or ablation;
- what structure changes or remains;
- which valid observations remain;
- what proof becomes stronger;
- what dominated residue must disappear.

Only the first Construction in the authoritative v3 lineage may use
`mode: initial` with no predecessor. A successor Goal Contract, clean commit,
publication epoch, or other subject rebind does not restart Construction
lineage. Subject identity and causal lineage are independent: a subject change
invalidates subject-bound proof, operations, and review credit, but does not
erase predecessor decisions or stable Counterexample classes.

An accepted Review Fold uses `accepted-review-fold`, names the latest
Counterexample Set, and records the exact accepted-class set in both
`counterexample_class_refs` and `evaluated_class_refs`. The Set evaluates the
predecessor Construction on the exact current committed subject. When a stable
class recurs, the new Set names the most recent Set carrying it in
`predecessor_refs`; omission blocks and does not make the class novel.

Proof references are artifact-relative. Predecessor-factor observation refs
resolve only through the predecessor Construction. Candidate,
successor-factor, essential-addition, and surface-completeness refs resolve only
through the successor. Reusing a local proof ID cannot silently change its
owner.

`realization-repair` preserves architecture and corrects implementation or a
bypass. `architecture-repair` changes architecture. `ablation-repair`
preserves the selected replacement while completing retirements.

Every `preserved_observations` entry names an `obligation_id` in the same
Construction. It cannot claim preservation without an executable proof
obligation.

## Committed Git subject

The durable Actuating subject is one clean Git commit target. Dirty index,
worktree, untracked, and ignored state is provisional implementation state and
never an Evidence subject.

For a Git repository, derive the subject exactly as:

~~~text
subject_digest = sha256(
  "actuating-git-subject/v1" || 0x00 ||
  repository_id || 0x00 ||
  commit_oid || 0x00 ||
  tree_oid
)
~~~

Where:

- `commit_oid = git rev-parse --verify HEAD^{commit}`;
- `tree_oid = git rev-parse --verify HEAD^{tree}`;
- `git status --porcelain=v2 --untracked-files=all --ignore-submodules=none`
  must be empty;
- ignored files do not participate because they are not candidates for the
  committed target;
- branch attachment is not part of semantic identity; Ship binds publication
  refs separately.

The `sha256:` textual form uses 64 lowercase hexadecimal digits. Actuating owns
this framing and computes it from Git output; Ledger stores and compares the
opaque digest but never invokes Git or infers repository identity.

## Operation projection

`execution.allowed_paths` is a duplicate-free canonical literal repository
path set. `.` is valid Goal scope but never executable Construction or
operation scope. `.git`, `.ledger`, their descendants, and ancestors selected
only to reach them are reserved under ASCII case-folding. A broader Goal scope
does not authorize them.

Actuating selects the next exact operation from the current Goal, Construction,
clean committed subject, and Evidence. An operation envelope or validator pass
supplies no mutation authority.

Every operation carries the current `expected_subject_digest`. Before preparing
or delegating it, Actuating requires the checkout to be clean and its
repository, commit OID, tree OID, and derived subject digest to match the
current Evidence subject.

### Edit

An edit has this lifecycle:

~~~text
clean parent target
-> prepare exact operation
-> one-seam-operator creates one provisional diff
-> Actuating inspects the complete diff and exact changed paths
-> Actuating commits exactly that operation
-> require one-parent clean successor
-> derive successor subject
-> record effect parent -> successor
-> run verifier and falsifier on the clean successor
~~~

`one-seam-operator` never stages, commits, amends, pushes, or publishes. It
re-reads target files before mutation and returns to Actuating when the selected
seam or assumptions are no longer current. Compatible concurrent changes may be
incorporated only when they remain inside the selected operation; unrelated or
ambiguous dirty state blocks before preparation.

The committed successor must:

- have exactly one parent equal to the prepared parent commit;
- contain a nonempty path set exactly equal to the selected edit operation;
- keep every changed path inside Construction scope and outside Goal
  prohibitions;
- leave the checkout clean;
- produce a subject digest different from the parent;
- receive no verifier or review credit until required proofs run on that exact
  clean commit.

The resulting `effect_recorded` event advances the current subject directly
from the parent digest in `pre_effect_subject_digest` to the successor digest in
the event envelope. No dirty-state subject, commit-equivalence observer, or
separate commit-rebinding event exists.

### Inspect and verify

Inspect and verify operations run only on the exact clean committed target.
Their commands and outputs remain owner evidence. After execution, the checkout
must still be clean and the commit/tree-derived subject must be unchanged.
Any correctness-bearing generated change requires a selected edit, commit, and
fresh proof; it cannot be smuggled into a read-only observation.

## Ablation

A replacement is incomplete while a dominated predecessor, duplicate owner,
bypass, representation, validator, adapter, flag, or proof path remains live.
For every collapse, replacement, or retirement, account for each displaced
production, semantic, proof, and comprehension surface through deletion, a
successor-owner and proof-obligation mapping, or explicit retention by a
distinct live obligation. Every retirement names an absence verifier and must
be independently observed before closure.
