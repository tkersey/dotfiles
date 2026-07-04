---
name: goal-grind
description: "Execute a GoalContract through recursive work/evidence loops: choose one frontier node, act minimally, verify, fold evidence, memoize repeated classes, and continue or stop. Use for /goal grindability, hard debugging, review closure, and migrations with proof surfaces."
metadata:
  version: "1.0.0"
  activation_cost: medium
  default_depth: high
---

# Goal Grind

## Mission

Drive a recursive coding goal without becoming a random walk.

```text
unfold next work -> act -> verify -> fold evidence -> memoize -> continue|stop
```

Use the smallest state artifact that can keep the loop honest.

## Loop state

For lightweight goals, state may be kept in the answer and `update_plan`.
For material goals, use a local `.goal/` directory only when it is ignored or explicitly local-only for the repository:

```text
.goal/contract.yml
.goal/workgraph.jsonl
.goal/attempts.jsonl
.goal/evidence.yml
.goal/memo.jsonl
.goal/proof.md
```

For durable, multi-plan, fenced, or resource-sensitive work, use `$st` instead of inventing a parallel plan store.

## Attempt row

```json
{
  "attempt_id": "A001",
  "goal_id": "goal-...",
  "node_id": "W001",
  "mode": "minimal-fix",
  "hypothesis": "...",
  "changed_paths": [],
  "commands": [],
  "result": "passed|failed|blocked|regress",
  "failure_signature": "",
  "score_delta": "",
  "kept": true,
  "next": ""
}
```

## Procedure

1. Read or create the GoalContract.
2. Create or refresh the WorkGraph when decomposition matters.
3. Select exactly one ready node unless `branch-race` mode is active.
4. State the hypothesis in one sentence.
5. Make the smallest owner-correct change for that node.
6. Run the node verifier or record why it cannot run.
7. Call `$evidence-fold` on test output, diffs, logs, and artifacts.
8. Continue only when the fold says `continue`.
9. Stop when the fold says `done`, `blocked`, `regress`, or `invalid-proof`.

## Modes

```yaml
goal_grind_mode:
  persistence: update_plan|goal-artifacts|st
  implementation: proof-only|minimal-fix|refactor-kernel|branch-race
  review_scope: none|in-scope-only|adjudicate-all|user-selected
  frontier: verifier-first|highest-risk-first|representative-class-first|dependency-order
  proof_bar: focused|current-artifact|release-ready
```

## Minimality rule

Minimal does not mean local. Minimal means the smallest change that fixes the owning cause without making future work worse.

Prefer `refactor-kernel` over local patching when many local fixes would duplicate an invariant check, adapter, state transition, proof obligation, review-only special case, or owner boundary.

## `$st` boundary

`$st` is not deprecated.

Use `$st` when any of these are true:

```text
multiple plans or branches need durable coordination
resource claims or fencing tokens are required
the task spans independent worktrees
overlapping edits must be serialized
branch epoch / base-head proof matters
the user explicitly asks for $st or .step/st-plan.jsonl already participates
```

Do not start `$st` merely because the goal has several steps. Use `update_plan` or `goal-workgraph` first.

## Guardrails

- Do not weaken tests, skip checks, or delete assertions to satisfy a goal.
- Do not implement raw review prose without `$review-fold`.
- Do not broaden scope after a new observation; fold it first.
- Do not continue after regression unless the next action is isolate, revert, or prove non-regression.
- Do not claim completion without current-artifact evidence.
