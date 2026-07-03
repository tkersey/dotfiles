---
name: review-fold
description: "Compress review pressure into intent-anchored review work: classify findings, reject non-liabilities, choose proof-only vs minimal-fix vs refactor-kernel, and prevent one-patch-per-comment churn. Use after $cas review, PR review comments, CAS findings, reviewer suggestions, and review-like claims. Owns active review finding classification for goal workflows."
metadata:
  version: "1.2.0"
  activation_cost: medium
  default_depth: high
---

# Review Fold

## Mission

Turn review pressure into the right next action, not more code by default.

```text
review comments + goal contract + current diff
-> review fold
-> proof-only | reject | minimal-fix | refactor-kernel | ask | follow-up
```

This skill is the review-specific evidence fold for the recursive goal scheme. It owns active review finding classification for goal workflows: reduce review pressure to dispositions, group duplicates and same-family findings, and decide which liabilities may be considered by the resolution fold.

`$review-fold` consumes review findings. It does not replace code review. When the workflow needs to perform fresh, adversarial, or exhaustive code review, the review source must be `$cas`.

## Relationship to review closure

`$review-fold` classifies findings. It does not, by itself, decide that review work stops and it does not directly authorize mutation.

For `$actuating` review workflows, default review mode is `review-closeout` unless the user explicitly requests `triage`, `remediation-plan`, audit-only, or no implementation.

```text
$cas = review source
$review-fold = finding classifier
resolution fold = resolution plan compiler
$goal-grind = implementation engine for accepted liabilities
```

For `review-closeout` and exhaustive review, final completion requires three consecutive clean normalized `$cas` review runs after implementation. `$review-fold` decides whether each CAS run is normalized clean.

## Review source rule

```text
workflow-initiated code review -> $cas review -> $review-fold -> resolution fold -> implementation only for accepted liabilities
```

Existing PR comments, human reviewer comments, or prior CAS verdicts may be folded directly as review pressure. But if the workflow itself is asked to do code review, close review, run adversarial review, or satisfy a review proof bar, it must obtain that review through `$cas` first.

## Minimal review law

Use the smallest law that prevents review prose from becoming executable:

```text
claim != fact
fact != liability
liability != scope
scope != code change
code-change candidate != mutation authority
```

Operationally:

- A review claim is not automatically true.
- A true observation is not automatically branch-liable.
- A branch-liable observation is not automatically in the accepted scope.
- An in-scope liability is not automatically a code change.
- A code-change candidate is not mutation authority until the resolution fold accepts it.

This is a routing guard, not a counterexample compiler. Do not introduce CEX/AC/kernel ceremony merely to classify ordinary review findings.

## Review fold schema

```yaml
review_fold:
  version: RF-v1.2
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
      suggested_repair:
      validity: valid|invalid|unproven|needs-owner
      liability: blocks-goal|regression-risk|style|new-requirement|out-of-scope|proof-gap
      intent_relation: core|adjacent|unrelated|expands-scope
      novelty: duplicate|same-class|new-class
      disposition: reject|proof-only|minimal-fix|refactor-kernel|ask-human|follow-up|blocked
      minimal_response:
      proof_needed:
      code_change_candidate: yes|no
      finding_mutation_authority:
        allowed: no
        reason:
  compression:
    equivalence_classes: []
    repeated_kernel:
    reabstraction_candidate: yes|no
    one_patch_per_comment_risk: low|medium|high
  recommended_resolution:
    review_mode: triage|remediation-plan|review-closeout
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

- `reject`: claim is false, stale, duplicate with no new proof value, unrelated, already handled, incompatible with the goal, or merely preference/style without accepted liability.
- `proof-only`: current code likely satisfies the goal and the right response is proof, inspection, or reviewer explanation before editing.
- `minimal-fix`: one valid, in-scope, owner-correct liability has a small local response and does not share a broader missing boundary with other findings.
- `refactor-kernel`: multiple findings share one missing abstraction, owner boundary, state transition, validation rule, or proof surface.
- `ask-human`: review introduces a product, compatibility, API, UX, performance, security, or scope decision.
- `follow-up`: valid but not part of the intended change.
- `blocked`: validity, liability, current artifact state, review source, or accepted scope is unclear enough that implementation would be guesswork.

Deterministic downroutes:

```text
invalid | stale | unrelated -> reject
reviewer preference only -> reject unless the accepted goal made it material
valid but outside accepted scope -> follow-up or ask-human
scope expansion -> ask-human
missing proof -> proof-only before code
unknown validity/liability/scope -> blocked or ask-human
duplicate/same-class -> compress; do not create a new implementation distinction
```

A finding row never grants mutation authority. It only marks whether the resolution fold may consider code-changing work.

## Modes

### Workflow review modes

- `triage`: classify findings and stop without a remediation agenda or implementation.
- `remediation-plan`: classify findings and produce a resolution plan without implementation.
- `review-closeout`: default `$actuating` review mode; implement only accepted code-change liabilities after the resolution fold, then require three clean normalized CAS review runs before completion.

### `adjudicate-only`

Classify findings and stop. No mutation.

### `proof-only`

Run checks, inspect current artifacts, or draft a response. No code unless proof fails and the resolution fold creates an accepted liability.

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
4. Separate the claim, observed fact, and suggested repair when the review text includes all three.
5. Reject, block, ask, or follow up before code whenever validity, liability, or scope is not established.
6. Collapse duplicates and same-family comments.
7. Recommend `triage`, `remediation-plan`, or `review-closeout` from the user's requested mode and the accepted liabilities.
8. Decide whether each finding's proper response is no code, proof, local fix, refactor, branch race, ask, or follow-up.
9. Mark review-class fanout safe only for classification/investigation classes; raw findings must not fan out directly to patch workers.
10. Produce a small work graph only for accepted liabilities and only after the resolution fold accepts code-changing work.
11. Hand off to `$goal-grind` for implementation and `$evidence-fold` for proof only after a resolution fold accepts code-change liabilities.
12. For post-implementation CAS runs, mark whether the normalized result is clean and whether the clean-run counter resets.
13. Preserve reviewer response drafts as drafts; do not post public comments unless explicitly asked.

## Default behavior in `$actuating`

When called by `$actuating`:

- default to `review-closeout` for review requests;
- require three consecutive clean normalized `$cas` review runs before completing `review-closeout` or exhaustive review;
- use `triage` when the user names `triage`, or asks for no implementation or classification only;
- use `remediation-plan` when the user names `remediation-plan`, or asks for a plan/agenda without implementation;
- preserve no-code dispositions for rejected, proof-only, follow-up, or human-owned findings;
- never send raw review findings directly to implementation;
- never treat a finding row as mutation authority.

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
- Do not claim review closure before three clean normalized CAS runs when `review-closeout` or exhaustive review requires them.
- Do not resolve or reply to PR threads without explicit public-side-effect intent.
- `$review-fold` owns active review adjudication; do not route findings through retired skill paths.
