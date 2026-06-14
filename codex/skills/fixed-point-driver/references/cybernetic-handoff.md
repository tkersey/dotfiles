# Cybernetic Handoff

`$fixed-point-driver` consumes cybernetic context; it does not rediscover it by default.

## Consume

```yaml
cybernetic_context:
  system_type:
  pattern:
  feedback_loop:
  leverage_level:
  selected_intervention:
  local_patch_allowed:
  monitoring_or_probe:
```

## Rules

- If `system_type: clear`, checklist-style convergence is acceptable.
- If `system_type: complicated`, use analysis/expert-style decomposition before mutation.
- If `system_type: complex`, do not force a one-shot deterministic fix; prefer bounded probes, proof matrix, monitoring, or review distillation.
- If `system_type: chaotic`, stabilize first before optimization.
- If `local_patch_allowed: no`, reject local point-fix handoff.
- Preserve the selected leverage level; do not reduce a rule/feedback intervention into a parameter tweak.
