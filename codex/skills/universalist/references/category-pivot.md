# Category Pivot / Easy-World Transfer

## Core idea

Universal Architecture should not force every hard operation to remain in the ordinary executable-program world. That world is expressive, but it often hides structure inside functions, callbacks, services, mutable state, prompts, and runtime effects.

Use a **Category Pivot** when another world makes the hard part explicit:

```text
current world -> easy world -> certified interpretation back
```

Slogan:

```text
Do not force a problem to stay in Hask when syntax, semantics, posets, relations, coalgebras, schemas, resources, presheaves, functor categories, or comonadic spaces make the structure explicit.
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

When two spatial worlds compose, Day convolution may lift cartesian/product patch composition to their density-comonadic descriptions. This is a second decision after the spatial worlds and their effective subbases are named.

## Track H protocol

1. Name the current world.
2. Name the hard operation.
3. Name the easy world.
4. Explain what becomes easy there.
5. Define the transfer/encoding into the easy world.
6. Define the interpretation/transport back.
7. State what is forgotten, approximated, quotiented, or intentionally made syntax.
8. Add a preservation law.
9. Add a falsifier.
10. When spatiality is used, add an effective halo/basis representation and a continuity/resource law.
11. When convolution is used, add an index tensor/kernel, decomposition/quotient policy, representable law, and effectivity bound.

## Certificate fields

Use `templates/category-pivot-certificate.md` when the pivot is significant enough to guide code. For comonadic spatiality, attach or reference `templates/mechanics/comonadic-spatiality-report.md`. For Day/promonoidal composition, attach or reference `templates/mechanics/day-convolution-report.md`.

## Guardrail

Do not pivot categories merely to sound profound. A pivot is justified only when it changes code shape, test shape, proof obligation, or the set of possible states/actions/observations.

Do not call a contextual wrapper a comonad, example coverage a basis, or value preservation continuity without center, coherence, reconstruction, halo, and falsifier evidence.

Do not call a nested loop Day convolution without a real index category, tensor/kernel, unit, decomposition law, quotient/normal form, interpreter, and effective implementation. A pointwise product, operadic substitution, monadic sequence, pullback, pushout, or ordinary product may be the honest route.
