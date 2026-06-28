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
review-adjudication
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
- review/fix/closure loop: use `$goal-actuating` or `$review-adjudication`;
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
    downstream_skill: goal-actuating | st-bounded-slice | review-adjudication | universalist | reduce | negative-ledger | tune | proof-patch | none
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
    downstream_skill: goal-actuating | st-bounded-slice | review-adjudication | universalist | reduce | negative-ledger | tune | proof-patch | none
    smallest_safe_move: "..."
    reversibility: reversible | partially_reversible | irreversible | unknown
    blast_radius: narrow | medium | broad | unknown
    leading_indicators: []
    lagging_indicators: []
    stop_conditions: []
  platform_view:
    mentors_or_outside_view: []
    data_needed: []
    time_comparison: []
  unintended_consequence_scan:
    who_might_game_it: []
    who_bears_costs: []
    second_order_effects: []
    delayed_harms: []
    local_vs_whole_tradeoff: "..."
  test_or_monitoring_plan:
    first_probe: "..."
    feedback_interval: "..."
    success_signal: "..."
    failure_signal: "..."
    rollback_or_adapt: "..."
  decision:
    recommendation: "..."
    confidence: high | medium | low | unknown
    next_action: "..."
```

## System classification

Classify before prescribing.

### Clear

Cause and effect are obvious, stable, and directly observable.

Use:

```text
checklist
standard work
precision
known process
```

Avoid overthinking and unnecessary innovation.

### Complicated

Cause and effect exist but require analysis, decomposition, or expertise.

Use:

```text
diagnosis
specialist expertise
modeling
root-cause analysis
comparison of alternatives
```

Avoid guessing and generic experts.

### Complex

Cause and effect are emergent and visible mostly in hindsight.

Use:

```text
safe-to-fail experiments
small probes
monitoring
adaptation
diverse perspectives
directional strategy
```

Avoid rigid plans, single-point forecasts, and pretending to control the system.

### Chaotic

Cause and effect are broken, hidden, or changing too fast to reason through.

Use:

```text
stabilize first
create safety
act quickly
bound harm
then sense and analyze
```

Avoid analysis paralysis.

### Mixed

Many real situations contain different subsystem types. Split them.

Example:

```text
technical rollout: complicated
human adoption: complex
incident response: chaotic until stabilized
checklist procedure: clear
```

## DART diagnostic

Use DART to quickly orient:

```text
D — Deconstruct: What are the parts, stocks, flows, and boundaries?
A — Analyze: What is the cause/effect relationship type?
R — Recognize: What pattern, archetype, or prior system does this resemble?
T — Test: What is the smallest safe probe or stabilizing action?
```

In chaos, T means stabilize first rather than experiment.

## Meadows ladder

Prefer higher leverage when available, but stay humble.

Approximate leverage order, from lower to higher:

```text
parameters / numbers
buffers
stock-flow structure
delays
balancing feedback
reinforcing feedback
information flows
rules / incentives / constraints
power to self-organize
goals
paradigms / mental models
ability to transcend paradigms
```

Rules:

- Do not obsess over parameters when structure, rules, goals, or mental models are producing the pattern.
- Do not jump to paradigm change when a missing information flow would solve the issue.
- Do not change goals or rules without scanning incentives, power, and second-order effects.
- Do not ignore delays; delayed feedback can make good actions look bad and bad actions look good.

## Iceberg model

When the user gives an event, move down the iceberg:

```text
Event: What just happened?
Pattern: What keeps happening over time?
Structure: What rules, incentives, flows, delays, and power relations produce it?
Mental model: What beliefs, goals, identities, or paradigms make the structure seem natural?
```

Do not stop at event-level explanation unless the system is clear and local.

## Stocks and flows

Ask:

```text
What is accumulating?
What drains it?
What fills it?
What is the buffer?
What is the bottleneck?
What is the delay between action and observable effect?
What stock is being ignored because it is intangible?
```

Common intangible stocks:

```text
trust
attention
morale
technical debt
organizational debt
reputation
skill
risk
customer goodwill
institutional memory
optionality
cognitive load
```

## Feedback loops

Name loops explicitly.

```yaml
feedback_loop:
  loop_id:
  type: reinforcing | balancing
  stock:
  signal:
  action:
  delay:
  gain:
  failure_mode:
