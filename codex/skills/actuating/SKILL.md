---
name: actuating
description: "User-facing workflow for implementation after spec work. Use `/goal $actuating` to run `$spec-pipeline` then `$goal-actuating`: get an accepted implementation spec, choose the execution mode, require $cas for workflow review, implement through the goal runtime, and close with current-artifact proof."
metadata:
  version: "6.1.0"
  activation_cost: medium
  default_depth: high
---

# Actuating

## Mission

Run the implementation workflow without making the user manage the lower-level goal skills.

```text
implementation request or draft spec
-> $spec-pipeline in gate-only/no-plan mode when the implementation spec is not yet accepted
-> $recursion-scheme-planner when the accepted spec has nontrivial recursive structure
-> $goal-actuating
-> proof-bearing result
```

Use it as:

```text
/goal $actuating implement the accepted spec
```

`$actuating` does not directly edit code, claim resources, patch review findings, spawn subagents, or publish PRs. It routes to the owner that should act.

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

In that mode, `$actuating` hands off to `$goal-actuating`, which then routes through `$st` with bounded execution slices.

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
3. Run $recursion-scheme-planner only when the accepted spec has nontrivial recursive structure.
4. Invoke $goal-actuating with the accepted spec and optional Scheme Plan.
5. Derive a goal contract from the accepted spec.
6. Choose update_plan, goal-artifacts, or $st persistence.
7. If code review is required, run it through $cas.
8. Use $review-fold before any review-originated code change.
9. Execute accepted work through $goal-grind, bounded subagents, or $st-governed slices.
10. Fold evidence after material verification.
11. Emit proof-patch or explicit $ship handoff.
12. Run ATCG-v1 terminal closure gate before any completion claim.
```

### Scheme-planning handoff

Run `$recursion-scheme-planner` after `$spec-pipeline` and before `$goal-actuating` when the accepted spec has nontrivial recursive structure.

Use it when the spec or direct goal contains:

```text
repeated failure or review classes
migration across many files/packages
review campaign or CAS closure requirement
branch choices or competing implementation strategies
proof fanout
parallel subagent opportunities
mutual client/server/schema/protocol changes
$st coordination, claims, fencing, or worktrees
unclear stop rule
risk of becoming a generic keep-going loop
```

Skip it for one-shot or obviously linear implementation.

### Direct goal implementation

Use when the user goal already contains scope, non-goals, done state, constraints, and proof checks:

```text
/goal $actuating <objective>, verified by <checks>, preserving <constraints>
```

If the request is still ambiguous, `$actuating` must call `$spec-pipeline` in gate-only/no-plan mode or stop as blocked rather than inventing scope.

### Review resolution implementation

Use when the work is review closure:

```text
/goal $actuating close the review for this branch
```

The default review behavior is `resolve-and-fix`.

When the user asks for review, review closure, code review, CAS review, review remediation, or to address review findings without explicitly saying not to implement, the workflow must:

1. Use `$cas` as the review backend for fresh or exhaustive workflow review.
2. Pass findings through `$review-fold`.
3. Run a resolve pass to produce the smallest correct closure agenda.
4. Implement only accepted code-change liabilities.
5. Preserve no-code dispositions: `reject`, `proof-only`, `follow-up`, and `ask-human`.
6. Prefer `refactor-kernel` when several findings share one owner boundary.
7. Run three consecutive clean CAS review evidence units on the same artifact scope.
8. Close with `$evidence-fold` and `$proof-patch`.

Do not treat `resolve-and-fix` as one patch per comment.

#### Review-only

Use when the user wants review findings classified without implementation:

```text
/goal $actuating review this branch; do not implement
```

The workflow performs:

```text
$cas review
-> $review-fold
-> review disposition report
-> stop
```

Do not call `$goal-grind`. The three-clean-review closure bar does not apply unless the user explicitly asks for exhaustive review certification.

#### Resolve-only

Use when the user wants a closure agenda without implementation:

```text
/goal $actuating resolve review findings for this branch; do not implement
```

The workflow performs:

```text
$cas review or existing review findings
-> $review-fold
-> resolve pass
-> resolution agenda
-> stop
```

Do not call `$goal-grind`. The three-clean-review closure bar does not apply because no remediation has occurred.

#### Resolve-and-fix

This is the default for review work unless the user explicitly requests no implementation:

```text
/goal $actuating review and fix this PR
```

The workflow performs:

```text
$cas review
-> $review-fold
-> optional review-class-fanout
-> resolve pass
-> optional branch-race
-> $goal-grind accepted liabilities only
-> optional patch-fanout over disjoint accepted liabilities only
-> $evidence-fold
-> 3 clean CAS review evidence units
-> $proof-patch
-> $ship only when PR update/publication is requested
```

Only accepted code-change liabilities may reach implementation.
Raw review prose never reaches implementation directly.

#### Three clean CAS review evidence units

For `resolve-and-fix` and exhaustive review, completion requires three consecutive clean CAS review evidence units against the same current artifact scope unless the user explicitly lowers the review bar.

A clean CAS review evidence unit is either a `CAS-RER-v1` record or, on dispatchers without the ledger surface, a normalized tuple-bound `reviewVerdict` compatibility projection. It must carry current-tuple clean evidence with strong usable principal for the caller's proof bar and no new in-scope accepted liability after `$review-fold` and the resolve pass. The unit is not made dirty by findings that are duplicate, rejected, out-of-scope, already-proven proof-only, deferred follow-up, or already-resolved by the current refactor kernel.

Do not increment the clean-run counter from repeated normalization of one cached
CAS receipt or record. After terminal evidence exists for the tuple, request each
additional independent run with `--fresh-attempt REASON`, then track the streak in the caller workflow from independent CAS review evidence units.

Reset the clean-run counter to zero when:

```text
code changes
review scope changes
base/head/diff changes
accepted proof bar changes
the workflow cannot prove CAS review evidence units are current, strong, and distinct
accepted parallel patch result is integrated
branch-race winner is integrated
serial integration changes the artifact
```

Stop with `actuation verdict: cas-review-blocked` when `$cas` cannot run or the three-clean-run bar cannot be reached because of resource limits.

### Parallelism policy

`$actuating` may use bounded subagent parallelism only after the work has been shaped.

Allowed fanout modes:

- `scout-fanout`: parallel read-only repository investigation.
- `review-class-fanout`: parallel investigation or classification of review finding classes after `$cas review` and `$review-fold`.
- `branch-race`: compare isolated strategies under the same verifier.
- `patch-fanout`: implement disjoint accepted liabilities after the resolve pass.
- `proof-fanout`: run independent verification checks in parallel.

Forbidden fanout:

- raw review finding -> patch worker
- public side effects from subagents
- patch fanout over shared invariants, shared files, or shared owner boundaries
- subagents declaring the goal complete
- subagents updating, creating, or publishing PRs
- branch racing without a common verifier

The lead loop owns goal scope, review resolution, integration, CAS clean-run counting, proof closure, and `$ship` handoff.

### Dry actuation plan

Use when the user wants to inspect execution shape but not mutate:

```text
/goal $actuating dry-plan the accepted spec
```

Output only:

```text
goal contract summary
scheme plan, if needed
mode selection
optional work list
$st required? yes/no
review source required? none|cas-probe|cas-lane|cas-exhaustive
parallelism: none|scout-fanout|review-class-fanout|patch-fanout|proof-fanout|branch-race
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

