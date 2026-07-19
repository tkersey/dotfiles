# Effects, Coalgebras, and Context-Stable Morphisms

These artifact families cover systems that are not just static syntax or migration. Distinguish static description composition, context framing, effect interpretation, behavioral unfolding, and comonadic situatedness.

## Effect signatures and handlers

Use when operation syntax is mixed with execution, logging, retries, validation, explanation, simulation, or runtime policy.

Code shape:

```text
data Operation = ...
data Program = Pure(value) | Perform(Operation, continuation)
handleTest : Program -> TestResult
handleProd : Program -> RuntimeResult
handleAudit : Program -> AuditTrace
```

Universal reading:

```text
free effect syntax + handlers as interpreters
```

Proof signals:

```text
testHandler(program) == expectedFixture
observe(prodHandler(program)) == expectedObservation
handler omits operation case -> compile/test failure
```

First seam examples:

- one workflow command;
- one retryable operation;
- one audit/emission operation;
- one plugin/rule operation;
- one test handler for an existing service call.

## Applicative / Day static descriptions

Use when an effectful computation's full operation/dependency shape is known before intermediate results are available.

Description shape:

```text
StaticPlan a
pure    : a -> StaticPlan a
combine : Day StaticPlan StaticPlan a -> StaticPlan a
```

or an equivalent free-applicative/indexed representation.

Day reading:

```text
indexed/static descriptions compose by Day convolution;
a monoid multiplication supplies applicative combination;
interpreters execute, analyze, price, document, or audit the same description.
```

Use for:

- build task graphs with statically known dependencies;
- request batches;
- configuration/form/CLI descriptions;
- independent validation plans;
- static tool-operation plans;
- cost, capability, or input analysis before execution.

Proof signals:

```text
represent(a) star represent(b) ~= represent(a tensor b)
analysisInterpreter(plan) agrees with executionInterpreter(plan) on declared structure
unit and associativity hold under normalization
all legal supported decompositions contribute
```

Guardrails:

- select a free monad/monadic syntax when later operation structure depends on earlier results;
- static/applicative structure does not prove runtime effect commutativity;
- parallelization still requires Freyd centrality, observational commutativity, or resource-disjointness;
- decomposition enumeration and normalization require an effective resource model.

## Context-stable profunctors / Tambara modules

Use when the problem is not how descriptions combine or how effects execute, but how one generalized transformation remains valid when an admissible context is added around both endpoints.

Shape:

```text
(M, tensor, I)       context world
L : M x C -> C       source action
R : M x D -> D       target action
P : C^op x D -> V    generalized capability
frame_m : P(a,b) -> P(L(m,a), R(m,b))
```

Universal reading:

```text
context acts on endpoint worlds;
Tambara structure frames a profunctorial capability through that context.
```

Use for:

- one validator or observation reused under tenant, evidence, policy, or capability context;
- repeated product/coproduct residual handling behind lenses, prisms, or mixed optics;
- a domain/wire or read/write boundary whose endpoint contexts differ;
- a bare local capability that should be closed under every legal context;
- a capability that must expose coherent behavior for all supported contexts;
- typed context changes requiring a dependent/double-categorical action.

Proof signals:

```text
frame_I(p) ~= p
frame_(m tensor n)(p) ~= frame_m(frame_n(p))
dimap(f,g,frame_m(p)) ~= frame_m(dimap(f,g,p))
interpret(frame_m(p)) == frameSemantics(m, interpret(p))
```

If an optic/residual representation is used:

```text
interpretOptic(m,decompose,rebuild,p)
  == dimap(decompose,rebuild,frame_m(p))
```

Guardrails:

- a `Context<T>` wrapper, Reader parameter, middleware stack, or dependency-injection container is not automatically a Tambara module;
- Tambara framing does not prove effect commutativity, parallelism, duplication, discard, or resource independence;
- optic interpretation/composition does not prove Get-Put, Put-Get, Put-Put, validation, provenance, or business laws;
- a generalized Tambara module may not be representable by a concrete function/module functor;
- free/cofree context closure requires a finite, bounded, symbolic, queryable, or otherwise effective presentation;
- this Tambara terminology is distinct from equivariant Tambara functors.

