# Double-Category Architecture Doctrine

## Thesis

Use a double category when a software seam has **two genuinely different kinds of arrows that both compose**, and correctness depends on explicit squares witnessing that the two kinds of change remain compatible.

```text
Processes compose horizontally.
Changes compose vertically.
Squares certify compatibility.
Interchange makes local change compositional.
```

This is not a visual-diagram preference. It is an architecture choice that separates:

```text
what the system does or how components interact
from
how the system, interface, schema, implementation, or context changes
```

and makes compatibility between those directions a first-class boundary artifact.

## Architectural reading

A double category has four kinds of data:

```text
objects
  systems, interfaces, schemas, states, versions, worlds

horizontal arrows
  processes, open systems, generalized connections, queries,
  executable interactions, or boundary-spanning behavior

vertical arrows
  strict maps, refinements, migrations, reindexings, deployments,
  ownership transfers, interface changes, or implementation changes

squares / cells
  certified compatibility between a horizontal behavior before and after
  vertical change
```

A square has the shape:

```text
A ---H---> B
|          |
f    α     g
|          |
v          v
A'--K---> B'
```

The square `α` states that the vertical changes `f` and `g` transport or compare the horizontal behavior `H` with `K` under declared observations, effects, authority, compatibility, and resource policy.

## The architectural capability it adds

Ordinary category-based architecture asks:

```text
How do components or transformations compose?
```

Double-category architecture also asks:

```text
How do architecture changes compose?
How does a local change act on a composed system?
Can separately certified changes be pasted into a certified global change?
Does changing-then-composing agree with composing-then-changing?
```

This creates a **compositional change calculus**. It is useful when a repository repeatedly needs to prove that:

- a migration respects a process or query;
- a refactor preserves boundary behavior across a composite pipeline;
- an interface update transports open-system behavior;
- a schema function and relational/query interpretation remain compatible;
- a local graph/model rewrite composes with surrounding rewrites;
- a strict implementation map induces or restricts a generalized relation, profunctor, span, or cospan;
- dependent context/index changes preserve a contextual capability.

## Selection rule

Select the `two_dimensional_composition` construction card only when repository evidence establishes all of:

```text
1. two arrow families with different architectural meanings;
2. horizontal composition and identities;
3. vertical composition and identities;
4. a square/cell that is more than a boolean assertion;
5. horizontal and vertical square pasting;
6. an interchange or bounded interchange-equivalence law;
7. an effective representation and normalization policy;
8. a material delta over an ordinary pipeline, migration object, or square test.
```

Typical positive signals:

```text
runtime composition plus architecture evolution
process composition plus interface migration
strict maps plus generalized relations/profunctors
open-system composition plus maps of open systems
queries/relations plus functional data maps
local rewrites plus compositional rewrite transport
dependent/index-changing context plus framed capability
```

Prefer a smaller construction when:

- there is only one meaningful arrow family;
- one arrow family never composes;
- a 2-category suffices because both arrow kinds are really the same morphism type;
- a single compatibility-square test is enough and no square pasting matters;
- a typed adapter plus migration test already closes the seam;
- interchange would falsely imply effect commutativity or resource independence;
- the square family cannot be represented or checked effectively.

## Double category versus nearby structures

```text
Category:
  one kind of arrow and one composition.

2-category / bicategory:
  one kind of 1-cell plus transformations between parallel composites.

Double category:
  two distinct kinds of 1-cell plus squares relating their boundaries.

Operad / PROP:
  grammar of component assembly; not by itself a calculus of changes to assemblies.

Freyd / premonoidal category:
  ordered effectful execution; not a second independent change direction.

Pullback / pushout / DPO:
  particular universal constructions or rewrite steps; a double category can
  organize how such steps and their maps compose.

Day convolution:
  composition of indexed descriptions; not composition of changes to those descriptions.

Tambara module:
  a generalized capability stable under context action; dependent Tambara
  theory may use a double-category action, but the two structures are not synonyms.
```

## Strict, pseudo, virtual, and equipment choices

Use the weakest honest variant.

### Strict double category

Use only when horizontal and vertical associativity, units, and interchange are represented literally or by a chosen normal form.

### Pseudo double category

Use when horizontal composition is associative/unital only up to coherent isomorphism, as is common for spans, cospans, profunctors, and open systems. Record the associators, unitors, and normalization observed by software.

### Equipment / framed bicategory

Use when vertical or **tight** maps induce coherent horizontal or **loose** generalized arrows through companions, conjoints, or restrictions. Architecturally this supports lawful base change:

```text
strict map / migration / reindexing
  -> induced generalized boundary behavior
```

Do not claim equipment structure unless the induced proarrows and companion/conjoint laws are represented and useful.

### Virtual double category

Use when generalized horizontal arrows and multi-source cells are meaningful but horizontal composition is unavailable, partial, or too expensive to materialize globally. This is more honest than forcing sentinel composites.

### Monoidal double category

Use when the entire two-dimensional calculus also has a meaningful side-by-side tensor. Do not infer this tensor from the existence of two composition directions.

## Boundary Artifact Contract extension

When double-category structure is selected, add:

```text
Double-category claim:
  strict / pseudo / virtual / equipment / monoidal
Objects:
Horizontal arrow family:
Vertical arrow family:
Horizontal identity/composition owner:
Vertical identity/composition owner:
Square representation:
Square boundary constructor:
Horizontal square pasting:
Vertical square pasting:
Interchange law or observed equivalence:
Interpretation / double-functor lowering:
Companion/conjoint/restriction policy, if applicable:
Canonical square normal form:
Bypass prevention:
Resource bound:
Proof-lease invalidators:
```

