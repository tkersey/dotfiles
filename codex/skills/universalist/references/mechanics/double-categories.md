# Double Categories

## Scope

This reference concerns double categories in the Ehresmann/Grandis-Paré/Shulman sense: objects, two different kinds of arrows, and squares that compose in two directions.

It does not mean:

```text
a category with twice as many objects
a pair of unrelated categories
a double-pushout rewrite by itself
a 2-category with renamed cells
a visual diagram that happens to be square
```

The Universalist architectural reading is:

> A double category is the canonical setting when both **systems/processes compose** and **changes/maps between those systems compose**, while squares witness that changing and composing remain compatible.

## 1. Basic structure

A strict double category `D` can be presented as a category internal to `Cat`. Concretely it contains:

```text
objects
vertical arrows
horizontal arrows
squares / 2-cells
```

A square is drawn:

```text
A ---H---> B
|          |
f    α     g
|          |
v          v
A'--K---> B'
```

where:

```text
H : A => B       horizontal arrow
K : A' => B'     horizontal arrow
f : A -> A'      vertical arrow
g : B -> B'      vertical arrow
α                 square with boundary (H,K,f,g)
```

The symbols `=>` and `->` are only mnemonic. A repository may choose the opposite orientation. What matters is that the two arrow kinds have distinct meaning and independent composition.

### Horizontal composition

```text
A ---H---> B ---J---> C
```

composes to `H ;H J : A => C`.

### Vertical composition

```text
A --f--> A' --f'--> A''
```

composes to `f ;V f' : A -> A''`.

### Square pasting

Squares paste horizontally when their adjacent vertical edges match, and vertically when their adjacent horizontal edges match.

Horizontal pasting:

```text
A ---H---> B ---J---> C
|    α     |    β     |
f          g          h
|          |          |
v          v          v
A'--K---> B'--L---> C'
```

produces `α pasteH β`.

Vertical pasting:

```text
A ---H---> B
|    α     |
f          g
|          |
v          v
A'--K---> B'
|    γ     |
f'         g'
|          |
v          v
A''-M---> B''
```

produces `α pasteV γ`.

### Interchange

For a compatible 2x2 grid:

```text
(α pasteH β) pasteV (γ pasteH δ)
  =
(α pasteV γ) pasteH (β pasteV δ)
```

in a strict double category. In a pseudo or weak implementation this may hold up to a declared coherent isomorphism or normalization.

Interchange is the defining architectural gain: local compatibility proofs can be assembled in either dimension without changing the resulting global proof.

## 2. Strict versus pseudo

Many important examples are pseudo double categories. Horizontal arrows such as spans, cospans, and profunctors often compose only up to canonical isomorphism because their composition uses pullbacks, pushouts, or coends.

Use:

```text
strict
  when identities, composition, and interchange are literal or normalized

pseudo
  when associativity/unit laws hold through explicit coherent isomorphisms
```

A software implementation often realizes a pseudo double category through a normal form:

```text
compose
  -> normalize
  -> compare by sanctioned observations
```

Do not claim strictness merely because a programming language's equality operator returns true on a few fixtures.

## 3. Double category versus 2-category

A 2-category has:

```text
objects
one kind of 1-cell
2-cells between parallel 1-cell composites
```

A double category has:

```text
objects
two distinct kinds of 1-cell
squares with one kind on the horizontal boundary and the other on the vertical boundary
```

Use a 2-category or bicategory when the two proposed arrow families are really one kind of morphism seen at different levels. Use a double category when the distinction is architectural, for example:

```text
functors versus profunctors
functions versus relations
interface maps versus open systems
migrations versus executable processes
refinements versus simulations
```

A double category can yield horizontal and vertical 2-categories by restricting squares, but those shadows forget the full two-direction interaction.

## 4. The canonical examples

### Categories, functors, profunctors, transformations

The double category `Prof` has:

```text
objects             categories
vertical arrows     functors
horizontal arrows   profunctors
squares              natural transformations with functorial boundaries
```

