---
name: review-fold
description: "Compress review pressure into intent-anchored kernel-fold decisions: classify findings, reject non-liabilities, attach a refactor-kernel account to every material finding, quarantine unknowns, and prevent review prose from becoming mutation authority. Use after reviewer comments, PR threads, CAS-backed review evidence, human review, prior artifacts, local audit output, or review-like claims. Owns active review finding classification for goal workflows; does not own review backend selection, closeout policy, resolution planning, or implementation authority."
metadata:
  version: "1.7.0"
  activation_cost: medium
  default_depth: high
---

# Review Fold

## Mission

Turn review pressure into classified evidence plus a kernel account, not a
patch queue.

```text
review findings + goal contract + current artifact state
-> review fold
-> reject | proof-only | ask-human | follow-up | blocked
-> kernel_fold: none | refactor-kernel | unknown
```

`$review-fold` is the review-specific evidence reducer for goal workflows. It
classifies review-like claims, separates claims from facts and liabilities,
compresses duplicates and same-family findings, and gives every material
finding a kernel account that the downstream resolution fold can consume.

It is deliberately **review-backend neutral**. Review findings may come from
CAS-backed review evidence, GitHub PR comments, human review, prior artifacts,
local audit output, or another normalized source. `$review-fold` consumes the
evidence; it does not choose the backend.

## Ownership boundaries

`$review-fold` owns:

```text
review finding -> validity / liability / intent relation / disposition / kernel_fold
```

It does not own:

```text
fresh review backend selection
review-profile / auxiliary-lens selection
resolution planning
implementation authority
PR thread mutation or public replies
terminal closeout authority
```

Workflow owners such as `$actuating` and `$goal-actuating` decide whether fresh
review is required and which backend satisfies that requirement. In the current
goal workflow, fresh or closure-grade code review may be CAS-backed; that
policy lives in the caller workflow and `$cas`, not in `$review-fold`.

The normal review-closeout chain is:

```text
review source evidence
-> $review-fold finding classification + kernel_fold
-> resolution fold work-node decision
-> implementation only for refactor-kernel work with valid mutation authority
-> evidence fold / proof / terminal closure gate
```

A review finding never grants mutation authority by itself. A material
`refactor-kernel` becomes implementation work only after the resolution fold
accepts it and the actuation loop has valid mutation authority.

## Minimal review law

Use the smallest law that prevents review prose from becoming executable:

```text
claim != fact
fact != liability
liability != scope
scope != code change
code-change pressure != mutation authority
kernel fold != repair plan
```

Operationally:

- A review claim is not automatically true.
- A true observation is not automatically branch-liable.
- A branch-liable observation is not automatically in accepted scope.
- An in-scope liability is not automatically a code change.
- Code-change pressure is not mutation authority until the resolution fold accepts a work node.
- A kernel account classifies shape and pressure; it does not choose the patch.

This is a routing guard, not a counterexample compiler. Do not introduce CEX,
AC, or review-backend ceremony merely to classify ordinary review findings.

## Source model

Preserve source identity when it exists, but do not make one backend the
ontology.

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
- CAS-specific fields are evidence references only. They do not imply validity, liability, kernel status, clean-run effect, or mutation authority.
- PR thread IDs are source references only. Do not resolve threads, post replies, or mutate public review state without explicit public-side-effect intent.
- If fresh workflow review is required but no review source evidence is present, `$review-fold` reports a source blocker and hands control to the caller or review-source owner.

## RF-v1.5 schema

```yaml
review_fold:
  version: RF-v1.5
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
      model_state: intact|kernel-gap|unknown
      validity: valid|invalid|unproven|needs-owner
      liability: blocks-goal|regression-risk|style|new-requirement|out-of-scope|proof-gap|misuse-hazard|invariant-gap|complexity-stall
      intent_relation: core|adjacent|unrelated|expands-scope
      novelty: duplicate|same-class|new-class
      disposition: reject|proof-only|ask-human|follow-up|blocked
      kernel_fold:
        status: none|refactor-kernel|unknown
        pressure: none|low|medium|high
        equivalence_class:
        owner_boundary:
        law_family:
        falsifier:
        boundary_proof: proven|not-proven|not-applicable
        proof_gap:
        next_evidence_action: inspect-more|ask-human|blocked|branch-race|reclassify
        evidence_refs: []
      minimal_response:
      proof_needed:
      alternatives_considered: []
      evidence_refs: []
      finding_mutation_authority:
        allowed: no
        reason:
  compression:
    equivalence_classes: []
    repeated_kernel:
    kernel_pressure: none|low|medium|high
    reabstraction_candidate: yes|no
    patch_per_comment_risk: low|medium|high
    local_response_regret_risk: low|medium|high
  recommended_resolution:
    review_mode: triage|remediation-plan|review-closeout
    reason:
    no_code_modifier_detected: yes|no
    refactor_kernel_count:
    quarantined_unknown_count:
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
```

