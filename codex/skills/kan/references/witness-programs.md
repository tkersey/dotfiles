# Witness programs

## Witness: pointwise `Lan`

Use when building a generative/free extension.

Kan data:

- `C`: core operations.
- `D`: extended target operations.
- `K`: inclusion.
- `F`: existing semantics.
- Witness `d`: one new operation.

Code witness:

- enumerate all core paths into `d`;
- construct generated target behavior;
- quotient equivalent paths;
- test unit naturality on one old morphism.

Failure witness: two generated paths yield conflicting behavior for the same old operation.

## Witness: pointwise `Ran`

Use when building a compatibility facade.

Kan data:

- `C`: legacy observations.
- `D`: new model.
- `K`: observation embedding/projection.
- `F`: legacy behavior.
- Witness `d`: one new model object.

Code witness:

- enumerate old observations of `d`;
- build coherent product/record;
- reject inconsistent observations;
- test counit naturality.

Failure witness: old clients observe inconsistent values.

## Witness: codensity

Use when optimizing bind-heavy free structures.

Code witness:

- old direct program;
- lifted codensity program;
- lowered result;
- semantic equality test;
- benchmark.

Failure witness: same result but changed error/resource ordering.

## Witness: schema migration

Use when migrating `v1` to `v2`.

- `S`: v1 schema.
- `T`: v2 schema.
- `K`: schema mapping.
- `I`: source instance.
- Choose `Σ`, `Δ`, or `Π`.
- Test old reports using `Δ` after migration.

Failure witness: quotient merges two rows that business rules require to stay distinct.

## Witness: plugin API

Use when adding third-party extensions.

- `C`: core AST or operation category.
- `D`: plugin-capable AST or operation category.
- `K`: core-to-plugin embedding.
- `F`: old interpreter/exporter.
- `Lan_K F`: generated/default plugin semantics.
- `η`: embed core semantics into plugin semantics.

Test:

```text
for every core node n:
  pluginEval(embed(n)) == coreEval(n)
```

Failure witness: plugin author reimplements core semantics and diverges.
