# Review Governor Memory

`$negative-ledger` is the Review Governor's route memory.

Nominal checks are insufficient. Same-cluster recurrence requires operational evidence:

```yaml
negative_route_gate:
  checked: yes
  evidence_source:
    skill_read: yes | no
    query_or_map: yes | no
    ledger_cli: ledger
    store: .ledger/negative-ledger.jsonl
    command: "ledger map --route ... --cluster ... --artifact ..."
    exit_code: 0 | 2 | 3
    ledger_available: yes | no
    prior_route_search_terms: []
    current_cluster_compared_to_prior: yes | no
  active_exclusion_match: yes | no | null
  exclusion_id: "none | NEG-..."
  fuzzy_candidates: 0
  fuzzy_authority: suggest_only | none
  failure: none | ledger_missing
  route_changed_by_exclusion: yes | no
  capture_created: yes | no
  handoff_allowed: yes | no
```

If `query_or_map: no`, `ledger_available: no`, or `exit_code: 3` and same-cluster count is at least 2, mutation is blocked.

Capture a negative evidence candidate when a route fails, same-cluster findings recur, or a proof matrix misses a family case.
