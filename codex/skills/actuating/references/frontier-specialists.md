# Read-Only Actuation Specialists

Root is the sole writer.

## `actuation_frontier_mapper`

Use before route selection when the state space/owner is unclear.

Returns:

```yaml
actuation_frontier_map:
  packet_version: AFM-v1
  artifact_state:
  gcr_id:
  st_task_ids: []
  dimensions: []
  counterexamples: []
  equivalence_classes: []
  plausible_owners: []
  recommended_selected_class:
  unresolved: []
  evidence_refs: []
```

## `actuation_proof_mapper`

Use when proof coverage/cadence is unclear.

Returns:

```yaml
actuation_proof_map:
  packet_version: APM-v1
  artifact_state:
  afr_id:
  obligations: []
  existing_proof: []
  stale_proof: []
  focused_cut: []
  affected_aggregate_cut: []
  full_closure_cut: []
  invalidators: []
  evidence_refs: []
```

## `actuation_wave_skeptic`

Use after a material wave.

Returns:

```yaml
actuation_wave_review:
  packet_version: AWS-v1
  artifact_state:
  afr_ids: []
  uncovered_classes: []
  duplicate_classes: []
  orphan_constructs: []
  surface_budget_violations: []
  wound_specific_proof: []
  new_observations: []
  recommended_next_frontier:
  verdict:
    close_wave |
    return_to_frontier |
    block
```

## Fanout discipline

Use specialists at frontier/wave boundaries, not after every patch.

Stop fanout when one packet answers the material question.
