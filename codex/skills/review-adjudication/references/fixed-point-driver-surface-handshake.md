# Fixed-point-driver Surface Handshake

`review-adjudication` issues surface budgets. `$fixed-point-driver` consumes them
and proves the final diff stayed inside budget or obtained an explicit expansion
warrant.

## Required handoff request

When a mutation-capable warrant routes to `$fixed-point-driver`, the Handoff
Agenda must request:

```md
Surface Budget Preflight
Surface Delta Receipt after each patch group
Expansion Warrant Request before exceeding budget
Surface Budget Closure before final proof/ship
```

## Surface Budget Preflight

```md
- warrant id:
- feature to preserve:
- deletion / reuse / collapse / canonicalization / refactor probes:
- selected first implementation shape:
- budget status before patch:
```

## Surface Delta Receipt

```md
- warrant id:
- patch group:
- files changed:
- insertions/deletions/net:
- public symbols/helpers/flags/state/branches added:
- deleted/collapsed paths:
- budget status: within-budget / expansion-needed / violation
```

## Expansion Warrant Request

```md
- warrant id:
- additive surface requested:
- lower-surface routes defeated:
- proof that added surface reduces total semantic surface:
- approved: yes/no
```

## Surface Budget Closure

```md
- warrant id:
- final diff within budget: yes/no
- proof passed:
- unresolved expansion debt:
```
