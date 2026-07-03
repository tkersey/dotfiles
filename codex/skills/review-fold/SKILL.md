---
name: review-fold
description: "Compress review pressure into intent-anchored review work: classify findings, reject non-liabilities, choose proof-only vs minimal-fix vs refactor-kernel, and prevent one-patch-per-comment churn. Use after $cas review, PR review comments, CAS findings, reviewer suggestions, and review-like claims."
metadata:
  version: "1.1.0"
  activation_cost: medium
  default_depth: high
---

# Review Fold

## Mission

Turn review pressure into the right next action, not more code by default.

```text
review comments + goal contract + current diff
-> review fold
-> proof-only | reject | minimal fix | refactor kernel | ask | follow-up
```

This skill is the review-specific evidence fold for the recursive goal scheme. It complements `$review-adjudication`: use `$review-adjudication` for detailed claim law; use `$review-fold` to control the whole review loop and pick the smallest correct response.

`$review-fold` consumes review findings. It does not replace code review. When the workflow needs to perform fresh, adversarial, or exhaustive code review, the review source must be `$cas`.

## Relationship to resolve

`$review-fold` classifies findings. It does not, by itself, decide that review work stops.

For `$actuating` review workflows, default closure mode is `resolve` unless the user explicitly requests `review-only`, `resolution-plan-only`, audit-only, or no implementation.

```text
$cas = review source
$review-fold = finding classifier
resolution fold = resolution plan compiler
$goal-grind = implementation engine for accepted liabilities
```

For `resolve` and exhaustive review, final completion requires three consecutive clean normalized `$cas` review runs after implementation. `$review-fold` decides whether each CAS run is normalized clean.

## Review source rule

```text
workflow-initiated code review -> $cas review -> $review-fold -> implementation only for accepted liabilities
```

Existing PR comments, human reviewer comments, or prior CAS verdicts may be folded directly as review pressure. But if the workflow itself is asked to do code review, close review, run adversarial review, or satisfy a review proof bar, it must obtain that review through `$cas` first.

## Review fold schema

```yaml
review_fold:
  version: RF-v1
  goal_id:
  source:
    pr:
    review_backend: github-comments|cas-review-session|human-review|prior-artifact
    cas_review:
      required: yes|no
      mode: none|cas-probe|cas-lane|cas-exhaustive
      verdict_ref:
      lane_ref:
      clean_run:
        normalized_clean: yes|no
        resets_counter: yes|no
        reason:
  intent_anchor:
    original_goal:
    accepted_scope:
    non_goals: []
    changed_paths: []
  findings:
    - id:
      claim:
      observed_fact:
      validity: valid|invalid|unproven|needs-owner
      liability: blocks-goal|regression-risk|style|new-requirement|out-of-scope|proof-gap
      intent_relation: core|adjacent|unrelated|expands-scope
      novelty: duplicate|same-class|new-class
      disposition: reject|proof-only|minimal-fix|refactor-kernel|ask-human|follow-up
      minimal_response:
      proof_needed:
      code_change_allowed: yes|no
  compression:
    equivalence_classes: []
    repeated_kernel:
    reabstraction_candidate: yes|no
    one_patch_per_comment_risk: low|medium|high
  recommended_resolution:
    mode: review-only|resolution-plan-only|resolve
    reason:
    no_code_modifier_detected: yes|no
    accepted_liability_count:
    refactor_kernel_candidate_count:
    clean_cas_runs:
      required: yes|no
      current_count: 0|1|2|3
      normalized_clean_this_run: yes|no
      reset_reason:
  parallelism:
    review_class_fanout_safe: yes|no
    patch_fanout_safe_after_resolve: yes|no
    unsafe_parallel_reasons: []
  action_plan:
    mode: adjudicate-only|proof-only|minimal-fix|refactor-kernel|branch-race|st-governed
    work_nodes: []
    do_not_fix: []
    reviewer_response_draft: []
```

## Disposition law

