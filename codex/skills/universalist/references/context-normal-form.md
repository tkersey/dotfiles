# Context Normal Form

A system is in Context Normal Form when every significant semantic consumer receives a certified context object rather than raw source data.

## Normal form criteria

For each semantic consumer:

- task schema is named;
- required observables are named;
- candidate sources and freshness requirements are named;
- source-to-context mapping is explicit;
- deterministic closure/chase steps are applied before consumption;
- provenance paths are structural;
- missingness and contradictions are first-class;
- context is minimized relative to observables;
- rendering declares what it preserves and loses;
- a Context Certificate exists;
- raw retrieval-to-consumer bypasses are removed or justified as primitive exceptions.

## Bypass examples

- raw vector-search chunks directly stuffed into a prompt;
- tool output pasted into a model without schema mapping;
- stale memory used without freshness check;
- human reviewer receives a pile of documents rather than a review context;
- policy engine receives unnormalized input;
- model receives a summary that erases contradictions or sources.

## Target rhythm

```text
task -> schema -> observables -> source candidates -> context compiler -> certificate -> rendering -> semantic consumer
```
