---
name: review-compression-compiler
description: "Read-only compiler for repeated review findings. Use when `$resolve` needs comments compressed into clusters and counterexample families, branch liability separated from validity, one-shot normal forms tracked/falsified, cumulative owner pressure measured, lower-surface routes compared, a governor fuse decision made, or Review Distillation input prepared. Do not edit code."
metadata:
  version: "2.0.0"
  activation_cost: medium
  default_depth: strict
---

# Review Compression Compiler

## Mission

Compile repeated review findings into a route decision that reduces the system's ability to generate the family again.

```text
Review findings are counterexamples.
A normal form is a closure prediction.
A repeated family falsifies that prediction.
```

Do not edit files.

## Required triggers

Use:

- required at second same-cluster finding;
- blocking at third same-cluster finding;
- required immediately after same-family recurrence following a normal form;
- required when cumulative owner pressure crosses a budget;
- required before review distillation.

## Output

Contribute directly to RGR-v3:

```yaml
review_cluster_compilation:
  compilation_version: RCC-v2
  cluster_id:
  findings: []
  counterexample_families:
    - family_id:
      findings: []
      branch_liability:
      canonical_owner_candidate:
  normal_forms_tried:
    - normal_form_id:
      family_id:
      closure_prediction:
      status: active | falsified | superseded | closed
  falsified_route_families: []
  owner_pressure:
  lower_surface_candidates:
    - route:
      surfaces_retired: []
      leverage_level:
      proof_needed:
      status: selected | defeated | blocked
      reason:
  surfaces_to_retire: []
  proof_matrix:
  fuse_recommendation:
    state: open | tripped
    reasons: []
  distillation_required: yes | no
  final_call:
    validate_only |
    capture_followup |
    delete-collapse-canonicalize |
    normal-form-decision |
    review-distillation-mode |
    boundary-redesign |
    blocked
```

## Hard rules

- Valid finding does not imply branch liability.
- Same cluster does not necessarily mean same family.
- One ordinary normal form per family.
- Same-family recurrence falsifies the normal form.
- A falsified normal form cannot be repaired by another ordinary normal form.
- Runtime predicate accretion is not representation elimination.
- When the fuse trips, `normal-form-decision` is no longer a valid final call.
- Do not call the same coarse owner viable without cumulative pressure evidence.
- Do not output patch hunks.
- Do not hand off raw findings.
