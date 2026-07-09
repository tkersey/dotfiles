---
name: agent-loop-schemes
description: "Translate an accepted GoalContract into normalized actuation-run step topology. Use when work has repeated classes, migrations, debugging history, review campaigns, proof fanout, branch comparison, or nontrivial stopping conditions; remain advisory and never grant mutation or completion."
---

# Agent Loop Schemes

## Mission

Describe the smallest step topology that `$goal-actuating` can place inside
`actuation-run/v1`.

~~~text
GoalContract
-> run-topology-advice/v1
-> $goal-actuating selects and records steps
~~~

This skill owns topology advice only. It does not create execution authority,
run actions, fold evidence, count review attempts, or close the goal.

## Advice shape

~~~yaml
run_topology_advice:
  version: run-topology-advice/v1
  goal_id:
  source_digest:
  shape: direct | iterative | memoized-migration | debug-history | review-closeout | branch-comparison
  step_producer:
    rule:
    owner_boundary:
    decomposition:
  step_template:
    kinds: []
    required_bindings: []
    verifier_rule:
  evidence_rule:
    reducer: evidence-fold
    continuation_requires_current_fold: true
  review_rule:
    classifier: review-fold
    resolution: review-resolution/v1
    raw_findings_are_steps: false
  parallelism:
    mode: none | scout-fanout | review-class-fanout | proof-fanout | branch-comparison
    safe_when: []
    fan_in_owner: goal-actuating
  stop_rule:
    success:
    blocked:
    invalid_proof:
  invalidators: []
  next_owner: goal-actuating
~~~

## Selection

- Use `direct` for one bounded step with one known verifier.
- Use `iterative` for an ordinary dependency-ordered goal.
- Use `memoized-migration` when many failures share one repair rule.
- Use `debug-history` when hypotheses or failure signatures may repeat.
- Use `review-closeout` when findings must be classified, resolved, repaired,
  and reviewed to a current clean suffix.
- Use `branch-comparison` only when isolated strategies share one verifier.

## Laws

1. Every material action becomes one selected run step.
2. Every continuation consumes a current evidence fold.
3. Review findings become resolution classes before they become work.
4. Repeated owner-boundary pressure becomes one replacement-kernel node.
5. Parallel leaves must be resource-disjoint and fold back through the lead.
6. Public effects remain outside the topology and belong to `$ship`.
7. Only a live closure decision completes the goal.

## Procedure

1. Bind advice to the accepted source digest and GoalContract.
2. Choose one shape and one stop rule.
3. Name the work producer, owner boundary, verifier, and evidence reducer.
4. Preserve repeated-class memoization and invalid strategies.
5. Describe only safe parallelism; shared owners remain serial.
6. Hand advice to `$goal-actuating`, which decides whether to project a
   WorkGraph.

## Guardrails

- Do not invent a persistent controller.
- Do not emit executable work from raw review prose.
- Do not choose product scope or mutation authority.
- Do not create a second runtime beside `$goal-actuating`.
- Do not treat topology advice as proof or closure.