This is often an **equipment** or framed bicategory: a strict map/functor can induce generalized proarrows through companions and conjoints, and profunctors can be restricted along functors.

Software reading:

```text
strict representation-changing map
versus
generalized many-to-many boundary relation
```

The double category keeps both without pretending the relation is a function.

### Sets, functions, relations, implications

A double category of relations can use:

```text
objects             sets / data types
vertical arrows     functions
horizontal arrows   relations
squares              implication or relation-preservation witnesses
```

Double-functorial semantics can unify functional and relational knowledge representations and express relational-algebra-style queries while preserving functional data maps.

### Spans

```text
objects             objects of a category C
vertical arrows     maps in C
horizontal arrows   spans
squares              maps of spans
```

Horizontal composition uses pullback. The pseudo coherence records the canonical comparison among chosen pullbacks.

### Cospans and structured cospans

```text
objects             interfaces
vertical arrows     interface maps
horizontal arrows   open systems / structured cospans
squares              maps of open systems
```

Horizontal composition uses pushout to glue shared interfaces. Symmetric monoidal double categories of structured or decorated cospans model open circuits, Petri nets, Markov processes, dynamical systems, and other systems that compose through interfaces.

### Double categories of open dynamical systems

Some system theories need two different kinds of system map, for example covariant behavior witnesses such as trajectories and contravariant plugging/substitution of variables or parameters. Double categories keep those directions separate while supporting compositional semantics.

## 5. Squares as architectural evidence

A square should not be stored as `bool compatible` when the architecture needs to know why compatibility holds.

A repository-native square may carry:

```text
source horizontal arrow id
source vertical boundary id
target vertical boundary id
target horizontal arrow id
mapping or rewrite witness
observation-preservation evidence
provenance
resource/cost delta
normalization/coherence token
proof-lease context id
```

The square constructor owns boundary matching. The square interpreter owns the semantic comparison.

Examples:

```text
API migration square
  old request process + client/server migrations -> new request process

schema/query square
  source query + schema maps -> target query

refactor square
  old pipeline + component refactors -> new pipeline

open-system square
  interface maps + system map -> transformed open system

rewrite square
  host/rule maps + rewrite witness -> compatible rewritten host
```

## 6. Repository-native IR

A narrow effective realization might look like:

```typescript
type HArrow<A, B> = {
  readonly source: A;
  readonly target: B;
  readonly program: ProcessIR;
};

type VArrow<A, A2> = {
  readonly source: A;
  readonly target: A2;
  readonly migration: MigrationIR;
};

type Square<A, B, A2, B2> = {
  readonly top: HArrow<A, B>;
  readonly left: VArrow<A, A2>;
  readonly right: VArrow<B, B2>;
  readonly bottom: HArrow<A2, B2>;
  readonly witness: CompatibilityWitness;
  readonly proofLease: ContextFingerprint;
};
```

Owner-controlled operations:

```text
identityH
composeH
identityV
composeV
makeSquare
pasteH
pasteV
normalizeSquare
interpretSquare
invalidateByBoundary
```

The public API should make edge mismatch impossible in a strongly typed host or return a structured mismatch in a weaker host.

Do not start by building a generic higher-category library. Implement the one horizontal family, one vertical family, and one square family needed by the witness seam.

## 7. Laws and tests

### Arrow laws

```text
composeH(idH(A), H) ~= H
composeH(H, idH(B)) ~= H
composeH(composeH(H,J),K) ~= composeH(H,composeH(J,K))

composeV(idV(A), f) ~= f
composeV(f, idV(A')) ~= f
composeV(composeV(f,g),h) ~= composeV(f,composeV(g,h))
```

### Boundary law

```text
makeSquare(top,left,right,bottom,witness)
```

succeeds only if every corner and shared boundary matches under the declared identity/equivalence policy.

### Horizontal pasting law

The right boundary of the left square must equal the left boundary of the right square. The composite square exposes only the external boundary and preserves internal provenance when observable.

### Vertical pasting law

The bottom boundary of the upper square must equal the top boundary of the lower square.

### Interchange law

