# Latent Structure Recognition

Use algebraic and categorical knowledge to derive and recognize structure.
The result is repository-native meaning and behavior, not mathematical vocabulary.

The goal is not:

```text
code resemblance -> impressive name
```

The goal is:

```text
required uses and concrete evidence <-> relevant mathematical hypotheses
  -> derived carriers, operations, observations, laws, and non-laws
  -> one evidenced general pattern
  -> one repository-native realization
  -> one observation-preserving transition when needed
```

Recognition nominates. Existing comparison, theorem-card, route, authority, and obstruction rules still decide whether anything changes.

## Governing rule

```text
Let theory suggest hypotheses; establish structure by laws, not labels.
Derive the formulation as well as recognizing an existing encoding.
Retain a generalization only for a material dividend.
Justify the native realization and any required transition.
```

A general pattern may be useful even when no advanced construction card is selected. Products, coproducts, monoids, actions, homomorphisms, folds, state machines, adapters, and checked witnesses often remain `UNI-ORDINARY`.

## When this guidance helps

Use within task-relevant semantic inquiry, including before a boundary decision
or candidate is named. A required use may call for deriving the carrier, operations,
composition, or proof from scratch; no existing encoding or duplicate is required.
`UNI-RECOGNIZE` can coincide with `UNI-BOUNDARY`. Reuse the common inquiry, not a
second mandatory pass. The following cues are examples, not exhaustive prerequisites:

- required behavior whose carrier, operations, observations, or composition needs derivation;
- a fixed public contract whose internal algorithm or representation remains open;
- a task-grounded mathematical hypothesis that suggests a useful discriminator;

- the same invariant checked at several creation or boundary paths;
- repeated branches that differ only by a case or parameter;
- several joins or compatibility checks through a shared observation;
- callbacks, closures, handlers, or predicates crossing an ownership boundary;
- several interpreters over the same operation vocabulary;
- repeated folds, traversals, accumulators, reducers, or transition loops;
- a temporary structure is built only to be consumed through a stable fold, with a material representation or traversal cost;
- wrapper families that repeatedly add the same context;
- projections or reports that duplicate one observation vocabulary;
- composition code that repeatedly checks the same compatibility rule;
- migration, rewrite, or translation functions that preserve the same structure;
- a concrete implementation plus an imminent variant whose shape is already constrained by the same law;
- a requirement-bound alternative already derived on the common path whose law needs discrimination, even at a first-use boundary.

Syntactic duplication alone is not enough. Reuse the common path's derivation rather than running a second challenger. A first-use derivation starts from attributed requirements and permitted operations; do not fabricate representative implementations.

## Recognition packet

The fields below guide applicable evidence, not mandatory headings or a separate
report. Reuse the common-path or receiving-workflow argument; the Actuating adapter
owns presentation when composed. The techniques are available ways to establish
that evidence, not a requirement to repeat work already discharged.

```text
Current encoding:
Representative instances:
Carriers:
Operations / constructors / eliminators:
Sanctioned observations:
Candidate equations:
Known non-laws / counterexamples:
Stable structure:
Varying parameters:
Candidate general pattern:
Encoding relation:
Nearest false friend:
Discriminating law:
Generalization dividend:
Transition witness:
Evidence debt:
```

Do not erase effects, authority, provenance, ordering, failure, locality, or resources while anti-unifying the instances.

## Encoding relations

When a current implementation exists, describe the material aspects of its
relation together. Correspondence, scope, law strength, and placement are not
mutually exclusive labels. Reuse the existing `Encoding relation` field; do not
add a mandatory matrix or invent uninspected properties. First-use synthesis
records its requirement-bound derivation rather than inventing an encoding.

A relation may be literal or observational, hold on the full claimed domain or
only a named restricted/degenerate fragment, and be concentrated or distributed.
For example: **a distributed observational realization on immutable snapshots**.
Retain each qualifier needed for the decision and its evidence; distribution
alone neither proves nor refutes the laws.

