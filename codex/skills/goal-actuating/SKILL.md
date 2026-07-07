---
name: goal-actuating
description: "Run an accepted implementation spec or direct /goal through the goal runtime. Interprets HYL-v1 as a defunctionalized actuation machine, emits HSR-v1 step receipts, schedules bounded subagents when safe, requires $cas for workflow review, and closes through proof plus ATCG."
metadata:
  version: "2.1.0"
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
plan handoff
review findings bound to the current diff
direct /goal with enough proof surface
```

When an accepted implementation spec is present, treat it as the source of truth. Do not reinterpret scope, non-goals, compatibility, or proof requirements.

## Modes

```yaml
goal_actuating_mode:
  source: direct-goal|spec-first|review|dry-plan
  persistence: update_plan|goal-artifacts
  implementation: none|proof-only|minimal-fix|refactor-kernel|branch-race
  review_mode: none|triage|remediation-plan|review-closeout
  review: none|existing-review|cas-probe|cas-lane|cas-exhaustive
  review_lanes: []
  resolution: none|review-fold-only|resolution-fold|accepted-liabilities|resolution-campaign
  scheme_plan: none|required|present
  loop_contract: fused|ALSR-HYL|required
  parallelism: none|scout-fanout|review-class-fanout|patch-fanout|proof-fanout|branch-race
  closure: triage-report|remediation-plan|review-closeout|ship-handoff|blocked
```

## Procedure

1. Locate the accepted spec, Scheme Plan, ALSR/HYL, plan handoff, review input, or direct goal.
2. If the work is not yet approved enough to execute, hand off to `$spec-pipeline` in gate-only/no-plan mode and stop.
3. If no Scheme Plan exists and the work shape is unclear, hand off to `$recursion-scheme-planner`.
4. If material loop governance is required and no current ALSR/HYL exists, hand off to `$agent-loop-schemes`.
5. Derive a goal contract with `$goal-contract`.
6. Choose `update_plan` or `goal-artifacts` persistence.
7. Interpret HYL-v1: unfold a legal work node/frontier, execute it, fold evidence, and emit HSR-v1.
8. If the workflow performs fresh or exhaustive review, select a CAS review profile and run required CAS review lanes.
9. Classify standard and auxiliary review-lane findings with `$review-fold`.
10. Run a resolution fold when review work needs a resolution plan.
11. Create a work list with `$goal-workgraph` only when decomposition changes execution.
12. Schedule bounded subagents only for explicit safe frontier nodes.
13. Execute one useful action at a time with `$goal-grind`.
14. Fold verification, review, and subagent results with `$evidence-fold`, `$review-fold`, or the resolution fold as appropriate.
15. For `review-closeout` and exhaustive review, require three consecutive clean normalized **standard** `$cas` review attempts on the same artifact scope before completion.
16. Run ATCG-v1 before completion.
17. Close with `$proof-patch`, or hand off to `$ship` only when publication is requested and ready.

Persistence is projection, not authority. `update_plan`, work lists, and
goal-artifact projections may show the current frontier, but they do not replace
ALSR-v1, HYL-v1, HSR-v1, evidence-fold, proof-patch, review-fold, or ATCG-v1
receipts.

Before executing an HSR-v1 action, `$goal-actuating` must have or emit a
positive runtime interlock. If invoked through `$actuating`, consume the wrapper
interlock. If invoked directly or implicitly, emit the interlock from the current
ALSR/HYL/frontier state before acting. A missing loop contract emits
`blocked-loop-contract-missing`; stale branch/head or diff binding emits
`blocked-loop-contract-stale`; a missing unfolded node emits
`blocked-hylo-frontier-missing`; a missing previous fold emits
`blocked-hylo-fold-missing`.

## HYL-v1 interpreter

A material action is legal only as an HSR-v1 transition:

```text
state_before
-> unfold work_node|parallel_frontier|terminal|blocked
-> action
-> fold evidence
-> continuation
```

No mutation is valid without an unfolded work node.
No continuation is valid without a fold verdict.
No completion is valid without terminal ATCG-v1.

The minimum valid material transition is therefore `unfold -> action -> fold`.
If any one of those fields is missing, the run is not governed actuation even
when tests, summaries, or progress projections exist.

Do not repair a missing interlock by performing more inspection or patching.
Return the blocker as the next HSR-v1 state and wait for the correct owner.

## Review lanes

Workflow review is CAS-backed and lane-aware. `standard` is the only CAS review lane required for the clean-review streak; auxiliary lanes are workflow-selected review lenses whose folded evidence must be current-artifact-bound.

```text
standard          ordinary CAS code-review attempt; the only lane that counts toward the 3-clean-review streak
footgun-finder   auxiliary CAS review lens for latent misuse hazards, unsafe defaults, misleading affordances, and future caller traps
invariant-ace    auxiliary CAS review lens for illegal states, owner/source-of-truth gaps, transition preservation, policy exceptions, witness parity, races, retries, duplicates, and loop invariants
complexity-mitigator
                  auxiliary CAS review lens for comprehension stalls, boolean soup, mixed responsibilities, dominated branches, hidden state, and one-patch-per-comment pressure
