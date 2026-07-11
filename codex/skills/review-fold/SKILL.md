---
name: review-fold
description: "Classify and quotient review findings from CAS, GitHub, human review, prior artifacts, or local audits against accepted intent and current artifact state. Use before any review resolution: separate claim, fact, and suggested repair; reject non-liabilities; route material findings as resolution inputs; never select repairs, count clean runs, or grant mutation."
---

# Review Fold

## Mission

Turn review pressure into pure classified evidence.

~~~text
review source + accepted intent + current artifact
-> RF-v2 classification and quotient
-> no-code disposition or resolution input
~~~

`$review-fold` owns validity, liability, intent relation, disposition, and
equivalence class. `review-resolution/v1` owns repair strategy, abstraction
accounting, selected work, and semantic balance. The caller owns review
backend, lens selection, clean-suffix accounting, and closure.

## Minimal law

~~~text
claim != fact
fact != liability
liability != accepted scope
accepted scope != code change
review classification != mutation authority
~~~

## RF-v2

~~~yaml
review_fold:
  version: RF-v2
  fold_id:
  goal_id:
  source:
    backend: cas | github-comments | human-review | prior-artifact | local-audit | other
    source_batch_id:
    source_state: clean | findings | invalid-proof | incomplete
    artifact:
      repo:
      base_sha:
      branch:
      head_sha:
      state_fingerprint:
    source_ref:
  intent_anchor:
    original_goal:
    accepted_scope: []
    non_goals: []
  findings:
    - finding_id:
      source_ref:
      claim:
      observed_fact:
      suggested_repair:
      validity: valid | invalid | unproven | needs-owner
      liability: blocks-goal | regression-risk | proof-gap | misuse-hazard | invariant-gap | complexity-stall | style | new-requirement | out-of-scope
      intent_relation: core | adjacent | unrelated | expands-scope
      novelty: duplicate | same-class | new-class
      disposition: reject | proof-only | ask-human | follow-up | resolution-input | blocked
      quotient_key:
      owner_boundary:
      law_family:
      falsifier:
      evidence_refs: []
      mutation_authority:
        allowed: false
        reason:
  compression:
    equivalence_classes:
      - quotient_key:
        finding_ids: []
        owner_boundary:
        law_family:
  routing_obligations:
    - trigger: misuse-hazard | invariant-gap | complexity-stall
      finding_ids: []
      owner_lens: footgun-finder | invariant-ace | complexity-mitigator
~~~

A current clean source may contain zero findings. That is valid classified
evidence, not caller-owned clean-run credit.

## Dispositions

- `reject`: false, stale, duplicate without new evidence, unrelated, already
  satisfied, or preference-only.
- `proof-only`: likely satisfied; inspect or prove before editing.
- `ask-human`: introduces a product, API, compatibility, UX, security,
  performance, or scope choice.
- `follow-up`: valid but outside the accepted goal.
- `resolution-input`: valid, in-scope material pressure ready for owner-boundary
  strategy selection.
- `blocked`: validity, ownership, artifact binding, or evidence remains unknown.

Only `resolution-input` may enter `review-resolution/v1`, and even then the
finding grants no mutation. Every resolution input requires a nonblank observed
fact distinct from its claim. If the observation is not established, keep the
finding `unproven` and route it to `proof-only` or `blocked`; a proof gap still
names the inspected proof surface and the missing obligation.

## Procedure

1. Bind the source to accepted intent and current artifact state.
2. Separate claim, observation, and suggested repair.
3. Classify validity, liability, intent relation, and novelty.
4. Assign every finding a no-code disposition or `resolution-input`.
5. Give each material finding a quotient key, owner boundary, law family,
   falsifier, and evidence references.
6. Collapse duplicates and same-class findings into equivalence classes.
7. Emit routing obligations for specialized liability classes.
8. Materialize RF-v2 as canonical JSON and validate it through `$ledger` with
   `$ledger run -- validate review-fold --input <rf-v2-json-file>`.
9. Hand only resolution inputs to the caller; never choose the patch.

Use [review-fold.valid.example.json](assets/review-fold.valid.example.json) as a
shape example, not as reusable evidence or authority.

## Guardrails

- Do not choose review backend or auxiliary lenses.
- Do not emit a selected work node, repair strategy, clean count, or closure
  verdict.
- Do not turn style or speculation into code.
- Do not accept scope expansion without user authority.
- Preserve source identity and current artifact binding.
- Treat `$ledger run -- validate` as pure receipt validation. Its pass verdict grants no
  mutation, repair selection, clean-run credit, or closure authority.
