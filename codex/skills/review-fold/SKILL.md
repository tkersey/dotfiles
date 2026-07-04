---
name: review-fold
description: "Compress review pressure into intent-anchored review work: classify findings, reject non-liabilities, choose proof-only vs minimal-fix vs refactor-kernel, and prevent one-patch-per-comment churn. Use after $cas review, PR review comments, CAS findings, reviewer suggestions, and review-like claims. Owns active review finding classification for goal workflows."
metadata:
  version: "1.4.11"
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

For `review-closeout` and exhaustive review, final completion requires three consecutive clean normalized **standard** `$cas` review attempts after implementation. `$review-fold` decides whether each review lane is normalized clean, blocking, or reset-worthy. `$actuating` / `$goal-actuating` own the `review_profile` that records which auxiliary lenses were selected or explicitly not required. Auxiliary CAS lanes do not increment or interrupt the standard clean streak.

## Review source rule

```text
workflow-initiated code review -> $cas review lanes -> $review-fold -> resolution fold -> implementation only for accepted liabilities
```

Existing PR comments, human reviewer comments, or prior CAS verdicts may be folded directly as review pressure. But if the workflow itself is asked to do code review, close review, run adversarial review, or satisfy a review proof bar, it must obtain that review through `$cas` first.

## CAS review lanes

Supported CAS-backed review lanes:

```text
standard              ordinary CAS code review; counts toward the 3-clean standard streak
footgun-finder       auxiliary lens for misuse hazards, unsafe defaults, hidden traps, misleading affordances, degraded success, and copy/paste hazards
invariant-ace        auxiliary lens for illegal states, owner/source-of-truth, transition preservation, exceptions, witness parity, races, retries, duplicates, stale handles, and loop invariants
complexity-mitigator auxiliary lens for comprehension stalls, boolean soup, mixed responsibilities, hidden state, dominated branches, incidental complexity, and one-patch-per-comment pressure
```

Only `standard` may set `contributes_to_standard_streak: yes`. Auxiliary lanes are review evidence; they may create blockers or accepted liabilities, but they do not count as standard clean reviews and do not interrupt standard-review consecutiveness. `$cas` transports tuple-bound evidence; it does not own the auxiliary lane selection policy.

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
  version: RF-v1.3
  goal_id:
  source:
    pr:
    review_backend: github-comments|cas-review-session|cas-review-bundle|human-review|prior-artifact
    cas_review:
      required: yes|no
      mode: none|cas-probe|cas-lane|cas-exhaustive
      bundle_ref:
      verdict_ref:
      lane: standard|footgun-finder|invariant-ace|complexity-mitigator|none
      lane_ref:
      clean_run:
        normalized_clean: yes|no
        contributes_to_standard_streak: yes|no
        resets_standard_counter: yes|no
        reason:
      auxiliary_lanes:
        - lane: footgun-finder|invariant-ace|complexity-mitigator
          verdict_ref:
          head_sha:
          target_fingerprint:
          folded: yes|no
          unresolved_blockers: yes|no
          rerun_required: yes|no
          reason:
  intent_anchor:
    original_goal:
    accepted_scope:
    non_goals: []
    changed_paths: []
  findings:
    - id:
      source_ref:
        cas_finding_id:
        finding_fingerprint:
        review_attempt_id:
        review_thread_id:
        review_turn_id:
        lane_role: standard|auxiliary|unknown
        head_sha:
        target_fingerprint:
      lane: standard|footgun-finder|invariant-ace|complexity-mitigator|human|prior-artifact|unknown
      claim:
      observed_fact:
      suggested_repair:
      law_family:
      falsified_law:
      owner_boundary:
      model_state: intact|local-gap|boundary-gap|unknown
      validity: valid|invalid|unproven|needs-owner
      liability: blocks-goal|regression-risk|style|new-requirement|out-of-scope|proof-gap|misuse-hazard|invariant-gap|complexity-stall
      intent_relation: core|adjacent|unrelated|expands-scope
      novelty: duplicate|same-class|new-class
      disposition: reject|proof-only|minimal-fix|refactor-kernel|ask-human|follow-up|blocked
      repair_level: none|proof-only|minimal-fix|refactor-kernel|branch-race|ask-human|follow-up|blocked
      minimal_response:
      proof_needed:
      alternatives_considered: []
      evidence_refs: []
      code_change_candidate: yes|no
      finding_mutation_authority:
        allowed: no
        reason:
  compression:
    equivalence_classes: []
    repeated_kernel:
    kernel_pressure: none|low|medium|high
    refactor_trigger:
      present: yes|no
      reason:
    reabstraction_candidate: yes|no
    one_patch_per_comment_risk: low|medium|high
    minimal_fix_regret_risk: low|medium|high
    lane_overlap:
      footgun_to_invariant: []
      footgun_to_complexity: []
      invariant_to_complexity: []
  recommended_resolution:
    review_mode: triage|remediation-plan|review-closeout
    reason:
    no_code_modifier_detected: yes|no
    accepted_liability_count:
    refactor_kernel_candidate_count:
    standard_clean_cas_runs:
      required: yes|no
      current_count: 0|1|2|3
      normalized_clean_this_run: yes|no
      reset_reason:
    auxiliary_review_lanes:
      footgun-finder: not-required|clean|findings-folded|blocked|rerun-required
      invariant-ace: not-required|clean|findings-folded|blocked|rerun-required
      complexity-mitigator: not-required|clean|findings-folded|blocked|rerun-required
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

