---
name: goal-actuating
description: "Run an accepted implementation spec or direct /goal through the goal runtime. Builds a goal contract, chooses the execution mode, optionally consumes a recursion Scheme Plan, requires $cas for workflow review, schedules bounded subagents when safe, and closes with proof."
metadata:
  version: "1.1.0"
  activation_cost: medium
  default_depth: high
---

# Goal Actuating

## Mission

Run approved work through the goal workflow.

```text
accepted implementation spec or direct goal
-> optional Scheme Plan
-> goal contract
-> execution mode
-> work list when useful
-> one focused action or bounded subagent frontier
-> evidence
-> proof
```

`$actuating` is the user-facing wrapper. `$goal-actuating` is the runtime that does the lowering, scheduling, fan-in, and routing.

## Inputs

```text
accepted implementation spec
Scheme Plan from $recursion-scheme-planner
plan or $st handoff
review findings bound to the current diff
direct /goal with enough proof surface
```

When an accepted implementation spec is present, treat it as the source of truth. Do not reinterpret scope, non-goals, compatibility, or proof requirements.

## Modes

```yaml
goal_actuating_mode:
  source: direct-goal|spec-first|review-only|agenda-only|review-fix|dry-plan|st-governed
  persistence: update_plan|goal-artifacts|st
  implementation: none|proof-only|minimal-fix|refactor-kernel|branch-race
  review: none|existing-review|cas-probe|cas-lane|cas-exhaustive
  resolution: none|review-fold-only|closure-agenda|review-fix|review-campaign
  scheme_plan: none|required|present
  parallelism: none|scout-fanout|review-class-fanout|patch-fanout|proof-fanout|branch-race
  closure: review-disposition|closure-agenda|proof-patch|ship-handoff|blocked
```

- `spec-first`: execute an accepted implementation spec without scope drift.
- `direct-goal`: execute a goal that already has outcome, constraints, and proof checks.
- `review-only`: classify review findings and stop without mutation.
- `agenda-only`: classify findings and produce a closure agenda without mutation.
- `review-fix`: default review mode; classify findings, implement accepted liabilities only, and require three clean normalized CAS review runs before completion.
- `dry-plan`: show the goal contract and work list only; do not mutate.
- `st-governed`: hand off to `$st` with bounded execution slices when durable coordination owns the work.

## Procedure

1. Locate the accepted spec, Scheme Plan, plan handoff, review input, or direct goal.
2. If the work is not yet approved enough to execute, hand off to `$spec-pipeline` in gate-only/no-plan mode and stop.
3. If no Scheme Plan exists and the work shape is unclear, hand off to `$recursion-scheme-planner`.
4. Derive a goal contract with `$goal-contract`.
5. Choose `update_plan`, `goal-artifacts`, or `$st` persistence.
6. If the workflow performs fresh or exhaustive review, run `$cas` review.
7. Classify review findings with `$review-fold`.
8. Run a closure-agenda pass when review work needs a closure agenda.
9. Create a work list with `$goal-workgraph` only when decomposition changes execution.
10. Schedule bounded subagents only for explicit safe frontier nodes.
11. Execute one useful action at a time with `$goal-grind`, unless `$st` owns execution.
12. Fold verification, review, and subagent results with `$evidence-fold`, `$review-fold`, or the closure-agenda pass as appropriate.
13. Use `$failure-memory` when failures or review classes repeat.
14. For `review-fix` and exhaustive review, require three consecutive clean normalized `$cas` review runs on the same artifact scope before completion.
15. Close with `$proof-patch`, or hand off to `$ship` only when publication is requested and ready.

## Scheme Plan consumption

A Scheme Plan may choose:

```text
direct
cata
ana
hylo
para
apo
histo
futu
zygo
dyna
chrono
meta
mutu
parallel-traverse
st-governed
```

Use the Scheme Plan to decide:

```text
work graph shape
memory policy
review compression path
branch-race need
parallel fanout mode
proof fanout
$st handoff
stop condition
```

If a Scheme Plan says `blocked`, stop and report the blocker.

## Parallel scheduler

`$goal-actuating` owns bounded parallel scheduling for the goal workflow.

It may spawn subagents only over explicit work nodes, review classes, isolated strategy branches, or proof checks.

Allowed scheduler decisions:

