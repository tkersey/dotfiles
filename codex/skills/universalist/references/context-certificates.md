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

Source instance
  Source worlds:
  Candidate retrieval methods:
  Source versions:
  Freshness requirements:
  Provenance roots:

Mapping
  Source-to-context mapping:
  Entity resolution rules:
  Evidence extraction rules:
  Join rules:
  Unit/date normalization rules:

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

Rendering
  Renderer:
  Token/bandwidth/layout budget:
  Ordering/salience rules:
  Lossy rendering steps:
  Observables preserved by rendering:

Law witnesses
  Schema law:
  Observable preservation law:
  Provenance path law:
  Freshness law:
  Missingness/contradiction law:
  Rendering law:

Falsifier
  Missing required context:
  Irrelevant distracting context:
  Stale context:
  Unsupported claim:
```

## Status values

- **verified**: context schema, observables, provenance, freshness, rendering, and falsifiers are in place.
- **stale**: freshness requirements fail.
- **missing**: required observables cannot be answered, contradicted, or marked unsupported.
- **contradictory**: known incompatible evidence is preserved and surfaced.
- **overfull**: retained data does not affect observables.
- **undercertified**: context exists but lacks provenance, schema, or rendering laws.
