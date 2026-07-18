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

## Context as a germ

When locality changes correctness, refine Exact Context with Comonadic Spatiality:

```text
task / semantic consumer q = a point
relevant local structure   = Halo(q)
prepared Context(q)        = a certified section or germ over an effective halo
rendering                  = a consumer-specific presentation of that germ
```

This changes the preparation question from:

```text
Which globally retrieved facts should be trimmed?
```

to:

```text
Which local patch around q supports the required observations,
and how does validity survive restriction and boundary transport?
```

Spatial context is optional. Use it when scope, dependency, ownership, capability, evidence, provenance, or temporal neighborhoods are semantic. A plain context schema remains sufficient when no locality law changes implementation.

Spatial fields:

```text
task point
spatial world
patch vocabulary / subbasis
effective basis or explicit non-basis
halo approximation and budget
local points / global point / identification map
restriction and germ rules
labelled-halo schema
continuity law across compilation, publication, and rendering
```

Guardrails:

- retrieval output is not automatically the halo;
- a dependency list is not automatically a comonadic neighborhood;
- local identity must not be collapsed into global identity before provenance is recorded;
- a context boundary preserving facts may still be discontinuous if it loses their validity neighborhood;
- formal/infinite halos require a finite or effective approximation and resource law.

## Requirement-indexed convolution

Use Day or promonoidal convolution only when context requirements themselves form a real composition world:

```text
(Requirement, tensor, UnitRequirement)
ContextFragment : Requirement -> ContextData
```

Then:

```text
(ContextA star ContextB)(r)
```

ranges over lawful decompositions:

```text
r1 tensor r2 -> r
```

or over an explicit partial/relational kernel:

```text
ComposeRequirement(r1,r2;r)
```

This may support:

- combining independently justified context fragments;
- capability- or policy-indexed context;
- context assembled over decomposed task obligations;
- static context plans with execution, cost, provenance, and rendering interpreters;
- residual questions such as which additional context would suffice for a requirement.

A closed/residuated description world may express:

```text
KnownContext star MissingContext <= RequiredContext
```

as a residual-obligation query. This is an architecture inference, not a default retrieval formula.

Required fields:

```text
requirement index world
tensor or promonoidal kernel
unit requirement
context fragment family
legal decomposition witnesses
coend/normalization policy
schema/provenance merge semantics
residual, if claimed
effective enumeration and resource bound
```

Guardrails:

- context concatenation is not Day convolution;
- evidence union/deduplication is not Day convolution;
- shared-key agreement is usually a pullback;
- overlap reconciliation is usually a pushout;
- requirement-independent context combination is usually an ordinary or pointwise product;
- a legal context decomposition does not waive schema, constraint, provenance, freshness, missingness, contradiction, germ, or rendering laws.

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

When spatial locality is claimed, add:

```text
No context germ without a named point and effective halo.
No halo without restriction and coherence laws.
No locality-sensitive boundary without a continuity falsifier.
```

When requirement-indexed convolution is claimed, add:

```text
No context convolution without a requirement tensor/kernel.
No composite fragment without a legal decomposition witness.
No quotient without a provenance/collision policy.
No residual without an order/closedness law.
No convolution without an effective enumeration/normalization bound.
```

## Retrieval is candidate generation

Retrieval produces candidate material. It does not produce context.

```text
retrieval + mapping + closure + provenance + minimization + rendering = context preparation
```

A chunk is not evidence until it is typed, mapped, provenance-linked, freshness-checked, and placed in a task schema. When spatiality is material, it must also be placed in the right local neighborhood with its labels and local/global identity retained. When requirements compose, the fragment must also carry its requirement index and legal composition witness.

## Context versus rendering

```text
semantic context != prompt text
```

The prompt, report, dashboard, JSON payload, tool argument, policy input, deployment packet, or review packet is downstream rendering. Optimize semantic exactness first, then optimize rendering.

## Verified context technology stance

Exact Context Doctrine is implementation-agnostic. CQL/categorical database tooling is a reference architecture for verified context publication when schemas, mappings, constraints, integration, provenance, and canonicalization dominate. It is not automatically the right live operational store.

Comonadic spatial tooling is likewise implementation-agnostic. In ordinary systems, an effective labelled graph, query, incremental index, or bounded halo may implement the spatial laws without a literal generic comonad library.

Day/promonoidal context composition is also implementation-agnostic. A sparse indexed map, relational query, constraint solver, semiring dynamic program, or static plan IR may implement the laws without a generic coend library.
