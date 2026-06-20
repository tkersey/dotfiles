# SDR-v1

Optional structured receipt:

```yaml
skill_decision_receipt:
  receipt_version: SDR-v1
  decision_id:
  skill:
  skill_version:
  skill_contract_fingerprint:
  trigger_refs: []
  clause_refs: []
  question:
  alternatives_considered: []
  selected_route:
  rejected_routes: []
  expected_outcome:
  artifact_state:
  evidence_refs: []
```

Use only when a skill makes a consequential route decision.

An SDR receipt records a decision; it does not prove a good result.
