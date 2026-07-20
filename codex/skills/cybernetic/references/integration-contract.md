# Cybernetic Integration Contract

`$cybernetic` is the sensemaking and leverage-selection layer.

It answers:

```text
What kind of system are we in?
What pattern is being produced?
What feedback loops sustain it?
What leverage level should we intervene at?
Which downstream skill owns the action?
```

## Shared context

Use this compact field in other skills:

```yaml
cybernetic_context:
  required: yes | no
  trigger: "..."
  system_type: clear | complicated | complex | chaotic | mixed | unknown
  pattern: "..."
  feedback_loop: "..."
  leverage_level: parameter | buffer | stock_flow_structure | delay | balancing_loop | reinforcing_loop | information_flow | rules | self_organization | goal | paradigm | none
  selected_intervention:
    route: checklist | expert_analysis | safe_to_fail_probe | stabilize_first | redesign_feedback | change_rules | change_goal | handoff | blocked
    downstream_skill: actuating | blocked | review-fold | universalist | reduce | negative-ledger | tune | proof-patch | none
  local_patch_allowed: yes | no
  monitoring_or_probe: "..."
```

## Use when

- repeated events imply structure;
- same-cluster review findings recur;
- a prior fix created new adjacent failures;
- incentives, proxies, metrics, delayed feedback, or local-vs-whole tradeoffs matter;
- the system type is ambiguous;
- chaotic stabilization may be needed.

## Do not use when

- one clear local bug has a direct owner and direct proof;
- the route is already selected and only execution remains;
- the question is purely artifact formatting or local implementation.
