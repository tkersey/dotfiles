# Normal Form Selection

A normal form is a model-level route that resolves a counterexample family.

## Priority order

```text
no-change-proof
validate-only
delete-collapse-canonicalize
refactor-existing-owner
mutate-existing-owner
add-new-surface
blocked
```

## Selection objective

Minimize:

```text
production_surface
+ duplicate_owner_penalty
+ abstraction_variance
+ future_review_risk
+ proof_complexity
+ public_surface_penalty
+ fallback_tolerance_penalty
```

Subject to:

- selected counterexamples killed or explicitly routed;
- existing behavior preserved;
- canonical owner named;
- proof executable;
- forbidden actions respected.

## Add-new-surface

`add-new-surface` is last among mutation routes. It must pay abstraction rent.

If a new surface cannot pay rent, select `blocked`, `validate-only`, or a smaller normal form.
