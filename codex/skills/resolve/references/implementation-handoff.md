# Fixed-Point Implementation Handoff

Every mutation-capable route from `$resolve` to `$fixed-point-driver` must include the abstraction ladder receipt, cluster checkpoint if triggered, surface budget, ablation status, forbidden actions, and proof requirements.

## Required shape

```yaml
implementation_handoff:
  source_skill: resolve
  target_skill: fixed-point-driver
  artifact_state_id: "branch/head/base/diff/phase"
  review_item_id: "provider-or-review-id"
  cluster_id: "..."
  abstraction_ladder_rung: "complexity-mitigator | simplify-isomorphic | reduce | universalist | fixed-point-driver | accretive-implementer"
  selected_adjudication_route: address | delete-collapse-canonicalize | validate-only | resolve-thread-only | do-not-address | blocked
  selected_route: no-change | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked
  permitted_action: mutate-code | add-validation-only | resolve-thread | draft-reply | defer | none
  permitted_scope: []
  forbidden_actions: []
  surface_budget:
    production_surface: zero_or_negative | bounded_positive | explicit_expansion
    added_helpers_allowed: yes | no
    added_wrappers_adapters_allowed: yes | no
    added_flags_or_fallbacks_allowed: yes | no
    public_symbols_allowed: yes | no
    compatibility_paths_allowed: yes | no
  ablation_status: not-required | local-preflight | external-clearance-required | blocked
  proof_required: []
  stale_if: []
```

## Defaults

For ordinary review fixes, default to:

```yaml
surface_budget:
  production_surface: zero_or_negative
  added_helpers_allowed: no
  added_wrappers_adapters_allowed: no
  added_flags_or_fallbacks_allowed: no
  public_symbols_allowed: no
  compatibility_paths_allowed: no
ablation_status: local-preflight
```

Use `bounded_positive` only when adjudication, ladder, or cluster evidence shows no-change, validation, isomorphic collapse, owner refactor, and existing-owner mutation cannot satisfy the contract.

Use `explicit_expansion` only when user/upstream warrant explicitly accepts expansion.

## Handoff to accretive-implementer

If `$fixed-point-driver` delegates mutation to `$accretive-implementer`, require `right_sized_route`, `surface_delta_call`, `surface_budget`, `ablation_status`, and `proof_required` in the resulting companion ledger/final report.
