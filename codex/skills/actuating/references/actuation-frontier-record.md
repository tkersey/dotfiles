# Actuation Frontier Record: AFR-v1

AFR is the domain-decision layer for one `$st` aperture.

It does not own task status.

```yaml
actuation_frontier:
  record_version: AFR-v1
  afr_id:
  run_id:
  slice_id:

  artifact_state:
    repository:
    branch:
    base:
    head:
    dirty_fingerprint:

  graph_binding:
    plan_ref:
    plan_seq:
    gcr_id:
    gcr_ref:
    structure_fingerprint:
    contract_fingerprint:
    coverage_fingerprint:
    execution_fingerprint:
    selected_task_ids: []
    execution_allowed:
    blocking_debt: []

  skill_contracts:
    actuating:
    fixed_point_driver:
    language_skills: {}

  domain:
    owner:
    invariant:
    objective:
    non_goals: []
    state_space:
      dimensions: []
      observed_counterexamples: []
      equivalence_classes:
        - class_id:
          governing_invariant:
          canonical_owner:
          representative_witness:
          covered_combinations: []
          proof_obligation:
          status:
            open |
            selected |
            closed |
            rejected |
            unknown
    selected_class_id:
    prior_closed_classes: []
    next_untested_class:

  decision:
    question:
    alternatives:
      - route:
        evidence_refs: []
        expected_surface:
        risk:
    selected_route:
    rejected_routes:
      - route:
        reason:
        evidence_refs: []
    route_changed_by_evidence:
    canonical_owner:
    permitted_scope: []
    forbidden_actions: []
    surface_budget:
      helpers_added_max:
      branches_added_max:
      fields_added_max:
      public_symbols_added_max:
      fallback_paths_added_max:
      test_families_added_max:
      surfaces_to_retire: []
    route_flip_condition:
    expected_outcome:

  proof_dag:
    nodes:
      - proof_id:
        scope:
          focused |
          affected_aggregate |
          full_closure
        command:
        dependencies: []
        artifact_fingerprint:
        status:
          missing |
          running |
          pass |
          fail |
          stale
        evidence_ref:
        invalidators: []
    selected_proof_ids: []
    current_receipts: []
    stale_receipts: []

  specialists:
    frontier_mapper_ref:
    proof_mapper_ref:
    wave_skeptic_ref:

  realization:
    handoff_ref:
    result_ref:
    patch_ref:
    result:
      not_started |
      valid |
      return_to_frontier |
      blocked |
      invalid
    new_observations: []

  outcome:
    focused_proof:
    graph_updates: []
    next_frontier:
    terminal:
```

## Laws

1. Selected task IDs must be a subset of the current GCR aperture.
2. Material mutation requires `execution_allowed: true` and no blocking debt.
3. The selected class must exist and be marked `selected`.
4. The route and owner are chosen before realization.
5. Every added construct must fit the surface budget.
6. Focused proof maps to the selected class/invariant.
7. A new observation makes the current route nonterminal.
8. AFR never changes `$st` task status directly.