RF-v1.3 folds the useful RFDEC-v1 receipt ideas into one review-fold schema
rather than creating a second active finding-decision format. CAS finding IDs
and fingerprints are evidence references only; `$review-fold` still classifies
validity, liability, owner boundary, and repair level, and the resolution fold
still owns mutation-authorizing work nodes.

## Compact receipt floor

Full RF-v1.3 is preferred for artifacts, handoffs, and review bundles. For
progress updates or tight review-closeout loops, do not collapse a material fold
to bare prose such as `valid minimal-fix`. Emit at least one joinable block
headed `RF-v1.3 compact:` whenever a fold affects mutation, clean-run counting,
thread disposition, or closure state.

Minimum compact fields:

```yaml
RF-v1.3 compact:
  source_ref:
    cas_finding_id:
    review_attempt_id:
    review_thread_id:
    lane_role: standard|auxiliary|human|prior-artifact|unknown
    head_sha:
    target_fingerprint:
  validity: valid|invalid|unproven|needs-owner
  liability: blocks-goal|regression-risk|style|new-requirement|out-of-scope|proof-gap|misuse-hazard|invariant-gap|complexity-stall
  intent_relation: core|adjacent|unrelated|expands-scope
  disposition: reject|proof-only|minimal-fix|refactor-kernel|ask-human|follow-up|blocked
  repair_level: none|proof-only|minimal-fix|refactor-kernel|branch-race|ask-human|follow-up|blocked
  owner_boundary:
  law_family:
  evidence_refs: []
  clean_run:
    normalized_clean: yes|no|not-applicable
    standard_count:
    reset_reason:
  finding_mutation_authority:
    allowed: no
    reason:
```

If a source lacks a field, write `unknown` and name the backend rather than
omitting the field. A compact receipt is not a second schema; it is the minimum
observable projection of RF-v1.3 needed by `$seq`, `$tune`, `$actuating`, and PR
thread sweeps.

Shortcut labels do not relax the floor. Phrases such as `straightforward
liability`, `obvious fix`, `valid P1`, `valid P2`, `accepted P1`, `accepted P2`,
or `both findings are liabilities` are material fold decisions, not receipts.
Emit full RF-v1.3 or `RF-v1.3 compact:` before those findings leave
`$review-fold`, before they are sent to the resolution fold, and before
implementation starts.