```

Common failure modes:

- missing feedback;
- delayed feedback;
- distorted feedback;
- feedback routed to someone without decision rights;
- proxy metric replacing goal;
- response too strong or too weak;
- balancing loop overwhelmed by reinforcing loop.

## Incentive and cobra-effect scan

Before recommending a metric, reward, target, policy, or automation, ask:

```text
What behavior will this reward?
What proxy replaces the real goal?
Who can game it?
What gets worse if people optimize for the measure?
What delayed harm might appear after the success metric improves?
```

If the proxy can beat the purpose, redesign the rule or measure.

## Platform view

When inside the system, seek outside perspective through:

```text
mentor / outsider / stakeholder not captured by the current incentive
data / measurement independent of narrative
time / before-after and trend comparison
```

If all evidence comes from inside the current mental model, mark confidence lower.

## Intervention design

Match intervention to system type:

| System type | Best first move | Bad first move |
|---|---|
| clear | checklist / standard process | clever reinvention |
| complicated | analysis / expertise | generic intuition |
| complex | safe-to-fail probes / adaptation | rigid master plan |
| chaotic | stabilize / create safety | analysis paralysis |

## Output modes

### Standard

Use sections:

```text
System boundary
System type
Events -> patterns -> structure -> mental models
Stocks / flows / feedback
Incentives and delays
Leverage map
Intervention
Probe / monitoring plan
Cybernetic Bottom Line
```

### Fast

Use:

```text
System type:
Pattern:
Leverage:
Move:
Watch:
Cybernetic Bottom Line:
```

## Cybernetic Bottom Line

Always end with:

```text
Cybernetic Bottom Line:
- system_type:
- pattern:
- highest_leverage_available:
- selected_move:
- downstream_skill:
- why_not_lower_leverage:
- feedback_to_watch:
- next_action:
```

## Guardrails

- Do not confuse activity with progress.
- Do not optimize a subsystem without naming whole-system effects.
- Do not assume the measured proxy is the real goal.
- Do not ignore delayed feedback.
- Do not treat complex systems as controllable machines.
- Do not treat chaotic systems as analysis problems before safety is restored.
- Do not overgeneralize from one event.
- Do not use systems language to avoid making a concrete recommendation.
- Do not recommend broad transformation when a small feedback repair would work.
- Do not recommend a local metric, reward, or rule without a gaming scan.
- Do not claim certainty in complex systems; use probes and monitoring.
- Do not hand off implementation without naming downstream owner, proof/probe, and stop conditions.

## Companion skills

Use with:

- `$goal-actuating` when same-cluster review recurrence or review-process feedback needs execution routing.
- `$review-adjudication` when a review item signals system-pattern risk.
- `$review-adjudication` when counterexamples may represent system feedback in review findings.
- `$negative-ledger` when prior interventions failed or recurring strategies need exclusion.
- `$universalist` when the system diagnosis says the boundary artifact or shape of truth is wrong.
- `$reduce` when abstraction/layer tax may be producing the pattern.
- `$complexity-mitigator` when comprehension risk blocks action.
- `$tune` when the system is a skill/workflow usage loop.
- `$st` bounded execution when the selected intervention requires claims, fencing, worktrees, and proof-bound integration.
- `$proof-patch` when closure must prove feedback/probe readiness.
- `$goal-actuating` only after the system intervention has become a scoped implementation route.

## Resources

- [integration-contract.md](references/integration-contract.md)
- [system-types-and-dart.md](references/system-types-and-dart.md)
- [iceberg-model.md](references/iceberg-model.md)
- [leverage-ladder.md](references/leverage-ladder.md)
- [stocks-flows-feedback.md](references/stocks-flows-feedback.md)
- [incentives-and-cobra-effects.md](references/incentives-and-cobra-effects.md)
- [dancing-with-systems.md](references/dancing-with-systems.md)
- [intervention-design.md](references/intervention-design.md)
- [cybernetic-packet.md](references/cybernetic-packet.md)
- [example-invocations.md](references/example-invocations.md)
