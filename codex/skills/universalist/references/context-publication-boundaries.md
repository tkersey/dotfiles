# Context Publication Boundaries

A Context Publication Boundary is the point where mutable operational sources become stable semantic context for consumers.

```text
Operational Source Snapshot -> Verified Context Snapshot -> Published Context -> Semantic Consumer
```

## Use when

- source data is mutable or heterogeneous;
- consumers need stable, explainable context;
- provenance and freshness matter;
- operational stores should not be queried directly by the semantic consumer;
- the system needs a reviewable context certificate.

## Code/data shape

```text
SourceSnapshot
CanonicalSchema
ContextInstance
ConstraintReport
ProvenanceManifest
PublishedView
ContextCertificate
```

## Laws

- publication derives from a stable source snapshot;
- schema constraints pass or failures are represented;
- all published evidence has provenance;
- freshness requirements hold at publication time;
- rendering preserves required observables;
- semantic consumers read the published context, not raw operational state, unless marked primitive exception.
