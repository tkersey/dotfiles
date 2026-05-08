# Kan lift law tests

## Test taxonomy

| Law | Mathematical form | Software approximation |
|---|---|---|
| Left-lift unit naturality | `P(Lh) · η_a = η_a' · Fh` | synthesized implementation preserves required behavior across feature morphisms |
| Right-lift counit naturality | `Fh · ε_a = ε_a' · P(Rh)` | residual obligations remain sound across feature morphisms |
| Left-lift factorization | `α = (P·α#) · η` | every realization of the public contract factors through the central synthesized implementation interface |
| Right-lift factorization | `β = ε · (P·β#)` | every sound implementation obligation factors through the central residual interface |
| Poset left-lift minimality | no smaller implementation covers desired behavior | prevent over-engineered or duplicate realization paths |
| Poset right-lift maximality | no larger implementation remains sound | prevent missing obligations or unsound approximations |
| Projection centrality | all public behavior is observed through `P` | no bypass around the boundary being lifted through |

## Minimal left-lift test

Given `h : a -> a'`, desired behavior `F`, projection `P`, synthesized implementation `L`, and unit `η : F -> P·L`, assert:

```text
P(L(h))(eta(a, x)) == eta(a', F(h)(x))
```

Software reading: changing or refining the requirement before synthesis gives the same observable behavior as synthesizing first and then projecting through the boundary.

## Minimal right-lift test

Given `h : a -> a'`, residual implementation `R`, projection `P`, and counit `ε : P·R -> F`, assert:

```text
F(h)(epsilon(a, projected)) == epsilon(a', P(R(h))(projected))
```

Software reading: residual obligations remain sound when the requirement/test/workflow moves along its own structure.

## Poset left-lift test

For each witness `a`:

```text
desired(a) <= project(left_lift(a))
forall b < left_lift(a): not (desired(a) <= project(b))
```

## Poset right-lift test

For each witness `a`:

```text
project(right_lift(a)) <= desired(a)
forall b > right_lift(a): not (project(b) <= desired(a))
```

## Factorization test strategy

For `Lft`:

1. Define a sample implementation candidate `G : A -> B`.
2. Define a public realization witness `α : F -> P·G`.
3. Implement the induced map `α# : Lft_P F -> G`.
4. Assert `α == (P·α#)·η` on the witness slice.
5. Assert no public realization bypasses `α#`.

For `Rft`:

1. Define a sample implementation candidate `G : A -> B`.
2. Define a soundness witness `β : P·G -> F`.
3. Implement the induced map `β# : G -> Rft_P F`.
4. Assert `β == ε·(P·β#)` on the witness slice.
5. Assert no obligation check bypasses `β#`.

## Failure interpretation

- Unit naturality failure: synthesized implementation does not preserve the structure of requirements.
- Counit naturality failure: residual obligations are not sound across the requirement structure.
- Factorization failure: there is an ungoverned implementation or obligation path.
- Minimality failure: the left lift overbuilds or duplicates implementation paths.
- Maximality failure: the right lift is unnecessarily weak or misses permitted obligations.
- Projection centrality failure: the chosen `P` is not the real architectural boundary.
