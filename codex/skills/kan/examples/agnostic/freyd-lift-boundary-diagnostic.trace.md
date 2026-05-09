# Freyd/AFT lift-boundary diagnostic trace

## Problem

Refactor an orders service from controller-driven CRUD to workflow modules while preserving public API behavior.

## Lift data

- `A`: public endpoint scenarios from contract tests.
- `B`: internal workflow architecture.
- `C`: observable behavior: HTTP response, emitted events, audit trace.
- `P : B -> C`: run workflow through controller and observe response/events/trace.
- `F : A -> C`: required behavior from golden contract fixtures.

## Freyd/AFT diagnostic

- Structure forgotten by `P`: workflow internals, repository calls, state-transition implementation.
- Constraints available in `B`: workflow composition, shared-state validation, transition guards, audit-event builders.
- Constraint preservation test: if two workflow branches agree on final order state, their public response projections agree on order status.
- Solution-set-like templates:
  - synchronous workflow;
  - event-sourced workflow;
  - saga with compensation;
  - external fulfillment adapter.

## Candidate free builder

```text
Free : ObservableBehavior -> WorkflowSkeleton
Free(required response + events + trace) = workflow skeleton with required state transitions and audit hooks
```

Candidate lift:

```text
L = Free · F
```

## Law test

```text
projectWorkflow(Free(F(cancel_order_case))) == F(cancel_order_case)
```

If exact equality is too strong, classify as covering:

```text
F(case) embeds into projectWorkflow(Free(F(case)))
```

## Obstruction example

No exact lift for `cancellationReason` if the current order model stores only `status` and `updatedAt`.

Repair options:

1. persist `cancellationReason`;
2. reconstruct from event history;
3. add an external audit lookup;
4. weaken the public contract.
