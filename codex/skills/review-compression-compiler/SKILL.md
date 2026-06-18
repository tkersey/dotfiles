---
name: review-compression-compiler
description: "Read-only compiler front-end for `$resolve`. Convert raw review/CAS/PR/validation findings into branch-liable counterexample families, proof obligations, falsified routes, lower-surface candidates, and delivery patch recipe inputs. Use for hot review clusters, same-family recurrence, cleanroom review labs, counterexample_contract / CEC-v1, delivery_patch_recipe / DPR-v1, or review-lab route falsification. Do not edit code."
metadata:
  version: "3.0.0"
  activation_cost: medium
  default_depth: strict
---

# Review Compression Compiler

## Mission

Compile review information into the counterexample contract.

```text
Review findings are not tasks.
They are possible counterexamples.
```

This skill is the front-end for the cleanroom `$resolve` compiler.

It does not edit files.

## Use when

- a review wave has any findings;
- a same-cluster or same-family pattern appears;
- PR sweep reopens a supposedly clean branch;
- CAS finds adjacent issues after local proof;
- `$resolve` needs CEC-v1, RLL-v1, DPR-v1, or lab route classification;
- review feedback risks becoming serial delivery patches.

## Output

```yaml
review_compilation:
  compilation_version: RCC-v3
  frozen_delivery_base:
  raw_findings:
    - finding_id:
      source:
      observed_fact:
      review_claim:
      proposed_change:
  branch_liability:
    include_in_contract: []
    exclude_from_contract: []
    unknown_or_blocked: []
  counterexample_families:
    - family_id:
      findings: []
      required_behavior:
      proof_obligations: []
      canonical_owner_candidate:
      failure_surface:
  route_learning:
    routes_tried_in_lab: []
    routes_falsified: []
    negative_ledger_captures_required: []
  delivery_recipe_inputs:
    selected_boundary_candidates: []
    surfaces_to_retire: []
    permitted_new_surface_candidates: []
    forbidden_lab_artifacts: []
    proof_matrix: []
  final_call:
    ready_for_contract |
    needs_lab |
    needs_user_decision |
    capture_followup_only |
    blocked
```

## Hard rules

- Do not output patch hunks.
- Do not authorize delivery mutation.
- Do not include non-branch-liable findings in contract inputs.
- Do not treat same cluster as same family without evidence.
- Do not call a route normal form unless it has a closure prediction.
- Do not let a falsified route family remain eligible for the delivery recipe.
- Do not say "no active exclusion" without route-learning evidence or capture decision.
