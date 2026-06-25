# ETR-v1 — Execution Transition Receipt

Every executed policy action emits predicted-versus-observed evidence.

```yaml
execution_transition_receipt:
  receipt_version: ETR-v1
  transition_id:
  policy_id:
  policy_revision:
  policy_digest:
  action_id:
  decision_ref:
  state_before:
    state_id:
    state_digest:
    potential: {}
  artifact_state_before:
  predicted:
    facts_added: []
    unknowns_resolved: []
    obligations_closed: []
    observation_refs: []
    potential_after: {}
  observed:
    facts_added: []
    unknowns_resolved: []
    obligations_closed: []
    observations:
      - observation_id:
        outcome:
        evidence_ref:
    potential_after: {}
  proof:
    obligations: []
    evidence_refs: []
    status:
  surprise:
    present:
    classification:
      none |
      expected_variance |
      new_branch |
      model_failure |
      intent_failure
    statement:
  artifact_state_after:
  state_after:
    state_id:
    potential: {}
  result:
    success |
    failure |
    return_to_policy |
    return_to_spec |
    rollback |
    blocked
  evidence_refs: []
```

## Interpretation

```text
prediction confirmed
  apply the modeled state transition

new branch
  update state and follow an existing policy branch

model failure
  stop; revise policy before further material action

intent failure
  return to source authority
```

A transition receipt is evidence, not a source-code mutation permit.