- `reject`: claim is false, outside accepted scope, already handled, or incompatible with the goal.
- `proof-only`: code likely correct; run or expose proof instead of editing.
- `minimal-fix`: valid liability with a single owner-correct local repair.
- `refactor-kernel`: multiple findings share one missing abstraction, boundary, state transition, or proof surface.
- `ask-human`: review introduces a product, compatibility, or API decision.
- `follow-up`: valid but not part of the intended change.

## Modes

### Workflow resolution modes

- `review-only`: classify findings and stop without a remediation agenda.
- `resolution-plan-only`: classify findings and produce a resolution plan without implementation.
- `resolve`: default `$actuating` review mode; implement only accepted code-change liabilities after the resolution fold, then require three clean normalized CAS review runs before completion.

### `adjudicate-only`

Classify findings and stop. No mutation.

### `proof-only`

Run checks, inspect current artifacts, or draft a response. No code unless proof fails.

### `minimal-fix`

Make the smallest owner-correct change for accepted liabilities.

### `refactor-kernel`

Replace many local fixes with one normal-form correction.

### `branch-race`

Compare two or more plausible fix/refactor strategies under the same verifier.

### `st-governed`

Hand off to `$st` when review remediation requires durable resource claims, external worktrees, or serialized integration.

## Exhaustive review behavior

When the source is `cas-exhaustive`, do not treat review as optional or merely advisory. Continue review/fix/fold cycles until one of these holds:

```text
three consecutive clean normalized CAS review runs are complete
CAS review is blocked and the blocker is reported
user explicitly lowers the review proof bar
```

A clean normalized CAS run means no new in-scope accepted liability, unresolved proof gap, unresolved refactor-kernel candidate, or human-owned blocker remains after `$review-fold` and the resolution fold. Duplicate, rejected, out-of-scope, already-proven proof-only, follow-up, or already-resolved findings do not make the run dirty.

Reset the clean-run counter to zero when code changes, review scope changes, base/head/diff changes, the proof bar changes, or CAS lane continuity is lost.

`$review-fold` may reject or mark findings proof-only, but it must not convert an exhaustive review gate into a no-review closure.

## Procedure

1. Bind reviews to the original goal and current diff.
2. If fresh/exhaustive workflow code review is required and no CAS result is present, stop and request `$cas` review.
3. Classify each finding before any implementation.
4. Collapse duplicates and same-family comments.
5. Recommend `review-only`, `resolution-plan-only`, or `resolve` from the user's requested mode and the accepted liabilities.
6. Decide whether each finding's proper response is no code, proof, local fix, refactor, branch race, ask, or follow-up.
7. Mark review-class fanout safe only for classification/investigation classes; raw findings must not fan out directly to patch workers.
8. Produce a small work graph only for accepted liabilities.
9. Hand off to `$goal-grind` for implementation and `$evidence-fold` for proof only after a resolution fold accepts code-change liabilities.
10. For post-implementation CAS runs, mark whether the normalized result is clean and whether the clean-run counter resets.
11. Preserve reviewer response drafts as drafts; do not post public comments unless explicitly asked.

## Default behavior in `$actuating`

When called by `$actuating`:

- default to `resolve` for review requests;
- require three consecutive clean normalized `$cas` review runs before completing `resolve` or exhaustive review;
- use `review-only` only when the user explicitly asks for no implementation or classification only;
- use `resolution-plan-only` only when the user explicitly asks for a plan/agenda without implementation;
- preserve no-code dispositions for rejected, proof-only, follow-up, or human-owned findings;
- never send raw review findings directly to implementation.

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

## Guardrails

- Raw review text is not executable.
- Do not add code to satisfy style or speculation when proof or rejection is correct.
- Do not accept scope expansion without user authority.
- Do not miss the refactor when many comments share one owner boundary.
- Do not replace a requested or required CAS review with non-CAS critique.
- Do not claim review closure before three clean normalized CAS runs when `resolve` or exhaustive review requires them.
- Do not resolve or reply to PR threads without explicit public-side-effect intent.
