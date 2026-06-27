---
name: actuating
description: "User-facing workflow for implementation after spec work. Use `/goal $actuating` to run `$spec-pipeline` then `$goal-actuating`: get an accepted implementation spec, choose the execution mode, require $cas for workflow review, implement through the goal runtime, and close with current-artifact proof."
metadata:
  version: "6.0.0"
  activation_cost: medium
  default_depth: high
---

# Actuating

## Mission

Run the implementation workflow without making the user manage the lower-level goal skills.

```text
implementation request or draft spec
-> $spec-pipeline in gate-only/no-plan mode when the implementation spec is not yet accepted
-> $goal-actuating
-> proof-bearing result
```

Use it as:

```text
/goal $actuating implement the accepted spec
```

`$actuating` does not directly edit code, claim resources, or patch review findings. It routes to the skill that should act.

## Relation to the old execution controller

The former transaction-controller behavior is still available as **st-governed mode**.

Use st-governed mode when the accepted work requires:

```text
stable plan identity
existing .ledger/st or .step/st-plan.jsonl state
resource claims
fencing tokens
external worktrees
serialized integration
branch/head proof
multi-plan coordination
```

In that mode, `$actuating` hands off to `$goal-actuating`, which then routes through `$st` and `$fixed-point-driver`.

## Normal flow

### Spec-first implementation

```text
$spec-pipeline on <draft implementation spec> in gate-only/no-plan mode
/goal $actuating implement the accepted spec
```

The workflow performs:

```text
1. Accept or refresh the implementation spec with $spec-pipeline in gate-only/no-plan mode.
2. Treat the accepted spec as the source of truth.
3. Invoke $goal-actuating in spec-first mode.
4. Derive a goal contract from the accepted spec.
5. Choose update_plan, goal-artifacts, or $st persistence.
6. If code review is required, run it through $cas.
7. Use $review-fold before any review-originated code change.
8. Execute accepted work through $goal-grind or $st-governed slices.
9. Fold evidence after material verification.
10. Emit proof-patch or explicit $ship handoff.
```

### Direct goal implementation

Use when the user goal already contains scope, non-goals, done state, constraints, and proof checks:

```text
/goal $actuating <objective>, verified by <checks>, preserving <constraints>
```

If the request is still ambiguous, `$actuating` must call `$spec-pipeline` in gate-only/no-plan mode or stop as blocked rather than inventing scope.

### Review-first implementation

Use when the work is review closure:

```text
/goal $actuating close the review for this branch
```

The workflow obtains review input from `$cas` when fresh or exhaustive review is needed, then folds it:

```text
$cas review findings
-> $review-fold
-> reject | proof-only | minimal-fix | refactor-kernel | ask-human | follow-up
-> implement only accepted code-change liabilities
-> evidence-fold
-> proof-patch
```

Raw review prose never reaches implementation directly.

### Dry actuation plan

Use when the user wants to inspect execution shape but not mutate:

```text
/goal $actuating dry-plan the accepted spec
```

Output only:

```text
goal contract summary
mode selection
optional work list
$st required? yes/no
review source required? none|cas-probe|cas-lane|cas-exhaustive
proof obligations
blockers
```

## Required source handling

Before running `$goal-actuating`, establish one of:

```text
accepted implementation spec
direct user goal with enough proof surface
review findings bound to current diff and intended change
plan handoff / $st handoff for st-governed mode
```

If none exists, run `$spec-pipeline` in gate-only/no-plan mode or stop with:

```yaml
actuating_status:
  verdict: blocked-needs-accepted-spec
  next_owner: $spec-pipeline|$grill-me|$codebase-doctrine
  reason:
```

## Runtime handoff

`$actuating` owns the handoff, not the internals. It asks `$goal-actuating` to map:

```text
accepted spec -> goal contract
goal contract -> work list only if decomposition changes execution
review requirement -> $cas review source mode
CAS/existing review output -> $review-fold disposition before code
work list -> $goal-grind next action
verification output -> $evidence-fold verdict
completion -> $proof-patch or $ship handoff
```

## CAS review mandate

If `$actuating` performs code review or relies on a review gate, it must use `$cas` as the review backend through `$goal-actuating`.

Use `$cas` review when:

```text
the user asks for review closure, code review, or exhaustive review
the accepted spec includes review in the proof requirements
proof-patch or ship-handoff would otherwise rely on a review claim
review-first mode needs a fresh review artifact
repeated review/fix cycles need a persistent detached lane
```

Existing PR comments or prior review artifacts may be consumed as existing review pressure, but they do not replace a requested fresh or exhaustive CAS review.

## Mode selection

Choose the narrowest mode that can complete safely:

```yaml
actuating_mode:
  source: direct-goal|spec-first|review-first|dry-plan|st-governed
  persistence: update_plan|goal-artifacts|st
  implementation: proof-only|minimal-fix|refactor-kernel|branch-race
  review_source: none|existing-review|cas-probe|cas-lane|cas-exhaustive
  closure: proof-patch|ship-handoff|blocked
```

Default:

```text
spec-first + update_plan + minimal-fix + proof-patch
```

Switch to `review-first` when reviews, CAS findings, or reviewer suggestions are present.
Switch to `cas-exhaustive` when exhaustive review is requested or required by the proof bar.
Switch to `refactor-kernel` when repeated findings share an owner boundary.
Switch to `st-governed` only when durable claims, fencing, worktrees, or serialized integration are required.
Switch to `ship-handoff` only when PR/publication intent is explicit or inherited from the accepted spec.

## Stop rules

Stop rather than implement when:

```text
$spec-pipeline has not approved execution
scope, non-goals, compatibility, or proof bar are unresolved
review findings expand product/API scope
raw review text has not been reduced to dispositions
review is required but $cas review is unavailable or not run
$st authority is required but absent
verification regresses and the next action is not isolate/revert/prove
public tracker or PR side effects would occur without explicit intent
```

## Final report

```text
Actuating:
- source: direct goal | accepted spec | review | $st handoff
- authority source:
- mode / persistence:
- review source / CAS verdict, if required:
- goal contract / work list:
- review-fold disposition:
- execution owner: goal-grind | st/fixed-point-driver | none
- evidence-fold verdict:
- proof-patch / ship handoff:
- blockers / residual risk:
```

If no accepted spec or goal contract exists, say:

```text
actuation verdict: blocked-needs-accepted-spec
```

If $st authority is required but not obtained, say:

```text
actuation verdict: st-authority-blocked
```

If review is required but CAS review is unavailable or not run, say:

```text
actuation verdict: cas-review-blocked
```

Do not describe direct implementation as a fenced actuation run.