```

Rules:

- `standard` is required whenever workflow review is required or any auxiliary lane is selected.
- Auxiliary lanes are selected before review from the diff surface, accepted proof bar, user request, or prior review class, and the decision lives in the workflow-owned `review_profile`.
- Auxiliary lanes are real CAS review evidence, but they do not increment or interrupt the standard clean-review streak.
- Auxiliary findings must be folded through `$review-fold` and may block closeout or become accepted liabilities.
- Do not require unsupported `$cas` commands to produce semantic footgun/invariant/complexity lane labels. CAS transports and tuple-binds review evidence; the workflow owns auxiliary lens selection, folding, and blocker state.
- A selected auxiliary lane must carry current `head_sha`, `target_fingerprint`, `lens_contract`, `lens_evidence_state`, and `lens_evidence_ref` before ATCG may complete. `clean` and `findings-folded` are not enough without the lane contract.
- ATCG lane contracts are `footgun-lens-v1`, `invariant-gate-v1`, and `complexity-preflight-v1`. `lens_evidence_state` must be `valid` for completion.
- When workflow review is required, `review_profile` must explicitly account for `footgun-finder`, `invariant-ace`, and `complexity-mitigator` as selected/folded evidence or `not-required` with a reason; absence is unknown coverage, not clean review.
- Record `complexity_pressure` when standard or auxiliary reviews show repeated same-class findings, one-patch-per-comment pressure, review churn, or comprehension blockage. That pressure selects `complexity-mitigator` unless it is explicitly marked not applicable.
- A code change from any lane resets the standard clean-review streak to zero.
- Read-only or classification-only auxiliary lane results do not reset the standard streak unless they change artifact scope or proof bar.
- Do not rerun auxiliary lanes on every standard clean attempt unless their surface was touched, their prior result was blocked/validate-first, the proof bar changed, or a standard review exposes a new class owned by that lens.

### Review Obligation Router

`review_profile.obligation_router` records `ROR-v1` obligations when standard,
GitHub, human, or local review pressure contains specialized claims owned by an
auxiliary lens.

```yaml
obligation_router:
  version: ROR-v1
  obligations:
    - id: stable-obligation-id
      trigger: misuse-hazard | invariant-gap | complexity-pressure | complexity-stall | repeated-owner-boundary
      source_ref: {}
      owner_lens: footgun-finder | invariant-ace | complexity-mitigator
      state: clean | findings-folded | blocked | rerun-required | not-required
      evidence_ref: current folded lens evidence
      not_required_reason: source-bound reason when state is not-required
