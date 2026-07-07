---
name: actuating
description: "User-facing workflow for implementing approved work and no-code review modes. It gets an accepted spec when needed, checks whether a loop receipt is required, runs the goal runtime, requires CAS-backed review when review is in scope, and closes material work only through proof plus ATCG."
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

## Essential governance spine

The essential material `$actuating` spine is:

```text
accepted source
-> current loop receipt or valid FUSION-v1
-> unfolded work item/frontier
-> HSR-v1 material step
-> current evidence fold
-> proof/review closure
-> ATCG-v1
-> proof-patch or `$ship` handoff when publication was requested
```

Everything else is supporting machinery. Work graphs, `update_plan`, summaries,
progress projections, cached checks, stale review runs, and raw review text may
help select the next action, but they are not receipt evidence and cannot
replace the spine.

No-code review modes have a smaller spine:

```text
current review source
-> review-fold
-> triage report or resolution fold -> remediation plan
-> stop without mutation, proof-patch, ATCG, or `$ship`
```

They do not claim implementation closure and must not be upgraded into material
actuation merely because they inspect code, run review, or plan a fix.

## Runtime interlock

Before any material mutation, and before continuing after any material action,
`$actuating` must make the interlock decision explicit:

```yaml
actuation_interlock:
  mutation_allowed: yes | no
  continuation_allowed: yes | no
  blocker: none | blocked-loop-contract-missing | blocked-loop-contract-stale | blocked-hylo-frontier-missing | blocked-hylo-fold-missing | blocked-unsupported-controller
  current_binding:
    branch:
    head:
    diff_fingerprint:
```

`mutation_allowed: yes` requires either a valid FUSION-v1 receipt or a current
ALSR-v1 + HYL-v1 with an unfolded work item/frontier. HSR-v1 is required once a
material step exists, and `continuation_allowed: yes` requires the previous HSR
fold to be current. If the interlock is `no`, stop immediately with the blocker.
Do not keep inspecting, patching, or relying on `update_plan` to make progress
inside `$actuating`.

The interlock gates material mutation and continuation only. In `triage` and
`remediation-plan`, omit the interlock unless the workflow leaves no-code mode.
Missing loop receipts or a missing interlock must not block review collection,
classification, or plan production. If the next action would edit files, resolve
public threads, push, publish, or claim implementation closure, first transition
to `review-closeout`, `$ship`, or `$land` and satisfy that owner’s gates.

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
4. If the explicit mode is `triage` or `remediation-plan`, run the selected
   review source, `$review-fold`, and the resolution fold when needed, then stop
   with the report or plan.
5. Use `$agent-loop-schemes` when material work needs ALSR/HYL loop receipts.
6. Send the accepted material work to `$goal-actuating`.
7. Emit the runtime interlock before the first material mutation.
8. Use `$cas` when workflow review is requested or required.
9. Pass findings through `$review-fold` before any review-driven code change.
10. Implement only accepted code-change liabilities.
11. Fold current evidence after each material action before continuing.
12. Run ATCG-v1 before any material completion claim.
13. Emit a proof-patch result or a `$ship` handoff when PR publication/update was requested.

## Source requirement

Before `$goal-actuating` runs, establish one of:

```text
accepted implementation spec
direct user goal with enough scope, constraints, and proof checks
review findings bound to the current diff and intended change
plan handoff for goal-artifact execution
```

These sources authorize routing only. They do not authorize mutation unless the
loop/fusion receipt, unfolded work item, and evidence-fold requirements below
are also current for the branch/head/diff.

For no-code review modes, a current review source authorizes inspection,
classification, and planning only. It does not require or imply mutation
authority.

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
review-closeout or CAS closure
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
current ALSR-v1 + HYL-v1 with an unfolded work item/frontier
current HSR-v1 fold before continuation after any material action
```

The receipt must bind the current branch, head, and diff. A prose declaration,
checklist item, or `update_plan` row is not a loop receipt.

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

`triage` and `remediation-plan` do not require loop receipts solely because they
use review or CAS. They become material only if the workflow accepts a
code-change liability for implementation, performs a public side effect, or
claims implementation closure.

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

Unqualified review closure requests default to `review-closeout`.

When review closeout is active, the workflow is:

```text
$cas review
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

Raw review text never reaches implementation directly.

`triage` and `remediation-plan` are no-code control modes. They may read files,
inspect diffs, run `$cas` or consume existing review evidence, fold findings,
and produce reports or plans. They must not require ALSR/HYL/HSR, a positive
actuation interlock, proof-patch, three clean review attempts, or ATCG unless
they explicitly transition to `review-closeout`.

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
ADD-v1 `handoff_to_ship` for terminal completion. A `$ship` result is delivery
evidence, not completion evidence, until ATCG-v1 folds it into the terminal
state.

ATCG is not required for a `triage` report or `remediation-plan` because those
outputs intentionally do not claim implementation completion.

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
actuation interlock returns `mutation_allowed: no` for a material action
actuation interlock returns `continuation_allowed: no` for material continuation
unfold is missing before material mutation
fold is missing after material action
goal-focus frames are missing, stale, or not folded to parent
verification regresses and the next action is not isolate/revert/prove
public tracker or PR side effects would occur without explicit intent
ATCG-v1 does not return can_mark_goal_complete=yes
```

In no-code review modes, a missing interlock is not a blocker by itself. The
blocker appears only when the workflow attempts mutation, public side effects,
or implementation closure.

## Final report

```text
Actuating:
- source: direct goal | accepted spec | review
- authority source:
- scheme plan: none|required|present
- actuation interlock:
  - mutation_allowed:
  - continuation_allowed:
  - blocker:
- loop receipt:
  - fusion receipt:
  - ALSR-v1:
  - HYL-v1:
  - latest HSR-v1:
  - goal-focus frame:
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
