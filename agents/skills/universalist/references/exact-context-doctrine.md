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

## Context-stable semantic capability

A Context Certificate proves that a particular context instance `m` is valid for a task. A Tambara/contextual-morphism law answers a different question:

```text
Can one local/generalized capability be transported through m coherently?
```

Model:

```text
(M, tensor, I)          certified context world
L : M x C -> C          source/payload action
R : M x D -> D          target/result action
P : C^op x D -> V       validation/decision/observation/update capability
frame_m : P(a,b) -> P(L(m,a), R(m,b))
```

Potential uses:

- one validator reused under tenant, evidence, capability, or policy context;
- one observation/update rule reused across plain, audited, and provenance-bearing representations;
- mixed domain/wire or read/write context actions;
- a local semantic operation lifted into a certified task germ;
- a residual optic that retains the context needed to rebuild a result.

Required fields:

```text
ambient context world and certification boundary
source and target actions
underlying profunctor/generalized capability
frame operation
unit and nested-framing law
endpoint naturality and context-reindexing coherence
schema/provenance/freshness/authority preservation
interpreter and effect-order owner
representability status
effective context/residual representation
```

Core laws:

```text
frame_I(p) ~= p
frame_(m tensor n)(p) ~= frame_m(frame_n(p))
interpret(frame_m(p)) == frameSemantics(m, interpret(p))
```

The Context Certificate and Tambara certificate must agree on what `m` means. A frame operation cannot make an uncertified context valid, and a valid context does not automatically imply that every capability can be framed through it.

Guardrails:

- raw prompt concatenation is not a context action;
- passing a `Context` argument or wrapping a value in a record is not Tambara structure;
- context framing does not waive schema, provenance, freshness, missingness, contradiction, locality, or rendering laws;
- Tambara framing does not justify effect reordering or parallel execution;
- optic composition does not prove domain lens/prism/business laws;
- if context changes indices, use dependent/double-categorical structure rather than erasing types.

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

When a context-stable semantic capability is claimed, add:

```text
No contextual frame without an ambient context action.
No frame without unit, associativity, naturality, and interpretation laws.
No context framing without agreement with the Context Certificate.
No representability claim without a concrete realizer or obstruction.
No framing law may justify effect commutativity.
```

## Retrieval is candidate generation

Retrieval produces candidate material. It does not produce context.

```text
retrieval + mapping + closure + provenance + minimization + rendering = context preparation
```

A chunk is not evidence until it is typed, mapped, provenance-linked, freshness-checked, and placed in a task schema. When spatiality is material, it must also be placed in the right local neighborhood with its labels and local/global identity retained. When requirements compose, the fragment must also carry its requirement index and legal composition witness. When a capability is framed, its context action and preservation laws must also be explicit.

## Context versus rendering

```text
semantic context != prompt text
```

The prompt, report, dashboard, JSON payload, tool argument, policy input, deployment packet, or review packet is downstream rendering. Optimize semantic exactness first, then optimize rendering.

## Verified context technology stance

Exact Context Doctrine is implementation-agnostic. CQL/categorical database tooling is a reference architecture for verified context publication when schemas, mappings, constraints, integration, provenance, and canonicalization dominate. It is not automatically the right live operational store.

Comonadic spatial tooling is likewise implementation-agnostic. In ordinary systems, an effective labelled graph, query, incremental index, or bounded halo may implement the spatial laws without a literal generic comonad library.

Day/promonoidal context composition is also implementation-agnostic. A sparse indexed map, relational query, constraint solver, semiring dynamic program, or static plan IR may implement the laws without a generic coend library.

Tambara/contextual-morphism structure is implementation-agnostic as well. A typed frame API, residual IR, action dictionary, generated wrapper, or mixed optic may implement the laws without a generic optics library, provided the action, profunctor, framing laws, and falsifiers remain explicit.