```text
normalize(
  pasteV(pasteH(alpha,beta), pasteH(gamma,delta))
)
==
normalize(
  pasteH(pasteV(alpha,gamma), pasteV(beta,delta))
)
```

under the sanctioned observations.

A falsifier should include a grid where one ordering changes:

```text
effect trace
authority
failure mode
provenance
resource cost
schema meaning
```

If the difference is required, ordinary strict interchange is invalid; use a weaker or ordered structure, split the axis, or return obstruction.

### Interpreter / double-functor law

For an interpreter `F`:

```text
F(composeH(H,J)) ~= composeH(F(H),F(J))
F(composeV(f,g)) ~= composeV(F(f),F(g))
F(pasteH(alpha,beta)) ~= pasteH(F(alpha),F(beta))
F(pasteV(alpha,gamma)) ~= pasteV(F(alpha),F(gamma))
```

with identity and coherence preservation.

## 8. Equipments, companions, and conjoints

A proarrow equipment distinguishes:

```text
tight / vertical arrows
  strict maps, adapters, migrations, reindexings

loose / horizontal arrows
  spans, profunctors, relations, open systems, generalized boundaries
```

A tight map may have:

```text
companion   a loose arrow in the same direction
conjoint    a loose arrow in the opposite direction
```

These support restrictions/base change of loose arrows along strict maps.

Architectural use:

```text
schema map
  -> restrict or transport a relational query

interface map
  -> reindex an open system

representation map
  -> transport a generalized boundary capability
```

Companion/conjoint structure is not free. Record:

```text
which strict maps admit companions/conjoints
construction API
unit/counit or triangle witnesses
base-change/restriction law
resource cost
failure/obstruction case
```

If only some maps support base change, expose a partial or capability-indexed equipment rather than a universal claim.

## 9. Double functors and transformations

A double functor maps:

```text
objects -> objects
horizontal arrows -> horizontal arrows
vertical arrows -> vertical arrows
squares -> squares
```

and preserves both compositions and identities, strictly or through declared lax/pseudo comparison cells.

In software, a double functor may be:

```text
compiler/lowering of a process-and-migration IR
query semantics from schema syntax to functions-and-relations
deployment lowering from logical services to runtime units
simulation semantics for open systems
cost/security/audit interpretation of the same two-dimensional architecture
```

This supports multiple interpretations of one architecture, similar to an operad algebra but with two arrow directions and square compatibility.

## 10. Open-system architecture

Double categories of structured or decorated cospans are especially important for software architecture.

A structured cospan has the form:

```text
L(input) -> system <- L(output)
```

Horizontal composition glues output and input interfaces by pushout. Vertical arrows change interfaces. Squares map the internal systems while respecting both interface legs.

Repository reading:

```text
object              interface/schema/port set
horizontal arrow    service/process/network with exposed boundary
vertical arrow      interface migration or renaming
square              implementation/system map compatible with interface changes
```

A monoidal product may place systems side-by-side. Do not confuse this tensor with horizontal composition through connected interfaces.

## 11. Knowledge and database semantics

A double category of functions and relations can preserve both:

```text
functional data transformations
relational query semantics
```

A double functor can interpret a syntactic knowledge/schema world into this semantic world. Squares witness that a functional map preserves or transports a relation/query.

Universalist implications:

- do not force a relation into a partial function;
- do not hide query transport in ad hoc mapper code;
- make function/relation compatibility a square;
- use the square's boundary to preserve provenance and schema version;
- invalidate affected query squares when a schema map or relation changes.

## 12. Rewriting and double-pushout mechanics

A double category is not the same as double-pushout rewriting.

DPO rewriting requires a rule:

```text
L <- K -> R
```

plus a match and a pushout complement. Adhesive or adhesive-like hypotheses control existence and compositionality.

A double-category layer may organize:

```text
horizontal arrows   rules or rewrite processes
vertical arrows     maps of graphs/models/rules
squares              compatible transformations between rewrites
pasting              sequential or contextual composition of rewrite witnesses
```

Keep the DPO existence, dangling, and identification checks as independent proof obligations.

