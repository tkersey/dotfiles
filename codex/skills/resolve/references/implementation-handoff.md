# Implementation Handoff

Every mutation-capable route from `$resolve` to `$fixed-point-driver` must include selected normal form, surface budget, rent status, forbidden actions, and proof requirements.

```yaml
implementation_handoff:
  source_skill: resolve
  target_skill: fixed-point-driver
  artifact_state_id:
  review_item_id:
  review_compression_packet_id:
  selected_normal_form:
    kind:
    owner:
  permitted_action:
  permitted_scope: []
  forbidden_actions: []
  surface_budget:
    production_surface: zero_or_negative | bounded_positive | explicit_expansion
    added_helpers_allowed: yes | no
    added_wrappers_adapters_allowed: yes | no
    added_flags_or_fallbacks_allowed: yes | no
    public_symbols_allowed: yes | no
    compatibility_paths_allowed: yes | no
  abstraction_rent_status: paid | unpaid | not-applicable
  proof_required: []
  stale_if: []
```

Defaults for ordinary fixes:

```yaml
surface_budget:
  production_surface: zero_or_negative
  added_helpers_allowed: no
  added_wrappers_adapters_allowed: no
  added_flags_or_fallbacks_allowed: no
  public_symbols_allowed: no
  compatibility_paths_allowed: no
```

If `$fixed-point-driver` delegates to `$accretive-implementer`, require `right_sized_route`, `surface_delta_call`, and proof receipt.
