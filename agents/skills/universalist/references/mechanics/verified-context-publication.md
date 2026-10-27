# Verified Context Publication

Verified context publication is the boundary from operational sources to certified context snapshots.

```text
SourceSnapshot -> VerifiedContextSnapshot -> PublishedContext -> SemanticConsumer
```

## Artifacts

- SourceSnapshot
- CanonicalSchema
- ContextInstance
- ConstraintReport
- ProvenanceManifest
- PublishedView
- ContextCertificate

## Laws

- source snapshot stability;
- schema conformance;
- mapping preservation;
- constraint satisfaction or explicit violation;
- provenance for every evidence-bearing fact;
- freshness at publication time;
- rendering preserves observables;
- no raw live-source bypass.
