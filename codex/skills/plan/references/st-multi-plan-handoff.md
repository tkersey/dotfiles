# `$st` Multi-Plan Handoff

```yaml
st_handoff:
  workspace: .ledger/st
  plan_id:
  plan_alias:
  policy_ref:
  policy_digest:
  synthesis_receipt_ref:
  synthesis_receipt_digest:
  source_digest:
  target_branch:
  resource_predictions:
    - action_id:
      resources: []
  proposed_cross_plan_dependencies: []
  mutation_allowed: no
```

Importing a policy creates or updates one plan namespace only.

If the plan ID already exists, update requires the expected current plan
sequence and source-policy digest.

If another plan owns a prerequisite, propose a qualified dependency. Do not copy
its work into the current plan.

A `$st` handoff is not ready unless the corresponding PSR-v1 proves synthesis
convergence and radical-candidate disposition.
