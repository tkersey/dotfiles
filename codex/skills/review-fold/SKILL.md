---
name: review-fold
description: "Compress review pressure into intent-anchored review work: classify findings, reject non-liabilities, choose proof-only vs minimal-fix vs refactor-kernel, and prevent one-patch-per-comment churn. Use for PR review loops, CAS findings, reviewer suggestions, and review-like claims."
metadata:
  version: "1.0.0"
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

This skill is the review-specific evidence fold for the recursive goal scheme. It complements `$review-adjudication`: use `$review-adjudication` for detailed CEX-v1 claim law; use `$review-fold` to control the whole review loop and pick the smallest correct response.

## Review fold schema

```yaml
review_fold:
  version: RF-v1
  goal_id:
  source:
    pr:
    comments: []
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

## Procedure

1. Bind reviews to the original goal and current diff.
2. Classify each finding before any implementation.
3. Collapse duplicates and same-family comments.
4. Decide whether the proper response is no code, proof, local fix, refactor, branch race, ask, or follow-up.
5. Produce a small work graph only for accepted liabilities.
6. Hand off to `$goal-grind` for implementation and `$evidence-fold` for proof.
7. Preserve reviewer response drafts as drafts; do not post public comments unless explicitly asked.

## Guardrails

- Raw review text is not executable.
- Do not add code to satisfy style or speculation when proof or rejection is correct.
- Do not accept scope expansion without user authority.
- Do not miss the refactor when many comments share one owner boundary.
- Do not resolve or reply to PR threads without explicit public-side-effect intent.
