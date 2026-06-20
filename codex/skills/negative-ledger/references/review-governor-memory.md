# Review Governor Memory

`$negative-ledger` is the Review Governor's operational route memory.

## Operational Gate

```yaml
negative_route_gate:
  checked: yes
  evidence_source:
    query_or_map: yes
    ledger_cli: ledger
    store: .ledger/negative-ledger.jsonl
    command: "ledger map --route ... --cluster ... --artifact ..."
    exit_code: 0 | 2 | 3
    ledger_available: yes | no
  active_exclusion_match: yes | no | null
  exclusion_id: "none | NEG-..."
  fuzzy_candidates: 0
  fuzzy_authority: suggest_only | none
  failure: none | ledger_missing | store_invalid
  route_changed_by_exclusion: yes | no
  capture_created: yes | no
  handoff_allowed: yes | no
```

If the parent workflow requires an operational same-cluster gate and the ledger is unavailable or invalid, mutation is blocked.

## Memory Admission Receipt

Memory admission is downstream of the operational gate and never substitutes for it:

```yaml
negative_memory_admission:
  required: yes | no
  ledger_export_available: yes | no
  projection_fingerprint: "none | sha256..."
  memory_note_attempted: yes | no
  memory_note_id: "none | MSN-..."
  outcome: created | duplicate_skip | not_qualified | cli_unavailable | export_unavailable | failed
```

A failed or skipped memory admission does not invalidate a valid canonical ledger capture. It only means future global memory has not yet received the projection.
