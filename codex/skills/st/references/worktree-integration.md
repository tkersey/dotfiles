# Worktree and Integration Model

## Default execution substrate

```text
target branch:
  one canonical branch

workers:
  detached external worktrees created at current branch epoch

integration:
  one serialized queue
```

Workers may create commits inside their detached worktree only as an internal
change-set representation. They do not push or advance the target branch.

## CS-v1 change set

```yaml
change_set:
  change_set_version: CS-v1
  change_set_id:
  workspace_id:
  plan_id:
  item_ids: []
  claim_id:
  fencing_token:
  base_branch:
  base_head:
  branch_epoch:
  worktree_ref:
  changed_paths: []
  resource_roots: []
  patch_digest:
  resulting_tree_digest:
  focused_proof_refs: []
  integration_proof_required: []
  status:
    sealed |
    queued |
    integrated |
    rejected |
    superseded
```

## Integration

The integrator acquires:

```text
git:index / exclusive
git:branch:<target> / exclusive
```

It then verifies:

```text
expected target HEAD
expected branch epoch
change set still current
changed paths covered by claim
no unresolved integration predecessor
proof prerequisites current
```

After successful integration it emits IGR-v1:

```yaml
integration_receipt:
  receipt_version: IGR-v1
  change_set_id:
  target_branch:
  head_before:
  head_after:
  tree_after:
  branch_epoch_before:
  branch_epoch_after:
  integration_proof_refs: []
  invalidated_proof_refs: []
  result:
```

## Literal shared-checkout mode

This mode is optional and must be explicitly enabled.

It requires path guards around every mutation command and still serializes all
Git index/commit/push operations.

It is less safe than isolated worktrees and should not be the default.
