# Goal-to-Workspace Handoff

When `$goal` routes to `$actuating`, pass:

```yaml
goal_workspace_handoff:
  workspace: .ledger/st
  plan_id:
  target_branch:
  desired_delivery:
  integration_policy: serialized
```

Do not infer the plan from the branch when multiple plans target the same
branch.

Landing or merging occurs only after `$st` integration receipts and final proof
are current for the target branch epoch.
