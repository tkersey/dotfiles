# Kan Lifts

Use Kan lifts when the unknown lives behind a fixed projection `P : B -> C0`.

## Realization

```text
F(a) -> P(realizer(a))
```

Software law:

```text
project(realize(case)) == required(case)
```

or a named covering/refinement relation.

## Residual obligation

```text
P(obligation(a)) -> F(a)
```

Software law:

```text
satisfying obligations makes projection able to satisfy required behavior
missing obligation fails
```

## No exact lift

Report no exact lift when `P` forgets evidence needed by `F`, `B` lacks internal structure, templates are unbounded, or required observations are impossible.