The repository-native artifact is usually not a generic `DoubleCategory` class. Prefer a narrow typed IR or module:

```text
Process / Interaction / Query          horizontal arrow
Migration / Refinement / Adapter       vertical arrow
CompatibilitySquare / RewriteWitness   square
composeProcess / composeMigration
pasteHorizontal / pasteVertical
interpret / lower / execute
```

Opaque constructors should ensure that a square's four boundaries match. Public pasting operations should reject or make unrepresentable mismatched edges.

## Core laws

### Horizontal and vertical category laws

```text
idH ;H H == H == H ;H idH
(H ;H K) ;H L == H ;H (K ;H L)

idV ;V f == f == f ;V idV
(f ;V g) ;V h == f ;V (g ;V h)
```

### Square boundary soundness

Every square has matching source and target boundaries. A square with mismatched edges is unrepresentable or rejected by the owner.

### Horizontal and vertical pasting

Pasting produces a square whose external boundary is the composite of the external boundaries. Internal shared edges disappear only through an explicit equality or compatibility witness.

### Interchange

For a grid of compatible squares:

```text
(α pasteH β) pasteV (γ pasteH δ)
  ~=
(α pasteV γ) pasteH (β pasteV δ)
```

The equivalence `~=` is the context's declared equality, normalization, trace observation, or bounded approximation. Do not use interchange to erase effect order, authority, provenance, failure, or cost that remains observable.

### Interpretation / double-functor law

The selected interpreter or lowering preserves:

```text
objects
horizontal identities and composition
vertical identities and composition
squares
horizontal and vertical square pasting
interchange up to the declared coherence
```

### Equipment laws, when claimed

Companions, conjoints, restrictions, and base-change operations must satisfy their unit/counit or triangle-style laws and preserve declared observations.

## Correct-by-construction lowering

Allocate every requirement to the strongest honest locus:

```text
boundary-typed object representation
opaque horizontal/vertical constructors
square constructor with edge matching
pasting API
interpreter/double-functor owner
schema or migration constraint
runtime compatibility check
invalidation monitor
residual obligation
obstruction
```

The smallest effective implementation usually contains only the arrow and square cases needed by the witness seam. Do not create a repository-wide higher-category framework unless several seams share the exact same calculus and laws.

## Material architectural deltas

Double-category structure earns selection only when it changes at least one of:

```text
one explicit owner for process/change compatibility
separation of runtime behavior from architecture evolution
unrepresentability of boundary-mismatched squares
compositional pasting of local change proofs
interchange as an executable refactor/migration law
lawful base change from strict maps to generalized boundaries
preservation of provenance across pasted transformations
incremental invalidation of affected squares
ability to distinguish incompatibility, evidence debt, and obstruction
```

A diagram that merely documents four existing functions is not a material delta.

## Proof lease and invalidation

Double-category evidence becomes stale when any of these change:

```text
horizontal or vertical arrow meaning
identity/composition semantics
square observation or equivalence
normalization/coherence policy
interface/schema versions
migration or refinement rules
effect ordering
resource or failure model
companion/conjoint/base-change assumptions
interpreter/lowering semantics
```

Record which squares must be reconstructed or revalidated when a boundary changes. A useful implementation invalidates only squares whose horizontal or vertical boundaries changed rather than recomputing the entire grid.

## Strong applications

### Compositional refactoring and migration

Horizontal arrows are executable boundary behaviors. Vertical arrows are versions, migrations, or refinements. Squares certify that a local migration preserves behavior. Pasting squares yields a system-level migration witness.

### Open systems

Horizontal arrows are structured or decorated cospans representing systems with interfaces. Vertical arrows map interfaces. Squares map open systems while respecting their feet. A symmetric monoidal double category supports both plugging systems together and placing them side-by-side.

### Functions and relations

Objects are data types or schemas; vertical arrows are functions; horizontal arrows are relations or profunctors; squares are implication/naturality witnesses. This unifies functional transformations with relational queries without pretending relations are functions.

### Graph and model rewriting

DPO rules and rewrite steps remain governed by adhesive and pushout-complement hypotheses. Double-category structure may organize rewrite rules, matches, transformations between rules, and pasting of rewrite witnesses. It does not replace DPO existence checks.

### Dependent context and optics

A double category can act on doubly indexed categories. Dependent Tambara modules can then be horizontal natural transformations. Use this only when context genuinely changes indices and ordinary monoidal action would erase type-level obligations.

## Obstruction conditions

Return unresolved or obstructed rather than inventing a double category when:

- the two arrow families cannot be distinguished semantically;
- square boundaries cannot be checked;
- local squares do not paste;
- interchange fails under required observations;
- pseudo coherence has no effective normal form;
- companion/conjoint base change is claimed but not realizable;
- square enumeration or invalidation exceeds the resource budget;
- the ordinary candidate already provides every required law and owner.

Missing evidence is unresolved. A real obstruction needs a reproducible incompatibility or resource lower bound plus a reopening condition.

## Compact doctrine

```text
Use one category to compose behavior.
Use another to compose change.
Use squares to certify their compatibility.
Use interchange to prove that local change remains compositional.
Lower the result to typed arrows, typed squares, pasting, and one interpreter.
```
