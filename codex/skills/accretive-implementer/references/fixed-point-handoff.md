# Fixed-Point Handoff to Accretive Implementer

When `fixed-point-driver` delegates mutation to `accretive-implementer`, the handoff must carry enough budget and ablation state to prevent additive drift.

## Required handoff

```yaml
implementation_handoff:
  target_skill: accretive-implementer
  artifact_state_id: "branch/head/base/diff/phase"
  truth_unit_ids: []
  selected_rewrite: delete | privatize | merge | tighten-owner | reuse-owner | add-escrow | validate-only | no-change | blocked
  permitted_route: no-change | validate-only | delete-collapse-canonicalize | mutate-existing-owner | add-new-surface | routed | blocked
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
  addition_escrow_policy: not-allowed | allowed-with-rent-payment | required
  proof_required: []
  stale_if: []
```

## Status meanings

- `not-required`: fixed-point evidence shows the selected route is proof-only, validation-only, or owner-known with no additive/keep-surface decision.
- `local-preflight`: accretive-implementer must run its cheap ablation preflight before adding production surface.
- `external-clearance-required`: fixed-point or an ablation authority must clear deletion/collapse/canonicalization uncertainty before production addition.
- `blocked`: safe mutation cannot proceed.

## Budget rules

- `zero_or_negative`: production surface should not grow; prefer no-change, validation-only, delete/collapse/canonicalize, or mutate existing owner.
- `bounded_positive`: new surface is allowed only within the named scope and proof requirement.
- `explicit_expansion`: user or upstream warrant explicitly accepts expansion; still require proof that the new surface earns itself.

## Escrow rules

Any `add-new-surface` route from fixed-point should map to addition escrow unless the addition directly replaces retired surface in the same rewrite.

Do not close while `addition_escrow_policy: required` and no escrow rent/payment is recorded.
