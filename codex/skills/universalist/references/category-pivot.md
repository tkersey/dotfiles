# Category Pivot / Easy-World Transfer

## Core idea

Universal Architecture should not force every hard operation to remain in the ordinary executable-program world. That world is expressive, but it often hides structure inside functions, callbacks, services, mutable state, prompts, and runtime effects.

Use a **Category Pivot** when another world makes the hard part explicit:

```text
current world -> easy world -> certified interpretation back
```

Slogan:

```text
Do not force a problem to stay in Hask when syntax, semantics, posets, relations, coalgebras, schemas, resources, presheaves, functor categories, profunctor/Tambara worlds, double categories, or comonadic spaces make the structure explicit.
```

Here `Hask` means the ordinary executable-program world of computer science, not literal Haskell.

## Common pivots

| Current hard world | Easy world | What becomes easier |
|---|---|---|
| opaque functions / callbacks | syntax / IR | inspect, serialize, replay, validate, authorize, totalize |
| branchy runtime policy | poset / lattice | joins, meets, weakest obligations, capability envelopes |
| mutable state transitions | behavioral coalgebra / trace world | protocol observations, trace laws, bisimulation-style checks |
| raw text / retrieved chunks | schema-shaped context instance | provenance, constraints, missingness, contradiction, freshness |
| global dependency/context soup | comonadic space / density comonad / labelled halos | locality, nested context, restriction, impact, local/global identity, continuity |
| local call-site meanings | presheaf / usage site | overlap checks, gluing, sheafification |
| ad hoc graded/indexed combination loops | functor / presheaf category with Day convolution | lawful decomposition, quotient coherence, static analysis, multiple interpreters |
| partial resource/interface composition | promonoidal description world | admissibility witnesses, separation, residuals, provenance |
| repeated wrappers/middleware/residual threading around one operation | context-action / Tambara world | one lawful frame operation, mixed endpoint actions, residual optics, representation independence |
| context changes the endpoint type/index | double-category action / dependent Tambara world | typed index transport and dependent framing without dynamic erasure |
| runtime processes and architecture changes are interleaved | double category / equipment | separate process composition, change composition, typed compatibility squares, pasting, interchange, lawful base change |
| functions and relations/queries are conflated | double category of functions and relations | strict functional maps and generalized relational semantics coexist |
| resource/permission logic | resource category / separation model | ownership, disjointness, capability transfer |
| partial/nondeterministic specs | relation / profunctor world | backward reasoning, compatibility, bidirectional views |
| generated outputs | Coyoneda-like payload + path | provenance and lowering laws |

## Indexed-description pivot

Use this pivot when the hard operation is:

```text
combine graded families without duplicated decomposition loops
compose resource predicates over legal splits
inspect a static computation plan before execution
aggregate weighted behaviors over every index decomposition
compose local-space descriptions from patch products
separate pointwise, convolutional, substitutional, and monadic products
```

The easy world is a functor or presheaf category over an explicit index world:

```text
Index world C
  objects/grades/resources/interfaces
  tensor or promonoidal kernel
  unit and admissibility

Descriptions F,G : C -> V
  static/indexed artifacts

Product
  pointwise / Day / promonoidal / substitution / composition
```

The canonical Day route is:

```text
F star G = Lan_tensor(F external-product G)
```

The transport back is an interpreter, handler, evaluator, query, compiler, or renderer. It must be lax monoidal or otherwise satisfy the selected interpretation law.

Do not infer effect commutativity from static/applicative structure. Runtime order remains a Freyd/resource concern.

## Contextual-morphism pivot

Use this pivot when the hard operation is:

```text
reuse one validator/observer/update under many environments
lift a local generalized transformation through tenant/evidence/capability context
centralize repeated product/coproduct residual handling
represent a bidirectional focus with explicit residual context
close a bare capability under every admissible frame
prove one capability behaves coherently for every supported context
separate a generalized relation from a concrete implementation map
preserve typed context when context changes indices
```

Move from ad hoc wrappers and functions to:

```text
Ambient context world M
  tensor/unit or partial/dependent composition

Endpoint actions
  L : M x C -> C
  R : M x D -> D

Generalized boundary capability
  P : C^op x D -> V

Frame operation
  alpha_m : P(a,b) -> P(L(m,a), R(m,b))
```

Candidate artifacts:

```text
ordinary/generalized Tambara module
mixed Tambara module
optic/double/residual IR
free contextual closure
cofree all-context observation
dependent Tambara module
representability/module-functor witness or obstruction
```

The transport back is an interpreter, adapter, handler, optic evaluator, context compiler, or concrete module functor. It must preserve the selected observations under framing.

Required laws:

