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
      validate_only:
      delete_collapse:
      normal_form_decision:
      review_distillation:
      mutate_existing_owner:
      add_new_surface:
      blocked:
    production_net:
    test_net:
    helper_wrapper_adapter_added:
    public_symbols_added:
    fallback_or_compat_paths_added:
    duplicate_or_shadow_surfaces_retired:
    final_state: resolved | blocked | recurring | unknown
    next_required_change:
```

The key field is `findings_after_first_fix`.
