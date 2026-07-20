---
name: evidence-fold
description: "Fold tests, diffs, logs, benchmarks, screenshots, review results, and artifact state into a structured verdict: done, continue, regress, blocked, invalid-proof, ask-human, or refactor-kernel."
---

# Evidence Fold

## Mission

Consume implementation and proof evidence into a node-level decision. Within
Actuating, EF-v1 is a discardable supporting view over the current Goal,
Construction, subject, exact operation, and cited Evidence Ledger events. It
does not create authority, select the next operation, or become peer state.

```text
EvidenceTree -> Verdict
```

This reducer recommends whether the current node should stop, continue,
revert, ask, or reframe. Its output grants no operation authority. `done`
describes only the evaluated node; Actuating selects the next action and
applies the closure theorem to the whole goal.

## Verdict schema

```yaml
evidence_fold:
  version: EF-v1
  evidence_id:
  goal_id:
  construction_ref:
  operation_id:
  artifact_state:
    repo:
    subject_digest:
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
    action: stop|continue|revert|isolate|ask-human|spawn-branch-race|block-external-coordination|use-review-fold
    reason:
```

For Actuating, `construction_ref` and `operation_id` identify the exact current
Construction and Actuating-selected operation. `artifact_state` is the
post-operation subject binding; `changed_paths` must equal the observed path
set. A node-level `done` verdict requires `supports_done_claim=yes`, no proof
gaps, `recommendation.action=stop`, and passing cited observations.

## Procedure

1. Bind evidence to current branch/head/diff or mark proof invalid.
2. Accept a review finding only after `$review-fold` has classified it in a
   current Counterexample Set. Raw review prose is not EF input.
3. Separate what passed, what failed, and what was not run.
4. Compare the new result to the prior attempt when available.
5. Check anti-gaming before accepting success.
6. Name the largest remaining failure or proof gap.
7. Recommend exactly one next action.

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
- Do not convert node `done` into a goal-completion claim.
