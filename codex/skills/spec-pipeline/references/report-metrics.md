# Report Metrics

Future reports should measure:

```yaml
spec_pipeline_quality:
  modes:
  sgr_v2_present:
  gate_blocked_plan:
  gate_changed_decision:
  challenge_changed_spec:
  challenge_changed_route:
  fresh_eyes_changed_spec:
  returned_to_grill:
  pass_no_delta:
  plan_started_before_gate:
  mutation_started_before_handoff:
  retro_triggers:
```

Do not use standalone gate or challenge activation counts as the main success metric.
