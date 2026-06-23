# `$fixed-point-driver` 6.0 — Realization Authority

## Governing correction

The driver no longer owns route/normal-form selection.

It consumes:

```text
ARH-v1 when called by $actuating
kernel/RC-v1 for certified reduction
FPF-v1 for one unambiguous standalone task
```

and realizes only the accepted route.

## Added

- ARH-v1 validator.
- FPSR-v1 result and validator.
- explicit surface-budget accounting.
- construct-to-class/invariant/proof map.
- mandatory `return_to_frontier` on new observations.
- strict prohibition on task completion, projection, delivery, or shipping.
