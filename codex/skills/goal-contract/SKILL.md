---
name: goal-contract
description: "Start or tighten a /goal, long-running coding task, review campaign, migration, or hard debugging loop by compiling intent into a compact GoalContract with outcome, verifier, constraints, boundaries, review policy, authority, stop conditions, and human-owned ambiguity."
metadata:
  version: "1.0.0"
  activation_cost: low
  default_depth: standard
---

# Goal Contract

## Mission

Compile intent into the smallest contract that can drive a recursive goal loop.

```text
user intent + current artifact facts
-> GoalContract
-> work can unfold, evidence can fold, and stopping can be judged
```

This skill replaces large upfront specification ceremony for ordinary goal work. It does not replace `$grill-me`, `$codebase-doctrine`, or `$st`; it records when those specialist effects are required.

## Use when

- The user starts a `/goal`.
- The task is larger than one direct edit and has a verifiable stopping condition.
- Reviews, failures, migrations, or repeated attempts need one governing outcome.
- The agent is tempted to keep going without a stop rule.

Do not use for trivial one-shot edits, pure prose answers, or already-bound `$st` execution slices.

## Contract schema

```yaml
goal_contract:
  version: GC-v1
  id: goal-YYYYMMDD-short-name
  objective:
    summary:
    mode: direct|goal|review|debug|migration|hardening|st-governed
    non_goals: []
  done:
    success_state: []
    explicitly_not_done_when: []
    stop_when: success|blocked|budget|invalid-proof
  verification:
    primary_checks: []
    secondary_checks: []
    artifacts_to_inspect: []
    negative_checks: []
    unavailable_checks: []
  constraints:
    must_preserve: []
    forbidden_changes: []
    compatibility: []
    public_behavior: preserve|may-change-with-proof|unspecified
  boundaries:
    allowed_paths: []
    forbidden_paths: []
    allowed_tools: []
    external_side_effects: none|read-only|requires-explicit-approval
    public_tracker_side_effects: forbidden-without-explicit-intent
  review_policy:
    active: yes|no
    relation_to_goal: in-scope-only|include-nearby-risk|adjudicate-all|user-selected
    default_disposition: classify-before-code
    minimality: proof-only-first|minimal-fix|refactor-kernel
    reabstraction_trigger: repeated-class|ownership-boundary|surface-tax|canonical-owner|none
    response_mode: no-public-comments|draft-comments|reply-when-explicitly-asked
  authority:
    mutation_allowed: yes|no
    dependency_changes_allowed: yes|no
    deployment_allowed: no
    durable_orchestration: update_plan|goal-workgraph|st-required
  ambiguity:
    discoverable_facts_to_research: []
    human_owned_decisions: []
    assumptions_allowed: []
  grindability:
    verifier_cost: low|medium|high
    feedback_quality: strong|partial|weak
    decomposition: easy|mixed|hard
    metric_gaming_risk: low|medium|high
```

## Procedure

1. Identify the task shape: direct, goal, review, debug, migration, hardening, or st-governed.
2. Research discoverable repository facts before asking the user questions.
3. Separate observed facts from claims, proposals, and speculation.
4. Name the success state and proof surface before work graph or mutation.
5. Bind review policy if review comments, CAS findings, or review-like claims are involved.
6. Choose a persistence level: `update_plan`, `goal-workgraph`, or `$st`.
7. Escalate to `$grill-me` only for material human-owned choices.
8. Emit `GoalContract` and stop or hand off.

## Handoffs

- `$goal-workgraph` when decomposition matters.
- `$goal-grind` when the next move is executable.
- `$review-fold` when review pressure is present.
- `$codebase-doctrine` when correctness doctrine or authority maps are missing.
- `$grill-me` when human-owned choices block the contract.
- `$st` only when durable orchestration, resource claims, or fencing is required.

## Guardrails

- Do not create a large spec unless semantic closure is still the blocker.
- Do not ask the user for discoverable facts.
- Do not treat reviews as implementation instructions.
- Do not use `$st` merely because work has multiple steps.
- Do not claim a goal is grindable when no verifier or proof surface exists.
