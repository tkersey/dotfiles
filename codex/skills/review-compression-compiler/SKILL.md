---
name: review-compression-compiler
description: "Read-only compiler for hot review clusters. Converts review findings into a normal-form section inside `resolve_decision_record` / RDR-v1. Use when `$resolve` hits the same-cluster stop rule, needs review distillation, or needs to decide whether a cluster is validate-only, delete/collapse, normal-form-decision, distillation, or blocked. Do not edit code."
metadata:
  version: "austere-1.0.0"
  activation_cost: medium
  default_depth: strict
---

# Review Compression Compiler

## Mission

Review findings are counterexamples, not tasks.

This skill is no longer a broad packet factory by default. It compiles a hot review cluster into the normal-form portion of a single `resolve_decision_record`.

It does not edit files.

## Use when

- `$resolve` triggers the same-cluster stop rule;
- same-cluster recurrence appears after a fix;
- route would add public/fallback/compatibility/tolerance surface;
- negative evidence may exclude the current route;
- review-distillation mode may be needed;
- a cluster needs a normal-form decision before implementation.

## Output

Emit or update:

```yaml
resolve_decision_record:
  record_version: RDR-v1
  cluster:
    cluster_id:
    same_cluster_count:
    stop_rule:
    owner_candidates: []
    counterexample_family:
  selected_route:
    kind: validate-only | delete-collapse-canonicalize | normal-form-decision | review-distillation-mode | mutate-existing-owner | add-new-surface | blocked
    owner:
    why_this_route:
    why_not_smaller:
    why_not_point_fix:
  negative_evidence:
    checked:
    active_exclusion_match:
    route_changed_by_exclusion:
  universalist_check:
    required:
    decision:
    reason:
  distillation:
    required:
    mode:
  proof_matrix: []
  implementation_handoff:
    target_skill:
    permitted_scope: []
    forbidden_actions: []
    proof_required: []
```

Prose may explain the record. Prose is not the record.

## Route priority after stop rule

Prefer:

```text
validate-only
delete-collapse-canonicalize
normal-form-decision
review-distillation-mode
blocked
```

Allow `mutate-existing-owner` only if the normal-form decision proves it is not another local point fix.

`add-new-surface` requires explicit expansion acceptance.

## Negative evidence

Before selecting a route that resembles a prior failed route, require `$negative-ledger` or root-equivalent negative route check.

The selected route must not violate active negative evidence unless reopened, stale, superseded, or explicitly accepted.

## Distillation

Use review-distillation mode when review repair history is becoming branch history.

```text
The lab learns. The delivery branch forgets.
```

## Hard rules

- Do not edit files.
- Do not create patch hunks.
- Do not produce a normal-form decision without counterexamples.
- Do not choose a repeated route without negative evidence check.
- Do not treat YAML volume as improvement.
- Do not use add-new-surface as an escape hatch after the stop rule.
