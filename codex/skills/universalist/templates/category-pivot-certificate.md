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

## Falsifier

- Case where the easy-world result fails after transport back:
- Point preserved but locality lost:
- Example coverage mistaken for basis density:
- Halo approximation omits an observation-changing dependency:
- Illegal decomposition admitted:
- Legal decomposition omitted:
- Semantic collision under quotient:
- Static description used to justify unsafe effect reordering:
- Smaller product already suffices:

## Status

planned / implemented / verified / approximated / obstructed / primitive exception
