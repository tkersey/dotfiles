# Repo audit checklist

## Scan

- Locate core domain models, ASTs, schemas, interpreters, adapters, generated code, plugin points, and compatibility facades.
- Identify duplicated semantics or drift.
- Find tests that preserve old behavior across new APIs.

## Model

```text
C:
D:
K:
F:
Candidate direction:
Unit/counit:
Witness object d:
```

## Evaluate

- Does `K` preserve identities and composition in the engineering model?
- Are all old behaviors represented by `F`?
- Does new code factor through one extension path?
- Are old projections coherent?
- Is quotienting/canonicalization explicit?
- Is the abstraction simpler than the duplication it removes?

## Recommend

- Keep: if laws are already encoded and naming improves clarity.
- Refactor: if a central unit/counit adapter would remove drift.
- Downgrade: if plain interfaces are enough.
- Reject: if no meaningful categorical data exists.
