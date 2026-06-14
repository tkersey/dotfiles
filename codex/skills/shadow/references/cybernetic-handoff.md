# Cybernetic Handoff

Use `$cybernetic` only when shadowing itself is part of a repeated system pattern.

## Trigger

- repeated no-delta cycles continue despite productive-cycle gate;
- `/goal` cadence creates valid but low-value reports;
- watched session evidence is delayed or distorted;
- target-skill lens repeatedly produces the same proposal without terminal state.

## Expected result

```yaml
cybernetic_context:
  system_type:
  pattern:
  feedback_loop:
  selected_intervention:
    route: redesign_feedback | change_rules | handoff | blocked
    downstream_skill: tune | seq | shadow | none
```

## Rule

Do not run `$cybernetic` for every shadow cycle. Use it only when the monitoring loop itself is the system problem.
