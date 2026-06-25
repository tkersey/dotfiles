# Actuation Slice Contract — ASL-v1

ASL is the smallest durable control artifact that joins task, semantic, mutation, and proof frontiers.

It does not duplicate `$st` task status, the language route, or proof result content. It points to them.

```yaml
actuation_slice:
  slice_version: ASL-v1
  run_id:
  slice_id:
  created_at:
  updated_at:

  artifact_state:
    repository_root:
    branch:
    head:
    dirty_fingerprint:
    st_plan_fingerprint:

  task_control:
    plan_ref: .step/st-plan.jsonl
    gcr_id:
    gcr_ref:
    gcr_seq:
    gcr_current: yes | no
    execution_allowed: yes | no
    selected_task_ids: []
    graph_debt_refs: []
    projection_ref:

  semantic_control:
    semantic_route_refs: []
    owner:
    invariant:
    matrix_ref:
    selected_rows: []
    open_rows: []
    new_observations: []

  decision:
    question:
    alternatives:
      - route:
        evidence_refs: []
    selected_route:
    rejected_routes:
      - route:
        reason:
    selected_normal_form:
    patch_boundary:
      files: []
      symbols: []
    forbidden_actions: []
    surface_budget:
      max_files:
      max_production_net:
      max_new_private_helpers:
      max_new_public_symbols:
      max_new_state_fields:
      max_new_test_families:
      required_retirements: []

  realization:
    fixed_point_slice_ref:
    fixed_point_result_ref:
    status:
      not_started |
      prepared |
      valid |
      no_change |
      return_to_frontier |
      blocked |
      invalid

  proof:
    proof_dag_ref:
    focused_obligations: []
    current_epoch_refs: []
    focused_gate:
      pass |
      fail |
      missing |
      stale
    wave_gate:
      pass |
      fail |
      missing |
      stale
    final_gate:
      pass |
      fail |
      missing |
      stale

  active_skill_contracts:
    - skill:
      fingerprint:
      active_clauses: []
      route_ref:

  state:
    prepared |
    mutating |
    focused_proved |
    wave_proved |
    return_to_frontier |
    blocked |
    closed

  next_frontier:
    task_ids: []
    matrix_rows: []
    reason:

  gate:
    mutation_allowed: yes | no
    reason:
```

## Mutation gate

`mutation_allowed: yes` requires:

```text
gcr_current = yes
execution_allowed = yes
selected_task_ids non-empty
owner and invariant present
selected route and normal form present
patch boundary non-empty
focused obligations non-empty
state = prepared | mutating
no unresolved new observation
```

## State transitions

```text
prepared -> mutating
mutating -> focused_proved
focused_proved -> wave_proved | return_to_frontier
wave_proved -> closed | next prepared slice
any -> blocked
```

A new observation that changes owner, invariant, row set, route, or boundary forces `return_to_frontier`.

## Persistence

Recommended local path:

```text
.step/actuating/<run-id>/current.json
.step/actuating/<run-id>/history/<timestamp>-<slice-id>.json
```

These are workflow-control artifacts, not an alternate task graph.

Local-exclude by default unless the user deliberately wants reviewable actuation evidence.

## EPG policy binding

When an ASL realizes an EPG-selected action, add `policy_control` as documented in `policy-action-handoff.md`.

The policy block must be current and must match the active EPD and the selected `$st` materialization.

ASL remains the mutation gate. EPD by itself never grants mutation authority.
