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

Use when public behavior determines internals and the projection `P : B -> C` should support a canonical implementation-side builder.

Code shape:

```text
data RequiredBehavior = ...
data ImplementationTemplate = ...
data FreeRealizer = ...
free : RequiredBehavior -> FreeRealizer
project : FreeRealizer -> PublicBehavior
```

Proof signals:

```text
project(free(required(case))) satisfies required(case)
```

and, for obstructions:

```text
project(free(required(case))) fails because missing evidence/template is named
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
