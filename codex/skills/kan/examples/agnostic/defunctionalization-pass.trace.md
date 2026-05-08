# Defunctionalization pass trace

## Boundary

- Construction: `Lft_P F`
- `A`: public API contract cases
- `B`: internal service implementation plans
- `C`: observable HTTP behavior plus audit events
- `P : B -> C`: projection from internal implementation to public behavior
- `F : A -> C`: desired public contract

## Hidden functions before the pass

```text
buildImplementation : PublicCase -> InternalService
obligationPredicate : InternalDesign -> Bool
```

These functions crossed the architecture boundary anonymously. The agent could not inspect or test which implementation cases existed.

## Defunctionalized IR

```text
ImplementationPlan
  = UseReadModel(model)
  | UseTransactionalWrite(table)
  | UseExternalCapability(capability)

Obligation
  = NeedsField(table, field)
  | NeedsAuditEvent(event)
  | NeedsIdempotencyKey(scope)
```

## Interpreter/projector

```text
projectImplementation : ImplementationPlan -> PublicCase -> PublicBehavior
satisfyObligation : InternalDesign -> Obligation -> Bool
```

## Law tests

- Left-lift realization: `F(case)` is covered by `projectImplementation(plan(case), case)`.
- Right-lift soundness: if all derived obligations hold, the public projection stays within the accepted behavior for that case.
- Centralization: public behavior is produced only through `projectImplementation`, not ad hoc route handlers.

## Architecture result

The refactor creates a stable `lifts/plans.*`, `lifts/obligations.*`, and `projection/publicBehavior.*` boundary. Broad implementation changes now operate on first-order cases rather than scattered callbacks.
