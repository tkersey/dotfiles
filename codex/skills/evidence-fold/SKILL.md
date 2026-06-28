---
name: evidence-fold
description: "Fold tests, diffs, logs, benchmarks, screenshots, review results, and artifact state into a structured verdict: done, continue, regress, blocked, invalid-proof, ask-human, or refactor-kernel."
metadata:
  version: "1.0.0"
  activation_cost: low
  default_depth: standard
---

# Evidence Fold

## Mission

Consume evidence into a decision.

```text
EvidenceTree -> Verdict
```

This is the catamorphic side of the goal runtime. It decides whether the loop can stop, continue, revert, ask, or reframe.

## Verdict schema

```yaml
evidence_fold:
  version: EF-v1
  goal_id:
  node_id:
  artifact_state:
    branch:
    head:
    dirty_state: clean|dirty|unknown
    changed_paths: []
  evidence:
    observed: []
    commands:
      passed: []
      failed: []
      unavailable: []
    artifacts_inspected: []
    review_refs: []
  progress:
    status: done|continue|regress|blocked|invalid-proof|ask-human|refactor-kernel
    score_before:
    score_after:
    largest_remaining_failure:
    next_frontier:
  proof:
    supports_done_claim: yes|no
    proof_gaps: []
    residual_risks: []
    stale_or_missing_artifact_binding: yes|no
  anti_gaming:
    tests_deleted: yes|no|unknown
    assertions_weakened: yes|no|unknown
    checks_skipped: yes|no|unknown
    coverage_reduced: yes|no|unknown
    behavior_outside_goal_changed: yes|no|unknown
  recommendation:
    action: stop|continue|revert|isolate|ask-human|spawn-branch-race|hand-off-st|use-review-fold
    reason:
```

## Procedure

1. Bind evidence to current branch/head/diff or mark proof invalid.
2. Separate what passed, what failed, and what was not run.
3. Compare the new result to the prior attempt when available.
4. Check anti-gaming before accepting success.
5. Name the largest remaining failure or proof gap.
6. Recommend exactly one next action.

## Refactor-kernel result

Return `status: refactor-kernel` when local fixes pass narrowly but leave a shared cause intact:

```text
same bug appears in multiple call sites
review comments collapse to one missing abstraction
new tests would be wound-specific
the patch adds tolerance for invalid state instead of preventing it
the canonical owner is bypassed
```

## Guardrails

- Passing tests alone are insufficient when the goal also requires negative checks, review disposition, or artifact inspection.
- A stale command log cannot close a current-artifact goal.
- Absence of failure is not proof when the verifier did not run.
- Do not recommend more code when proof-only closure or review rejection is enough.
