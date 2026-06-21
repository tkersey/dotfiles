# Decision Context Packet: DCP-v1

`seq decision-capsule` freezes deterministic source evidence for one historical decision.

```yaml
decision_context_packet:
  packet_version: DCP-v1
  packet_id:

  source:
    session_id:
    rollout_path:
    thread_id:
    root_session_id:
    worker_session_id:
    decision_id:
    source_model:
    source_model_provider:
    source_codex_version:

  artifact_state:
    cwd:
    repository_root:
    branch:
    head:
    dirty_fingerprint:
    dirty_patch_ref:
    generated_artifact_refs: []
    dependency_refs: []
    reconstructability:
      exact |
      head_only |
      transcript_only |
      unavailable

  episode:
    question:
    selected_route:
    rejected_routes: []
    explicit_rationale: []
    explicit_assumptions: []
    evidence_refs: []
    tools_and_artifacts: []
    skills_and_instructions: []
    outcome_refs: []

  turns:
    total_turns:
    decision_turn_index:
    decision_turn_id:
    preceding_turn_id:
    following_turn_id:
    first_outcome_turn_index:
    source_turn_digest:

  anchors:
    pre_decision:
      available:
      keep_through_turn_index:
      drop_last_n_turns:
      anchor_digest:
    post_decision_pre_outcome:
      available:
      keep_through_turn_index:
      drop_last_n_turns:
      anchor_digest:
    outcome_aware:
      available:
      keep_through_turn_index:
      drop_last_n_turns:
      anchor_digest:

  contamination:
    injected_skill_blocks:
    generated_reports:
    current_audit_prompt:
    quoted_material:

  limitations: []
```

## Determinism

The capsule may classify visible text and structured receipts, but it must not ask a model to invent hidden alternatives or rationale.

## Anchor calculation

For each horizon, calculate:

```text
source total turns
desired final retained turn
last N turns to drop
digest of retained turn identities/content metadata
```

CAS verifies the fork after rollback against the anchor digest or equivalent turn list.

## Outcome horizon

The first outcome turn is the earliest turn containing evidence unavailable at the decision point that would materially inform evaluation, such as:

```text
test result
review finding
user correction
commit outcome
deployment/merge result
later failure
```

When ambiguous, mark the post-decision/pre-outcome anchor unavailable.

## Source identity

Prefer thread ID.

Use rollout path only when thread identity cannot be recovered.

Record whether source thread is stored, archived, or only file-backed.
