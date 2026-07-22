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

A strict double category can be presented as a category internal to `Cat`. Concretely it contains:

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

The symbols are mnemonic; a repository may choose the opposite orientation. What matters is that the arrow kinds have different meaning and independent composition.

### Horizontal and vertical composition

```text
A ---H---> B ---J---> C       H ;H J : A => C
A --f--> A' --g--> A''        f ;V g : A -> A''
```

### Square pasting

Squares paste horizontally when adjacent vertical edges match and vertically when adjacent horizontal edges match.

### Interchange

For a compatible 2x2 grid:

```text
(α pasteH β) pasteV (γ pasteH δ)
  =
(α pasteV γ) pasteH (β pasteV δ)
```

in a strict double category. In a pseudo implementation it may hold up to a declared coherent isomorphism or normalization.

Interchange is the central architectural gain: local compatibility witnesses assemble in either dimension without changing the resulting global witness under sanctioned observations.

## 2. Strict versus pseudo

Many important examples are pseudo double categories. Spans, cospans, and profunctors compose through pullbacks, pushouts, or coends and are often associative only up to canonical isomorphism.

Use:

```text
strict
  when identities, composition, and interchange are literal or normalized

pseudo
  when associativity/unit laws hold through explicit coherent isomorphisms
```

A software realization may implement pseudo coherence through:

```text
compose -> normalize -> compare by sanctioned observations
```

Do not claim strictness because a few fixtures happen to compare equal.

## 3. Double category versus 2-category

A 2-category has one kind of 1-cell and 2-cells between parallel 1-cell composites. A double category has two distinct kinds of 1-cell and squares with one kind on the horizontal boundary and the other on the vertical boundary.

Use a 2-category or bicategory when the two proposed arrow families are really one morphism type seen at different levels. Use a double category when the distinction is architectural:

```text
functors versus profunctors
functions versus relations
interface maps versus open systems
migrations versus executable processes
refinements versus simulations
```

Horizontal and vertical 2-category shadows forget the full two-direction interaction.

## 4. Canonical examples

### Categories, functors, profunctors, transformations

The double category `Prof` has:

```text
objects             categories
vertical arrows     functors
horizontal arrows   profunctors
squares              natural transformations with functorial boundaries
```

This is an equipment: strict maps can induce generalized proarrows through companions and conjoints, and profunctors can be restricted along functors.

### Sets, functions, relations, implications

```text
objects             sets / data types
vertical arrows     functions
horizontal arrows   relations
squares              implication or relation-preservation witnesses
```

This keeps functional transformation and relational/query semantics together without pretending relations are functions.

### Spans

```text
objects             objects of C
vertical arrows     maps in C
horizontal arrows   spans
squares              maps of spans
```

Horizontal composition uses pullback. Pseudo coherence records canonical comparison among chosen pullbacks.

### Cospans and structured cospans

```text
objects             interfaces
vertical arrows     interface maps
horizontal arrows   open systems / structured cospans
squares              maps of open systems
```

Horizontal composition uses pushout to glue interfaces. Symmetric monoidal double categories of structured or decorated cospans model open circuits, Petri nets, Markov processes, dynamical systems, and other open systems.

## 5. Squares as architectural evidence

A square should not be stored as `bool compatible` when architecture needs to know why compatibility holds.

A repository-native square may carry:

```text
source horizontal arrow id
left and right vertical boundary ids
target horizontal arrow id
mapping or rewrite witness
observation-preservation evidence
provenance
resource/cost delta
normalization/coherence token
proof-lease context id
```

The square constructor owns boundary matching. The interpreter owns semantic comparison.

Examples:

```text
API migration square
schema/query transport square
refactor-preservation square
open-system map square
rewrite-compatibility square
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

Make edge mismatch unrepresentable in a strongly typed host or return one structured mismatch in a weaker host. Do not begin with a generic higher-category library; implement one horizontal family, one vertical family, and one square family for the witness seam.

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

`makeSquare(top,left,right,bottom,witness)` succeeds only if every corner and shared boundary matches under the declared identity/equivalence policy.

### Pasting laws

Horizontal pasting requires the right boundary of the left square to match the left boundary of the right square. Vertical pasting requires the bottom boundary of the upper square to match the top boundary of the lower square. Composite squares expose the external boundary and retain internal provenance when observable.

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

under sanctioned observations.

A falsifier should include a grid where one order changes:

```text
effect trace
authority
failure mode
provenance
resource cost
schema meaning
```

If that difference is required, strict interchange is invalid; use a weaker or ordered structure, split the axis, or return obstruction.

### Interpreter / double-functor law

For interpreter `F`:

```text
F(composeH(H,J)) ~= composeH(F(H),F(J))
F(composeV(f,g)) ~= composeV(F(f),F(g))
F(pasteH(alpha,beta)) ~= pasteH(F(alpha),F(beta))
F(pasteV(alpha,gamma)) ~= pasteV(F(alpha),F(gamma))
```

with identities and coherence preserved.

## 8. Equipments, companions, and conjoints

A proarrow equipment distinguishes:

```text
tight / vertical arrows
  strict maps, adapters, migrations, reindexings

