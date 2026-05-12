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
