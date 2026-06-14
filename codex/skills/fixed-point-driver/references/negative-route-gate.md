# Negative Route Gate

Before implementing a selected normal form, check active negative evidence.

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

If `active_exclusion_match: yes` and status is not reopened/superseded/stale, implementation is blocked.