## 13. Relationship to other Universalist mechanics

### Operads and PROPs

```text
operad/PROP
  says which systems or components may be assembled

double category
  says how one kind of assembly/process and another kind of map/change coexist
  and how compatibility squares paste
```

A double operadic theory may use a double category of interfaces/interactions together with modules of systems. Treat this as linked base-composition and two-dimensional-composition packets.

### Freyd categories

Freyd/premonoidal structure owns effect ordering. Do not use double-category interchange to conclude that effectful changes commute. The square/interchange equivalence must preserve the selected effect observations.

### Day convolution

Day convolution lifts a base tensor to indexed descriptions. A double category can itself carry monoidal structure or support description categories, but Day composition and double composition are distinct axes.

### Tambara modules

Dependent Tambara modules can be formulated using actions of double categories and horizontal natural transformations. Use this when context changes indices in two directions. Ordinary Tambara framing remains the smaller choice when one monoidal action suffices.

### Comonadic spatiality

A vertical arrow may change a spatial world while a horizontal arrow represents a locality-sensitive process. Squares must then preserve center, restriction, halo labels, and continuity in addition to ordinary boundaries.

### Pullbacks and pushouts

Spans and cospans obtain horizontal composition from pullbacks and pushouts. The double category records maps and squares around those composites; it does not waive universal-property or effectivity obligations.

### Exact Context

One direction may represent semantic consumers/processes while the other represents context compilation/versioning. A square can certify that a context migration preserves the consumer's required observations. Do not spatialize or double-categorify context unless it changes enforcement or invalidation.

## 14. Universalist theorem-card fit

The `two_dimensional_composition` card should be considered when the typed hole is a `square` on the `two-dimensional-composition` axis.

Required evidence:

```text
two semantically distinct arrow families
horizontal identity/composition
vertical identity/composition
square semantics and edge matching
horizontal and vertical square pasting
interchange or coherent comparison
interpreter/double-functor lowering
effective representation and normalization
material delta over a smaller architecture
```

Universal role:

```text
Every admissible compatible change of a horizontal process
is represented by a square, and every grid of local squares
has a canonical pasted square up to the declared equivalence.
```

Claim scopes:

```text
literal
  explicit double category, compositions, squares, and laws

effective realization
  repository-native arrow/square IR with owner-controlled pasting and tests

bounded approximation
  a finite family of arrow/square cases with an explicit boundary and refinement trigger
```

## 15. Guardrails

1. A commutative square fixture is not automatically a double category.
2. Two unrelated categories are not a double category.
3. A 2-category may be the smaller honest structure.
4. Interchange is not effect commutativity.
5. Pseudo coherence must have an effective normal form or observation policy.
6. A double category of spans/cospans still depends on pullback/pushout existence.
7. Equipment structure requires companions/conjoints or restrictions, not merely strict and loose arrows.
8. A virtual double category may be more honest when horizontal composites are unavailable.
9. Do not introduce a generic framework when one typed square and two narrow composition APIs suffice.
10. Missing square evidence is unresolved, not an obstruction.

## 16. Falsifier catalogue

Use at least one:

```text
a square accepts mismatched boundaries
horizontal pasting loses a required intermediate provenance path
vertical pasting changes a required observation
interchange changes effect trace, authority, failure, or cost
an alleged vertical map cannot act on the horizontal process
an alleged companion/conjoint fails its triangle law
a pseudo composite has no canonical/effective normalization
one arrow family never composes, so an ordinary category/adapter suffices
square invalidation cannot be bounded after boundary changes
```

## 17. Compact architecture recipe

```text
1. Name the two arrow families in repository language.
2. State why each has identity and composition.
3. Define a typed square with all four boundaries.
4. Make edge matching owner-controlled.
5. Implement horizontal and vertical pasting.
6. State the interchange observation/equivalence.
7. Add one interpreter/double-functor lowering.
8. Add one mismatch falsifier and one interchange falsifier.
9. Record pseudo coherence, resource bounds, and invalidation.
10. Stop at one witness seam.
```
