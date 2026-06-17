# Cluster Trajectory

Track cluster outcomes over time.

```yaml
cluster_trajectory:
  - cluster_id:
    subsystem:
    first_seen:
    findings_total:
    findings_after_first_fix:
    review_iterations:
    selected_routes:
    mutation_permits_required:
    mutation_permits_emitted:
    production_net:
    test_net:
    validation_branches_added:
    evidence_predicates_added:
    duplicate_or_shadow_surfaces_retired:
    final_state:
    next_required_change:
```

The key fields are `findings_after_first_fix`, permit compliance, `production_net`, and branch/predicate growth.
