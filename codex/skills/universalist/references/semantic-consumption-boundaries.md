# Semantic Consumption Boundaries

A semantic consumption boundary is the point where prepared information is consumed to decide, act, rank, classify, answer, approve, execute, or infer.

## Consumer types

- LLM or model call;
- human reviewer;
- policy engine;
- workflow scheduler;
- agent action selector;
- deployment controller;
- compiler pass;
- ranker/classifier;
- planning engine;
- debugging assistant;
- financial/legal/medical decision support system.

## Boundary law

```text
consume(render(Context(q))) is allowed only if Context(q) is certified for q.
```

## Artifact mapping

| Pressure | Artifact | Proof signal |
| --- | --- | --- |
| raw retrieval enters model | Context Certificate | schema + observable law |
| evidence lacks sources | provenance graph | every claim has source/assumption/missingness path |
| answer depends on current facts | freshness certificate | source versions satisfy validity intervals |
| contradictions are smoothed | contradiction object | incompatible claims survive rendering |
| prompt too large/noisy | observational core | discarded data changes no required observable |
| summary loses distinctions | rendering certificate | rendered packet preserves required observables |
