# Negative Route Ratchet

Before repeating a route in a hot cluster, check active negative evidence.

```yaml
negative_route_gate:
  prior_route_checked: yes | no
  active_exclusion_match: yes | no
  if_match:
    neg_id:
    selected_route:
    exclusion_rule:
    status: reopened | superseded | stale | blocked
  handoff_allowed: yes | no
```

If active exclusion matches and is not reopened/stale/superseded, block implementation.
