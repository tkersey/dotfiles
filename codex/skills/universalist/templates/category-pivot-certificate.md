# Category Pivot Certificate

## Current world

- Representation/category:
- Hard operation:
- Why hard here:

## Easy world

- Representation/category:
- What becomes easy:

## Transfer

- Encode / abstract / reify:
- Interpret / concretize / observe:
- Forgotten or approximated structure:
- Quotiented presentation distinctions:

## Spatial transfer, when applicable

- Points:
- Local patches / subbasis:
- Basis or explicit non-basis:
- Local/global identity map:
- Effective halo representation:
- Labelled-halo fields:
- Restriction / germ operation:
- Point map:
- Coalgebra/context transport:
- Halo-map direction:
- Continuous map / comonad map / both / neither:
- Resource and invalidation budget:

## Description composition, when applicable

- Index category/world:
- Index tensor or promonoidal kernel:
- Unit:
- Indexed description family:
- Selected product: pointwise / Day / promonoidal / substitution / endofunctor composition
- Nearby product rejected:
- Legal decomposition witnesses:
- Coend/reindexing equivalence:
- Atomic/representable embedding:
- Executable representation:
- Enumeration/normalization strategy:
- Lax-monoidal interpreter:
- Residual/internal hom, if any:
- Effect-order restrictions:
- Complexity/resource bound:

## Context action / Tambara structure, when applicable

- Ambient context category/world:
- Tensor/unit/partiality/dependence:
- Source endpoint world and action:
- Target endpoint world and action:
- Underlying profunctor/generalized capability:
- Tambara form: ordinary / mixed / two-sided / dependent
- Frame operation:
- Unit law:
- Associativity/nested-framing law:
- Endpoint naturality:
- Context reindexing/coherence:
- Interpretation/framing law:
- Residual/optic IR, if any:
- Residual quotient/normal form:
- Free/cofree contextual closure, if any:
- Context basis/enumeration/query:
- Representability status:
- Concrete realizer/right-adjoint witness:
- Effect-order owner/restrictions:
- Effective representation/resource bound:

## Operation performed in easy world

- Operation:
- Result artifact:

## Preservation law

```text
<required observation after transport> == <expected observation>
```

Spatial law, if used:

```text
<required source halo and labels transported to target>
  satisfy
<target locality and restriction requirements>
```

Description-composition law, if used:

```text
interpret(F star G)
  ==
combine(interpret(F), interpret(G))
```

and:

```text
represent(a) star represent(b)
  ~=
represent(a tensor b)
```

Context-framing law, if used:

```text
frame_I(p) ~= p
frame_(m tensor n)(p) ~= frame_m(frame_n(p))
interpret(frame_m(p)) == frameSemantics(m, interpret(p))
```

## Falsifier

- Case where the easy-world result fails after transport back:
- Point preserved but locality lost:
- Example coverage mistaken for basis density:
- Halo approximation omits an observation-changing dependency:
- Illegal decomposition admitted:
- Legal decomposition omitted:
- Semantic collision under quotient:
- Static description used to justify unsafe effect reordering:
- No real context action exists:
- Identity context changes the capability:
- Nested framing depends on grouping:
- Endpoint reindexing and framing disagree:
- Residual identity leaks into observations:
- Tambara framing used to justify unsafe effect reordering:
- Claimed representable module has no realizer:
- Equivariant Tambara terminology confused with profunctor Tambara module:
- Smaller product/adapter/profunctor/context parameter already suffices:

## Status

planned / implemented / verified / approximated / obstructed / primitive exception