RF-v1.5 is a finding-classification and kernel-account receipt. It is not a
resolution plan, graph-control receipt, proof receipt, PR publication receipt,
or terminal completion proof.

## Compact receipt floor

Full RF-v1.5 is preferred for artifacts, handoffs, and review bundles. For
progress updates or tight review-closeout loops, do not collapse a material
fold to bare prose such as `valid liability` or `threads are clean`.

Emit at least one joinable block headed `RF-v1.5 compact:` whenever a fold
affects mutation, clean-run accounting, thread disposition, blocker state, or
closure state.

Minimum compact fields:

```yaml
RF-v1.5 compact:
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
  disposition: reject|proof-only|ask-human|follow-up|blocked
  kernel_fold:
    status: none|refactor-kernel|unknown
    pressure: none|low|medium|high
    equivalence_class:
    owner_boundary:
    law_family:
    falsifier:
    boundary_proof: proven|not-proven|not-applicable
    proof_gap:
    next_evidence_action: inspect-more|ask-human|blocked|branch-race|reclassify
    evidence_refs: []
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

If a source lacks a field, write `unknown` and name the backend rather than
omitting the field.

## Material fold trigger classes

Shortcut prose does not relax the receipt floor. Treat the semantic class, not the literal wording, as the trigger.

See `references/material-fold-triggers.yaml` for the canonical trigger
taxonomy.

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

- "valid finding," "in-scope liability," "both findings are liabilities," or a severity label used as acceptance is an acceptance shortcut.
- “owner fix,” “clean fix,” or “next patch” is a repair shortcut when it points to mutation; the fold must record kernel status and disabled mutation authority before resolution.
- “proof gaps remain” or “proof gaps resolved” is a proof-gap shortcut.
- “review attempt is clean,” “clean streak advances,” or “counter resets” is clean-run accounting.
- “threads are resolved,” “no unresolved threads,” or “thread sweep is clean” is thread disposition.
- “same owner boundary,” “same class,” or “larger repeated class” is grouped-liability pressure.
- A later review attempt, follow-up finding batch, reopened thread batch, or dirty clean-run attempt is a new source-batch boundary.

Emit a full or compact RF-v1.5 receipt before any such decision reaches the
resolution fold, mutation planning, closeout accounting, or public review-thread
handling.

## Disposition law

- `reject`: claim is false, stale, duplicate with no new proof value, unrelated, already handled, incompatible with the goal, or merely preference/style without goal authority.
- `proof-only`: current code likely satisfies the goal and the right response is proof, inspection, or reviewer explanation before editing.
- `ask-human`: review introduces a product, compatibility, API, UX, performance, security, or scope decision.
- `follow-up`: valid but not part of the intended change.
- `blocked`: validity, liability, current artifact state, review source, accepted scope, kernel status, unresolved refactor-kernel pressure, or unknown quarantine prevents closure or direct implementation.

Deterministic downroutes:

```text
invalid | stale | unrelated -> reject
reviewer preference only -> reject unless the accepted goal made it material
valid but outside accepted scope -> follow-up or ask-human
scope expansion -> ask-human
missing proof -> proof-only before code
unknown validity/liability/scope/source/current-artifact/kernel -> blocked or ask-human
duplicate/same-class -> compress; do not create a new implementation distinction
```

A finding row never grants mutation authority. It only marks whether the
resolution fold may consider no-code/control disposition or a refactor-kernel.
When `kernel_fold.status: refactor-kernel`, use `disposition: blocked` to mark
the current review source closure-blocked until the resolution fold acts. When
`kernel_fold.status: unknown`, use `blocked` or `ask-human`; no other
disposition may carry unknown material pressure.

## Kernel fold law

Every finding receives a `kernel_fold`.

- `none`: no in-scope code liability remains after rejection, proof, follow-up, or human-owned scope handling.
- `refactor-kernel`: material review pressure requires one owner-boundary kernel account before any code-changing work can be planned.
- `unknown`: the fold cannot prove whether a material kernel is required; it must record `proof_gap` and `next_evidence_action`, and the next owner must block, inspect, ask, branch-race, or reclassify before mutation.

When `kernel_fold.pressure: high`, do not silently shrink material pressure to a
local patch. Emit `status: refactor-kernel` with an owner boundary or
equivalence class, or emit `unknown`/`blocked` with the missing proof named.

Downstream implementation may realize a refactor-kernel as a small
owner-boundary change when `boundary_proof: proven`. That realization is not a
separate review-fold route; it belongs to the resolution fold and actuation loop.

## Modes

### Workflow review modes

- `triage`: classify findings and stop without a remediation agenda or implementation.
- `remediation-plan`: classify findings and produce resolution inputs without implementation.
- `review-closeout`: classify findings, preserve no-code dispositions, hand refactor-kernel accounts to the resolution fold, and let the caller workflow prove closure.

## Clean-run and exhaustive-review behavior

When the caller has a review-closeout or exhaustive-review proof bar,
`$review-fold` may decide whether a review source is normalized clean, dirty,
blocking, or reset-worthy. The caller owns the clean-run counter, proof bar,
backend, and terminal completion gate.

A normalized clean review source means no new in-scope refactor-kernel,
unresolved proof gap, unknown kernel, or human-owned blocker remains after
`$review-fold` and the resolution fold.

Duplicate, rejected, out-of-scope, already-proven proof-only, follow-up,
already-resolved findings, and clean auxiliary evidence do not make the source
dirty.

Reset conditions are caller-owned, but `$review-fold` should mark reset-worthy
facts when review evidence shows them:

```text
artifact changed
review scope changed
base/head/diff changed
proof bar changed
artifact-changing auxiliary remediation changed the artifact
review source continuity is lost
```

`$review-fold` may reject or mark findings proof-only, but it must not convert a
caller-required exhaustive review gate into a no-review closure.

## Procedure

1. Bind review findings to the original goal, accepted scope, non-goals, and current artifact state.
2. If fresh/exhaustive workflow review is required and no source evidence is present, stop with a source blocker for the caller or review-source owner.
3. Classify each finding before any implementation.
4. Separate claim, observed fact, and suggested repair when review text includes all three.
5. Reject, block, ask, or follow up before code whenever validity, liability, scope, or kernel status is not established.
6. Preserve source refs when present: backend, source batch, finding identity, review/thread identity, lane role, head SHA, and target fingerprint.
7. Name falsified law, owner boundary, model state, and kernel fold when a finding is valid or unresolved.
8. Emit full RF-v1.5 or the compact receipt floor before any material fold leaves `$review-fold`.
9. Treat material fold classes as semantic triggers, not literal phrase matching.
10. Treat each new review attempt, follow-up finding batch, reopened thread batch, thread disposition, or dirty clean-run attempt as a new receipt scope.
11. Collapse duplicates and same-family comments across sources and lanes.
12. Mark whether the current source is normalized clean and whether the caller's clean-run accounting should increment, reset, stay unchanged, or block.
13. Recommend `triage`, `remediation-plan`, or `review-closeout` from the user's requested mode and refactor-kernel pressure.
14. Decide whether each finding's proper review response is no code, proof, refactor-kernel, ask, follow-up, or block.
15. Emit `kernel_fold.status: refactor-kernel` or `unknown` when repeated owner-boundary pressure cannot be safely dismissed.
16. Mark review-class fanout safe only for classification/investigation classes; raw findings must not fan out directly to patch workers.
17. Produce resolution inputs only for refactor-kernel findings and only after the resolution fold accepts code-changing work.
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
- Do not miss the refactor-kernel when many comments share one owner boundary.
- Do not make `$review-fold` a review-backend transcript parser.
- Do not count auxiliary evidence as standard clean-review evidence.
- Do not store caller-owned review profile policy only in source-transport fields.
- Do not let refactor-kernel findings, blockers, clean-run decisions, or thread dispositions leave only as unjoinable prose.
- Do not let one RF receipt for an earlier source batch stand in for later findings, dirty clean-run attempts, or reopened thread batches.
- Do not claim review closure when the caller's terminal proof bar still requires review evidence, proof, delivery, or ATCG.
