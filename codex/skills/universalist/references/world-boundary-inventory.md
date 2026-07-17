# World and Boundary Inventory

Use this inventory before Track D. It prevents vague universal-architecture claims by forcing concrete worlds, transformations, and boundary laws.

## World fields

```text
World:
Objects:
Transformations:
Invariants:
Observations:
Primitives:
Composition rules:
Equality/coherence notion:
```

A world is too weak if it has only nouns, no transformations, no equality/coherence notion, no observations, unstable invariants, or no law test.

## Optional spatial-world fields

Fill these only when locality, neighborhoods, scope, dependency, situated context, or local-to-global reconstruction changes correctness.

```text
Points:
Local patches / subbasis:
Local points:
Global points:
Local-to-global map:
Candidate density comonad or practical spatial approximation:
Basis / reconstruction claim:
Representative halo:
Labelled halo fields:
Restriction / germ operation:
Coalgebra / situated-object interpretation:
Underlying topological or categorical shadow, if useful:
Effective representation and resource budget:
```

A dependency list is not automatically a halo; a collection of examples is not automatically a basis; a contextual wrapper is not automatically a comonad. Require code/test consequences and the relevant laws.

## Boundary fields

```text
Boundary:
Kind:
Source world:
Target world:
Preserved:
Forgotten:
Generated:
Observed:
Unknown location:
Candidate artifact:
Law test:
Falsifier:
```

For a locality-sensitive boundary, also record:

```text
Point map:
Source / target halos:
Halo-map direction:
Labels preserved / translated / forgotten / generated:
Coalgebra or context transport:
Continuity / restriction law:
Continuity falsifier:
Ordinary comonad map / continuous map / both / neither:
```

## Boundary kinds

| Boundary kind | Software shape | Usually suggests |
| --- | --- | --- |
| Embedding | old/core included in new/target | transported semantics, `Lan`, `Delta` |
| Projection | internals observed as public behavior | lifted implementation, residual obligations |
| Forgetful map | rich structure erased to raw view | free builder / left-adjoint question |
| Interpreter | syntax/effect/program -> behavior | free syntax, handler, fold |
| Compiler/lowering | source syntax/IR -> target IR/code | transported semantics, generation path |
| Serializer/codec | internal model -> wire/storage | adapter, round-trip/invariant law |
| View/query | model -> report/client view | coherent observations, Yoneda vocabulary |
| Handler | effect syntax -> runtime behavior | effect signature, handler laws |
| Locality-preserving map | points/entities cross while neighborhoods, scopes, dependencies, or contexts must remain valid | comonadic spatiality, labelled halos, continuous-map law |
| Observer | subject -> observation result | Yoneda vocabulary, law-test oracle |
| Migration | old schema/world -> new schema/world | `Delta`, Sigma/Lan, Pi/Ran, provenance path |

## Drift mapping

| Drift | Artifact |
| --- | --- |
| semantic drift | transported semantics / Lan-style artifact |
| observation drift | coherent observations / Ran / Yoneda vocabulary |
| implementation drift | lifted implementation / Freyd diagnostic |
| generation drift | Coyoneda-style generation path vocabulary |
| control-flow drift | defunctionalized explicit IR |
| behavioral drift | behavioral coalgebra / protocol observation law |
| effect drift | effect signature + handler laws |
| locality drift | density-comonadic spatial presentation, effective halo, labelled continuity law |