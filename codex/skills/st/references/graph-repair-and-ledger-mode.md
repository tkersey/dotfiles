# Graph Repair and Ledger Mode

`$st` is useful as a ledger, but material execution requires compiled graph
control.

## Failure classes

```text
intake_parser_failure
intake_semantic_failure
graph_audit_failure
aperture_compile_failure
stale_fingerprint
missing_capability
missing_proof_cut
missing_claim
workspace_conflict
```

## GRR-v1

```yaml
graph_repair_receipt:
  receipt_version: GRR-v1
  workspace:
  plan_id:
  command:
  failure_class:
  observed_exit_code:
  blocking_debt: []
  graph_invariants_lost: []
  repair_actions: []
  waived_items: []
  current_status:
    blocked |
    repaired |
    waived_for_readonly |
    migration_only
  execution_allowed: no
```

## Rules

- Graph debt is named, not ignored.
- A debt waiver must name exact scope and expiry.
- Material mutation remains blocked while GRR is open.
- Manual `st add` repairs are allowed only as graph repair, not as a bypass of
  intake/audit.
- `update_plan` may project current graph state but cannot repair it.

## Final reporting

If graph repair is incomplete, final output must say:

```text
Graph not compiled; material execution blocked.
```

Do not say "ready" or "complete" for material work when the active plan is in
ledger mode.