Fresh CAS-result prose has the same floor even when there is only one finding.
Treat the pattern class, not only the exact examples, as receipt-triggering:
`CAS attempt ... found ... P1/P2`, `CAS attempt ... returned ... P1/P2
findings`, `CAS found ... valid items`, `CAS found one remaining valid P1/P2`,
`CAS attempt ... returned another accepted P1/P2`, `the finding is valid`, `this
finding is valid too`, `CAS is right`, `accepted code-change liabilities`, `the
owner fix is`, `owner-correct fix is`, `the clean fix is`, `clean streak stays
at 0`, or `streak remains 0`. Those phrases accept liability or reset review
accounting; they are not RF receipts. Emit the fresh RF-v1.3 compact/full
receipt before describing the fix path, resolution node, or next mutation.

Grouped or same-boundary CAS prose has the same requirement. Treat the pattern
class, not only the exact examples, as receipt-triggering: `CAS found ... more`,
`CAS is still finding`, `CAS continues to find`, `same ... boundary`, `same
owner-boundary refactor`, `same owner boundary`, or `same-class finding`.
Those phrases accept a refactor-kernel or grouped-liability route when they
point to a repair direction. Emit the fresh RF-v1.3 compact/full receipt before
describing the refactor, replacement strategy, or next patch.

Receipt scope is per review result, not per closeout. A prior RF-v1.3 receipt
does not cover later CAS attempts, follow-up finding batches, reopened PR
threads, or dirty clean-streak attempts. Phrases such as `terminal CAS list
confirms`, `remaining findings`, `expected findings`, `next bounded node`, or
`compact follow-up patch` are also material folds when they accept findings,
reset clean-run accounting, or authorize another patch. Emit a fresh full or
compact RF-v1.3 receipt for that new source batch before it reaches the
resolution fold.

## Disposition law

- `reject`: claim is false, stale, duplicate with no new proof value, unrelated, already handled, incompatible with the goal, or merely preference/style without accepted liability.
- `proof-only`: current code likely satisfies the goal and the right response is proof, inspection, or reviewer explanation before editing.
- `minimal-fix`: one valid, in-scope, owner-correct liability has a small local response and does not share a broader missing boundary with other findings.
- `refactor-kernel`: multiple findings share one missing abstraction, owner boundary, state transition, validation rule, invariant, proof surface, or misuse trap.
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

When `one_patch_per_comment_risk: high`, do not silently recommend more
minimal fixes. Route to one of:

```text
refactor-kernel
branch-race
remediation-plan
blocked
```

Use an explicit exception only when `alternatives_considered` shows why a local
minimal fix is still owner-correct and does not preserve the repeated failure
class. Record that exception in `evidence_refs`.

## Modes

### Workflow review modes

