# Multi-Plan Proof Epochs

## Receipt lineage

```yaml
proof_receipt:
  receipt_version: PRF-v3
  workspace_id:
  workspace_sequence:
  plan_id:
  plan_sequence:
  item_id:
  obligation_id:
  action_id:
  claim_id:
  branch_epoch:
  base_head:
  tree_digest:
  dependency_cut:
    resources: []
    files: []
    generated_artifacts: []
  foreign_change_sets: []
  scope:
    focused |
    wave |
    final
  state:
    pass |
    fail |
    stale |
    waived
  command:
  evidence_ref:
  recorded_at:
  invalidators: []
```

## Invalidation

Any target-branch integration increments `branch_epoch`.

```text
final proof:
  always stale after epoch advance

wave proof:
  stale when integrated resources intersect its dependency cut

focused proof:
  stale when files/resources/generated artifacts intersect its dependency cut

external/live proof:
  stale according to declared external invalidators
```

## Completion

Plan-local completion may use current focused/wave proof.

Workspace delivery closure requires:

```text
quiescent integration queue
current branch epoch
current final-tree proof
all required plan closures
no unresolved cross-plan dependency
```
