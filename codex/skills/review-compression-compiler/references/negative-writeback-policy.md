# Negative Writeback Policy

Do not write every local failure to `.learnings.jsonl`.

```yaml
negative_writeback_policy:
  in_wave_only:
    - one-off same-session route failure
    - low confidence
    - unclear applicability
  route_wave_artifact:
    - same-cluster recurrence
    - proof matrix gap
    - failed selected normal form
  durable_learnings:
    - repeated across sessions
    - generalizable to future branches
    - benchmark/regression/revert/public-bypass pattern
    - current proof anchors exist
```

Root owns durable writeback.
