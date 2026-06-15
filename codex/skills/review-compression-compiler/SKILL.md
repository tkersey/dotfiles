---
name: review-compression-compiler
description: "Read-only compiler for hot review clusters. Use when `$resolve` as Review Governor needs to compress review findings into counterexample families, candidate routes, and normal-form decisions inside `review_governor_record`. Do not edit code."
metadata:
  version: "governor-1.0.0"
  activation_cost: medium
  default_depth: strict
---

# Review Compression Compiler

## Mission

Review findings are counterexamples, not tasks.

This skill helps `$resolve` compress a hot review cluster into the `review_governor_record`. It is no longer a default packet factory.

It does not edit files.

## Use when

- same-cluster recurrence appears;
- `$resolve` governor rule fires;
- repeated review findings need counterexample-family compression;
- route choices need comparison by surface delta, proof cost, recurrence risk, and review-entropy reduction;
- review-distillation mode may be needed.

## Output

Contribute to:

```yaml
review_governor_record:
  sensor_input:
  state_estimate:
    counterexample_family:
    review_entropy:
  candidate_routes: []
  selected_route:
    why_not_lower_surface:
    why_not_point_fix:
  proof_matrix: []
```

## Route priority

After same-cluster recurrence, prefer:

```text
no-change
validate-only
delete-collapse-canonicalize
normal-form-decision
review-distillation-mode
blocked
```

Do not select ordinary local mutation as a route. It can only implement a normal-form decision.

## Hard rules

- Do not edit files.
- Do not output patch hunks.
- Do not produce "normal form" prose without a route comparison.
- Do not treat add-new-surface as normal.
- Do not skip negative route memory when a prior route failed.