Distinguish strict equations from lax comparison maps and pseudo/invertible
coherence, with the actual structure's coherence laws. A normal form is a
realization technique whose correspondence needs proof, not automatically a lax
or pseudo structure. Do not call violated strict equations lawful merely by
renaming them lax; establish the weaker structure or leave it unresolved.

Unknown evidence remains unknown. A counterexample contradicts the scoped claim
it addresses, not every weaker or differently scoped interpretation. Reserve
**analogy only** for resemblance without an established structural correspondence;
a lawful structure with no engineering dividend is still lawful and need not
produce new machinery. Explain a law-violating approximation at its actual scope.

This characterization describes the current code. It remains separate from the
proposed artifact's realization strength and actual proof kind:

```text
literal
effective realization
bounded approximation
```

## Recognition protocol

### 1. Excavate the concrete encoding

Inspect available code or attributed first-use requirements before accepting a
pattern. Theory may already suggest a hypothesis or deciding question:

```text
representations
construction paths
elimination paths
operations
composition
observations
effects and order
owners
bypasses
tests and counterexamples
```

### 2. Extract the latent algebra

Record:

```text
carriers
operations
observations
candidate laws
known non-laws
interpreters
effect boundaries
```

Use tests, callers, schemas, traces, and compatibility behavior as evidence. Names and comments are hints, not proof.

When the operation vocabulary, interacting equations, or observation carrier
remains unresolved, use [domain algebra discovery](domain-algebra/algebra-driven-design.md)
within this extraction. Derive from required uses; let contradictory laws revise
the vocabulary or carrier, and consider a unifying observation when production
traversals duplicate semantics. Reuse this packet and discriminator; preserve
independent verification, complete caller contracts, and the existing gates.
Do not load the method merely to rename an already-dispositive ordinary design.

### 3. Anti-unify neighboring instances

Ask:

- what structure remains invariant across the instances?
- what varies parametrically?
- which differences are incidental representation?
- which differences remain observable and therefore cannot be quotiented?
- which special cases compensate for a missing general operation?
- which operations preserve the same law across representations?
- is one owner missing, or is the distribution intentional?

Anti-unify behavior and proof obligations, not merely shared syntax. At first use,
derive the carrier and operation vocabulary from required uses and observations;
neither needs to be fixed on entry. Anti-unification is inapplicable without
neighboring instances.

