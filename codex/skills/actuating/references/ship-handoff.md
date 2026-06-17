# Ship Handoff

```yaml
ship_handoff:
  target_skill: ship
  pr_mode: ready | draft | update-existing | promote-draft | blocked
  pr_mode_reason:
  draft_allowed_reason:
  validation_state:
  graph_state:
  proof_summary:
  existing_pr:
```

`$ship` must honor `pr_mode` and must not create a draft PR when `pr_mode: ready`.
