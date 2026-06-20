# Concrete Primitive Register

Category theory governs composition; primitives connect software to reality.

## Primitive register fields

```text
Primitive:
Capability:
Input / output:
World entered:
Handler / adapter:
Failure modes:
Determinism / probability:
State mutation:
Security / approval:
Resource cost:
Observations / audit trace:
Test double / simulation:
```

## Rules

- Every external effect has one canonical primitive owner.
- Primitive behavior is not silently duplicated in business logic.
- Failure and retry semantics are part of the primitive boundary.
- Lossy serialization/projection declares preserved observables.
- A primitive exception is contained; it is not permission for arbitrary composition.
- The register distinguishes trusted internal kernels from untrusted external inputs.

## Common primitive families

- computation/runtime kernels;
- storage and persistence;
- network and foreign services;
- time and randomness;
- human approval and policy authority;
- models, solvers, theorem provers, and numeric kernels;
- operating-system and hardware capabilities.