```

Routing rules:

- `misuse-hazard` selects `footgun-finder`.
- `invariant-gap` selects `invariant-ace`.
- `complexity-pressure`, `complexity-stall`, and repeated owner-boundary pressure select `complexity-mitigator`.
- A non-`not-required` obligation means the corresponding auxiliary lane must be selected in `review_profile.auxiliary_review_lanes` with current lens evidence before ATCG may complete.
- A `not-required` obligation must explain why the source-bound trigger does not require that lens. A bare clean or summary-shaped review-fold is not enough.

## HYL coalgebra

The default coalgebra is obligation-driven:

```text
if no accepted spec -> blocked
if topology nontrivial and no Scheme Plan -> produce scheme-planner node
if material and no ALSR/HYL -> produce agent-loop-schemes node
if no goal contract -> produce goal-contract node
if runtime interlock blocks mutation -> emit blocked HSR-v1 node
if review requested and no review profile -> produce review-profile node
if review requested and no standard CAS result -> produce standard CAS review node
if required auxiliary review lane missing or invalidated -> produce auxiliary review-lens evidence node
if CAS lane findings unclassified -> produce review-fold node
if review requested and no resolution agenda -> produce resolution-fold node
if accepted liabilities remain -> produce patch/refactor/branch-race node
if proof missing -> produce verifier/proof node
if standard clean CAS count < 3 -> produce fresh standard CAS review node
if proof-patch missing -> produce proof-patch node
if ATCG not run -> produce ATCG node
else -> terminal complete
```

## HYL algebra

The algebra folds effects into actuation state:

```text
code change -> reset standard clean CAS count and proof freshness
standard CAS review -> normalize through review-fold and update standard clean counter
auxiliary CAS review -> normalize through review-fold; do not update standard clean counter
review-fold -> update dispositions, lane blockers, and quotient findings into classes
resolution fold -> update accepted liabilities / no-code dispositions / blockers
proof check -> update verifier state
proof patch -> update proof state
subagent result -> accept/reject/integrate through lead reducer
ATCG -> complete|continue|blocked
```

Supporting effects cannot skip the algebra. A clean command, cached review,
proof summary, or `$ship` handoff updates state only after the owner reducer
folds it against the current artifact.

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

Parallelism does not weaken the three-standard-clean-CAS closure bar.

The standard clean-run counter resets to 0 after any accepted artifact-changing subagent result, including auxiliary-lane fixes, patch fanout results, and branch-race winner integration.

Read-only fanout, classification-only fanout, and clean auxiliary review lanes do not reset the standard counter unless the artifact scope or proof bar changes.

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
workflow review_profile selection
-> $cas standard review
-> optional auxiliary review lenses: footgun-finder | invariant-ace | complexity-mitigator
-> $review-fold
-> optional review-class-fanout
-> resolution fold
-> optional branch-race
-> $goal-grind accepted liabilities only
-> optional patch-fanout over disjoint accepted liabilities only
-> $evidence-fold
-> 3 clean normalized standard $cas review attempts
-> $proof-patch
-> ATCG-v1
```

Auxiliary lane selection:

- Use `footgun-finder` when the diff touches APIs, CLIs, config, examples, docs, defaults, flags, fallbacks, auth/permissions, persistence, lifecycle/state-machine surfaces, degraded success, or partial-success ambiguity.
- Use `invariant-ace` when the diff or proof bar touches illegal states, owner/source-of-truth ambiguity, transition preservation, policy exceptions, witness parity, fixture preconditions, races, retries, duplicates, stale handles, or loop invariants.
- Use `complexity-mitigator` when reviewability is blocked by hard-to-follow existing code, deep nesting, boolean soup, hidden state, mixed responsibilities, cross-file hops, duplicated/dominated factors, or likely one-patch-per-comment churn.
  Record this as `complexity_pressure` in `review_profile`; do not leave the lane implicit.

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
durable external coordination is required but unsupported
verification regresses
proof is stale or not bound to the current artifact
public tracker side effect would be needed without explicit intent
review is required but $cas standard review is unavailable or not run
workflow review is required but review_profile is missing, partial, or lacks explicit not-required reasons
required auxiliary CAS review lane is unavailable, blocked, or not folded
three clean normalized standard $cas review attempts are required but cannot be completed
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
- review profile:
  - standard CAS review: required|not-required, current verdict:
  - auxiliary lanes: footgun-finder|invariant-ace|complexity-mitigator each not-required|clean|findings-folded|blocked|rerun-required, with `lens_contract` / `lens_evidence_state` / `lens_evidence_ref` when selected
  - auxiliary blockers:
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
- clean normalized standard CAS review attempts: 0|1|2|3|not-required
  - ATCG fields: `standard_clean_runs_count` / `standard_clean_cas_runs`
  - required auxiliary lanes: folded|blocked|rerun-required|not-required
- goal contract summary:
- work list / next action:
- review-fold disposition, if any:
- review resolution, if any:
- evidence-fold verdict:
- ATCG-v1 verdict:
- proof-patch / ship handoff:
- learnings or memory-source handoff, if justified:
```
