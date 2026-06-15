# Negative Route Gate

Before repeating any route in a hot cluster:

```yaml
negative_route_gate:
  checked: yes | no
  active_exclusion_match: yes | no
  route_changed_by_exclusion: yes | no
  capture_created: yes | no
  handoff_allowed: yes | no
```

If active evidence excludes the route and is not reopened/stale/superseded/accepted, implementation is blocked.
