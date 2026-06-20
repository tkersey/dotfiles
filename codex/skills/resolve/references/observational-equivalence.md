# Observational Equivalence

Two states or execution paths are equivalent when every accepted observation gives the same required result.

```text
x ≈ y
iff
for every accepted observation o:
  o(x) = o(y)
```

A distinction survives only with a witness.

Finite deterministic kernels should use exact partition refinement. Finite nondeterministic kernels should use bisimulation when supported. General kernels use a witnessed manual quotient and may not claim exact minimality.
