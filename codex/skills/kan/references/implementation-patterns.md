# Implementation patterns

## Finite `Lan`

Represent generated target values as:

```text
Generated = (source c, path Kc -> d, payload F(c)) / equations
```

Use union-find or canonicalization for quotients.

## Finite `Ran`

Represent target views as coherent records:

```text
ObservationFamily = { (c, u : d -> Kc) -> F(c) } satisfying equations
```

Use validators for partial/inconsistent observations.

## Defunctionalized boundary IR

Replace boundary functions with:

```text
data Case = ...payloads...
interpret : Case -> Meaning
```

Use for paths, observations, requirements, continuations, handlers, and projection realizers.

## Freyd/free-builder boundary

For lift-shaped refactors:

```text
RequiredBehavior -> Free -> ImplementationPlan -> P -> ObservableBehavior
```

Add projection tests before moving modules.

## Yoneda/Coyoneda

- Yoneda pass: centralize observations.
- Coyoneda pass: keep raw payload plus deferred path until lowering.

Sources: `[KAN-MILEWSKI-2017]`, `[KAN-HASKELL-KAN-EXTENSIONS]`, `[KAN-HASKELL-YONEDA]`, `[KAN-HASKELL-COYONEDA]`.
