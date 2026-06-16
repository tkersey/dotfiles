---
name: review-compression-compiler
description: "Read-only compiler for hot review clusters. Use when `$resolve` as Review Governor needs to compress review findings into counterexample families, candidate routes, owner-coarseness decisions, proof matrices, production-embargo checks, and normal-form decisions inside `review_governor_record`. Do not edit code."
metadata:
  version: "governor-embargo-1.0.0"
  activation_cost: medium
  default_depth: strict
---

# Review Compression Compiler

## Mission

Review findings are counterexamples, not tasks.

This skill helps `$resolve` compress a hot review cluster into a `review_governor_record`. It is not a default packet factory and it does not edit files.

## Use when

- same-cluster recurrence appears;
- `$resolve` governor rule fires;
- repeated review findings need counterexample-family compression;
- candidate routes need comparison by surface delta, proof cost, recurrence risk, and review-entropy reduction;
- owner coarseness must be adjudicated;
- positive production net is under embargo;
- proof tests risk becoming a wound catalog;
- review-distillation or boundary redesign may be needed.

## Required contribution

```yaml
review_governor_record:
  state_estimate:
    counterexample_family:
    review_entropy:
  owner_coarseness_gate:
  boundary_inventory:
  candidate_routes: []
  selected_route:
    why_not_lower_surface:
    why_not_point_fix:
  proof_matrix_gate:
  production_embargo:
```

## Route priority after recurrence

Prefer:

```text
no-change
validate-only
delete-collapse-canonicalize
normal-form-decision
review-distillation-mode
boundary-redesign
blocked
```

Do not select ordinary local mutation. It can only implement a normal-form decision.

## Hard rules

- Do not edit files.
- Do not output patch hunks.
- Do not produce "normal form" prose without route comparison.
- Do not use `mutate-existing-owner` as a selectable route after recurrence.
- Do not allow positive production growth without explicit warrant.
- Do not add one-test-per-wound proof unless it extends a family matrix.
- Do not skip negative route memory when a prior route failed.
