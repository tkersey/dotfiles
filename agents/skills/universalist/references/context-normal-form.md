# Context Normal Form

A system is in Context Normal Form when every significant semantic consumer receives a certified context object rather than raw source data.

## Criteria

1. Every semantic consumer has a task-indexed context schema.
2. Every context is compiled from candidate sources through explicit mappings.
3. Every context satisfies constraints or represents missingness/contradiction.
4. Every evidence-bearing fact has provenance.
5. Every context has freshness and validity metadata.
6. Every context is minimized relative to task observables.
7. Every rendering preserves required observables.
8. Every published context has a Context Certificate.
9. Live operational stores and verified context publication are not confused.

## Anti-patterns

- raw retrieval directly into model/human/policy/workflow input;
- citations added after generation instead of provenance in context;
- stale source data with no validity interval;
- contradictions summarized away;
- semantic consumer pulls directly from mutable operational stores without publication boundary;
- CQL-like verification engine used as hot mutable storage without operational substrate.
