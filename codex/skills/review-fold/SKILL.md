---
name: review-fold
description: "Compress review pressure into intent-anchored review decisions: classify findings, reject non-liabilities, choose proof-only vs minimal-fix vs refactor-kernel, and prevent review prose from becoming mutation authority. Use after reviewer comments, PR threads, CAS-backed review evidence, human review, prior artifacts, local audit output, or review-like claims. Owns active review finding classification for goal workflows; does not own review backend selection, closeout policy, or implementation authority."
metadata:
  version: "1.5.0"
  activation_cost: medium
  default_depth: high
---

# Review Fold

## Mission

Turn review pressure into the right next decision, not more code by default.

```text
review findings + goal contract + current artifact state
-> review fold
-> reject | proof-only | minimal-fix | refactor-kernel | ask-human | follow-up | blocked
```

`$review-fold` is the review-specific evidence reducer for goal workflows. It classifies review-like claims, separates claims from facts and liabilities, compresses duplicates and same-family findings, and decides which findings may be considered by the resolution fold.

It is deliberately **review-backend neutral**. Review findings may come from CAS-backed review evidence, GitHub PR comments, human review, prior artifacts, local audit output, or another normalized source. `$review-fold` consumes the evidence; it does not choose the backend.

## Ownership boundaries

`$review-fold` owns:

```text
review finding -> validity / liability / intent relation / disposition / repair level
```

It does not own:

```text
fresh review backend selection
review-profile / auxiliary-lens selection
implementation authority
PR thread mutation or public replies
terminal closeout authority
```

Workflow owners such as `$actuating` and `$goal-actuating` decide whether fresh review is required and which backend satisfies that requirement. In the current goal workflow, fresh or closure-grade code review may be CAS-backed; that policy lives in the caller workflow and `$cas`, not in `$review-fold`.

The normal review-closeout chain is:

```text
review source evidence
-> $review-fold finding classification
-> resolution fold work-node decision
-> implementation only for accepted code-change liabilities
-> evidence fold / proof / terminal closure gate
```

A review finding never grants mutation authority by itself. A code-change candidate becomes implementation work only after the resolution fold accepts it and the actuation loop has valid mutation authority.

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
- A branch-liable observation is not automatically in accepted scope.
- An in-scope liability is not automatically a code change.
- A code-change candidate is not mutation authority until the resolution fold accepts it.

This is a routing guard, not a counterexample compiler. Do not introduce CEX, AC, kernel, or review-backend ceremony merely to classify ordinary review findings.

## Source model

Preserve source identity when it exists, but do not make one backend the ontology.

```yaml
source_ref:
  backend: cas|github-comments|human-review|prior-artifact|local-audit|other|unknown
  source_batch_id:
  finding_id:
  finding_fingerprint:
  review_attempt_id:
  review_thread_id:
  review_turn_id:
  lane_role: standard|auxiliary|human|prior-artifact|unknown
  head_sha:
  target_fingerprint:
  backend_specific: {}
```

Rules:

- `backend` is required for material receipts; use `unknown` only when the source really lacks identity.
- CAS-specific fields are evidence references only. They do not imply validity, liability, repair level, clean-run effect, or mutation authority.
- PR thread IDs are source references only. Do not resolve threads, post replies, or mutate public review state without explicit public-side-effect intent.
- If fresh workflow review is required but no review source evidence is present, `$review-fold` reports a source blocker and hands control to the caller or review-source owner.

## RF-v1.3 schema

