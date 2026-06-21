# Fork Inquiry Receipt: FIR-v1

```yaml
fork_inquiry_receipt:
  receipt_version: FIR-v1
  receipt_id:
  inquiry_id:
  lane_id:

  source:
    capsule_id:
    source_thread_id:
    source_rollout_path:
    source_turn_digest:

  fork:
    fork_thread_id:
    forked_from_id:
    anchor:
      temporal_horizon:
      turns_before:
      turns_dropped:
      turns_after:
      anchor_digest_expected:
      anchor_digest_observed:
      exact:
    model:
    model_provider:
    service_tier:
    codex_version:
    ephemeral:
    permissions:
    sandbox:
    approval_policy:
    hooks:
    multi_agent_mode:

  workspace_reconstruction:
    mode:
    path:
    head_exact:
    dirty_state_exact:
    dependencies_exact:
    generated_artifacts_exact:
    tools_allowed:
    network_allowed:
    limitations: []

  inquiry:
    mode:
    question:
    evidence_allowed: []
    evidence_withheld: []
    client_user_message_id:
    turn_id:
    started_at:
    ended_at:
    status:
    token_usage:

  answer:
    reconstructed_decision:
    selected_route:
    rejected_routes: []
    evidence_refs: []
    assumptions: []
    alternatives: []
    route_flip_conditions: []
    uncertainty:
    hindsight_available:
    unsupported_claims: []
    final_text_ref:

  lifecycle:
    event_log_ref:
    interrupted:
    archived:
    deleted:
    cleanup_status:

  gate:
    lineage_valid:
    anchor_valid:
    permissions_valid:
    hindsight_label_valid:
    answer_complete:
    receipt_valid:
```

## Validity

`receipt_valid` requires:

- source/fork lineage;
- exact or honestly unavailable anchor;
- requested temporal horizon;
- permission proof;
- terminal turn result;
- answer schema;
- hindsight classification;
- cleanup state.

## Failure

A model answer is preserved as raw evidence when useful, but an invalid receipt cannot contribute to consensus/stability counts.
