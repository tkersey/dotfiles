---
name: evidence-fold
description: "Fold tests, diffs, logs, benchmarks, screenshots, review results, and artifact state into a structured verdict: done, continue, regress, blocked, invalid-proof, ask-human, or refactor-kernel."
---

# Evidence Fold

## Mission

Consume implementation and proof evidence into a node-level decision.

```text
EvidenceTree -> Verdict
```

This reducer decides whether the current node can stop, continue, revert, ask,
or reframe. `done` closes the node; only `closure-decision/v1` may complete the
parent goal.

## Verdict schema

```yaml
evidence_fold:
  version: EF-v1
  evidence_id:
  run_id:
  step_id:
  artifact_state:
    repo:
    base_sha:
    branch:
    head_sha:
    state_fingerprint:
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

For actuation, `run_id` and `step_id` are the exact `actuation-run/v1`
identities. `artifact_state` is the post-step binding; `changed_paths` is the
observed path set and must equal the completed step claim. A closure-eligible
completed step requires `progress.status=done`, `supports_done_claim=yes`, no
proof gaps, and `recommendation.action=stop`.

## Procedure

1. Bind evidence to current branch/head/diff or mark proof invalid.
2. Accept review evidence only after `$review-fold` classification and, for
   material findings, `review-resolution/v1`. Raw review output is not EF input.
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
