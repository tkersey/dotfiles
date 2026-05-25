# Exact Context Doctrine

## Maxim

```text
Allow arbitrary sources. Forbid uncertified semantic consumption.
```

Exact Context Doctrine is the data-readiness layer of Universal Composition. It applies whenever a model, human, policy engine, workflow, scheduler, agent planner, approval gate, compiler pass, or other semantic consumer is about to decide, act, rank, classify, answer, approve, execute, or infer.

The central artifact is not a prompt. It is a task-indexed context instance.

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
- `render` serializes the semantic context for a consumer.

## Doctrine

A semantic consumer should not receive raw source data. It should receive the smallest task-indexed, constraint-satisfying, provenance-preserving, freshness-valid context instance that preserves the observables required for the next decision, action, or inference.

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

The prompt, report, dashboard, JSON payload, tool argument, or review packet is downstream rendering. Optimize semantic exactness first, then optimize rendering.

## Generalized consumer

Do not over-specialize this doctrine to LLM inference. The general boundary is:

```text
Prepared Context -> Semantic Consumer
```

Semantic consumers include models, humans, policy engines, workflow schedulers, rankers, classifiers, action selectors, deployment controllers, and agent runtimes.
