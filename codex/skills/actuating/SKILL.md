---
name: actuating
description: "User-facing workflow for implementing approved work and no-code review modes. It gets an accepted spec when needed, checks whether a loop receipt is required, runs the goal runtime, requires CAS-backed review when review is in scope, and closes material implementation only through proof plus ATCG."
metadata:
  version: "7.1.0"
  activation_cost: medium
  default_depth: high
---

# Actuating

## Mission

Run implementation and review-routing work without making the user manage the
lower-level skills.

```text
implementation request or draft spec
-> accepted implementation spec, when needed
-> loop shape decision, when work is not one simple action
-> goal runtime
-> proof and review evidence
-> terminal closure gate
-> final result or explicit handoff
```

Use it as:

```text
/goal $actuating implement the accepted spec
/goal $actuating triage this PR
/goal $actuating remediation-plan this PR
/goal $actuating review-closeout this PR
/goal $actuating dry-plan the accepted spec
```

`$actuating` is the front door. It does not directly edit code, claim resources,
spawn subagents, publish PRs, or mark work complete. It chooses the right owner
and checks that the required evidence exists.

## Plain rules

```text
Do not run an untracked loop.
Do not change code unless the next work item was selected.
Do not keep going unless the previous action was checked.
Do not claim completion until the terminal gate allows it.
```

## Removed controller path

The old transaction-controller/APMA path is not active in this workspace. If the
work needs durable claims, fencing, external worktrees, serialized integration,
or multi-plan coordination, `$actuating` must block or ask for a supported
controller. It must not pretend that local edits are a fenced actuation run.

## Normal flow

1. Get or refresh an accepted implementation spec through `$spec-pipeline` in
   gate-only/no-plan mode when the request is not already approved enough.
2. Treat the accepted spec as the source of truth.
3. Use `$recursion-scheme-planner` when the work has branching, repeated classes,
   review campaigns, migrations, proof fanout, or unclear stopping conditions.
4. If the explicit mode is `triage` or `remediation-plan`, use supplied existing
   GitHub, human, or CAS findings when present; CAS runs only when no current
   review source exists or fresh review is explicitly requested.
5. Use `$agent-loop-schemes` when material work needs ALSR/HYL loop receipts.
6. Send the accepted work to `$goal-actuating`.
7. Use `$cas` when workflow review is requested or required.
8. Pass findings through `$review-fold` before any review-driven code change.
9. Implement only accepted code-change liabilities.
10. Fold current evidence after each material action.
11. Run ATCG-v1 before any material completion claim.
12. Emit a proof-patch result or a `$ship` handoff when PR publication/update was requested.

## Source requirement

Before `$goal-actuating` runs, establish one of:

```text
accepted implementation spec
direct user goal with enough scope, constraints, and proof checks
review findings bound to the current diff and intended change
current review source for a no-code review mode
plan handoff for goal-artifact execution
```

If none exists, run `$spec-pipeline` in gate-only/no-plan mode or stop with:

```yaml
actuating_status:
  verdict: blocked-needs-accepted-spec
  next_owner: $spec-pipeline|$grill-me|$codebase-doctrine
  reason:
```

## When a loop receipt is required

Simple, one-shot work may be direct-action fused. Anything more complex needs a
current loop receipt before material changes.

Require ALSR/HYL when the work has:

```text
repeated failure or review classes
many-file migration
review closeout or CAS closure
branch choices or competing implementation strategies
proof fanout
parallel subagent opportunities
mutual client/server/schema/protocol changes
unclear stop rule
risk of turning into a generic keep-going loop
```

For material runs, `$actuating` must establish one of:

```text
valid FUSION-v1 direct-action receipt
current ALSR-v1 + HYL-v1 + HSR-v1 chain
```

If none exists, stop with:

```text
actuation verdict: blocked-loop-contract-missing
```

If the loop receipts do not match the current branch/head/diff, stop with:

```text
actuation verdict: blocked-loop-contract-stale
```

If the next material action has no selected work item, stop with:

```text
actuation verdict: blocked-hylo-frontier-missing
```

If the previous material action has no current evidence fold, stop with:

```text
actuation verdict: blocked-hylo-fold-missing
```

No-code review modes do not require material loop receipts, proof-patch, three
clean CAS attempts, or ATCG. They become material only if the workflow accepts a
code-change liability for implementation, performs a public side effect, or
claims implementation completion.

## Direct-action fusion

Direct-action fusion is allowed only when all are true:

```text
one legal work item
known verifier
no review requirement
no parallelism
no public side effect
no repeated class, migration, or branch choice
objective, artifact scope, and stop condition are bound to the final proof
```

A fused run must carry a `FUSION-v1` receipt. A raw flag such as
`direct_action_fused: yes` is not enough.

## Material loop operation

For material runs, `$goal-actuating` interprets HYL-v1:

```text
current state
-> select exactly one legal work item or safe parallel frontier
-> execute only that item/frontier
-> fold current evidence
-> continue | complete | blocked | regress | replan | refactor-kernel
```

Every material step must produce an HSR-v1 receipt that records the selected
work, the action, the evidence fold, and the next owner.

## Goal-focus frames

Receipt field name: `goal_focus`.


A long parent goal may use smaller focus frames. The parent goal stays stable;
only the active focus changes.

Before completion, ATCG must verify:

```text
primary_goal_stable = yes
all child focus frames folded or blocked = yes
terminal focus matches parent stop rule = yes
no child frame claimed parent completion = yes
latest focus fold is parent-bound = yes
```

A focus frame is not a nested `/goal`; it is a local work frame owned by the
parent actuation run.

## Review modes

Review modes are explicit:

- `triage`: classify findings and stop without implementation.
- `remediation-plan`: classify findings, produce a fix plan, and stop without implementation.
- `review-closeout`: classify findings, implement only accepted code-change liabilities, prove closure, and stop at ATCG or `$ship` handoff.

`triage` and `remediation-plan` end in mode-terminal outputs, not terminal
completion. No-code outputs must report review source/currentness and must not
claim implementation completion. ATCG is not required for a `triage` report or
`remediation-plan`; proof-patch, three clean CAS attempts, and material loop
receipts are not required either.

Unqualified review closure requests default to `review-closeout`.

When review closeout is active, the workflow is:

```text
review source acquisition or $cas review
-> $review-fold
-> resolution fold
-> optional branch-race/refactor-kernel decision
-> implementation of accepted code-change liabilities only
-> evidence fold
-> three clean normalized standard CAS review attempts
-> proof-patch
-> ATCG-v1
-> $ship only when publication/update is requested
```

Missing tuple-bound CAS evidence is a `$cas` acquisition node for
`review-closeout`, not an entry failure. Terminal completion still requires
tuple-bound independent fresh standard CAS clean evidence when review closeout
requires CAS.

Raw review text never reaches implementation directly.

## Review lanes

The standard CAS review lane is the only lane that counts toward the three-clean
review streak. Auxiliary review lanes may block completion, but they do not add
to the standard clean count.

Available auxiliary lanes:

```text
footgun-finder       misuse hazards, unsafe defaults, misleading affordances
invariant-ace        illegal states, ownership gaps, transition or policy breaks
complexity-mitigator reviewability stalls, repeated owner-boundary churn, boolean soup
```

When workflow review is required, `review_profile` must explicitly account for
all auxiliary lanes as selected/folded or `not-required` with a reason.

## Refactor-kernel escalation

When repeated accepted liabilities share one owner boundary, missing abstraction,
state transition, validation rule, invariant, proof surface, or misuse trap,
`$actuating` records the decision before more mutation.

```yaml
actuation_escalation_receipt:
  version: AER-v1
  run_id:
  owner_boundary:
  repeated_finding_class:
  accepted_liabilities:
    - cas_finding_id:
      finding_fingerprint:
      review_fold_ref:
      liability:
  prior_resolution_mode: minimal-fix|proof-only|refactor-kernel|branch-race|none
  next_resolution_mode: minimal-fix|refactor-kernel|branch-race|remediation-plan|blocked
  escalation_trigger:
  alternatives_considered: []
  selected_route:
  verifier: []
  current_artifact_scope:
    branch:
    head_sha:
    target_fingerprint:
```

