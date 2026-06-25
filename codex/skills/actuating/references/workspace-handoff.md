# Workspace Handoff

```yaml
actuation_workspace_handoff:
  workspace_ref:
  plan_id:
  session_id:
  executor:
  claim_ref:
  fencing_token:
  gcr_ref:
  branch_epoch:
  worktree_ref:
  resource_roots: []
  selected_task_ids: []
  selected_policy_action:
  proof_obligations: []
```

This handoff is stale when any referenced sequence, epoch, claim, fencing token,
or worktree binding changes.
