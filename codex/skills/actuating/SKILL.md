---
name: actuating
description: "User-facing workflow façade for implementation after spec work. Use as `/goal $actuating` to run `$spec-pipeline -> $goal-actuating`: close or validate semantic spec, lower the accepted SGR-v2/spec into GC-v1, choose lightweight/review-first/st-governed mode, require $cas for workflow code review, execute through the recursive goal runtime, and close with current-artifact proof."
metadata:
  version: "6.0.0"
  activation_cost: medium
  default_depth: high
---

# Actuating

## Mission

Run the spec-to-implementation workflow without exposing the lower-level recursion machinery.

```text
user implementation intent / draft spec / accepted SGR-v2
-> $spec-pipeline when semantic closure is not yet proven
-> $goal-actuating
-> proof-bearing result
```

`$actuating` is now a workflow façade. It is the skill to invoke when you want to say:

```text
/goal $actuating implement the spec
```

It does not directly own code mutation, resource claims, or review patching. It routes to the owner that should act.

## Relation to the old execution controller

The former `$actuating` transaction-controller role is now the **st-governed mode** of this workflow.

Use st-governed execution when the accepted spec or plan requires:

```text
PSR-v1 / stable plan identity
.ledger/st or .step/st-plan.jsonl continuity
resource claims
fencing tokens
external worktrees
serialized integration
branch-epoch proof
multi-plan coordination
```

In that mode, `$actuating` must hand off to `$goal-actuating` with `mode: st-governed`, which then routes through `$st` and `$fixed-point-driver`. Do not perform direct mutation while still claiming fenced actuation authority.

## Normal user flow

### Spec-first implementation

```text
$spec-pipeline on <draft implementation spec>
/goal $actuating implement the accepted spec
```

The workflow performs:

```text
1. Find or create semantic closure with $spec-pipeline.
2. Treat SGR-v2 / implementation_spec.md as semantic authority.
3. Invoke $goal-actuating in spec-first mode.
4. Derive GC-v1 from the accepted spec.
5. Choose update_plan, goal-artifacts, or st-governed persistence.
6. If code review is part of the proof bar, run it through $cas.
7. Use review-fold before any review-originated code change.
8. Execute accepted work through goal-grind or st-governed slices.
9. Fold evidence after material verification.
10. Emit proof-patch or ship handoff.
```

### Direct goal implementation

Use when the user goal already contains scope, non-goals, done state, constraints, and proof surface:

```text
/goal $actuating <objective>, verified by <checks>, preserving <constraints>
```

If semantic closure is incomplete, `$actuating` must call `$spec-pipeline` or return a semantic-blocked result rather than inventing execution scope.

### Review-first implementation

Use when the work is review closure:

```text
/goal $actuating close the review for this branch
```

The workflow starts by obtaining review input from `$cas` when fresh/exhaustive review is needed, then folds it:

```text
$cas review verdict / findings
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
GC-v1 summary
mode selection
optional WG-v1 frontier
st-required? yes/no
review source required? none|cas-probe|cas-lane|cas-exhaustive
proof obligations
blockers
```

## Required source handling

Before running `$goal-actuating`, establish one of:

```text
accepted SGR-v2 with planning/execution allowed
accepted implementation_spec.md with no unresolved semantic blockers
direct user goal with enough proof surface to derive GC-v1
review findings bound to current diff and intended change
PSR-v1 / st handoff for st-governed mode
```

If none exists, run `$spec-pipeline` or stop with:

```yaml
actuating_status:
  verdict: semantic_blocked
  next_owner: $spec-pipeline|$grill-me|$codebase-doctrine
  reason:
```

## Spec-to-runtime lowering

`$actuating` owns the handoff, not the internals. It should ask `$goal-actuating` to map:

```text
implementation spec / SGR-v2 -> GC-v1 GoalContract
GC-v1 -> WorkGraph only if decomposition changes execution
review proof bar -> $cas review source mode
CAS/existing review output -> review-fold disposition before code
WorkGraph -> goal-grind frontier
verification output -> evidence-fold verdict
completion -> proof-patch or ship handoff
```

## CAS review mandate

If `$actuating` performs code review or relies on a review gate, it must use `$cas` as the review backend through `$goal-actuating`. Do not substitute generic critique, non-CAS subagent review, or a prose pass for workflow code review.

Use `$cas` review when:

```text
the user asks for review closure, code review, adversarial review, or exhaustive review
the accepted spec/SGR-v2 includes review in the proof bar
proof-patch or ship-handoff would otherwise rely on a review claim
review-first mode needs a fresh review artifact
repeated review/fix cycles need a persistent detached lane
```

Existing PR comments or prior review artifacts may be consumed as existing review pressure, but they do not replace a requested fresh/exhaustive CAS review.

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

Switch to `review-first` when reviews/CAS findings/reviewer suggestions are present.
Switch to `cas-exhaustive` when exhaustive review is requested or required by the proof bar.
Switch to `refactor-kernel` when repeated findings share an owner boundary.
Switch to `st-governed` only when durable claims/fencing/worktrees/serialized integration are required.
Switch to `ship-handoff` only when PR/publication intent is explicit or inherited from the accepted spec.

## Stop rules

Stop rather than implement when:

```text
$spec-pipeline has not allowed planning/execution
scope, non-goals, compatibility, or proof bar are unresolved
review findings expand product/API scope
raw review text has not been reduced to dispositions
review is required but $cas review is unavailable or not run
st-governed authority is required but absent
verification regresses and the next action is not isolate/revert/prove
public tracker or PR side effects would occur without explicit intent
```

## Final report

```text
Actuating:
- source: direct goal | spec | SGR-v2 | PSR-v1 | review
- semantic authority:
- mode / persistence:
- review source / CAS verdict, if required:
- GC-v1 / WorkGraph:
- review-fold disposition:
- execution owner: goal-grind | st/fixed-point-driver | none
- evidence-fold verdict:
- proof-patch / ship handoff:
- blockers / residual risk:
```

If no accepted spec or GC-v1 exists, say:

```text
actuation verdict: semantic-blocked
```

If st-governed authority is required but not obtained, say:

```text
actuation verdict: st-authority-blocked
```

If review is required but CAS review is unavailable or not run, say:

```text
actuation verdict: cas-review-blocked
```

Do not describe direct implementation as a fenced actuation run.
