# `$grill-me` Handoff for Codebase Doctrine

`$codebase-doctrine` may invoke `$grill-me` only for material user-owned intent decisions.

## CDGH-v1

```yaml
codebase_doctrine_grill_handoff:
  handoff_version: CDGH-v1
  gate_id:
  provisional_artifact_state:
  current_frame:
  researched_facts: []
  working_defaults: []
  material_judgment_gaps:
    - gap_id:
      lane:
      question:
      why_material:
      options: []
  allowed_question_lanes:
    - target_boundary
    - consumers
    - posture
    - desired_products
    - correctness_priorities
    - non_goals
    - proof_bar
    - persistence
  forbidden_questions:
    - repository facts discoverable from artifacts
    - implementation design
    - skill-file content
    - codebase laws not yet researched
  closure_projection:
    target:
    consumers:
    posture:
    desired_products:
    primary_invariant:
    correctness_priorities:
    non_goals:
    proof_bar:
    compatibility_posture:
    persistence_posture:
```

## Question pack

Ask no more than three high-leverage questions per round.

Preferred order:

1. Subject boundary: whole coherent repository, named subsystem, or cross-cutting workflow/law family.
2. Doctrine posture: descriptive, prescriptive, gap analysis, or mixed.
3. Desired products: atlas only, atlas plus knowledge routing, atlas plus root skill, or atlas plus focused candidates.

Later rounds may ask consumer, correctness priority, non-goal, proof bar, or persistence only when still material.

## Output

`$grill-me` emits its standard `grill_decision_packet`.

The following fields project naturally:

```text
goal                         -> target and desired products
problem_layer                -> doctrine posture/problem layer
target_user_or_maintainer    -> consumers
scope                        -> included/excluded boundaries
non_goals                    -> non-goals
primary_invariant            -> primary invariant
success_criteria             -> desired doctrine outcomes
proof_bar                    -> evidence/proof requirement
compatibility_posture        -> compatibility posture
locked_decisions             -> posture/products/priorities
researched_facts             -> intake provenance only
default_assumptions          -> CDI assumptions
deferred_questions           -> CDI deferred questions
plan_allowed                 -> doctrine inquiry may proceed
```

Do not insert repository-derived laws into the grill packet as if the user supplied them.

## Closure rule

Proceed only when `plan_allowed: true`.

This allows doctrine analysis only. It does not authorize code changes, skill creation, persistence, commit, or push.
