# Usage Telemetry Receipts

The usage hardening adds receipts so future reports can distinguish high-throughput execution from decision-complete spec generation.

## Required run-level receipt

```text
## Spec Pipeline Receipt
profile:
lane:
evidence_brief_emitted:
grill_rounds:
no_grill_justification:
decision_packet_emitted:
gate_verdict:
plan_allowed:
mutation_allowed:
subagent_budget:
subagent_receipt:
invariant_challenge:
fresh_eyes:
lint_verdict:
execution_handoff:
```

## No-grill receipt

Use when no user questions are asked:

```yaml
no_grill_justification:
  reason:
    - repo evidence resolved current behavior
    - user supplied all material judgment calls
  material_unknowns_remaining: false
  defaulted_decisions:
    compatibility_posture:
    rollout_rollback_posture:
```

## Blocked receipt

Use when the pipeline cannot proceed:

```yaml
blocked_receipt:
  blocked: true
  kind: decision_missing | evidence_missing | proof_failed | environment | dirty_worktree | external_dependency | plan_mode_boundary | review_unresolved | subagent_timeout | scope_conflict
  unblock_action: ask_user | inspect_repo | run_tests | revise_spec | return_to_grill | abort | campaign_checkpoint
  owner:
  consequence:
```

## Subagent accounting

Every spawned subagent must end as consumed, rejected, timed out, superseded, ignored with reason, or open-at-end zero.