```text
frame_I ~= id
frame_(m tensor n) ~= frame_m . frame_n
endpoint reindexing commutes with framing
coherent context reindexing preserves observations
interpret(frame_m(p)) == frameSemantics(m, interpret(p))
```

Do not infer effect commutativity, parallelism, duplication, discard, or domain optic laws from Tambara framing. Those remain separate Freyd/resource/domain obligations.

## Two-dimensional architecture pivot

Use this pivot when the hard operation is the interaction between **composition of behavior** and **composition of change**.

Signals:

```text
processes/pipelines/open systems compose
migrations/refinements/interface maps also compose
local compatibility proofs need system-level pasting
functional maps must transport relational/profunctor/query behavior
architecture evolution and runtime behavior are tangled in scripts
```

Move to an explicit double-category world:

```text
Objects
  systems, interfaces, schemas, states, versions

Horizontal arrows
  processes, open systems, generalized relations, queries, interactions

Vertical arrows
  migrations, refinements, strict maps, reindexings, deployments

Squares
  typed compatibility witnesses between a top and bottom horizontal arrow
  with left and right vertical boundaries
```

What becomes easy:

```text
horizontal process composition
vertical change composition
edge-checked square construction
horizontal square pasting
vertical square pasting
interchange / compositional local change
multiple double-functor interpretations
incremental square invalidation
```

Candidate structures:

```text
strict double category
pseudo double category with explicit coherence/normal form
virtual double category when loose composition is absent/partial
equipment/framed bicategory when strict maps induce companions, conjoints, or restrictions
monoidal double category when side-by-side tensor is independently meaningful
```

Transport back through a repository-native IR:

```text
HorizontalArrow
VerticalArrow
CompatibilitySquare
composeH / composeV
pasteH / pasteV
normalizeSquare
interpretSquare
```

Required laws:

```text
both arrow families satisfy identity and associativity
square boundaries match
both pasting operations preserve external boundaries
normalize((a pasteH b) pasteV (c pasteH d))
  ==
normalize((a pasteV c) pasteH (b pasteV d))
interpretation preserves arrows, squares, pasting, and coherence
```

Do not infer effect commutativity from interchange. Preserve effect order, authority, failure, provenance, schema meaning, and resources. Prefer a category, 2-category, typed adapter plus one compatibility witness, PROP, or DPO rewrite when the second arrow family does not independently compose or square pasting is not architecture.

## Comonadic spatial pivot

Use this pivot when the hard operation is:

```text
compute exact local context
preserve scope/dependency/ownership neighborhoods
reason about impact around a point
separate local identity from global identity
reconstruct situated objects from local patches
prove a refactor preserves locality
```

The easy-world artifacts are:

```text
points
patch vocabulary / subbasis
density comonad or effective approximation
coalgebras / situated objects
halos and labelled halos
germs and restriction
continuous locality-preserving maps
```

The transport-back law must state what locality is preserved in executable code. A plain graph is preferable if it already makes the required operation exact.

When two spatial worlds compose, Day convolution may lift product patch composition to their density-comonadic descriptions. When a local transformation must survive context extension, Tambara may be a separate linked axis. When a locality-sensitive process and a spatial migration both compose, a double-category square may additionally preserve centers, restrictions, labels, and continuity.

## Track H protocol

1. Name the current world.
2. Name the hard operation.
3. Name the easy world.
4. Explain what becomes easy there.
5. Define the transfer/encoding into the easy world.
6. Define interpretation/transport back.
7. State what is forgotten, approximated, quotiented, or made syntax.
8. Add preservation law and falsifier.
9. When spatiality is used, add effective halo/basis and continuity/resource law.
10. When convolution is used, add index tensor/kernel, decomposition/quotient policy, representable law, and effectivity bound.
11. When Tambara is used, add ambient and endpoint actions, profunctor, frame, laws, representability, and effect/resource owner.
12. When double categories are used, add both arrow families and laws, typed square boundaries, both pastings, interchange/coherence, double-functor interpretation, normalization/invalidation, and an effect/resource falsifier.

## Certificate fields

Use `templates/category-pivot-certificate.md`. For spatiality attach the spatial report; for Day attach the Day report; for Tambara attach the Tambara report. For double categories complete the two-dimensional sections of the Category Pivot and Composition Certificates and link the double-category doctrine/mechanics.

## Guardrail

Do not pivot categories merely to sound profound. A pivot is justified only when it changes code shape, test shape, proof obligation, ownership, composition, or possible states/actions/observations.

Do not call a contextual wrapper a comonad, example coverage a basis, a nested loop Day convolution, a Reader parameter Tambara, or one commuting square a double category without the corresponding structure, laws, effective lowering, and falsifier. Use equipment terminology only with companions, conjoints, or restrictions and their laws.
