# SDR-v1

Optional JSON receipt:

```json
{
  "skill_decision_receipt": {
    "receipt_version": "SDR-v1",
    "decision_id": "<stable-id>",
    "skill": "<skill>",
    "skill_version": "<version>",
    "skill_contract_fingerprint": "<fingerprint>",
    "trigger_refs": [],
    "clause_refs": [],
    "question": "<decision question>",
    "alternatives_considered": [],
    "selected_route": "<route>",
    "rejected_routes": [],
    "expected_outcome": "<outcome>",
    "artifact_state": {},
    "evidence_refs": []
  }
}
```

Use only when a skill makes a consequential route decision.

Validate or content-address it through Tune's canonical passive definition:

```bash
ledger validate \
  --definition <tune-skill-root>/definitions/ledger/skill-decision-receipt.json \
  --input receipt=<receipt.json> \
  --format json

ledger materialize \
  --definition <tune-skill-root>/definitions/ledger/skill-decision-receipt.json \
  --input receipt=<receipt.json> \
  --format json
```

A pass means only that the receipt is structurally valid under the reported
definition digest. An SDR receipt records a decision; it does not prove a good
result or grant authority.
