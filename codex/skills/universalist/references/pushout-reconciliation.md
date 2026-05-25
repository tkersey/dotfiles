# Pushout Reconciliation

Use Pushout Reconciliation when multiple systems, teams, agents, or stores have overlapping context that must be merged with explicit overlap semantics.

```text
Context A  <-  Overlap Context  ->  Context B
     \                              /
      \                            /
       ---- Integrated Context ----
```

## Use when

- two source worlds overlap;
- entity identity must be explicit;
- conflicting overlap must be surfaced;
- provenance from each side must survive;
- merging by string similarity would be unsafe.

## Artifacts

```text
OverlapSchema
OverlapInstance
SourceContextA
SourceContextB
IntegratedContext
ConflictReport
ProvenanceManifest
```

## Laws

- overlap identities are explicit;
- non-overlap facts are preserved;
- overlap conflicts are reported or resolved by named policy;
- provenance from both sides survives integration;
- integrated context satisfies target constraints.
