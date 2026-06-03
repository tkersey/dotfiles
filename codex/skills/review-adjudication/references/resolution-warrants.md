# Resolution Warrants

Resolution Warrants are scoped, expiring permission artifacts for review-, CAS-,
or thread-derived claims. They convert adjudication from advice into a downstream
capability boundary.

## Contract

A downstream workflow may not mutate code, add validation-only probes, resolve
threads, or draft/defer/rebut a claim unless it has an active matching warrant.

Required columns:

```md
| warrant id | claim id | source | claim excerpt | decision | concern validity | proposed fix validity | no-change status | resolution value | route rationale | permitted action | permitted scope | forbidden actions | evidence refs | countercase ref | proof required | expiry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

## Permission mapping

| resolve decision | permitted action | downstream meaning |
|---|---|---|
| address | mutate-code | code mutation is allowed only inside `permitted_scope` |
| validate-only | add-validation-only | tests/probes/logs/inspection only; no production mutation |
| resolve-thread-only | resolve-thread | proof-bearing reply/thread cleanup only |
| do-not-address | draft-reply/defer/none | no implementation handoff |
| blocked | none | no downstream action |

## Expiry

Every warrant expires when HEAD, base, diff, claim/thread set, or scoped artifact
state changes unless explicitly revalidated against the new artifact state.

## Consumption checks

The checker can validate the adjudication itself and can optionally check changed
files or resolved threads against warrant scope.
