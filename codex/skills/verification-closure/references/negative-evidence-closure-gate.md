# Negative Evidence Closure Gate

Before closing material review-resolution work, require:

```yaml
negative_evidence_closure_gate:
  active_exclusions_checked: pass | fail
  selected_route_violates_active_exclusion: yes | no
  negative_route_exclusion_cards_resolved: pass | fail
  capture_required_entries_handled: pass | fail
  durable_writeback_decision: appended | duplicate-skip | not-attempted | unavailable
  closure_allowed: yes | no
```

If the selected route violates active negative evidence and is not reopened/stale/superseded/accepted, closure is blocked.
