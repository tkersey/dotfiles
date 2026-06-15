# Review Governor Context

When `$resolve` acts as Review Governor, `$cybernetic` classifies repeated feedback patterns.

```yaml
cybernetic_context:
  required: yes | no
  system_type: clear | complicated | complex | chaotic | mixed | unknown
  pattern: "..."
  feedback_loop: "..."
  leverage_level: parameter | information_flow | rules | goal | paradigm | none
  selected_intervention:
    route: checklist | expert_analysis | safe_to_fail_probe | stabilize_first | redesign_feedback | change_rules | change_goal | handoff | blocked
    downstream_skill: resolve | fixed-point-driver | universalist | reduce | negative-ledger | none
  local_patch_allowed: yes | no
  monitoring_or_probe: "..."
  route_changed: yes | no
```

Use when repeated review events imply structure.

Do not use for isolated local bugs.