AER-v1 is not review adjudication and not mutation authority. `$seq` may later
audit whether this receipt existed and whether behavior contradicted it;
`$actuating` owns the active escalation decision. AER-v1 is treated as review
finding acceptance or mutation authority only by mistake; that is a failure.

If `selected_route` or `next_resolution_mode` is `refactor-kernel`, validate the
AER-v1 before mutation and emit RKO-v1 after proof/review.

## Parallelism policy

Parallel work is allowed only after the work has been shaped and a safe frontier
has been selected.

Allowed:

```text
read-only scout fanout
review-class fanout after review folding
branch race under one verifier
patch fanout over disjoint accepted liabilities
proof fanout over independent checks
```

Forbidden:

```text
raw review finding -> patch worker
subagent chooses scope
subagent declares completion
subagent updates or publishes PRs
patch fanout over shared invariants or owner boundaries
branch race without a common verifier
```

The lead loop owns scope, review resolution, integration, clean CAS counting,
proof closure, and `$ship` handoff.

## Terminal closure

Before `$actuating` may report material implementation completion or call
`update_goal complete`, run ATCG-v1 over the current branch/head/diff, loop
receipts or fusion receipt, latest HSR/focus evidence, evidence fold,
proof-patch, CAS state, delivery state, and side-effect boundary.

Completion is legal only when:

```text
ATCG-v1 verdict = complete
ATCG-v1 can_mark_goal_complete = yes
```

Do not substitute local proof, a proof-complete graph, cached CAS receipts, or
ADD-v1 `handoff_to_ship` for terminal completion.

Mode-terminal no-code outputs are different: a `triage` report or
`remediation-plan` can end successfully without terminal completion because it
does not claim implementation closure.

## Stop rules

Stop rather than implement when:

```text
execution has not been approved
scope, non-goals, compatibility, or proof bar are unresolved
review findings expand product/API scope
raw review text has not been reduced to dispositions
review is required but CAS review is unavailable or not run
three clean standard CAS reviews are required but cannot be completed
parallel fanout would cross shared invariants or conflicting resources
ALSR/HYL/HSR is required but missing or stale
FUSION-v1 is claimed but not proven
unfold is missing before material mutation
fold is missing after material action
goal-focus frames are missing, stale, or not folded to parent
verification regresses and the next action is not isolate/revert/prove
public tracker or PR side effects would occur without explicit intent
ATCG-v1 does not return can_mark_goal_complete=yes
```

For no-code review modes, missing CAS evidence is a blocker only when no current
review source exists or fresh review was explicitly requested. For
`review-closeout`, missing tuple-bound CAS evidence routes to `$cas` until
terminal closeout evidence exists.

## Final report

```text
Actuating:
- source: direct goal | accepted spec | review
- authority source:
- scheme plan: none|required|present
- loop receipt:
  - fusion receipt:
  - ALSR-v1:
  - HYL-v1:
  - latest HSR-v1:
  - goal-focus frame:
- mode / persistence:
- mode-terminal output:
- parallelism:
  - mode:
  - subagents used:
  - fanout frontier:
  - fan-in reducer:
  - accepted results:
  - rejected results:
  - integration order:
  - conflicts:
  - standard CAS clean-run counter reset: yes|no
- review source / CAS verdict, if required:
- normalized standard CAS clean runs: 0|1|2|3|not-required
- goal contract / work list:
- review-fold disposition:
- actuation escalation receipt:
- execution owner: goal-grind | none
- evidence-fold verdict:
- proof-patch / ship handoff:
- ATCG-v1 verdict / next owner:
- blockers / residual risk:
```

If no accepted spec or goal contract exists, say:

```text
actuation verdict: blocked-needs-accepted-spec
```

If review is required but CAS review is unavailable or not run, say:

```text
actuation verdict: cas-review-blocked
```

If ALSR/HYL/HSR is required but missing or stale, say:

```text
actuation verdict: blocked-loop-contract-missing
actuation verdict: blocked-loop-contract-stale
```

Do not describe direct implementation as a fenced actuation run.
