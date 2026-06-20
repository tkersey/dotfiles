# Behavioral Model

Use the smallest vocabulary that explains correctness.

```yaml
behavioral_model:
  carriers: []
  operations: []
  observations: []
  state_classes: []
  transitions: []
  laws: []
  non_laws: []
  forbidden_states_or_transitions: []
  interpreters_or_projections: []
```

## Carriers

State, values, evidence, requests, commands, receipts, manifests, graphs, snapshots, or other domain objects.

## Operations

Creation, mutation, validation, replay, projection, persistence, publication, restoration, deletion, or query.

## Observations

Externally or testably visible results.

Observations help distinguish true semantic differences from implementation distinctions.

## Laws

A law requires:

```text
statement
owner
accepted observations
counterexamples
proof obligations
```

## Non-laws

Record behavior that is intentionally not guaranteed.

This prevents later agents from turning incidental current behavior into doctrine.

## State/transition fallback

Use a state-machine description when algebraic vocabulary does not clarify the domain.

## Boundary pivot

Repeated conditionals may indicate:

```text
wrong representation
wrong owner
missing context
protocol mismatch
syntax/semantic confusion
unmodeled state transition
```

Do not recommend a new abstraction merely because repeated code exists.
