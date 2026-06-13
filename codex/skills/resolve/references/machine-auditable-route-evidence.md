# Machine-Auditable Route Evidence

The ladder only improves future behavior when it leaves structured evidence.

## Rule

Every mutation-capable review item must leave this receipt in the durable ledger or final report.

```yaml
review_closure_abstraction_receipt:
  receipt_version: RCA-LADDER-v2
  review_item_id: "..."
  cluster_id: "..."
  adjudication_route: "address | delete-collapse-canonicalize | validate-only | resolve-thread-only | do-not-address | blocked"
  receipt_status: structured | root-equivalent-structured | missing
  primary_smell:
    hard_to_understand_or_spec_risk: yes|no
    duplicate_or_pass_through_surface: yes|no
    layer_or_tooling_tax: yes|no
    missing_boundary_artifact: yes|no
    coupled_or_repeated_findings: yes|no
    implementation_only_after_route_selection: yes|no
  earliest_applicable_rung: "complexity-mitigator | simplify-isomorphic | reduce | universalist | fixed-point-driver | accretive-implementer"
  selected_skill: "..."
  reason_selected: "..."
  rejected_later_rungs:
    - skill: "..."
      reason: "earlier rung owned the pathology"
  selected_route: "no-change | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked"
  proof_required: []
```

## Status

- `structured`: a normal receipt was emitted.
- `root-equivalent-structured`: the root produced the same fields without a distinct skill invocation.
- `missing`: no structured receipt exists.

`missing` blocks production mutation and resolved completion.

## Prose rule

Prose may explain a route. Prose is not a route receipt.

If a future audit would need to infer the selected route from narrative text, the route evidence is insufficient.