`$actuating` owns the handoff, not the internals. It asks downstream skills to map:

```text
accepted spec -> optional $recursion-scheme-planner -> goal contract
goal contract -> work list only if decomposition changes execution
review requirement -> $cas review source mode
CAS review evidence/existing review output -> $review-fold disposition before code
review classes -> optional review-class fanout
competing strategies -> optional branch-race
accepted disjoint liabilities -> optional patch-fanout
work list -> $goal-grind next action
verification output -> $evidence-fold verdict
completion -> $proof-patch or $ship handoff
terminal closure -> ATCG-v1 decision
```

## CAS review mandate

If `$actuating` performs code review or relies on a review gate, it must use `$cas` as the review backend through `$goal-actuating`.

Use `$cas` review when:

```text
the user asks for review closure, code review, or exhaustive review
the accepted spec includes review in the proof requirements
proof-patch or ship-handoff would otherwise rely on a review claim
review resolution mode needs a fresh review artifact
repeated review/fix cycles need a persistent detached lane
```

Existing PR comments or prior review artifacts may be consumed as existing review pressure, but they do not replace a requested fresh or exhaustive CAS review.

## Mode selection

Choose the narrowest mode that can complete safely:

```yaml
actuating_mode:
  source: direct-goal|spec-first|review-only|resolve-only|resolve-and-fix|dry-plan|st-governed
  persistence: update_plan|goal-artifacts|st
  implementation: none|proof-only|minimal-fix|refactor-kernel|branch-race
  review_source: none|existing-review|cas-probe|cas-lane|cas-exhaustive
  scheme_plan: none|required|present
  parallelism: none|scout-fanout|review-class-fanout|patch-fanout|proof-fanout|branch-race
  closure: review-disposition|resolution-agenda|proof-patch|ship-handoff|blocked
```

