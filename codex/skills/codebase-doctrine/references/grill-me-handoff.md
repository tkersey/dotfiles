# `$grill-me` handoff for Codebase Doctrine

`$grill-me` owns only material user judgments. It does not analyze the
repository, infer current laws, choose knowledge destinations, or design skill
files.

## Mandatory dispatch

When DIG-v2 sets `grill_required: yes`, Codebase Doctrine must not keep
working locally. The validated DIG must include:

```yaml
gate:
  doctrine_may_proceed: no
  intent_route:
    route: grill-me
    hard_stop: yes
    next_action: activate_grill_me
    handoff_kind: codebase_doctrine_grill_handoff
    handoff_digest: sha256:...
```

The root must load `$grill-me` immediately with the exact
`codebase_doctrine_grill_handoff`. The root must not ask the material DIG
questions directly, choose defaults, compile CDI-v2, or continue doctrine
analysis until the returned `grill_decision_packet` is bound to the handoff and
`plan_allowed: true`.

## CDGH-v2

```yaml
codebase_doctrine_grill_handoff:
  handoff_version: CDGH-v2
  gate_id:
  provisional_artifact_state_digest:
  current_frame:
  researched_fact_ids: []
  working_defaults: []
  material_judgment_gaps:
    - gap_id:
      lane:
      question:
      why_material:
      options: []
  allowed_question_lanes: []
  forbidden_questions:
    - discoverable repository facts
    - implementation design
    - skill-file content
    - repository laws not yet researched
  closure_projection:
    - target
    - consumers
    - posture
    - desired_products
    - primary_correctness_question
    - primary_risk_or_priority
    - correctness_priorities
    - non_goals
    - proof_bar
    - compatibility_posture
    - persistence_posture
```

Ask at most three high-leverage questions per round.

## Required grill closure

The normal `grill_decision_packet` must add:

```yaml
codebase_doctrine_closure:
  source_gate_id:
  source_handoff_digest:
  resolved_gap_ids: []
  deferred_gap_ids: []
  doctrine_projection:
    target:
    consumers: []
    posture:
    desired_products: []
    primary_correctness_question:
    primary_risk_or_priority:
    user_supplied_invariant_hypotheses: []
    correctness_priorities: []
    non_goals: []
    proof_bar:
    compatibility_posture:
    persistence_posture:
    skill_portfolio_requested:
    enforcement_routing_requested:
    assumptions: []
    deferred_questions: []
```

`plan_allowed: true` is valid only when every material DIG gap is resolved and
`deferred_gap_ids` is empty.

The compiler checks gate ID, handoff digest, and exact gap closure.
