# Pushout Reconciliation

Use pushout-style reconciliation when two or more contexts overlap and must be merged with explicit identity/overlap semantics.

```text
ContextA <- OverlapContext -> ContextB
      \                         /
       \                       /
        IntegratedContext
```

## Recover

- source contexts;
- overlap schema;
- overlap instance / identity correspondences;
- conflict policy;
- target integrated context schema;
- provenance survival policy.

## Laws

- overlap identities are explicit;
- non-overlap facts are preserved;
- conflicts are reported or resolved by named policy;
- provenance from each source survives;
- integrated context satisfies target constraints.
