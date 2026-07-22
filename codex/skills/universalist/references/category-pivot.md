# Category Pivot / Easy-World Transfer

## Core idea

Universal Architecture should not force every hard operation to remain in ordinary executable code, where structure hides inside callbacks, services, mutable state, migrations, wrappers, and effects.

Use a **Category Pivot** when another world makes the hard part explicit:

```text
current world -> easy world -> certified interpretation back
```

Do not force a problem to stay in Hask when syntax, semantics, posets, relations, coalgebras, schemas, resources, presheaves, functor categories, profunctor/Tambara worlds, double categories, or comonadic spaces make the structure explicit. Here `Hask` means ordinary executable-program space, not literal Haskell.

## Common pivots

| Current hard world | Easy world | What becomes easier |
|---|---|---|
| opaque functions / callbacks | syntax / IR | inspect, serialize, replay, validate, authorize, totalize |
| branchy runtime policy | poset / lattice | joins, meets, weakest obligations, capability envelopes |
| mutable state transitions | behavioral coalgebra / trace world | trace laws and behavioral comparison |
| raw data/chunks | schema-shaped context | provenance, constraints, missingness, contradiction, freshness |
| dependency/context soup | comonadic space / labelled halos | locality, restriction, impact, continuity |
| local call-site meanings | presheaf / usage site | overlap checks, gluing, sheafification |
| ad hoc graded loops | functor/presheaf category with Day convolution | decomposition, quotient coherence, multiple interpreters |
| repeated wrappers/residual threading | Tambara/context-action world | one lawful frame operation and representation independence |
| context changes endpoint indices | double-category action / dependent Tambara world | typed index transport without dynamic erasure |
| processes and architecture changes tangled together | double category / equipment | separate compositions, typed compatibility squares, pasting, interchange, and base change |
| functions and relational queries mixed | double category of functions and relations | strict maps and generalized relation semantics coexist |
| partial specs | relation / profunctor world | backward reasoning and generalized mappings |
| generated outputs | Coyoneda payload + path | provenance and lowering laws |

## Indexed-description pivot

Move to a functor or presheaf category when graded families, resource predicates, static plans, weighted behaviors, or local-space descriptions must compose over an explicit index world. Select pointwise, Day, promonoidal, substitutional, or monadic composition from the actual index/dependency semantics. Transport back through an interpreter and do not infer effect commutativity from static structure.

## Contextual-morphism pivot

Move from ad hoc wrappers to:

```text
ambient context world M
source and target actions
P : C^op x D -> V
frame_m : P(a,b) -> P(L(m,a),R(m,b))
```

Candidate artifacts include ordinary/mixed/dependent Tambara modules, optic/residual IRs, free/cofree framing, and representability witnesses. Require unit, nested framing, naturality/coherence, interpretation, effective representation, and a separate effect-order owner.

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

Move to:

```text
Objects
  systems, interfaces, schemas, states, versions

Horizontal arrows
  processes, open systems, relations, queries, interactions

Vertical arrows
  migrations, refinements, strict maps, reindexings, deployments

Squares
  typed compatibility witnesses with explicit four-edge boundaries
```

What becomes easy:

```text
horizontal process composition
vertical change composition
edge-checked square construction
horizontal and vertical square pasting
interchange / compositional local change
multiple double-functor interpretations
incremental square invalidation
```

Use the weakest variant:

```text
strict double category
pseudo double category with explicit coherence/normal form
virtual double category when loose composition is absent/partial
equipment when strict maps induce companions, conjoints, or restrictions
monoidal double category when a side-by-side tensor is independently meaningful
```

Transport back through a narrow repository-native IR:

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

Do not use interchange to infer effect commutativity. Preserve effect order, authority, failure, provenance, schema meaning, and resources. Prefer a category, 2-category, typed adapter plus one witness, PROP, or DPO rewrite when the second arrow family does not independently compose or square pasting is not architecture.

## Comonadic spatial pivot

Use comonadic spatiality when scope, dependency, ownership, evidence, capability, or temporal neighborhoods are semantic. Name points, patch vocabulary, local/global identity, effective halos, restriction, and continuity. Day composition and Tambara framing are separate linked axes. A locality-sensitive process plus a migration of spatial worlds may additionally require a two-dimensional packet whose squares preserve centers, restrictions, labels, and continuity.

## Track H protocol

1. Name the current world and hard operation.
2. Name the easy world and what becomes explicit.
3. Define encoding and interpretation back.
4. State forgotten, approximated, or quotiented structure.
5. Add preservation, effectivity, and falsifier.
6. For spatiality, add halo/basis and continuity/resource laws.
7. For convolution, add index tensor/kernel, quotient, representable law, and resource bound.
8. For Tambara, add context actions, profunctor, framing laws, representability, and effect owner.
9. For double categories, add both arrow families, both category laws, typed square boundaries, both pastings, interchange/coherence, double-functor interpretation, normalization/invalidation, and an effect/resource falsifier.

## Certificate fields

Use `templates/category-pivot-certificate.md`. For double categories, complete its two-dimensional section and the matching section of `templates/composition-certificate.md`; link `references/double-category-architecture.md` and `references/mechanics/double-categories.md`.

## Guardrail

A pivot is justified only when it changes code shape, tests, proof obligation, ownership, composition, or possible states/actions/observations.

Do not call one square, two categories, a PROP diagram, or DPO rewriting a double category. Do not use equipment terminology without companions, conjoints, or restrictions and their laws. Preserve all existing Day, Tambara, spatiality, and ordinary-construction guardrails.
