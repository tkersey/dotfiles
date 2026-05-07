# Functorial data migration

## Model

A database schema can be modeled as a category, and an instance on a schema can be modeled as a set-valued functor. A schema mapping is a functor:

```text
K : S -> T
```

between source schema `S` and target schema `T`.

The three standard migration operations are:

```text
Σ_K ⊣ Δ_K ⊣ Π_K
```

where:

- `Δ_K` is restriction/precomposition along `K`;
- `Σ_K` is left Kan extension along `K`;
- `Π_K` is right Kan extension along `K`.

Sources: `[KAN-SPIVAK-WISNESKY-FQL-2014]`, `[KAN-SCHULTZ-WISNESKY-AQL-2015]`, `[KAN-RIEHL-CTIC]`.

## Engineering reading

### `Δ_K` restriction

Use to view a target database as if it were a source database. Good for backward compatibility checks, old reports over new schema, and verifying that migration preserves old columns/relationships.

### `Σ_K` left migration

Push source data forward into the target schema. The pointwise colimit means:

- create target rows from all source rows mapping into that target table;
- identify rows when source paths force them to be equal;
- generate foreign keys/relationships by functorial action.

Good for generative migrations, denormalization where collisions are intentional, and materializing new tables from old data.

Watch out for quotient collisions, accidental merging, dangling relationships, and losing provenance.

### `Π_K` right migration

Push source data forward by coherent families of observations. The pointwise limit means:

- create target rows as compatible tuples of source rows/observations;
- reject or flag incompatible combinations;
- preserve constraints by construction.

Good for conservative migrations, compatibility facades, derived read models, and constraint-heavy target schemas.

Watch out for combinatorial explosion, empty result sets from overconstraint, and confusing semantics for product-like rows.

## Migration law tests

For a migration `K : S -> T`:

- `Δ_K(target)` should match the old source view.
- `η : I -> Δ_K Σ_K I` should preserve old source data up to intended quotienting.
- `ε : Δ_K Π_K I -> I` should project coherent target-like data back to source behavior.
- Round-trip tests must state whether equality is strict, up to quotient, or only observational.

## Practical migration memo

```text
Source schema S:
Target schema T:
Schema mapping K:
Instance functor I:
Operation: Δ / Σ / Π
Tables affected:
Paths that create quotienting or matching:
Unit/counit compatibility:
Lossy fields:
Provenance strategy:
Rollback strategy:
Law tests:
```
