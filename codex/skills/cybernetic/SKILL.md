---
name: cybernetic
description: "Systems-thinking and feedback-control skill. Use for `$cybernetic`, cybernetics, complex adaptive systems, root-cause vs structure, feedback loops, stocks/flows, leverage points, incentives, delayed effects, unintended consequences, DART diagnosis, clear/complicated/complex/chaotic classification, intervention/policy design, organizational dynamics, product/business/ecosystem diagnosis, workflow loops, same-cluster review recurrence, or avoiding local optimizations that harm the whole. Produces cybernetic_context or cybernetic_packet; read-only unless routed to implementation."
metadata:
  version: "1.1.0"
  activation_cost: medium
  default_depth: adaptive
---

# Cybernetic

## Mission

`$cybernetic` is the systems-thinking and leverage-selection skill.

It helps the agent understand and act within systems by moving from:

```text
events -> patterns -> structures -> mental models -> leverage -> feedback-aware intervention
```

It does not merely identify causes. It asks:

```text
What pattern keeps being produced?
What structure produces it?
What feedback loops stabilize or amplify it?
Where are the delays, incentives, stocks, flows, and information gaps?
What intervention changes the system without making it worse?
```

## Core doctrine

```text
A system is connected parts producing a pattern.
Use $cybernetic when repeated events imply structure.
Do not use $cybernetic for isolated local work.
Do not optimize a part while damaging the whole.
Do not mistake an event for the system.
Do not use a clear-system checklist in a complex system.
Do not use analysis paralysis in chaos.
Do not intervene before identifying feedback, delay, incentives, and leverage level.
```

## Integration contract

`$cybernetic` classifies the system and selects leverage. It does not implement.

It should output a downstream owner:

```text
goal-actuating
st-bounded-slice
review-fold
negative-ledger
universalist
reduce
tune
proof-patch
blocked
none
```

Use it as a route-selection companion when repeated patterns, feedback loops, incentives, delayed effects, or whole-system tradeoffs matter.

Do not invoke it as ceremony for one clear local bug.

## Activation boundary

Use this skill when the task involves:

- systems thinking or cybernetics;
- repeated patterns with unclear causes;
- same-cluster review recurrence;
- skill or workflow loop theatre;
- organizational, social, technical, economic, product, or ecological dynamics;
- incentives, cobra effects, and unintended consequences;
- delayed feedback or long-term consequences;
- stocks, flows, queues, inventories, backlogs, trust, debt, reputation, risk, knowledge, morale, or capacity;
- loops, flywheels, vicious cycles, self-reinforcing or self-correcting behavior;
- choosing leverage points;
- diagnosing whether a problem is clear, complicated, complex, or chaotic;
- designing an intervention, policy, strategy, operating model, experiment, guardrail, or feedback process;
- avoiding local optimization, metric gaming, or overcorrection;
- understanding why a previous fix made the system worse.

Do not use as the primary skill when the task is only:

- straightforward implementation: use `$goal-actuating`;
- review/fix/closure loop: use `$goal-actuating` or `$review-fold`;
- code simplification only: use `$reduce`;
- final proof/closure only: use `$proof-patch`;
- broad skill tuning: use `$tune`;
- pure writing/formatting without system diagnosis.

Use `$cybernetic` as a companion lens when those skills need system classification, leverage analysis, or feedback-aware intervention design.

## Fast path: cybernetic_context

For companion use inside another skill, prefer this compact context:

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
    downstream_skill: goal-actuating | st-bounded-slice | review-fold | universalist | reduce | negative-ledger | tune | proof-patch | none
  local_patch_allowed: yes | no
  monitoring_or_probe: "..."
```

If used after a same-cluster stop rule, `local_patch_allowed` should usually be `no` unless the context proves the selected owner mutation is a system-level normal form rather than another local point fix.

## Full packet

For non-trivial systems work, emit:

```yaml
cybernetic_packet:
  packet_version: CYB-v1
  objective: "..."
  system_boundary:
    included: []
    excluded: []
    boundary_risk: "too_narrow | too_broad | adequate | unknown"
  system_type:
    classification: clear | complicated | complex | chaotic | mixed | unknown
    reason: "..."
    required_mode: checklist | expert_analysis | safe_to_fail_experiments | stabilize_first | split_by_subsystem
  observed_events: []
  repeating_patterns: []
  hidden_structure:
    parts: []
    connections: []
    rules_incentives_constraints: []
    information_flows: []
    decision_rights: []
    mental_models: []
  stocks_and_flows:
    stocks: []
    inflows: []
    outflows: []
    buffers: []
    bottlenecks: []
  feedback_loops:
    reinforcing: []
    balancing: []
    delayed_feedback: []
    missing_or_distorted_feedback: []
  incentives_and_gameability:
    intended_goal: "..."
    measured_or_rewarded_proxy: "..."
    gaming_risk: low | medium | high | unknown
    cobra_effect_risk: low | medium | high | unknown
  leverage_map:
    candidate_interventions:
      - intervention: "..."
        leverage_level: parameter | buffer | stock_flow_structure | delay | balancing_loop | reinforcing_loop | information_flow | rules | self_organization | goal | paradigm | transcend_paradigm
        expected_effect: "..."
        risk: "..."
        time_horizon: immediate | short | medium | long | unknown
    selected_leverage:
      intervention: "..."
      why_this_level: "..."
      why_lower_leverage_is_insufficient: "..."
      why_higher_leverage_is_not_available_or_not_needed: "..."
  intervention_design:
    route: no_action | observe_more | checklist | expert_analysis | experiment | stabilize | redesign_feedback | change_rules | change_goal | reframe | handoff | blocked
    downstream_skill: goal-actuating | st-bounded-slice | review-fold | universalist | reduce | negative-ledger | tune | proof-patch | none
    smallest_safe_move: "..."
    reversibility: reversible | partially_reversible | irreversible | unknown
    blast_radius: narrow | medium | broad | unknown
    leading_indicators: []
    lagging_indicators: []
    stop_conditions: []
```
