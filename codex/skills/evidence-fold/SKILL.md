---
name: evidence-fold
description: "Fold tests, diffs, logs, benchmarks, screenshots, review results, and current Git state into a bounded verdict: done, continue, regress, blocked, invalid-proof, ask-human, or refactor-kernel."
---

# Evidence Fold

## Mission

Consume owner-issued implementation and proof evidence into a bounded
current-head decision.

Within Actuating, EF-v1 is a discardable supporting view over the current Goal,
exact Git head, changed paths, validation outputs, and cited owner receipts. It
does not create authority, persist workflow state, select the next action, or
become a completion record.

```text
current owner evidence -> Evidence Fold -> recommendation
```

## Shape

```yaml
evidence_fold:
  version: EF-v1
  goal:
  artifact_state:
    repository:
    base:
    head:
    tree:
    changed_paths: []
  evidence:
    observed: []
    commands:
      passed: []
      failed: []
      unavailable: []
    artifacts_inspected: []
    review_receipts: []
  progress:
    status: done | continue | regress | blocked | invalid-proof | ask-human | refactor-kernel
    largest_remaining_failure:
    next_frontier:
  proof:
    supports_done_claim: yes | no
    proof_gaps: []
    residual_risks: []
    stale_or_missing_head_binding: yes | no
  anti_gaming:
    tests_deleted: yes | no | unknown
    assertions_weakened: yes | no | unknown
    checks_skipped: yes | no | unknown
    coverage_reduced: yes | no | unknown
    behavior_outside_goal_changed: yes | no | unknown
  recommendation:
    action: stop | continue | revert | isolate | ask-human | refactor-kernel | use-review-fold
    reason:
```

A node-level `done` requires exact current-head binding,
`supports_done_claim=yes`, no proof gaps, passing required observations, and
`recommendation.action=stop`. Actuating still evaluates whole-goal closure.

## Procedure

1. Bind every input to the current Git head or mark proof invalid.
2. Accept review pressure only after `$review-fold` has classified the observed
   fact against the current Goal and head.
3. Separate passed, failed, unavailable, and stale evidence.
4. Compare with a prior attempt only when its exact owner evidence is available.
5. Check anti-gaming before accepting improvement.
6. Name the largest remaining failure or proof gap.
7. Recommend one next action.

Return `refactor-kernel` when local fixes pass narrowly but leave a shared cause:

```text
the same failure appears at multiple call sites
findings collapse to one missing semantic mechanism
new tests would be wound-specific
the patch tolerates invalid state rather than preventing it
the canonical owner remains bypassed
```

## Guardrails

- Passing tests alone do not satisfy untested required observations.
- A stale command log cannot prove the current head.
- Absence of failure is not proof when the verifier did not run.
- Do not recommend more code when proof-only closure or review rejection is
  sufficient.
- Do not convert node `done` into whole-goal completion.
- Do not require or emit a Construction ref, operation step ID, Evidence Ledger
  event, or Ledger command.
