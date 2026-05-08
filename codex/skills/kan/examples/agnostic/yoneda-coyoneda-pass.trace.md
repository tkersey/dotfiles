# Yoneda/Coyoneda pass trace

## Problem

A service exposes several legacy public observations while a new implementation is being synthesized behind a fixed projection boundary.

## Kan classification

- Axis: lift/postcomposition.
- `A`: public contract cases.
- `B`: internal implementation design choices.
- `C`: observable API behavior.
- `P : B -> C`: public projection from internal design to behavior.
- `F : A -> C`: required behavior per contract case.
- Candidate: `Lft_P F` for realization, with residual `Rft_P F` obligations when exact realization fails.

## Yoneda side

Public behavior is observation-heavy.

Defunctionalized observations:

```text
Observation =
  | StatusCode
  | JsonField(path)
  | AuditEvent(name)
  | IdempotencyKey(key)
```

Interpreter:

```text
runObservation : ObservableBehavior -> Observation -> ObservationResult
```

Law:

```text
runObservation(P(realizer(a)), obs) == runObservation(F(a), obs)
```

## Coyoneda side

Candidate implementation is generation-heavy.

Defunctionalized realizers:

```text
CandidateRealizer =
  | ServiceMethod(methodName, payload)
  | RepositoryChange(table, fields)
  | WorkflowStep(stepName, input)
```

Deferred projection paths:

```text
ProjectionPath =
  | MethodToStatusCode
  | MethodToJsonField(path)
  | StepToAuditEvent(name)
  | RepositoryToIdempotency
```

Interpreter:

```text
projectImplementation : CandidateRealizer -> ProjectionPath -> ObservationResult
```

## Tests

- Every public observation in `F(a)` is explicit.
- Every candidate realizer declares which projection paths it supports.
- Projection of the realizer equals the required observation result.
- Missing projection path emits an explicit residual obligation instead of silently passing.

## Failure mode prevented

Without the pass, the implementation hard-codes public behavior in scattered callbacks. With the pass, observations and deferred projection paths become inspectable boundary data.
