# Negative-Ledger Operational Evidence

A nominal line saying "negative route gate checked" is insufficient.

Required:

```yaml
negative_route_gate:
  checked:
  evidence_source:
    skill_read:
    query_or_map:
    prior_route_search_terms: []
    current_cluster_compared_to_prior:
  active_exclusion_match:
  route_changed_by_exclusion:
  capture_created:
  handoff_allowed:
```

If same_cluster_count >= 2 and `query_or_map: no`, mutation is blocked.