## Behavioral coalgebras

Use when behavior unfolds over time and is best specified by transitions plus observations.

Code shape:

```text
data State = ...
data Input = ...
data Observation = ...
step : State × Input -> State
observe : State -> ObservationResult
```

Universal reading:

```text
stateful behavior as coalgebra; equivalence by observations/traces
```

Proof signals:

```text
trace(step, observe, initial, inputs) == expectedTrace
invalid transition is rejected
equivalent states produce equivalent observations
```

First seam examples:

- one protocol state transition;
- one scheduler transition;
- one actor mailbox step;
- one stream processor state update;
- one domain lifecycle with external observations.

## Comonad coalgebras / situated objects

Use when the problem is not primarily how a state evolves, but how an object is coherently situated inside a local neighborhood, scope, dependency region, evidence context, capability region, or other spatial world.

Code/mechanics shape:

```text
C : S -> S
epsilon : C => Id
delta : C => C . C
h : E -> C(E)
```

Reading:

```text
C(E)       E-valued local views
h(e)       the local context assigned to e
epsilon    e is the center of its context
delta      local contexts of nearby points agree coherently
```

Proof signals:

```text
epsilon(h(e)) == e
C(h)(h(e)) == delta(h(e))
restrict(germ, smallerValidHalo) preserves center meaning
continuousBoundary preserves required halos and labels
```

First seam examples:

- a symbol plus scope/call/test/ownership neighborhood;
- an endpoint plus tenant/principal/policy/persistence neighborhood;
- a task plus evidence/provenance/capability neighborhood;
- a schema object plus mappings/constraints/report neighborhood;
- a component plus provider/dependency/configuration neighborhood.

## Density comonads, bases, Day products, and spatial framing

Use density when local patch types generate the situated world:

```text
P : B -> S
<P> = Lan_P P
```

A subbasis generates a candidate spatial structure. A basis additionally permits canonical reconstruction of every situated object from basic patches. Example coverage alone is not density.

When two such spatial description worlds have a meaningful product of patches, first construct the external-product vocabulary on `B1 x B2`. Call the result a Day convolution only after naming one shared/product index world, its tensor/unit or promonoidal kernel, both reindexings, a density-Day comparison map, and an isomorphism, observational-equivalence, or bounded-approximation witness.

This is a description-level composition of locality descriptions, not a replacement for center/coherence, halo, continuity, or resource laws. External-product patches alone do not prove a Day equivalence.

When a local generalized transformation must remain valid while its halo/context expands, a Tambara action may frame it:

```text
frame_m : Capability(a,b)
       -> Capability(m act a, m act b)
```

The context/halo family must form an honest ordinary, promonoidal, or dependent action. The framing law must preserve center, restriction, labels/provenance, and continuity where those observations matter.

## Selection rule

- Choose **free monadic syntax/effects** when later operation structure may depend on earlier results or the main smell is dynamic sequencing with many interpreters.
- Choose **free applicative / Day static descriptions** when the whole operation/dependency shape is known before results and static analysis matters.
- Choose **Tambara/contextual-morphism structure** when one profunctorial capability must survive several context extensions.
- Choose **behavioral coalgebra** when the main smell is ongoing behavior with duplicated transition/observation logic.
- Choose **comonadic spatiality** when locality, neighborhoods, restriction, local/global identity, or continuity are semantic.
- Combine static/applicative descriptions with a Freyd runtime when plans are inspectable but execution order remains effectful.
- Combine Tambara framing with a Freyd runtime when an effectful capability must retain residual/context semantics but order remains observable.
- Combine Tambara framing with comonadic spatiality when a transformation must remain valid under lawful halo/context extension.
- Combine free effects with behavioral coalgebra when a workflow program drives a stateful runtime.
- Combine behavioral and comonad coalgebras when a situated process both evolves over time and must preserve its local context.

Guardrail: a type named `Context<T>` is not evidence of a comonad or Tambara module, and a binary static-plan combinator is not evidence of Day convolution. Require the relevant laws, effective representation, and a code/test delta.
