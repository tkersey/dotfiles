# CQL Context Management

CQL/categorical database tooling is useful for verified context publication when typed schemas, mappings, constraints, integration, colimits/pushouts, and provenance matter.

## Use CQL-like tooling for

- canonical context schemas;
- source-to-context mappings;
- verified migrations and queries;
- constraint/integrity checking;
- provenance-bearing derived rows/facts;
- schema evolution;
- multi-source integration;
- pushout/colimit reconciliation.

## Do not overuse for

- primary live mutable memory;
- low-latency multi-writer stores;
- streaming-first systems;
- row-level dynamic authorization as the main workload;
- unstable unstructured sources with no durable task schema.

## CQL placement principle

```text
Use CQL as the verified canonicalization, integration, and provenance layer around live context stores, not as the default online memory substrate.
```

## Report sections

1. source schemas and instances;
2. target context schema;
3. typeside/entities/attributes/foreign keys/equations;
4. mappings and queries;
5. `Delta`/`Sigma`/`Pi` usage, with `Pi` caution;
6. constraints and chase/validation;
7. colimits/pushouts for reconciliation;
8. provenance and lineage;
9. operational-store pairing;
10. snapshot publication boundary;
11. context certificate;
12. falsifiers and non-fit risks.