Distinguish packaging cases from deriving shared semantics. A coproduct of the
input types for `r_i : C_i -> V` gives one dispatcher, but may retain every
original mechanism and proof obligation. Even a factorization `r_i = h o e_i`
can hide the same case split in `h` or the encoders. For a claimed semantic
reduction, identify the common law-bearing carrier and the work actually removed;
include the remaining per-instance correspondence obligations in the comparison.
A tagged union may still be the best result for exhaustiveness or invalid-state
exclusion; do not require a shared algorithm when that is not the claimed dividend.
Use [carrier derivation](domain-algebra/algebra-driven-design.md#derive-the-operation-carrier-from-a-required-law)
when the required law can determine the operation space. Keep independent
verification independent even when production semantics are unified.

When a shared abstraction is disputed, state the exact common principle and the
distinctions it forgets. Determine whether the objection exposes an omitted,
more specific premise that changes required behavior, or invokes a broader
principle the candidate does not claim. Use a distinguishing required case to
refine or reject the boundary; a material premise may belong in a parameter,
carrier, or separate owner.

For example, retries and redelivery may share the rule that repeating one
logical operation must not duplicate its external effect. Short retention versus
historical replay changes the identity and lifetime obligations that must remain
explicit. By contrast, treating equal payloads as the same operation is a broader
claim: two distinct purchases with identical payloads refute it without refuting
idempotency by logical-operation identity.

This dispute discriminator adapts Eugenia Cheng, [*The Joy of Abstraction*](https://doi.org/10.1017/9781108769389),
sections 2.5–2.6 (printed pp. 28–30) and 3.5 (pp. 42–43). The retry example is
an engineering application.

### 4. Nominate a small candidate family

Develop task-relevant hypotheses from evidence and mathematical knowledge, then
discriminate them against ordinary native candidates, including unmet requirements
of an inadequate baseline. Reuse sufficient supplied
derivations. A candidate need not arrive with the proof its investigation is meant
to discover. Stop when the result is adequately supported and no material question
remains; neither a fixed count nor speculative enumeration establishes sufficiency.

For each candidate record:

```text
candidate
current-encoding relation
supporting evidence
missing evidence
nearest false friend
discriminating law
likely repository-native form
```

A theorem-card signal never proves the candidate. A recognized ordinary pattern does not need a theorem card.

### 5. Discriminate by law

Use the smallest executable law or counterexample that separates the candidates.

Typical discriminators:

```text
construction / projection round-trip
exhaustive elimination
predicate stability
shared-projection agreement
identity
associativity
homomorphism
naturality
interpreter equivalence
value dependence versus static shape
effect-order sensitivity
restriction / gluing
square boundary matching and interchange
```

Examples:

- **stored data versus its eliminator** — does a consumer need only a fold, or also constructor inspection, original substructures, sharing, or durable identity? Multiple interpreters alone do not decide this.
- **applicative versus monadic** — can later operation shape be known before earlier results?
- **pointwise versus Day composition** — does only the same index combine, or must every legal decomposition contribute?
- **Reader parameter versus Tambara framing** — is there an actual context action with unit, associative framing, and endpoint naturality?
- **commuting square versus double category** — do both arrow families independently compose, and do local squares paste in both directions?
- **arbitrary merge versus pushout** — is there an explicit overlap with source maps and a universal compatibility obligation?
- **operation coverage versus endpoint correspondence** — when lifting target
  transformations or distinguishing parallel source transformations is claimed,
  compare `C(a,b) -> D(Fa,Fb)` at the relevant endpoint pairs. For lifting,
  include pairs with no source transformation: collapsing both endpoints to one
  target introduces its identity despite an empty source homset. A scope,
  capability, or phase distinction may need to remain represented. A deliberately
  lossy view need not be full or faithful; strict identity and authority remain
  separate requirements. Use [endpoint-specific correspondence](claim-appropriate-proof.md#endpoint-specific-correspondence)
  for the applicable proof, not a mandatory endpoint matrix. The criterion comes
  from Cheng, *The Joy of Abstraction*, section 21.5 (printed pp. 323–325).

### 6. Require a generalization dividend

Adopting new abstraction machinery requires a material dividend such as:

- one owner replaces scattered validation or policy;
- invalid states or illegal compositions become unrepresentable;
- several special cases become one operation plus parameters;
- one interpreter replaces repeated execution semantics;
- one composition law replaces orchestration checks;
- one observation vocabulary replaces projection sprawl;
- a future variant becomes new data or a new interpreter instead of new control flow;
- migration becomes a structure-preserving map rather than per-case repair;
- a lawful fusion, specialization, or interpreter transformation removes work without changing required behavior;
- a derived algorithm or sufficient compositional summary eliminates rescanning or coordination;
- a preservation argument resolves a live question without changing an adequate incumbent;
- reusable property tests or proof obligations become possible;
- a genuine obstruction becomes visible.

No material dividend means no additional abstraction machinery is justified;
keep the adequate native candidate. It does not falsify an established mathematical
correspondence or require relabeling a lawful structure as an analogy.

### 7. Construct the transition witness

When changing an existing representation or path, account for the transition even if the route label is unchanged:

```text
Current encoding:
Generalized repository-native form:
Encode / translate:
Interpret / project:
Preservation law:
Compatibility boundary:
First witness seam:
Cutover order:
Retired obligations:
Retired bypasses:
Rollback:
Stop condition:
Invalidation triggers:
```

For a changed existing representation, the transition should normally be staged.
At first use, derive and verify the construction directly; do not manufacture a
legacy path, migration, or second implementation:

1. introduce the generalized core behind the current boundary;
2. translate one representative existing case;
3. prove observational agreement with the old path;
4. route one caller through the new interpretation;
5. extend only to instances governed by the same evidenced law;
6. close raw construction or bypass paths;
7. retire compatibility adapters only after their callers are gone.

A first witness is a checkpoint, not completion of remaining authorized callers or
proof that every sanctioned path is covered. Do not widen the migration merely
because the general pattern can express more.

### 8. Return to ordinary Universalist adjudication

Compare:

```text
ordinary candidate
recognized repository-native realization
other relevant registered or unlisted constructions
preserve, unresolved comparison, or witnessed obstruction
```

The existing comparison universe, dominance relation, current-context contract, host capabilities, effectivity, and authority rules determine the route.

## High-yield recognition atlas

| Concrete encoding | Candidate pattern | Discriminating evidence | Typical transition |
|---|---|---|---|
| flag matrix with rejected combinations | coproduct / explicit cases | impossible mixtures are semantically invalid | tagged union behind legacy decoder |
| stable predicate checked in many places | refined type / equalizer when claimed | one predicate remains stable under permitted operations | native invariant-preserving value or checked constructor; normalization is optional |
| two values repeatedly compared through one shared projection | pullback-shaped compatibility object | both required projections are recovered and shared views agree | shared-coordinate representation or checked aggregate |
| merges identify an explicit common overlap | pushout-shaped integration | source injections agree only on declared overlap | one provenance-preserving integration owner |
| callbacks need replay, audit, authorization, or multiple execution modes | free syntax or defunctionalized IR | cases are finite/effective and one interpreter preserves behavior | encode one callback family and add `apply` / interpreter |
| operation plan is inspectable before results | free applicative / static plan | later shape does not depend on earlier values | static operation IR |
| later operation depends on an earlier value | monadic / value-dependent sequence | dependency cannot be represented statically | bindable program IR or ordinary sequence |
| repeated associative combination with an identity | monoid / monoidal composition | identity and associativity hold under sanctioned observations | central combine operation plus property tests |
| conversions preserve operations across representations | homomorphism / natural transformation | operation then convert equals convert then operation | explicit structure-preserving adapter |
| many projections define effective equality | observation vocabulary; Yoneda only with its natural correspondence | equivalence is adequate under permitted future operations | observation IR plus one runner |
| repeated context wrappers around one capability | action / Tambara candidate | real unit, associative framing, and naturality exist | one typed frame operation or reject to ordinary context parameter |
| local rules repeatedly rebuild views at other positions | comonadic extension / co-Kleisli composition | extraction and nested extension cohere; later rules see derived neighbors, not stale ones | one native refocusing/extension owner; keep an adequate environment parameter |
| nested decomposition loops combine indexed descriptions | Day or promonoidal composition | all legal decompositions or witnesses must contribute | bounded indexed representation and normalizer |
| local meanings restrict and must glue across overlaps | presheaf / sheaf candidate | restrictions compose and compatible locals glue uniquely-up-to | usage-site index then exact global model |
| recursive traversals differ only by result algebra | fold / initial-algebra pattern | constructors determine the traversal homomorphism | one recursion scheme or repository-native fold |
| a temporary representation is built only to be folded | eliminator-oriented / Church-style producer | round trips, algebra-morphism preservation, and fold/build law under actual host assumptions | native fold or fused loop; retain required materialization |
| consumers repeatedly need one constructor layer or original substructures | native case analysis / Scott or paramorphism comparison | demand, sharing, and whole-workload costs remain correct | keep explicit data unless an alternative has a measured dividend |
| transitions expose observable ongoing behavior | coalgebra / state machine | step and observation determine traces | explicit transition and observation API |
| runtime processes compose and architecture changes compose separately | double-category candidate | both directions compose; compatibility squares paste; interchange is observable | typed arrows, squares, pasting, and interpreter |

The atlas and registry are abductive retrieval aids, not limits on available
knowledge. Investigate unlisted structures and combinations when they address the
task. A missing discriminator is a question to resolve, not proof of applicability;
leave acceptance unresolved or reject the candidate when it cannot be established.

For the contextual-extension row, use the focused-view derivation in
[`effects-and-coalgebras.md`](effects-and-coalgebras.md#co-kleisli-extension--context-consuming-rules).
Unlike Tambara framing of both endpoints, this lifts a context-consuming rule
across coherent alternative views. A fixed environment paired with a value can
already be a lawful product comonad; reject an unnecessary abstraction for lack
of dividend, not because that mathematical structure is absent.

## Worked derivation: compatibility without extra policy

Assume immutable `A` and `B`, total tenant projections `p : A -> T` and
`q : B -> T`, and a requirement to retain both values and admit every pair
whose projections agree. Derive:

```text
P = {(a,b) in A x B | p(a) = q(b)}
make(a,b) = Ok((a,b)) exactly when p(a) = q(b)
left(make(a,b)) = a; right(make(a,b)) = b       on successful construction
```

For any compatible producer `u : X -> A`, `v : X -> B`, the mediator is
`h(x) = (u(x),v(x))`. It lands in `P` by the agreement equation. Any other
mediator preserving both projections has the same pair at every `x`, so is equal
in this set model. That argument, not a private constructor, supplies the
pullback property. See `mechanics/pullbacks-and-pushouts.md` for the diagram.

An opaque checked aggregate is one native realization, not a pullback requirement.
When value-like sources factor through a shared coordinate, derive whether storing
that coordinate once removes the agreement check; see
[the transparent realization](canonical-boundary-artifacts.md#derive-away-duplicate-coordinates).
Do not sacrifice required object identity, independent mutation, or provenance.
No generic categorical framework is needed.
Reject both false friends: a raw pair admits mismatches; an additional
same-backend restriction rejects a required compatible cross-backend pair.
Test a mismatch, a valid cross-backend pair, and both projections. One rejected
invalid case does not establish representational adequacy. Tenant agreement is
not complete authorization; other requirements retain their actual owners.

If projection data may mutate, constructor validity is not enough. Freeze the
relevant identity, derive one value from the other when requirements permit, or
route mutation through an owner that preserves agreement. Test the mutation and
alias/deserialization paths together. Do not erase one source when both are
required observations. Translate one caller and retire its raw-pair bypass;
expand only after this witness holds.

## Derive transformations as well as carriers

A law can remove a traversal, intermediate representation, or coordination rule
without creating a new public abstraction. When this is the live alternative,
use `domain-algebra/property-test-derivation.md` for fold/interpreter preservation
and cost separation. When future behavior or phase ordering is the discriminator,
use the matching example in `effects-and-coalgebras.md`. These are targeted
references, not additional mandatory passes.

When the live alternative changes whether a representation is materialized,
load `syntax-semantics-pivot.md` for the eliminator-first comparison, then only
`domain-algebra/property-test-derivation.md` when the representation/fusion law
needs checking. Reuse the existing recognition packet's eliminators, observations,
false friend, dividend, and transition witness. This is not a new card, trigger,
proof profile, or separate pass. A callback or a familiar encoding name alone
supplies no reason to replace an already adequate datatype.

## False-positive guardrails

Do not adopt a generalization when:

- only names or surface syntax match;
- the proposed law is contradicted by required behavior;
- the domain rule is unstable;
- the representation would erase an observable distinction;
- the generalized API adds more obligations than it removes;
- an adequate local helper already resolves the question and the proposed machinery adds no dividend;
- the transition cannot preserve compatibility;
- the host cannot enforce the claimed structure;
- resource or effect costs make the realization dishonest.

The desired output is repository language:

```text
These three compatibility checks are one distributed agreement rule.
Introduce one checked owner for the compatible pair.
Preserve both source projections.
Translate one existing caller and prove the shared view still agrees.
Retire unchecked pair construction only after the witness seam passes.
```

The expert explanation may add:

```text
pullback-shaped observational realization
nearest false friend: ordinary pair plus repeated validators
discriminating law: both shared projections agree
generalization dividend: one owner and no bypass
```
