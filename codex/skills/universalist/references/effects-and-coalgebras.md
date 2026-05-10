# Effects and Coalgebras

These two artifact families complete Track D for systems that are not just syntax or migration.

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

## Selection rule

- Choose **free syntax/effects** when the main smell is many interpreters for the same operations.
- Choose **coalgebra** when the main smell is ongoing behavior with duplicated transition/observation logic.
- Combine them when a workflow program drives a stateful runtime.
