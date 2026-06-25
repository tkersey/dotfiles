# STW-v1 Workspace Model

```yaml
st_workspace:
  workspace_version: STW-v1
  workspace_id:
  sequence:
  artifact_root: .ledger
  st_root: .ledger/st

  repository:
    root:
    identity:
    target_branch:
    head:
    branch_epoch:
    working_tree_fingerprint:

  plans:
    - plan_id:
      alias:
      state:
        active |
        paused |
        completed |
        archived
      graph_ref:
      target_branch:
      source:
        kind:
        locator:
        fingerprint:
      plan_sequence:
      graph_fingerprints:
        structure:
        contract:
        coverage:
        execution:

  cross_plan_dependencies:
    - edge_id:
      from:
      to:
      type:
        blocks |
        validates |
        implements |
        documents |
        related
      reason:

  policy:
    plan_required_when_multiple: true
    unknown_scope_mode: repo-exclusive
    worktree_mode: isolated-external
    integration_mode: serialized-cas
    proof_invalidation_mode: dependency-cut
    max_active_plans:
    max_concurrent_claims:

  transaction:
    committed_sequence:
    recovery_required:
```

## Workspace ID

Derive from normalized repository identity, not a transient checkout path.

Recommended:

```text
sha256(git-common-dir identity + remote identity when available)
```

## Plan states

`active` plans participate in workspace scheduling.

`paused` plans keep graph state but emit no executable candidates.

`completed` plans are proof-closed.

`archived` plans remain addressable for lineage but are excluded from default
queries.

## Cross-plan dependency ownership

Only workspace mutations may create or remove cross-plan edges.

Plan-local graph patch commands cannot write another plan's references.
