# Specialist Value Receipt

Specialist count is not the same as specialist value. Record a receipt for every specialist packet, accepted or rejected.

## Shape

```yaml
specialist_value_receipt:
  role: verification_auditor | hazard_hunter | evidence_mapper | soundness_auditor | invariant_auditor | complexity_auditor | negative-ledger-mapper | other
  packet_status: accepted | stale | transport-invalid | wrong-scope | timeout | superseded
  artifact_state_id_match: yes | no | unknown
  scope_match: yes | no | unknown
  uncertainty_class: evidence | soundness | invariant | hazard | complexity | verification | negative-evidence | other
  route_changed: yes | no
  finding_added: yes | no
  proof_changed: yes | no
  risk_retired: yes | no
  value: positive | neutral | negative
  used_for: evidence-mapping | negative-evidence-pruning | soundness-pressure | invariant-pressure | hazard-pressure | complexity-pressure | verification-planning | none
  reason: "one sentence"
```

## Value classification

- `positive`: changed the route, added a material finding, changed the proof lane, or retired a plausible material risk.
- `neutral`: valid packet with no material decision delta.
- `negative`: stale, wrong-scope, transport-invalid, misleading, or avoidably duplicative.

## Acceptance rules

- `accepted` requires `artifact_state_id_match: yes` and `scope_match: yes`.
- `risk_retired: yes` requires a plausible material risk to have been ruled out by evidence.
- Rejected packets still receive receipts.
- A `negative-ledger-mapper` packet is value-positive when it changes active exclusions, reopening criteria, route choice, proof selection, or safest next frontier.