- `triage`: classify findings and stop without a remediation agenda or implementation.
- `remediation-plan`: classify findings and produce a resolution plan without implementation.
- `review-closeout`: default `$actuating` review mode; implement only accepted code-change liabilities after the resolution fold, then require three clean normalized standard CAS review attempts before completion.

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
three consecutive clean normalized standard CAS review attempts are complete
CAS review is blocked and the blocker is reported
user explicitly lowers the review proof bar
```

A clean normalized standard CAS review attempt means no new in-scope accepted liability, unresolved proof gap, unresolved refactor-kernel candidate, or human-owned blocker remains after `$review-fold` and the resolution fold. Duplicate, rejected, out-of-scope, already-proven proof-only, follow-up, already-resolved findings, and clean auxiliary review-lane results do not make the standard attempt dirty.

Reset the standard clean-run counter to zero when code changes, review scope changes, base/head/diff changes, the proof bar changes, accepted auxiliary-lane remediation changes the artifact, or standard CAS lane continuity is lost.

Auxiliary CAS review lanes may still block closeout. They do not increment the standard counter. They do not interrupt standard-review consecutiveness. Rerun them only when their surface was touched, their prior result was blocked or validate-first, the proof bar changed, or a standard review exposes a new class owned by that lens.

`$review-fold` may reject or mark findings proof-only, but it must not convert an exhaustive review gate into a no-review closure.

## Procedure

1. Bind reviews to the original goal and current diff.
2. If fresh/exhaustive workflow code review is required and no CAS standard review result is present, stop and request `$cas` standard review.
3. If the workflow `review_profile` selected auxiliary lanes, require their CAS-backed results before final review folding unless they are explicitly marked not-required with a reason.
4. Classify each finding before any implementation.
5. Separate the claim, observed fact, and suggested repair when the review text includes all three.
6. Reject, block, ask, or follow up before code whenever validity, liability, or scope is not established.
7. Preserve CAS source refs when present: `cas_finding_id`, `finding_fingerprint`, `review_attempt_id`, tuple, and lane role.
8. Name the falsified law, owner boundary, model state, and repair level when a finding is valid or unresolved.
9. Emit full RF-v1.3 or the compact receipt floor before any accepted liability, blocker, clean-run decision, or thread disposition leaves the fold.
10. Treat `straightforward liability`, `obvious fix`, P1/P2 labels, and same-sentence grouped acceptances as receipt-triggering folds, not as receipt substitutes.
11. Treat single or small-batch CAS prose like `CAS attempt found a P1/P2`, `CAS attempt returned P1/P2 findings`, `CAS found valid items`, `CAS found one remaining valid P1/P2`, `CAS attempt returned another accepted P1/P2`, `the finding is valid`, `this finding is valid too`, `CAS is right`, `accepted code-change liabilities`, `the owner fix is`, `owner-correct fix is`, `the clean fix is`, `clean streak stays at 0`, or `streak remains 0` as receipt-triggering folds before any repair path is described.
12. Treat grouped CAS prose like `CAS found ... more`, `CAS is still finding`, `CAS continues to find`, `same ... boundary`, `same owner-boundary refactor`, or `same-class finding` as a receipt-triggering fold before any refactor or replacement strategy is described.
13. Treat each new CAS attempt result, follow-up finding batch, reopened thread batch, or dirty clean-streak attempt as a new receipt scope; do not reuse an earlier RF receipt for later findings.
14. Collapse duplicates and same-family comments across lanes.
15. Mark whether the current standard attempt is normalized clean and whether the standard clean-run counter resets.
16. Mark auxiliary lane state as `clean`, `findings-folded`, `blocked`, or `rerun-required`; never count it as a standard clean run.
17. Recommend `triage`, `remediation-plan`, or `review-closeout` from the user's requested mode and the accepted liabilities.
18. Decide whether each finding's proper response is no code, proof, local fix, refactor, branch race, ask, or follow-up.
19. Escalate high one-patch-per-comment risk to `refactor-kernel`, `branch-race`, `remediation-plan`, or `blocked` unless an explicit owner-boundary exception is recorded.
20. Mark review-class fanout safe only for classification/investigation classes; raw findings must not fan out directly to patch workers.
21. Produce a small work graph only for accepted liabilities and only after the resolution fold accepts code-changing work.
22. Hand off to `$goal-grind` for implementation and `$evidence-fold` for proof only after a resolution fold accepts code-change liabilities.
23. For post-implementation CAS runs, mark whether the normalized standard result is clean and whether the standard clean-run counter resets.
24. Preserve reviewer response drafts as drafts; do not post public comments unless explicitly asked.

## Default behavior in `$actuating`

When called by `$actuating`:

- default to `review-closeout` for review requests;
- require three consecutive clean normalized standard `$cas` review attempts before completing `review-closeout` or exhaustive review;
- fold selected auxiliary CAS lanes through `$review-fold` before resolution/implementation;
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
- Do not count auxiliary CAS lanes as standard clean reviews.
- Do not store auxiliary lane selection policy only in `$cas` transport fields.
- Do not let accepted liabilities, blockers, or clean-run decisions leave only as unjoinable prose.
- Do not use `straightforward liability`, `obvious fix`, or severity labels as substitutes for RF-v1.3 receipt fields.
- Do not let one RF receipt for an earlier CAS batch stand in for later follow-up findings, dirty clean-streak attempts, or reopened thread batches.
- Do not claim review closure before three clean normalized standard CAS attempts when `review-closeout` or exhaustive review requires them.
- Do not resolve or reply to PR threads without explicit public-side-effect intent.
- `$review-fold` owns active review adjudication; do not route findings through retired skill paths.
