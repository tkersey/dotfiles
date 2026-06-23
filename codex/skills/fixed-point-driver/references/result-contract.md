# Fixed-Point Slice Result: FPSR-v1

FPSR is the sole realization result consumed by `$actuating`.

## Valid

Requires:

```text
artifact state accounted for
selected route unchanged
owner unchanged
all changed files in permitted scope
surface counts within budget
every construct mapped
focused proof pass
no new observation
```

## Return to frontier

Use when a new observation changes:

```text
counterexample class
owner
scope
route
surface budget
proof obligation
```

The current patch may be preserved as evidence, but further mutation is forbidden until a new AFR/ARH is issued.

## Blocked

Use for external/tooling/dependency/authority blockers without a contract violation.

## Invalid

Use for scope, budget, orphan, proof, or route violations.
