# Context Certificates

A Context Certificate certifies that a semantic consumer is receiving the right task-indexed data at the right time.

## Template

```text
Task
  Task:
  Task type:
  Semantic consumer:
  Consumption time:

Context schema
  Schema:
  Required entities:
  Required relations:
  Constraints:

Observables
  Required observables:
  Must preserve:
  May discard:
  Uncertainty to expose:

Source and publication
  Source worlds:
  Operational source plane:
  Candidate retrieval/extraction methods:
  Source snapshot IDs:
  Publication boundary:
  Published context snapshot:
  Source versions:
  Freshness requirements:
  Provenance roots:

Mapping and canonicalization
  Source-to-context mapping:
  Entity resolution rules:
  Evidence extraction rules:
  Join/reconciliation rules:
  Unit/date normalization rules:
  CQL / SQL / Datalog / custom mode:

Constraint closure
  Constraints enforced:
  Missing required fields:
  Contradictions:
  Equalities propagated:
  Unsupported claims:

Observational core
  Data removed:
  Data retained:
  Why retained:
  Minimality criterion:

Provenance manifest
  Context instance ID:
  Source snapshot IDs:
  Mapping/query names:
  Derivation steps:
  Rendered packet hash:

Rendering
  Renderer:
  Token/bandwidth/layout budget:
  Ordering/salience rules:
  Lossy rendering steps:
  Observables preserved by rendering:

Law witnesses
  Schema law:
  Mapping law:
  Constraint law:
  Observable preservation law:
  Provenance path law:
  Freshness law:
  Publication law:
  Rendering law:
  Operational boundary law:

Falsifier
  Missing required context:
  Irrelevant distracting context:
  Stale context:
  Unsupported claim:
  Contradiction collapsed:
  Raw source bypass:
```

## Status values

- **verified**: context schema, observables, provenance, freshness, rendering, and falsifiers are in place.
- **stale**: freshness requirements fail.
- **missing**: required observables cannot be answered, contradicted, or marked unsupported.
- **contradictory**: known incompatible evidence is preserved and surfaced.
- **overfull**: retained data does not affect observables.
- **undercertified**: context exists but lacks provenance, schema, publication, or rendering laws.
- **primitive exception**: a semantic consumer intentionally reads raw source data, and the exception is contained and justified.
