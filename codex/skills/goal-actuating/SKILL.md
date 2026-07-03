---
name: goal-actuating
description: "Run an accepted implementation spec or direct /goal through the goal runtime. Interprets HYL-v1 as a defunctionalized actuation machine, emits HSR-v1 step receipts, schedules bounded subagents when safe, requires $cas for workflow review, and closes through proof plus ATCG."
metadata:
  version: "2.0.0"
  activation_cost: medium
  default_depth: high
---

# Goal Actuating

## Mission

Run approved work through the goal workflow.

```text
accepted implementation spec or direct goal
-> optional Scheme Plan
-> ALSR-v1/HYL-v1 when material loop governance is required
-> goal contract
-> execution mode
-> work list when useful
-> HSR-v1 unfold/action/fold steps
-> evidence
-> terminal ATCG
-> proof
```

`$actuating` is the user-facing wrapper. `$goal-actuating` is the runtime that interprets HYL-v1.

## Inputs

```text
accepted implementation spec
Scheme Plan from $recursion-scheme-planner
ALSR-v1 / HYL-v1 from $agent-loop-schemes
plan or $st handoff
review findings bound to the current diff
direct /goal with enough proof surface
```

When an accepted implementation spec is present, treat it as the source of truth. Do not reinterpret scope, non-goals, compatibility, or proof requirements.

## Modes

```yaml
goal_actuating_mode:
  source: direct-goal|spec-first|review|dry-plan|st-governed
  persistence: update_plan|goal-artifacts|st
  implementation: none|proof-only|minimal-fix|refactor-kernel|branch-race
  review_mode: none|triage|remediation-plan|review-closeout
  review: none|existing-review|cas-probe|cas-lane|cas-exhaustive
  resolution: none|review-fold-only|resolution-fold|accepted-liabilities|resolution-campaign
  scheme_plan: none|required|present
  loop_contract: fused|ALSR-HYL|required|st-owned
  parallelism: none|scout-fanout|review-class-fanout|patch-fanout|proof-fanout|branch-race
  closure: triage-report|remediation-plan|review-closeout|ship-handoff|blocked
```

## Procedure

1. Locate the accepted spec, Scheme Plan, ALSR/HYL, plan handoff, review input, or direct goal.
2. If the work is not yet approved enough to execute, hand off to `$spec-pipeline` in gate-only/no-plan mode and stop.
3. If no Scheme Plan exists and the work shape is unclear, hand off to `$recursion-scheme-planner`.
4. If material loop governance is required and no current ALSR/HYL exists, hand off to `$agent-loop-schemes`.
5. Derive a goal contract with `$goal-contract`.
6. Choose `update_plan`, `goal-artifacts`, or `$st` persistence.
7. Interpret HYL-v1: unfold a legal work node/frontier, execute it, fold evidence, and emit HSR-v1.
8. If the workflow performs fresh or exhaustive review, run `$cas` review.
9. Classify review findings with `$review-fold`.
10. Run a resolution fold when review work needs a resolution plan.
11. Create a work list with `$goal-workgraph` only when decomposition changes execution.
12. Schedule bounded subagents only for explicit safe frontier nodes.
13. Execute one useful action at a time with `$goal-grind`, unless `$st` owns execution.
14. Fold verification, review, and subagent results with `$evidence-fold`, `$review-fold`, or the resolution fold as appropriate.
15. Use `$failure-memory` when failures or review classes repeat.
16. For `review-closeout` and exhaustive review, require three consecutive clean normalized `$cas` review runs on the same artifact scope before completion.
17. Run ATCG-v1 before completion.
18. Close with `$proof-patch`, or hand off to `$ship` only when publication is requested and ready.

## HYL-v1 interpreter

A material action is legal only as an HSR-v1 transition:

```text
state_before
-> unfold work_node|parallel_frontier|terminal|blocked|st_handoff
-> action
-> fold evidence
-> continuation
```

No mutation is valid without an unfolded work node.
No continuation is valid without a fold verdict.
No completion is valid without terminal ATCG-v1.

## HYL coalgebra

The default coalgebra is obligation-driven:

```text
if no accepted spec -> blocked
if topology nontrivial and no Scheme Plan -> produce scheme-planner node
if material and no ALSR/HYL -> produce agent-loop-schemes node
if no goal contract -> produce goal-contract node
if review requested and no CAS result -> produce CAS review node
if CAS findings unclassified -> produce review-fold node
if review requested and no resolution agenda -> produce resolution-fold node
if accepted liabilities remain -> produce patch/refactor/branch-race node
if proof missing -> produce verifier/proof node
if clean CAS count < 3 -> produce fresh CAS review node
if proof-patch missing -> produce proof-patch node
if ATCG not run -> produce ATCG node
else -> terminal complete
```

## HYL algebra

The algebra folds effects into actuation state:

```text
code change -> reset clean CAS count and proof freshness
CAS review -> normalize through review-fold and update clean counter
review-fold -> update dispositions and quotient findings into classes
resolution fold -> update accepted liabilities / no-code dispositions / blockers
proof check -> update verifier state
proof patch -> update proof state
subagent result -> accept/reject/integrate through lead reducer
ATCG -> complete|continue|blocked
```

## Parallel scheduler

`$goal-actuating` owns bounded parallel scheduling for the goal workflow.

It may spawn subagents only over explicit work nodes, review classes, isolated strategy branches, or proof checks.

Allowed scheduler decisions:

- use `repo_scout` for read-only fact-finding over independent repository areas;
- use `review_reducer` over review classes after `$cas review` and `$review-fold`;
- use `branch_racer` when strategies can be isolated and compared by the same verifier;
- use `patch_worker` only after the resolution fold accepts code-change liabilities and the nodes are file-disjoint or otherwise isolated;
- use `evidence_critic` for proof fan-in or contested evidence.

The lead must fold all subagent outputs before continuing.
No subagent may declare the goal complete, post/update public PR state, or broaden the accepted scope.

## Parallel fan-in law

Every subagent result must fold through exactly one owner:

- `review-fold` for review classification results;
- `resolution fold` for resolution plan decisions;
- `evidence-fold` for tests, proof, diffs, logs, and verifier output;
- lead integration for accepted patches;
- `$ship` only for PR creation/update/promotion/publication.

A subagent result is advisory until the lead folds it and either accepts, rejects, isolates, or reruns it.

## Parallel integration and CAS clean runs

Parallelism does not weaken the three-clean-CAS closure bar.

The clean-run counter resets to 0 after any accepted artifact-changing subagent result, including patch fanout results and branch-race winner integration.

Read-only fanout and classification-only fanout do not reset the counter unless the artifact scope or proof bar changes.

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

## Review behavior

If review is requested and no no-code modifier is present, use `review-closeout`.

Explicit review mode names carry the mutation rule:

- `triage`: classify findings and stop without implementation.
- `remediation-plan`: classify findings, produce the fix plan, and stop without implementation.
- `review-closeout`: classify findings, implement only accepted code-change liabilities, prove closure, and stop at ATCG or `$ship` handoff.

```text
$cas review
-> $review-fold
-> optional review-class-fanout
-> resolution fold
-> optional branch-race
-> $goal-grind accepted liabilities only
-> optional patch-fanout over disjoint accepted liabilities only
-> $evidence-fold
-> 3 clean normalized $cas review runs
-> $proof-patch
-> ATCG-v1
```

No-code modifiers include:

```text
do not implement
review only
audit only
classify only
resolution plan only
plan only
no changes
```

Prefer no-code outcomes when they are correct: `reject`, `proof-only`, `follow-up`, or `ask-human`.

Prefer `refactor-kernel` when several findings share one missing abstraction, invariant, canonical owner, state transition, or proof surface.

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
ALSR/HYL is required but missing or stale
material mutation lacks HSR-v1 unfold/action/fold
parallel fanout would cross shared invariants or conflicting resources
ATCG-v1 does not permit completion
```

## Output

```text
Goal Actuation:
- source: accepted spec | direct goal | plan handoff | review
- scheme plan: none|required|present
- ALSR/HYL:
- latest HSR:
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
- ATCG-v1 verdict:
- proof-patch / ship handoff:
- learnings or memory-source handoff, if justified:
```
