# Verified Context Plane

A Verified Context Plane transforms heterogeneous, mutable, operational source data into certified, schema-shaped, provenance-bearing context instances suitable for semantic consumption.

## Plane stack

```text
Operational Source Plane
  SQL DBs, event logs, graph stores, CRDTs, object stores, tools, documents, APIs

Candidate Plane
  candidate source instances from retrieval, extraction, sampling, snapshots, or tools

Verified Context Plane
  schema mappings, constraints, chase/closure, provenance, entity resolution, reconciliation

Publication Plane
  verified context snapshots, context certificates, freshness metadata

Rendering Plane
  prompt/report/JSON/dashboard/tool args/policy input

Semantic Consumption Plane
  model, human, policy engine, workflow scheduler, compiler pass, deployment controller, auditor
```

## Principle

```text
Operational stores own mutation.
Verified context planes own semantic publication.
```

Use operational stores for live writes, transactions, authorization, streaming, and low-latency serving. Use the verified context plane for canonicalization, integration, constraints, provenance, reconciliation, and publication.

## Strong fit

- heterogeneous structured sources;
- explicit schemas and mappings;
- cross-source consistency;
- provenance and lineage;
- context snapshots;
- task-indexed views;
- auditability and explanation;
- stable publication boundaries.

## Weak fit

- primary low-latency mutable memory;
- multi-writer distributed online writes;
- row-level dynamic authorization as a primary mechanism;
- streaming-first semantics;
- unstable schemas with no durable observables.
