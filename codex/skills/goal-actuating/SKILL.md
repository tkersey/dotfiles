---
name: goal-actuating
description: "Run an accepted implementation spec or direct /goal through the goal runtime. Builds a goal contract, chooses the execution mode, requires $cas for workflow review, then uses the work list, goal-grind, evidence-fold, review-fold, and proof-patch skills as needed."
metadata:
  version: "1.0.0"
  activation_cost: medium
  default_depth: high
---

# Goal Actuating

## Mission

Run approved work through the goal workflow.

```text
accepted implementation spec or direct goal
-> goal contract
-> execution mode
-> work list when useful
-> one focused action at a time
-> evidence
-> proof
```

`$actuating` is the user-facing wrapper. `$goal-actuating` is the runtime that does the lowering and routing.

## Inputs

```text
accepted implementation spec
plan or $st handoff
review findings bound to the current diff
direct /goal with enough proof surface
```

When an accepted implementation spec is present, treat it as the source of truth. Do not reinterpret scope, non-goals, compatibility, or proof requirements.

## Modes

```yaml
goal_actuating_mode:
  source: direct-goal|spec-first|review-first|dry-plan|st-governed
  persistence: update_plan|goal-artifacts|st
  implementation: proof-only|minimal-fix|refactor-kernel|branch-race
  review: none|existing-review|cas-probe|cas-lane|cas-exhaustive
  closure: proof-patch|ship-handoff|blocked
```

- `spec-first`: execute an accepted implementation spec without scope drift.
- `direct-goal`: execute a goal that already has outcome, constraints, and proof checks.
- `review-first`: classify review findings before code changes.
- `dry-plan`: show the goal contract and work list only; do not mutate.
- `st-governed`: hand off to `$st` and `$fixed-point-driver` when durable coordination owns the work.

## Procedure

1. Locate the accepted spec, plan handoff, review input, or direct goal.
2. If the work is not yet approved enough to execute, hand off to `$spec-pipeline` and stop.
3. Derive a goal contract with `$goal-contract`.
4. Choose `update_plan`, `goal-artifacts`, or `$st` persistence.
5. If the workflow performs fresh or exhaustive review, run `$cas` review.
6. Classify review findings with `$review-fold`.
7. Create a work list with `$goal-workgraph` only when decomposition changes execution.
8. Execute one useful action at a time with `$goal-grind`, unless `$st` owns execution.
9. Fold verification and review results with `$evidence-fold`.
10. Use `$failure-memory` when failures or review classes repeat.
11. Close with `$proof-patch`, or hand off to `$ship` only when publication is requested and ready.

## Spec to goal contract

Map the accepted spec into the goal contract:

```text
objective -> what must be done
non-goals -> what must not be done
success state -> when to stop
validation -> proof checks
compatibility -> behavior to preserve
rollback/risk -> stop and safety rules
review expectations -> review mode
human decisions -> questions for $grill-me
execution permission -> whether mutation is allowed
```

## CAS review mandate

If `$goal-actuating` performs code review, `$cas` is the review backend.

Use `$cas` review when:

```text
the user asks for review closure, code review, or exhaustive review
the accepted spec includes review in the proof requirements
review-first mode needs a fresh review artifact
repeated review/fix cycles need a persistent detached lane
proof-patch or ship-handoff would otherwise rely on a review claim
```

A goal may close without code review only when the accepted proof requirements do not include review and focused checks are enough. Once a review gate is present, CAS review is mandatory.

```text
$cas review findings
-> $review-fold
-> reject | proof-only | minimal-fix | refactor-kernel | ask-human | follow-up
-> $goal-grind only for accepted code-change liabilities
```

## Review behavior

Default review posture is `adjudicate-first`: classify and compress findings before code changes.

Prefer no-code outcomes when they are correct: `reject`, `proof-only`, `follow-up`, or `ask-human`.

Prefer `refactor-kernel` when several findings share one missing abstraction, invariant, canonical owner, state transition, or proof surface.

Exhaustive review is not optional once requested or required. `$review-fold` controls which findings become code changes; it must not remove the CAS review gate.

## Stop rules

Stop when:

```text
execution has not been approved
scope would drift from the accepted spec
review finding expands product/API scope
$st authority is required but absent
verification regresses
proof is stale or not bound to the current artifact
public tracker side effect would be needed without explicit intent
review is required but $cas review is unavailable or not run
```

## Output

```text
Goal Actuation:
- source: accepted spec | direct goal | plan handoff | review
- mode / persistence:
- review source / CAS verdict, if required:
- goal contract summary:
- work list / next action:
- review-fold disposition, if any:
- evidence-fold verdict:
- proof-patch / ship handoff:
- learnings or memory-source handoff, if justified:
```