Default:

```text
spec-first + update_plan + minimal-fix + proof-patch
```

Switch to `resolve-and-fix` when reviews, CAS findings, or reviewer suggestions are present and no no-code modifier is present.
Switch to `review-only` when the user asks for review-only, audit-only, classify-only, no changes, or do not implement behavior.
Switch to `resolve-only` when the user asks for a plan or resolution agenda without implementation.
Switch to `cas-exhaustive` when exhaustive review is requested or required by the proof bar.
Switch to `refactor-kernel` when repeated findings share an owner boundary.
Switch to `branch-race` when local fix and refactor-kernel are both plausible and can be compared under the same verifier.
Switch to `st-governed` only when durable claims, fencing, worktrees, or serialized integration are required.
Switch to `ship-handoff` only when PR/publication intent is explicit or inherited from the accepted spec.

## Terminal closure gate

Before `$actuating` may report completion or call `update_goal complete`, run
ATCG-v1 over the current branch/head/diff, evidence-fold verdict, proof-patch
state, CAS clean-run state, ADD-v1 delivery decision, and ship result when
publication is required.

Completion is legal only when:

```text
ATCG-v1 verdict = complete
ATCG-v1 can_mark_goal_complete = yes
```

If ATCG-v1 returns `continue`, continue with `next_owner`. If it returns
`blocked`, report the blocked actuation verdict and reasons. Do not substitute
local proof, proof-complete graph state, cached CAS receipts/records, or ADD-v1
`handoff_to_ship` for terminal completion.

## Stop rules

Stop rather than implement when:

```text
$spec-pipeline has not approved execution
scope, non-goals, compatibility, or proof bar are unresolved
review findings expand product/API scope
raw review text has not been reduced to dispositions
review is required but $cas review is unavailable or not run
three clean CAS review evidence units are required but cannot be completed
$st authority is required but absent
parallel fanout would cross shared invariants or conflicting resources
verification regresses and the next action is not isolate/revert/prove
public tracker or PR side effects would occur without explicit intent
ATCG-v1 does not return can_mark_goal_complete=yes
```

## Final report

```text
Actuating:
- source: direct goal | accepted spec | review | $st handoff
- authority source:
- scheme plan: none|required|present
- mode / persistence:
- parallelism:
  - mode:
  - subagents used:
  - fanout frontier:
  - fan-in reducer:
  - accepted results:
  - rejected results:
  - integration order:
  - conflicts:
  - CAS clean-run counter reset: yes|no
- review source / CAS evidence unit, if required:
- clean CAS review evidence units: 0|1|2|3|not-required
- goal contract / work list:
- review-fold disposition:
- execution owner: goal-grind | st-bounded-slice | none
- evidence-fold verdict:
- proof-patch / ship handoff:
- ATCG-v1 verdict / next owner:
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

If caller-owned repeated CAS reviews are required but unavailable, say:

```text
actuation verdict: cas-review-blocked
```

Do not describe direct implementation as a fenced actuation run.
