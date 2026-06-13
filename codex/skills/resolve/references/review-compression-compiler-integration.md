# Review Compression Compiler Integration

`$resolve` invokes `$review-compression-compiler` when review resolution risks code accumulation.

## Trigger conditions

Invoke when any is true:

```text
same_cluster_findings >= 2
same cluster reappears after selected normal form
route would add production surface
route would add helper/wrapper/adapter/fallback/flag/branch/state variant/public symbol/compatibility path
decision-bearing items repeatedly select address
surface_delta_call would be larger-with-warrant or larger-without-warrant
mutation-capable item lacks structured route receipt
```

## Required inputs

```yaml
review_compression_input:
  artifact_state_id:
  source_skill: resolve
  current_objective:
  cluster_trigger:
    reason:
    review_item_ids: []
  review_items: []
  current_patch_sites: []
  known_owner_candidates: []
  validation_commands: []
  forbidden_actions: []
  surface_budget_hint: {}
```

## Consumption

Consume:

```yaml
selected_normal_form
proof_matrix
implementation_handoff
closure_rule
```

Pass the implementation handoff to `$fixed-point-driver`.

## Closure

If the same cluster reappears after implementation, do not patch locally. Reopen compiler, block, or escalate according to `closure_rule`.
