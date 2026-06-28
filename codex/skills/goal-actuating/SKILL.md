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
  source: direct-goal|spec-first|review-only|resolve-only|resolve-and-fix|dry-plan|st-governed
  persistence: update_plan|goal-artifacts|st
  implementation: none|proof-only|minimal-fix|refactor-kernel|branch-race
  review: none|existing-review|cas-probe|cas-lane|cas-exhaustive
  resolution: none|review-fold-only|resolve-pass|resolve-and-fix|resolve-campaign
  closure: review-disposition|resolution-agenda|proof-patch|ship-handoff|blocked
```

- `spec-first`: execute an accepted implementation spec without scope drift.
- `direct-goal`: execute a goal that already has outcome, constraints, and proof checks.
- `review-only`: classify review findings and stop without mutation.
- `resolve-only`: classify findings and produce a closure agenda without mutation.
- `resolve-and-fix`: default review mode; resolve findings, implement accepted liabilities only, and require three clean normalized CAS review runs before completion.
- `dry-plan`: show the goal contract and work list only; do not mutate.
- `st-governed`: hand off to `$st` and `$fixed-point-driver` when durable coordination owns the work.

## Procedure

1. Locate the accepted spec, plan handoff, review input, or direct goal.
2. If the work is not yet approved enough to execute, hand off to `$spec-pipeline` in gate-only/no-plan mode and stop.
3. Derive a goal contract with `$goal-contract`.
4. Choose `update_plan`, `goal-artifacts`, or `$st` persistence.
5. If the workflow performs fresh or exhaustive review, run `$cas` review.
6. Classify review findings with `$review-fold`.
7. Run a resolve pass when review work needs a closure agenda.
8. Create a work list with `$goal-workgraph` only when decomposition changes execution.
9. Execute one useful action at a time with `$goal-grind`, unless `$st` owns execution.
10. Fold verification and review results with `$evidence-fold`.
11. Use `$failure-memory` when failures or review classes repeat.
12. For `resolve-and-fix` and exhaustive review, require three consecutive clean normalized `$cas` review runs on the same artifact scope before completion.
13. Close with `$proof-patch`, or hand off to `$ship` only when publication is requested and ready.

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
review resolution mode needs a fresh review artifact
repeated review/fix cycles need a persistent detached lane
proof-patch or ship-handoff would otherwise rely on a review claim
```

A goal may close without code review only when the accepted proof requirements do not include review and focused checks are enough. Once a review gate is present, CAS review is mandatory.

```text
$cas review
-> $review-fold
-> resolve pass
-> $goal-grind accepted liabilities only
```

## Review behavior

If review is requested and no no-code modifier is present, use `resolve-and-fix`.

```text
$cas review
-> $review-fold
-> resolve pass
-> $goal-grind accepted liabilities only
-> $evidence-fold
-> 3 clean normalized $cas review runs
-> $proof-patch
```

No-code modifiers include:

```text
do not implement
review only
audit only
classify only
resolve only
plan only
no changes
```

Prefer no-code outcomes when they are correct: `reject`, `proof-only`, `follow-up`, or `ask-human`.

Prefer `refactor-kernel` when several findings share one missing abstraction, invariant, canonical owner, state transition, or proof surface.

Exhaustive review is not optional once requested or required. `$review-fold` controls which findings become code changes; it must not remove the CAS review gate.

## Three clean normalized CAS review runs

For `resolve-and-fix` and exhaustive review, completion requires three consecutive clean normalized `$cas` review runs against the same artifact scope unless the user explicitly lowers the review bar.

A clean normalized CAS run means `$cas` produces no new in-scope accepted liability, unresolved proof gap, unresolved refactor-kernel candidate, or human-owned blocker after `$review-fold` and the resolve pass.

Do not reset the clean-run counter for findings that are duplicate, rejected, out-of-scope, already-proven proof-only, follow-up, or already resolved by the current implementation.

Reset the clean-run counter to zero when:

```text
code changes
review scope changes
base/head/diff changes
accepted proof bar changes
CAS lane/session continuity is lost
```

If `$cas` cannot run, or the three-clean-run bar cannot be reached because of resource limits, stop with `actuation verdict: cas-review-blocked`.

## Resolve pass

A resolve pass turns classified findings into the smallest correct closure agenda.

It decides:

- which findings are accepted code-change liabilities;
- which are rejected;
- which need proof only;
- which belong in follow-up work;
- which require a human decision;
- which findings collapse into one `refactor-kernel`.

The resolve pass must not mutate code.

Use `$resolve` as a handoff only when review findings require a dedicated closure agenda. Do not root-activate `$resolve`. Do not call `$resolve` for every review.

## Resolution output

```yaml
review_resolution:
  mode: review-only|resolve-only|resolve-and-fix
  source: cas-review|existing-review|human-review
  clean_cas_runs:
    required: yes|no
    count: 0|1|2|3
    artifact_scope:
    reset_reason:
  accepted_liabilities:
    - id:
      reason:
      owner:
      minimal_response:
      proof_required: []
  rejected:
    - id:
      reason:
      response_draft:
  proof_only:
    - id:
      proof_needed:
      command_or_artifact:
  follow_up:
    - id:
      reason:
      suggested_scope:
  ask_human:
    - id:
      decision_needed:
      options: []
  refactor_kernels:
    - kernel:
      findings: []
      owner_boundary:
      why_refactor_beats_local_fixes:
      proof_required: []
  implementation_queue:
    - action:
      mode: minimal-fix|refactor-kernel|branch-race
      files_or_areas: []
      verifier: []
  stop_reason:
```

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
three clean normalized $cas review runs are required but cannot be completed
```

## Output

```text
Goal Actuation:
- source: accepted spec | direct goal | plan handoff | review
- mode / persistence:
- review source / CAS verdict, if required:
- clean normalized CAS review runs: 0|1|2|3|not-required
- goal contract summary:
- work list / next action:
- review-fold disposition, if any:
- review resolution, if any:
- evidence-fold verdict:
- proof-patch / ship handoff:
- learnings or memory-source handoff, if justified:
```
