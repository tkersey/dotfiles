# Actuation Realization Handoff: ARH-v1

ARH is produced by `$actuating` from a valid AFR.

```yaml
actuation_realization_handoff:
  handoff_version: ARH-v1
  run_id:
  slice_id:
  gcr_id:
  afr_id:
  st_task_ids: []
  artifact_state:
    repository:
    branch:
    base:
    head:
    dirty_fingerprint:
  selected_route:
  canonical_owner:
  permitted_scope: []
  forbidden_actions: []
  non_goals: []
  surface_budget:
    helpers_added_max:
    branches_added_max:
    fields_added_max:
    public_symbols_added_max:
    fallback_paths_added_max:
    test_families_added_max:
    surfaces_to_retire: []
  counterexample_class:
    class_id:
    governing_invariant:
    representative_witness:
    covered_combinations: []
  invariant:
  proof_obligations: []
  proof_dag_ref:
```

The handoff is invalid when:

```text
selected route is not implementation-capable
owner/scope is empty
GCR/AFR identity is absent
budget is missing
proof obligations are empty
artifact state is incomplete
```