```yaml
review_fold:
  version: RF-v1.3
  goal_id:
  source:
    backend: cas|github-comments|human-review|prior-artifact|local-audit|other|unknown
    source_batch_id:
    source_ref:
    review_required_by_caller: yes|no|unknown
    review_mode: none|existing-review|fresh-review|exhaustive-review|unknown
    current_artifact:
      head_sha:
      target_fingerprint:
      changed_paths: []
  intent_anchor:
    original_goal:
    accepted_scope:
    non_goals: []
    changed_paths: []
  findings:
    - id:
      source_ref:
        backend: cas|github-comments|human-review|prior-artifact|local-audit|other|unknown
        source_batch_id:
        finding_id:
        finding_fingerprint:
        review_attempt_id:
        review_thread_id:
        review_turn_id:
        lane_role: standard|auxiliary|human|prior-artifact|unknown
        head_sha:
        target_fingerprint:
        backend_specific: {}
      lane: standard|auxiliary|human|prior-artifact|unknown
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
  recommended_resolution:
    review_mode: triage|remediation-plan|review-closeout
    reason:
    no_code_modifier_detected: yes|no
    accepted_liability_count:
    refactor_kernel_candidate_count:
    clean_run_accounting:
      applies: yes|no
      normalized_clean_this_source: yes|no|not-applicable
      count_effect: increment|reset|none|blocked|unknown
      reason:
    auxiliary_evidence:
      folded: yes|no|not-applicable
      blockers: []
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

RF-v1.3 is a finding-classification receipt. It is not a resolution plan, graph-control receipt, proof receipt, PR publication receipt, or terminal completion proof.

## Compact receipt floor

Full RF-v1.3 is preferred for artifacts, handoffs, and review bundles. For progress updates or tight review-closeout loops, do not collapse a material fold to bare prose such as `valid minimal-fix` or `threads are clean`.

Emit at least one joinable block headed `RF-v1.3 compact:` whenever a fold affects mutation, clean-run accounting, thread disposition, blocker state, or closure state.

Minimum compact fields:

```yaml
RF-v1.3 compact:
  source_ref:
    backend: cas|github-comments|human-review|prior-artifact|local-audit|other|unknown
    source_batch_id:
    finding_id:
    finding_fingerprint:
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
    count_effect: increment|reset|none|blocked|unknown
    reason:
  finding_mutation_authority:
    allowed: no
    reason:
```

If a source lacks a field, write `unknown` and name the backend rather than omitting the field.

## Material fold trigger classes

Shortcut prose does not relax the receipt floor. Treat the semantic class, not the literal wording, as the trigger.

See `references/material-fold-triggers.yaml` for the canonical trigger taxonomy.

Material fold classes:

```text
acceptance shortcut
repair shortcut
proof-gap shortcut
clean-run accounting
thread disposition
grouped-liability / owner-boundary shortcut
source-batch boundary
```

Examples:

- “valid finding,” “accepted liability,” “both are liabilities,” or a severity label used as acceptance is an acceptance shortcut.
- “owner fix,” “clean fix,” or “next patch” is a repair shortcut when it points to mutation.
- “proof gaps remain” or “proof gaps resolved” is a proof-gap shortcut.
- “review attempt is clean,” “clean streak advances,” or “counter resets” is clean-run accounting.
- “threads are resolved,” “no unresolved threads,” or “thread sweep is clean” is thread disposition.
- “same owner boundary,” “same class,” or “larger repeated class” is grouped-liability pressure.
- A later review attempt, follow-up finding batch, reopened thread batch, or dirty clean-run attempt is a new source-batch boundary.

Emit a full or compact RF-v1.3 receipt before any such decision reaches the resolution fold, mutation planning, closeout accounting, or public review-thread handling.

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
unknown validity/liability/scope/source/current-artifact -> blocked or ask-human
duplicate/same-class -> compress; do not create a new implementation distinction
```

A finding row never grants mutation authority. It only marks whether the resolution fold may consider code-changing work.

When `one_patch_per_comment_risk: high`, do not silently recommend more minimal fixes. Route to one of:

```text
refactor-kernel
branch-race
remediation-plan
blocked
```

Use an explicit exception only when `alternatives_considered` shows why a local minimal fix is still owner-correct and does not preserve the repeated failure class. Record that exception in `evidence_refs`.

## Modes

### Workflow review modes

- `triage`: classify findings and stop without a remediation agenda or implementation.
- `remediation-plan`: classify findings and produce a resolution plan without implementation.
- `review-closeout`: classify findings, preserve no-code dispositions, hand accepted liabilities to the resolution fold, and let the caller workflow prove closure.

### Action modes

- `adjudicate-only`: classify findings and stop. No mutation.
- `proof-only`: run checks, inspect current artifacts, or draft a response. No code unless proof fails and the resolution fold creates an accepted liability.
- `minimal-fix`: smallest owner-correct change for accepted liabilities.
- `refactor-kernel`: replace many local fixes with one normal-form correction.
- `branch-race`: compare two or more plausible fix/refactor strategies under the same verifier.
- `st-governed`: hand off when review remediation requires durable resource claims, external worktrees, or serialized integration.

## Clean-run and exhaustive-review behavior

When the caller has a review-closeout or exhaustive-review proof bar, `$review-fold` may decide whether a review source is normalized clean, dirty, blocking, or reset-worthy. The caller owns the clean-run counter, proof bar, backend, and terminal completion gate.

A normalized clean review source means no new in-scope accepted liability, unresolved proof gap, unresolved refactor-kernel candidate, or human-owned blocker remains after `$review-fold` and the resolution fold.

