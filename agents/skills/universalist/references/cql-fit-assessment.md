# CQL / Categorical Database Fit Assessment

CQL-like categorical database tooling is a candidate implementation for the Verified Context Plane. Use it when the hard problem is verified canonicalization, integration, constraints, and provenance—not when the hard problem is live mutable serving.

## Use CQL-like tooling when

- schemas are explicit or can be made explicit;
- source-to-target mappings are central;
- context must be canonicalized across heterogeneous systems;
- constraints/invariants must be checked before consumption;
- provenance/lineage matters;
- schema evolution matters;
- context snapshots can be materialized;
- batch/warm-path publication is acceptable;
- mappings and queries are stable enough to encode.

## Do not use as primary substrate when

- sub-second online mutation is central;
- distributed multi-writer access is central;
- row-level authorization is dynamic and primary;
- context is mostly unstructured and schema is unstable;
- low-latency streaming is primary;
- a simple SQL, Datalog, or materialized-view approach suffices.

## Placement rule

```text
Use CQL as verified canonicalization, integration, and provenance layer around live context stores—not as the default live memory substrate.
```

## Fit outputs

- recommended mode: lightweight / SQL / Datalog / CQL / hybrid;
- operational substrate;
- verified context plane technology;
- publication frequency;
- provenance strategy;
- constraints to prove/check;
- risks and non-fit reasons.
