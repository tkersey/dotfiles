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

## DART interaction layer

Use [dart-interaction-layer.md](dart-interaction-layer.md) as the conversational front end when the situation is ambiguous, mixed, or probe-driven.

DART structures the diagnosis:

```text
Deconstruct -> Analyze -> Recognize -> Test
```

It does not create a second authority. A DART trace compiles into `cybernetic_context` or `cybernetic_packet`; Cybernetic still owns leverage selection, mutation policy, downstream routing, and monitoring.

## Shared context

Use this compact field in other skills:

```yaml
cybernetic_context:
  required: yes | no
  trigger: "..."
  dart_trace_ref: "..." # optional; required when the expanded DART trace is decision-relevant
  system_type: clear | complicated | complex | chaotic | mixed | unknown
  pattern: "..."
  feedback_loop: "..."
  leverage_level: parameter | buffer | stock_flow_structure | delay | balancing_loop | reinforcing_loop | information_flow | rules | self_organization | goal | paradigm | none
  selected_intervention:
    status: selected | observe_more | stabilize | blocked | no_action
    route: checklist | expert_analysis | safe_to_fail_probe | stabilize_first | redesign_feedback | change_rules | change_goal | handoff | blocked
    downstream_skill: actuating | review-fold | universalist | reduce | negative-ledger | tune | proof-patch | none
  local_patch_allowed: yes | no
  temporary_containment:
    allowed: yes | no | not_applicable
    expiry_or_review: "..."
    durable_followup_owner: "..."
  monitoring_or_probe: "..."
```

`status` is the decision state. `downstream_skill` is the owner. Do not encode `blocked` as though it were a skill owner.

## Evidence discipline

Material claims about hidden structure, causal connections, mental models, or feedback loops should distinguish observation from inference:

```yaml
cybernetic_claim:
  statement: "..."
  status: observed | inferred | hypothesized | unknown
  evidence_refs: []
  confidence: high | medium | low | unknown
  competing_explanations: []
  disconfirming_observation: "..."
```

A coherent narrative without evidence or a falsifier is not sufficient for consequential intervention.

## Mutation policy

When `local_patch_allowed: no`, downstream execution must block a durable local point fix unless a successor Cybernetic context reopens that route.

Emergency containment is separate from durable correction. A chaotic system may permit a bounded temporary containment action while durable local mutation remains denied. The containment record must include a review or expiry condition and a durable follow-up owner.

## Use when

- repeated events imply structure;
- same-cluster review findings recur;
- a prior fix created new adjacent failures;
- incentives, proxies, metrics, delayed feedback, or local-vs-whole tradeoffs matter;
- the system type is ambiguous;
- subsystem classifications differ;
- chaotic stabilization may be needed.

## Do not use when

- one clear local bug has a direct owner and direct proof;
- the route is already selected and only execution remains;
- the question is purely artifact formatting or local implementation.
