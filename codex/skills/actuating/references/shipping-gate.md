# Shipping Gate

`$ship` is allowed only when:

```text
current artifact state
proof-complete $st graph
current executable GCR
all ASL slices terminal
no required open VMX row
PDAG final gate passes
no unresolved new observation
explicit pr_mode
PR publication in scope
```

Pass:

```yaml
ship_handoff:
  target_skill: ship
  pr_mode:
  pr_mode_reason:
  draft_allowed_reason:
  graph:
    plan_ref:
    gcr_ref:
    proof_complete:
  actuation:
    final_slice_refs: []
    open_matrix_rows: []
  proof:
    proof_dag_ref:
    final_epoch_refs: []
  existing_pr:
    exists:
    url:
    draft:
```

`$ship` opens, updates, or promotes a PR. It does not merge.
