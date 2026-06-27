---
name: failure-memory
description: "Use when goal or review loops repeat failures, oscillate, regress, or encounter many same-shaped compiler/test/review findings. Clusters failure signatures, memoizes solved and invalid strategies, and prevents repeated work."
metadata:
  version: "1.0.0"
  activation_cost: low
  default_depth: standard
---

# Failure Memory

## Mission

Use history operationally.

```text
attempt history + failure signatures -> memoized subproblem classes
```

This is the histomorphic/dynamorphic part of the goal runtime: later decisions can see prior results and avoid recomputing the same failed route.

## Memo row

```json
{
  "memo_key": "review-nullability-boundary",
  "class": "strict-nullability-migration",
  "representative_paths": [],
  "failed_strategies": [],
  "working_strategy": "",
  "invalid_strategies": [],
  "proof": [],
  "reuse_rule": "",
  "expires_when": ""
}
```

## Procedure

1. Read attempts, evidence folds, review folds, negative ledger entries, and relevant learnings when available.
2. Cluster by failure signature, review equivalence class, invariant, owner boundary, or proof gap.
3. Mark repeated invalid strategies so `$goal-grind` does not retry them.
4. Promote one representative fix before applying bulk edits.
5. Emit memo rows that change future frontier selection.
6. Hand durable, transferable lessons to `$learnings` only when they meet its decision-delta bar.

## Guardrails

- Do not store raw transcript summaries.
- Do not call something memory unless it changes a future decision.
- Do not promote local goal memo rows into durable memory without `$learnings` or `$memory-source-notes`.
- Do not overgeneralize a memo beyond its proof surface.
