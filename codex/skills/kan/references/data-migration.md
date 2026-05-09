# Data migration

For a schema map `K : S -> T`:

- `Δ_K`: restrict a target instance back to source schema by precomposition.
- `Σ_K = Lan_K`: push source data forward, merging/quotienting along target paths.
- `Π_K = Ran_K`: construct conservative/coherent target data by matching all observations.

Sources: `[KAN-SPIVAK-WISNESKY-FQL-2014]`, `[KAN-SCHULTZ-WISNESKY-AQL-2015]`.

Lift-shaped view update:

```text
source states B --P--> views C
required view change F : A -> C
unknown source-side update A -> B
```

Use lift and no-exact-lift reports when a view update asks for information not present in source state.
