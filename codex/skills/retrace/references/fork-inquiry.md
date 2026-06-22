# Fork Inquiry Receipt: FIR-v1

A FIR is controller evidence, not merely a model answer.

## Lineage modes

### `thread_fork`

```text
stored source thread
-> thread/fork
-> thread/rollback
-> retained-anchor verification
```

Requires source thread identity and matching `forked_from_id`.

### `rollout_transcript`

```text
verified source rollout
-> retained transcript prefix
-> fresh thread/start
-> bounded transcript-context turn/start
```

Requires:

- source rollout path;
- source and anchor digest verification;
- `workspace_reconstruction.mode = transcript_only`;
- no live historical workspace claim;
- fresh inquiry thread identity.

It is not a live fork of the source thread.

## Required receipt shape

```yaml
fork_inquiry_receipt:
  receipt_version: FIR-v1
  receipt_id:
  inquiry_id:
  lane_id:
  lineage_mode:
    thread_fork |
    rollout_transcript

  source:
    capsule_id:
    source_thread_id:
    source_rollout_path:
    source_turn_digest:
    source_artifact_reconstructability:

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
    codex_version:
    ephemeral:
    permissions:
    sandbox:
    approval_policy:

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

A valid FIR requires:

- source and replay lineage;
- exact outcome-blind anchor;
- requested hindsight horizon;
- read-only/no-network policy;
- terminal turn;
- structured answer;
- cleanup state.

Invalid receipts remain audit evidence but do not contribute to route distributions or consensus.
