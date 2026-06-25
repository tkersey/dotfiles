# Negative Evidence from EPG Transitions

Capture durable negative evidence when ETR/controller evidence proves an action model failed.

```yaml
action_model_negative_record:
  record_version: AMNR-v1
  policy_id:
  policy_revision:
  state_signature:
  action_id:
  predicted_effects:
  observed_effects:
  falsifying_evidence_refs: []
  failed_route_family:
  exclusion:
  applicability:
  reopening_criteria: []
  status:
    active |
    superseded |
    reopened
```

Capture on:

```text
model failure
same-state repeated failed action
proof-intrinsic route failure
surface or rollback prediction failure
controller-proven unsafe action
```

Do not capture ordinary expected variance as a hard exclusion.

Future policy selection should surface active matching records and whether they changed the candidate action.