Duplicate, rejected, out-of-scope, already-proven proof-only, follow-up, already-resolved findings, and clean auxiliary evidence do not make the source dirty.

Reset conditions are caller-owned, but `$review-fold` should mark reset-worthy facts when review evidence shows them:

```text
artifact changed
review scope changed
base/head/diff changed
proof bar changed
accepted auxiliary remediation changed the artifact
review source continuity is lost
```

`$review-fold` may reject or mark findings proof-only, but it must not convert a caller-required exhaustive review gate into a no-review closure.

## Procedure

1. Bind review findings to the original goal, accepted scope, non-goals, and current artifact state.
2. If fresh/exhaustive workflow review is required and no source evidence is present, stop with a source blocker for the caller or review-source owner.
3. Classify each finding before any implementation.
4. Separate claim, observed fact, and suggested repair when review text includes all three.
5. Reject, block, ask, or follow up before code whenever validity, liability, or scope is not established.
6. Preserve source refs when present: backend, source batch, finding identity, review/thread identity, lane role, head SHA, and target fingerprint.
7. Name falsified law, owner boundary, model state, and repair level when a finding is valid or unresolved.
8. Emit full RF-v1.3 or the compact receipt floor before any material fold leaves `$review-fold`.
9. Treat material fold classes as semantic triggers, not literal phrase matching.
10. Treat each new review attempt, follow-up finding batch, reopened thread batch, thread disposition, or dirty clean-run attempt as a new receipt scope.
11. Collapse duplicates and same-family comments across sources and lanes.
12. Mark whether the current source is normalized clean and whether the caller's clean-run accounting should increment, reset, stay unchanged, or block.
13. Recommend `triage`, `remediation-plan`, or `review-closeout` from the user's requested mode and accepted liabilities.
14. Decide whether each finding's proper response is no code, proof, local fix, refactor, branch race, ask, or follow-up.
15. Escalate high one-patch-per-comment risk to `refactor-kernel`, `branch-race`, `remediation-plan`, or `blocked` unless an explicit owner-boundary exception is recorded.
16. Mark review-class fanout safe only for classification/investigation classes; raw findings must not fan out directly to patch workers.
17. Produce work nodes only for accepted liabilities and only after the resolution fold accepts code-changing work.
18. Preserve reviewer response drafts as drafts; do not post public comments unless explicitly asked.

## Default behavior in `$actuating`

When called by `$actuating`:

- respect `$actuating` / `$goal-actuating` as the owner of review backend policy, review profile, clean-run counting, and ATCG terminal closure;
- classify all standard and auxiliary review evidence through `$review-fold`;
- preserve no-code dispositions for rejected, proof-only, follow-up, or human-owned findings;
- never send raw review findings directly to implementation;
- never treat a finding row as mutation authority;
- never count auxiliary review evidence as standard clean-review evidence; mark only the classification effect for the caller.

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

## Validation

Static skill validation:

```bash
uv run --with pyyaml -- python3 \
  codex/skills/.system/skill-creator/scripts/quick_validate.py \
  codex/skills/review-fold
```

Decision contract validation:

```bash
uv run --with pyyaml -- python3 \
  codex/skills/tune/tools/decision_contract_lint.py \
  codex/skills/review-fold/references/decision-contract.yaml
```

Receipt validation:

```bash
uv run python codex/skills/review-fold/tools/review_fold_receipt_gate.py \
  validate \
  --receipt path/to/review-fold-receipt.json \
  --format json
```

Behavioral tests:

```bash
uv run python -m unittest discover codex/skills/review-fold/tests
```

## Guardrails

- Raw review text is not executable.
- Do not add code to satisfy style or speculation when proof or rejection is correct.
- Do not accept scope expansion without user authority.
- Do not miss the refactor when many comments share one owner boundary.
- Do not make `$review-fold` a review-backend transcript parser.
- Do not count auxiliary evidence as standard clean-review evidence.
- Do not store caller-owned review profile policy only in source-transport fields.
- Do not let accepted liabilities, blockers, clean-run decisions, or thread dispositions leave only as unjoinable prose.
- Do not let one RF receipt for an earlier source batch stand in for later findings, dirty clean-run attempts, or reopened thread batches.
- Do not claim review closure when the caller's terminal proof bar still requires review evidence, proof, delivery, or ATCG.
- Do not resolve or reply to PR threads without explicit public-side-effect intent.
- `$review-fold` owns active review adjudication; do not route findings through retired skill paths.
