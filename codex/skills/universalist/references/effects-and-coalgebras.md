# Effects and Coalgebras

These artifact families cover systems that are not just static syntax or migration. Distinguish static description composition, effect interpretation, behavioral unfolding, and comonadic situatedness.

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

## Density comonads, bases, and Day products

Use density when local patch types generate the situated world:

```text
P : B -> S
<P> = Lan_P P
```

A subbasis generates a candidate spatial structure. A basis additionally permits canonical reconstruction of every situated object from basic patches. Example coverage alone is not density.

When two such spatial description worlds have a meaningful product of patches, Day convolution may compose them:

```text
<P1> star <P2>
  ~=
<(U,V) |-> P1(U) x P2(V)>
```

This is a description-level product of locality, not a replacement for center/coherence, halo, continuity, or resource laws.

## Selection rule

- Choose **free monadic syntax/effects** when later operation structure may depend on earlier results or the main smell is dynamic sequencing with many interpreters.
- Choose **free applicative / Day static descriptions** when the whole operation/dependency shape is known before results and static analysis matters.
- Choose **behavioral coalgebra** when the main smell is ongoing behavior with duplicated transition/observation logic.
- Choose **comonadic spatiality** when locality, neighborhoods, restriction, local/global identity, or continuity are semantic.
- Combine static/applicative descriptions with a Freyd runtime when plans are inspectable but execution order remains effectful.
- Combine free effects with behavioral coalgebra when a workflow program drives a stateful runtime.
- Combine behavioral and comonad coalgebras when a situated process both evolves over time and must preserve its local context.

Guardrail: a type named `Context<T>` is not evidence of a comonad, and a binary static-plan combinator is not evidence of Day convolution. Require the relevant laws, effective representation, and a code/test delta.
