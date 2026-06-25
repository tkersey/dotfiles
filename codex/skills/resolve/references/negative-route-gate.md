# Negative Route Gate

Before repeating any route in a hot cluster:

```yaml
negative_route_gate:
  query_or_map: yes | no
  ledger_cli: ledger
  store: .ledger/negative-ledger/events.jsonl
  command: "ledger map --route ... --cluster ... --artifact ..."
  exit_code: 0 | 2 | 3
  ledger_available: yes | no
  active_exclusion_match: yes | no | null
  exclusion_id: "none | NEG-..."
  fuzzy_candidates: 0
  fuzzy_authority: suggest_only | none
  failure: none | ledger_missing
  route_changed_by_exclusion: yes | no
  capture_created: yes | no
  handoff_allowed: yes | no
```

If `ledger map` is missing or exits `3`, same-cluster mutation is blocked. If active evidence excludes the route and is not reopened/stale/superseded/accepted, implementation is blocked. Fuzzy matches are advisory only.
