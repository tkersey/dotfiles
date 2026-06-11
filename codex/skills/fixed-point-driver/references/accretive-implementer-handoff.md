# Accretive Implementer Handoff Contract

Use this when `fixed-point-driver` routes implementation or remediation to `accretive-implementer`.

The corrected usage evidence shows `accretive-implementer` may be used as assistant-declared or root-equivalent companion workflow, even when native activation counters undercount it. Therefore every fixed-point route into it must carry explicit route, surface budget, ablation status, and proof requirements.

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

## Route mapping

- `delete`, `privatize`, `merge` -> `delete-collapse-canonicalize`
- `tighten-owner`, `reuse-owner` -> `mutate-existing-owner`
- `add-escrow` -> `add-new-surface`
- `validate-only` -> `validate-only`
- `no-change` -> `no-change`
- `blocked` -> `blocked`

## Budget rules

- `zero_or_negative`: the implementation should not increase production surface.
- `bounded_positive`: positive surface is allowed only inside permitted scope and proof requirements.
- `explicit_expansion`: positive surface was explicitly accepted by user/upstream warrant and still requires proof that it earns itself.

## Ablation rules

- `not-required`: no mutation-capable or keep-surface decision remains.
- `local-preflight`: `accretive-implementer` must run its cheap ablation preflight before adding production surface.
- `external-clearance-required`: fixed-point or ablation authority must clear deletion/collapse/canonicalization uncertainty before positive production surface.
- `blocked`: do not mutate.

## Companion ledger requirement

When this handoff is used, the Companion Skill Ledger row for `accretive-implementer` must include:

```text
right_sized_route=<route>; surface_budget=<budget>; ablation_status=<status>; proof_required=<summary>
```

Do not mark `accretive-implementer` as `used` unless the transcript or output includes a contract-shaped section or bottom-line fields from its skill.
