---
name: goal-contract
description: "Compile an accepted goal, implementation spec, review campaign, migration, or hard debugging loop into a compact source-bound GoalContract. Use before multi-step execution to bind outcome, verifier, authority source, artifact scope, constraints, review policy, stop conditions, and human-owned ambiguity."
---

# Goal Contract

## Mission

Compile intent into the smallest source-bound contract that can be projected
into the Zig kernel's `actuation-open/v1` authority, path scope, terminal route,
and verifier-backed obligations. This skill records authority; it does not
grant, select, or execute mutation.

## GC-v2

~~~yaml
goal_contract:
  version: GC-v2
  goal_id:
  objective:
    summary:
    mode: direct | goal | review | debug | migration | hardening
    non_goals: []
  source:
    kind: accepted-spec | direct-goal
    source_ref:
    source_digest:
    execution_authority_ref:
    authority_owner: spec-pipeline | user
    current: true | false
  artifact_scope:
    repo:
    base_sha:
    branch:
    head_sha:
    state_fingerprint:
    allowed_paths: []
  done:
    success_state: []
    explicitly_not_done_when: []
    stop_when: success | blocked | invalid-proof
  verification:
    primary_checks: []
    secondary_checks: []
    negative_checks: []
    artifacts_to_inspect: []
    unavailable_checks: []
  constraints:
    must_preserve: []
    forbidden_changes: []
    compatibility: []
    public_behavior: preserve | may-change-with-proof | unspecified
  review_policy:
    active: true | false
    relation_to_goal: in-scope-only | include-nearby-risk | adjudicate-all
    default_disposition: classify-before-resolution
    repair_policy: semantic-non-growth
    strategy_owner: review-resolution/v1
    reabstraction_trigger:
      - repeated-class
      - ownership-boundary
      - dominated-abstraction
      - new-semantic-machinery
  authority:
    mutation_requested: true | false
    dependency_changes_allowed: true | false
    public_effects: forbidden | ship-only
    unsupported_coordination_required: true | false
  ambiguity:
    discoverable_facts_to_research: []
    human_owned_decisions: []
    assumptions_allowed: []
~~~

## Procedure

1. Bind the contract to an accepted source and current artifact.
2. Separate the scope source from the execution authority reference.
3. Name terminal predicates and proof surfaces before work decomposition.
4. Preserve the accepted plan/spec without reinterpretation.
5. Set review policy to classification before resolution; raw findings never
   become work.
6. Use semantic non-growth for review-driven code changes.
7. Mark unsupported durable coordination explicitly; local workflows may not
   simulate claims or fencing.
8. Hand the contract to `$goal-actuating`. Use `$goal-workgraph` only when
   decomposition changes execution.
9. Assign every success predicate to at least one exact verifier command and
   `implementation`, `review`, `ship`, or `acceptance` proof kind before
   opening a material kernel generation; an unobservable obligation blocks.
10. Inspect the complete source-to-open projection before `ledger open --source
    actuation`; the kernel conserves accepted obligations but cannot recover an
    omitted predicate.

## Guardrails

- A plan handoff is scope and policy, not mutation authority.
- A review source is evidence, not mutation authority.
- A gate-only specification result is not an executable source.
- Do not recreate or loosen an accepted contract inside an executor.
- Ask the human only for choices that inspection cannot resolve.
