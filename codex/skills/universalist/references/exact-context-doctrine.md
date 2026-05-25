# Exact Context Doctrine

## Maxim

```text
Allow arbitrary sources. Forbid uncertified semantic consumption.
```

Exact Context Doctrine is the data-readiness layer of Universal Composition. It applies whenever a semantic consumer is about to decide, act, rank, classify, approve, execute, audit, or infer.

A semantic consumer may be a model, human reviewer, policy engine, compiler pass, workflow scheduler, deployment controller, planner, ranker, classifier, BI dashboard, auditor, test harness, action selector, or agent runtime. Agentic systems are a stress test, not the center of the doctrine.

The central artifact is not a prompt or dashboard. It is a task-indexed context instance.

```text
Context(q) = core_Obs(chase(migrate_{M_q}(I_candidate)))
DecisionPacket(q) = render(Context(q))
```

Where:

- `q` is the task/question/decision/action context.
- `I_candidate` is candidate source data.
- `M_q` is the task-specific source-to-context mapping.
- `migrate` moves source data into the task context schema.
- `chase` enforces constraints and deterministic closure.
- `core_Obs` minimizes relative to task observables.
- `render` serializes semantic context for a consumer.

## Doctrine

A semantic consumer should not receive raw source data. It should receive the smallest task-indexed, constraint-satisfying, provenance-preserving, freshness-valid context instance that preserves the observables required for the next decision, action, approval, execution, audit, or inference.

## Plane split

```text
Operational Source Plane
  mutable systems of record, event logs, documents, tools, APIs, live stores

Candidate Plane
  retrieved / observed / extracted candidate source instances

Verified Context Plane
  schemas, mappings, constraints, normalization, reconciliation, provenance

Publication Plane
  stable task-indexed context snapshots and Context Certificates

Rendering Plane
  prompt, report, JSON, dashboard, tool args, policy input, review packet

Semantic Consumption Plane
  consumer decision/action/execution/inference/audit
```

Rule:

```text
Operational stores own mutation.
Verified context planes own semantic publication.
```

## Engineering laws

```text
No semantic consumption without certified context.
No context without a schema.
No schema without observables.
No observables without provenance and freshness.
No rendering without an observable-preservation law.
```

## Retrieval is candidate generation

Retrieval produces candidate material. It does not produce context.

```text
retrieval + mapping + closure + provenance + minimization + rendering = context preparation
```

A chunk is not evidence until it is typed, mapped, provenance-linked, freshness-checked, and placed in a task schema.

## Context versus rendering

```text
semantic context != prompt text
```

The prompt, report, dashboard, JSON payload, tool argument, policy input, deployment packet, or review packet is downstream rendering. Optimize semantic exactness first, then optimize rendering.

## Verified context technology stance

Exact Context Doctrine is implementation-agnostic. CQL/categorical database tooling is a reference architecture for verified context publication when schemas, mappings, constraints, integration, provenance, and canonicalization dominate. It is not automatically the right live operational store.