loose / horizontal arrows
  spans, profunctors, relations, open systems, generalized boundaries
```

A tight map may have a companion in the same direction and a conjoint in the opposite direction. These support restrictions/base change of loose arrows along strict maps.

Architectural use:

```text
schema map       -> restrict/transport a relational query
interface map    -> reindex an open system
representation map -> transport a generalized boundary capability
```

Record which strict maps admit companions/conjoints, their construction APIs, unit/counit or triangle witnesses, base-change law, resource cost, and failure case. If only some maps support base change, expose a partial or capability-indexed equipment.

## 9. Virtual and monoidal variants

Use a virtual double category when generalized horizontal arrows or multi-source cells are meaningful but horizontal composition is unavailable, partial, or too expensive to materialize. Do not totalize with invalid sentinels.

Use a monoidal double category only when the two-dimensional calculus also has a genuine side-by-side tensor compatible with both arrow directions and squares. This tensor is independent from horizontal composition.

## 10. Open-system architecture

A structured cospan has the form:

```text
L(input) -> system <- L(output)
```

Horizontal composition glues output and input interfaces by pushout. Vertical arrows change interfaces. Squares map internal systems while respecting both interface legs.

Repository reading:

```text
object              interface/schema/port set
horizontal arrow    service/process/network with exposed boundary
vertical arrow      interface migration or renaming
square              implementation/system map compatible with interface changes
```

A monoidal product may place systems side-by-side. Do not confuse that tensor with horizontal composition through connected interfaces.

## 11. Knowledge and database semantics

A double category of functions and relations can preserve both functional data transformations and relational query semantics. A double functor can interpret a syntactic knowledge/schema world into this semantic world. Squares witness that a functional map preserves or transports a relation/query.

Universalist implications:

- do not force a relation into a partial function;
- do not hide query transport in mapper code;
- make function/relation compatibility a square;
- preserve provenance and schema version on the square boundary;
- invalidate affected query squares when a schema map or relation changes.

## 12. Rewriting and DPO mechanics

A double category is not double-pushout rewriting. DPO rewriting requires a rule `L <- K -> R`, a match, a pushout complement, and adhesive or adhesive-like hypotheses.

A double-category layer may organize rules or rewrite processes as horizontal arrows, graph/model maps as vertical arrows, compatible transformations between rewrites as squares, and pasting of rewrite witnesses. Keep DPO existence, dangling, and identification checks as separate obligations.

## 13. Relationship to other Universalist mechanics

```text
operad / PROP
  legal assembly grammar

double category
  compatibility between process composition and change composition

Freyd category
  ordered effectful runtime; interchange does not prove commutativity

Day convolution
  composition of indexed descriptions, not changes to descriptions

Tambara module
  profunctor stable under context action; dependent Tambara may use a double-category action

comonadic spatiality
  local neighborhoods; a square may additionally preserve center, restriction, labels, and continuity

pullbacks / pushouts
  often build span/cospan composites; the double category organizes maps and squares around them
```

## 14. Theorem-card fit

Consider `two_dimensional_composition` when the typed hole is `square` on axis `two-dimensional-composition`.

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
Every admissible compatible change of a horizontal process is represented by a square,
and every compatible grid of local squares has a canonical pasted square up to
observational equivalence.
```

Claim scopes:

```text
literal
  explicit double category, squares, compositions, and laws

effective realization
  repository-native arrow/square IR with owner-controlled pasting and tests

bounded approximation
  finite arrow/square cases with explicit boundary and refinement trigger
```

## 15. Guardrails

1. A commutative square fixture is not automatically a double category.
2. Two unrelated categories are not a double category.
3. A 2-category may be the smaller honest structure.
4. Interchange is not effect commutativity.
5. Pseudo coherence needs an effective normal form or observation policy.
6. Spans/cospans still depend on pullback/pushout existence.
7. Equipment requires companions/conjoints or restrictions.
8. A virtual double category may be more honest when horizontal composites are unavailable.
9. Do not introduce a generic framework when one typed square and two narrow composition APIs suffice.
10. Missing square evidence is unresolved, not obstruction.

## 16. Falsifier catalogue

Use at least one:

```text
a square accepts mismatched boundaries
horizontal pasting loses required provenance
vertical pasting changes a required observation
interchange changes effect trace, authority, failure, or cost
an alleged vertical map cannot act on the horizontal process
an alleged companion/conjoint fails its triangle law
a pseudo composite has no canonical/effective normalization
one arrow family never composes, so an ordinary category/adapter suffices
square invalidation cannot be bounded after boundary changes
```

## 17. Compact recipe

```text
1. Name the two arrow families in repository language.
2. State why each has identity and composition.
3. Define a typed square with all four boundaries.
4. Make edge matching owner-controlled.
5. Implement horizontal and vertical pasting.
6. State the interchange observation/equivalence.
7. Add one double-functor lowering.
8. Add mismatch and interchange falsifiers.
9. Record pseudo coherence, resources, and invalidation.
10. Stop at one witness seam.
```
