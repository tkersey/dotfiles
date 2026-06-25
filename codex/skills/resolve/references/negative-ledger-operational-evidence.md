# Negative-Ledger Operational Evidence

A nominal line saying "negative route gate checked" is insufficient.

Required:

```yaml
negative_route_gate:
  checked:
  evidence_source:
    skill_read:
    query_or_map:
    ledger_cli: ledger
    store: .ledger/negative-ledger/events.jsonl
    command: "ledger map --route ... --cluster ... --artifact ..."
    exit_code: 0 | 2 | 3
    ledger_available: yes | no
    prior_route_search_terms: []
    current_cluster_compared_to_prior:
  active_exclusion_match: yes | no | null
  exclusion_id: "none | NEG-..."
  fuzzy_candidates: 0
  fuzzy_authority: suggest_only | none
  failure: none | ledger_missing
  route_changed_by_exclusion:
  capture_created:
  handoff_allowed:
```

If same_cluster_count >= 2 and `query_or_map: no`, `ledger map` is missing, `ledger_available: no`, or `exit_code: 3`, mutation is blocked.
