---
name: proof-patch
description: "Render a concise human proof from Actuating's current complete closure receipt. Use after implementation or review closeout to bind the Goal, Construction, subject, Evidence Ledger head, Counterexample disposition, proof, retirements, applicable review convergence, publication, residual risk, and human review focus without deciding closure or publishing."
---

# Proof Patch

## Mission

Render a human-readable proof only after Actuating has applied its closure
theorem and returned a current `complete` receipt.

~~~text
current actuating-closure-receipt/v1
-> goal-relevant proof view
-> human review focus
~~~

Proof Patch does not decide completion, select architecture or repairs,
classify Counterexamples, count review attempts, append Evidence, choose a next
action, or publish.

## Required input

~~~yaml
proof_patch_input:
  closure_receipt:
    schema: actuating-closure-receipt/v1
    receipt_id:
    goal_contract_ref:
    construction_ref:
    subject_digest:
    evidence_head:
    review_contract_digest:
    closure_route: local-implementation | final-closeout
    verdict: complete
    cited_premise_refs: []
    blockers: []
  goal_contract: {}
  construction_contract: {}
  counterexample_sets: []
  evidence_refs: []
  review: # exactly one variant, matching closure_route
    local_implementation:
      review_required: false
    # OR
    final_closeout:
      auxiliaries_current: true
      clean_streak: 5
      full_wave_complete: true
      recovery_pending: false
  publication: # exactly one variant, matching closure_route
    local_implementation:
      publication_required: false
      ship_receipt: null
    # OR
    final_closeout:
      publication_required: true | false
      ship_receipt: {} | null
  changed_paths: []
  diff_summary:
  validation_results: []
  residual_risks: []
~~~

Require the complete canonical closure-receipt field set, replace only
`receipt_id` with JSON `null`, recompute its SHA-256 identity, and exact-match
`receipt_id` before rendering. Missing or extra fields block. Recheck that every
bound identity is current. Require exactly one review variant and one
publication variant, and exact-match both to `closure_route`. Render
architecture only from the Construction Contract,
classified bugs only from Counterexample Sets, observations only from cited
Evidence, final-closeout review convergence only from Actuating's current
evaluation of CAS owner receipts, and publication only from current Ship
evidence. For local implementation closure, require
`publication_required:false`, `ship_receipt:null`, and the no-review variant;
render review as not required, do not manufacture convergence, and reject any
supplied review-result or Ship-receipt payload. For final closeout, exact-match
`publication_required` to the Goal Contract and require current Ship evidence
when true or `ship_receipt:null` when false. Identifiers alone are insufficient
when a human claim requires source detail.

## Output

~~~markdown
# Proof Patch

## Goal
...

## Artifact
- Goal Contract:
- Construction Contract:
- Subject:
- Evidence Ledger head:
- Closure verdict:

## Changed
...

## Counterexamples and construction
- Accepted classes:
- Rejected or blocked classes:
- Invalid states eliminated:
- Preserved observations:
- Canonical owner:

## Evidence
| Check | Result | Binding |
|---|---|---|

## Review convergence
- Applicability: Not required for local implementation closure | Final closeout
- Auxiliary lenses: Not applicable | ...
- Standard clean streak: Not applicable | ...
- Request-local recovery: Not applicable | ...
- Unresolved Counterexamples:

## Retirements
- Required/completed retirements:
- Dominated constructs remaining:

## Anti-gaming
- Tests deleted:
- Assertions weakened:
- Checks skipped:
- Coverage reduced:
- Outside-goal behavior changed:

## Residual risk
...

## Human review focus
...
~~~

## Procedure

1. Require Actuating's current complete canonical `complete` receipt, its exact
   recomputed identity, and its explicit closure route.
2. Exact-match the Goal, Construction, subject, Evidence head, static Review
   Contract, route-selected review and publication variants, and applicable
   publication evidence. Require five-clean review facts only for
   `final-closeout`; require Ship evidence only when that route's Goal requires
   publication.
3. Bind every human claim to current source detail.
4. Summarize only goal-relevant changes, Counterexamples, proof observations,
   review convergence, and retirements.
5. State unavailable checks and residual risk directly.

## Guardrails

- Do not emit final proof before current complete closure.
- Do not accept a truncated, hand-edited, replayed, stale, or cross-subject
  receipt.
- Do not require review convergence for `local-implementation` or omit it for
  `final-closeout`.
- Do not accept a review-result or Ship-receipt payload for
  `local-implementation`, omit current Ship evidence for publication-required
  `final-closeout`, or manufacture Ship evidence when publication is not
  required.
- Do not treat the Proof Patch as authority or persist it as peer truth.
- Do not hide failed or unavailable verification.
- Do not publish, replace `$ship`, or perform public effects.
