# Intervention Design

## Match intervention to system type

| Type | Move |
|---|---|
| clear | checklist / standard process |
| complicated | analysis / expertise |
| complex | safe-to-fail probes / adaptation |
| chaotic | stabilize / create safety |

## Intervention packet

```yaml
intervention:
  route: no_action | observe_more | checklist | expert_analysis | experiment | stabilize | redesign_feedback | change_rules | change_goal | reframe | handoff | blocked
  downstream_skill:
  smallest_safe_move:
  reversibility:
  blast_radius:
  leading_indicators: []
  lagging_indicators: []
  stop_conditions: []
```

## Probe design

A good probe is:

- small;
- reversible or bounded;
- observable;
- tied to the system type;
- able to disconfirm the hypothesis;
- monitored at the right time scale.
