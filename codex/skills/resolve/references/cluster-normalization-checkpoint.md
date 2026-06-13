# Cluster Normalization Checkpoint

A second adjacent finding is enough to suspect an owner, abstraction, or boundary problem.

## Trigger

Trigger a checkpoint when any is true:

- `same_cluster_findings >= 2` in the current `$resolve` run;
- CAS finds an adjacent issue after a previous fix in the same cluster;
- validation or PR feedback targets the same owner after a review-driven fix;
- route selector repeatedly selects `mutate-existing-owner` in the same cluster without an owner map.

## Required checkpoint

```yaml
cluster_normalization_checkpoint:
  checkpoint_version: CNC-v1
  cluster_id:
  trigger_item_ids:
  subsystem:
  suspected_owner:
  owner_candidates: []
  invariant_or_protocol:
  current_patch_sites: []
  state_transition_or_authority_boundary_table:
    - state_or_boundary:
      owner:
      legal_transition_or_authority:
      forbidden_state_or_action:
      current_enforcement:
      gap:
  duplicate_or_shadow_surfaces: []
  local_patches_already_attempted: []
  selected_normal_form_route:
    no-change | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked
  required_skill:
    complexity-mitigator | simplify-and-refactor-code-isomorphically | reduce | universalist | fixed-point-driver
  disallowed_until_checkpoint_closes:
    - add-new-surface
    - local caller-side tolerance
    - wrapper/helper/fallback additions
  proof_required: []
  checkpoint_status: open | closed | blocked
```

## While open

Production mutation in the cluster is blocked except for validation-only work required to close the checkpoint.

## Release conditions

The checkpoint closes only when:

- a normal-form route is selected and proof is named;
- the cluster is proven to be a false grouping;
- or the checkpoint blocks and the run stops or asks for owner input.

## Defaults

- If hard to understand, choose `complexity-mitigator`.
- If duplicated/pass-through/shadow surface is visible, choose `simplify-and-refactor-code-isomorphically`.
- If layer/tooling/config tax dominates, choose `reduce`.
- If a boundary artifact is missing, choose `universalist`.
- If coupled mutation is already required, choose `fixed-point-driver`.

`add-new-surface` requires explicit proof that all earlier routes are insufficient.
