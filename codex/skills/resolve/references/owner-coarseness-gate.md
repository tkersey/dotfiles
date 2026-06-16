# Owner Coarseness Gate

Required when same cluster, same owner, or same file keeps growing.

```yaml
owner_coarseness_gate:
  required:
  trigger:
    same_cluster_count_gte_2:
    same_file_repeated_growth:
    same_owner_repeated_mutation:
    validation_branch_growth:
    evidence_predicate_growth:
    compatibility_or_version_branch_growth:
  owner:
  owner_too_coarse:
  decision:
    route: continue_owner | split_boundary | universalist_check | reduce_surface | distill | blocked
  reason:
```

If owner is too coarse or unknown after recurrence, do not add another branch to that owner.