- use `repo_scout` for read-only fact-finding over independent repository areas;
- use `review_reducer` over review classes after `$cas review` and `$review-fold`;
- use `branch_racer` when strategies can be isolated and compared by the same verifier;
- use `patch_worker` only after the closure-agenda pass accepts code-change liabilities and the nodes are file-disjoint or otherwise isolated;
- use `evidence_critic` for proof fan-in or contested evidence.

The lead must fold all subagent outputs before continuing.
No subagent may declare the goal complete, post/update public PR state, or broaden the accepted scope.

## Parallel fan-in law

Every subagent result must fold through exactly one owner:

- `review-fold` for review classification results;
- `closure-agenda pass` for closure agenda decisions;
- `evidence-fold` for tests, proof, diffs, logs, and verifier output;
- lead integration for accepted patches;
- `$ship` only for PR creation/update/promotion/publication.

A subagent result is advisory until the lead folds it and either accepts, rejects, isolates, or reruns it.

## Parallel integration and CAS clean runs

Parallelism does not weaken the three-clean-CAS closure bar.

The clean-run counter resets to 0 after any accepted artifact-changing subagent result, including patch fanout results and branch-race winner integration.

Read-only fanout and classification-only fanout do not reset the counter unless the artifact scope or proof bar changes.

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
-> closure-agenda pass
-> $goal-grind accepted liabilities only
```

## Review behavior

If review is requested and no no-code modifier is present, use `review-fix`.

```text
$cas review
-> $review-fold
-> optional review-class-fanout
-> closure-agenda pass
-> optional branch-race
-> $goal-grind accepted liabilities only
-> optional patch-fanout over disjoint accepted liabilities only
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
agenda only
plan only
no changes
```

Prefer no-code outcomes when they are correct: `reject`, `proof-only`, `follow-up`, or `ask-human`.

Prefer `refactor-kernel` when several findings share one missing abstraction, invariant, canonical owner, state transition, or proof surface.

Exhaustive review is not optional once requested or required. `$review-fold` controls which findings become code changes; it must not remove the CAS review gate.

## Three clean normalized CAS review runs

For `review-fix` and exhaustive review, completion requires three consecutive clean normalized `$cas` review runs against the same artifact scope unless the user explicitly lowers the review bar.

A clean normalized CAS run means `$cas` produces no new in-scope accepted liability, unresolved proof gap, unresolved refactor-kernel candidate, or human-owned blocker after `$review-fold` and the closure-agenda pass.

Do not reset the clean-run counter for findings that are duplicate, rejected, out-of-scope, already-proven proof-only, follow-up, or already addressed by the current implementation.

Do not increment the clean-run counter from repeated normalization of one cached
CAS receipt. After terminal evidence exists for the tuple, request each
additional independent run with `--fresh-attempt REASON`, then verify the streak
with `cas review_session receipt proof --clean-streak 3 ...`.

Reset the clean-run counter to zero when:

```text
code changes
review scope changes
base/head/diff changes
accepted proof bar changes
CAS lane/session continuity is lost
accepted parallel patch result is integrated
branch-race winner is integrated
serial integration changes the artifact
```

If `$cas` cannot run, or the three-clean-run bar cannot be reached because of resource limits, stop with `actuation verdict: cas-review-blocked`.

## Closure-agenda pass

A closure-agenda pass turns classified findings into the smallest correct closure agenda.

It decides:

- which findings are accepted code-change liabilities;
- which are rejected;
- which need proof only;
- which belong in follow-up work;
- which require a human decision;
- which findings collapse into one `refactor-kernel`.

The closure-agenda pass must not mutate code and must not hand raw review prose to implementation.

## Resolution output

```yaml
review_closure_agenda:
  mode: review-only|agenda-only|review-fix
  source: cas-review|existing-review|human-review
  clean_cas_runs:
    required: yes|no
    count: 0|1|2|3
    artifact_scope:
    reset_reason:
  parallelism:
    mode: none|review-class-fanout|patch-fanout|branch-race|proof-fanout
    subagents_used: []
    accepted_results: []
    rejected_results: []
    integration_order: []
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
parallel fanout would cross shared invariants or conflicting resources
```

## Output

```text
Goal Actuation:
- source: accepted spec | direct goal | plan handoff | review
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
