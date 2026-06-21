# Canonical Boundary Artifacts

## Free syntax

Use when syntax, execution, logging, explanation, or validation are tangled together.

Code shape:

```text
data Syntax = ...
interpret : Syntax -> Runtime -> Result
```

Proof signal:

```text
newInterpreter(translate(oldCase)) == oldEvaluator(oldCase)
```

## Coherent observations

Use when several old clients, reports, selectors, or policies must agree on new internals.

Code shape:

```text
data Observation = ...
runObservation : Observation -> Model -> Result
validateCoherence : [ObservationResult] -> Validation
```

Proof signals:

- overlapping observations commute;
- representation changes preserve observations;
- every public projection goes through `runObservation`.

## Transported semantics

Use when old/source semantics must move to a new target surface.

Code shape:

```text
data TransportPath = ...
transport : TransportPath -> SourceSemantics -> TargetSemantics
```

Proof signals:

- identity path preserves behavior;
- embedding path preserves old fixtures;
- invalid path/payload pairs fail explicitly.

## Lifted implementation

Use when public contract cases or traces define the internal implementation target.

Code shape:

```text
data PublicCase = ...
data Realizer = ...
realize : PublicCase -> Realizer
project : Realizer -> PublicBehavior
```

Proof signal:

```text
project(realize(case)) == requiredBehavior(case)
```

## Free builder behind a projection

Use when public behavior determines internals and the projection `P : B -> C` supports a canonical implementation-side builder.

Code shape:

```text
data RequiredBehavior = ...
data ImplementationTemplate = ...
free : RequiredBehavior -> ImplementationTemplate
project : ImplementationTemplate -> PublicBehavior
```

Proof signal:

```text
project(free(required(case))) satisfies required(case)
```

## Obstruction report behind a projection

Use when public behavior determines internals but no exact/free lifted implementation can honestly exist.

Code shape:

```text
data RequiredBehavior = ...
data Obstruction
  = MissingEvidence(...)
  | MissingCapability(...)
  | InconsistentRequirement(...)
  | UnboundedTemplates(...)
explainObstruction : RequiredBehavior -> Obstruction
```

Proof signal:

```text
project(free(required(case))) fails because missing evidence/template/constraint is named
```

## Residual obligations

Use when public requirements imply internal checks, fields, events, resources, or capabilities.

Code shape:

```text
data Requirement = ...
data Obligation = ...
deriveObligations : Requirement -> [Obligation]
satisfy : [Obligation] -> Implementation -> Bool
```

Proof signals:

- satisfying obligations makes projection possible;
- missing one obligation fails;
- each obligation has an owner module.

## Behavioral coalgebra

Use when stateful or ongoing behavior is better described by transitions plus observations than by one-shot construction.

Code shape:

```text
data State = ...
data Input = ...
data Observation = ...
step : State × Input -> State
observe : State -> ObservationResult
```

Proof signals:

- expected trace matches `observe` after repeated `step`;
- invalid transition is rejected;
- states claimed equivalent produce equivalent observations.

## Effect signature and handlers

Use when operations need multiple interpreters: production, test, audit, explanation, simulation, retry, or scheduling.

Code shape:

```text
data Operation = ...
data Program = Pure | Perform(Operation, Continuation)
handle : Program -> Runtime
```

Proof signals:

- test and production handlers agree on declared observations;
- every operation has a handler case;
- handler omits operation -> failing test or exhaustive-match failure.


## Freyd effect boundary

Use when pure transformations and ordered effectful computations share types, but the architecture must not grant interchange or parallelism without proof.

Code shape:

```text
Pure C
Effectful K
embedPure J : C -> K
sequence : K(A,B) × K(B,C) -> K(A,C)
centrality / commutativity witnesses
```

Proof signals:

- `J` preserves identity and composition;
- pure operations commute with effect context;
- reordered effectful operations agree observationally only when certified;
- at least one noncommuting pair demonstrates why sequencing matters.

## Operadic composition grammar

Use when typed components have input/output ports, assemble hierarchically, and the wiring itself is domain syntax.

Code shape:

```text
data Color / PortType
data Operation(inputs, output)
substitute : Operation × [Operation] -> Operation
interpret : Operation -> SemanticComponent
```

Proof signals:

- ports/colors type-check;
- identity and substitution laws hold;
- `interpret(substitute(...))` equals composition of interpreted components;
- forbidden wiring and unjustified permutations are rejected.

## Explicit IR

Use when callbacks, closures, handlers, continuations, predicates, or mappers cross an architecture boundary.

Code shape:

```text
data BoundaryCase = ...payloads...
applyBoundaryCase : BoundaryCase -> Input -> Output
```

Proof signal:

```text
applyBoundaryCase(encode(oldCallback), input) == oldCallback(input)
```


## Dense probe presentation / semantic compression

Use when a large semantic behavior is hard to present directly, and an algebraic/free syntax presentation would be awkward, infinitary, or misleading.

Code shape:

```text
data Probe = ...
data ObservationResult = ...
runProbe : Probe -> Subject -> ObservationResult
reconstruct : CoherentProbeFamily -> SemanticArtifact
validateDensity : ProbeFamily -> CoverageEvidence
```

Proof signals:

- every required semantic observation factors through probes;
- probe observations are coherent;
- reconstruction agrees with direct semantics on witness cases;
- missing probe yields falsifier.

Architecture reading:

```text
small dense probe world + dual/observation bridge -> semantic reconstruction
```
