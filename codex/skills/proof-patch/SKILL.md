---
name: proof-patch
description: "Render a concise terminal human proof from a current complete deterministic Artifact Kernel closure receipt, while preserving read compatibility with legacy closure-decision/v1. Use after implementation or review closeout to bind the goal, construction, subject, Evidence Ledger head, review convergence, counterexample disposition, retirements, validation, residual risk, and human review focus without deciding closure or publishing."
---

# Proof Patch

## Mission

Render the final human-readable proof after live closure has been derived.

```text
current actuating-closure-receipt/v1
or current legacy closure-decision/v1
-> goal-relevant proof view
-> human review focus
```

This skill does not decide completion, select architecture or repairs, classify
Counterexamples, count review attempts, append Evidence Ledger events, or
publish.

## Required input

Select exactly one protocol. Never combine their control artifacts.

```yaml
proof_patch_input:
  protocol: artifact-kernel-v1 | legacy-actuating-v1

  artifact_kernel:
    closure_receipt:
      schema: actuating-closure-receipt/v1
      receipt_id:
      goal_id:
      goal_contract_ref:
      construction_ref:
      subject_digest:
      evidence_material_head:
      evidence_head_at_projection:
      review_contract_digest:
      review_head_sha: null | GIT_OBJECT_ID
      review_merge_base_sha: null | GIT_OBJECT_ID
      publication_repository: null | owner/name
      publication_pr_url: null | URL
      publication_base_sha: null | GIT_OBJECT_ID
      publication_head_sha: null | GIT_OBJECT_ID
      verdict: complete
      blockers: []
      created_at:
    goal_contract: {}
    construction_contract: {}
    counterexample_sets: []
    evidence_refs: []
    ship_receipt: {} | null

  legacy:
    closure_decision:
      version: closure-decision/v1
      decision_id:
      run_id:
      evaluated_artifact: {}
      run_digest:
      resolution_digest:
      verdict: complete
      outcomes: {}
      evidence_basis: []
      review_basis: []
      ship_basis: []
      implementation_checkpoint: {} | null
    actuation_kernel_state: {}
    review_resolution: {} | null
    evidence_folds: []
    cas_evidence: {} | null
    ship_record: {} | null

  changed_paths: []
  diff_summary:
  validation_results: []
  review_dispositions: []
  residual_risks: []
```

For `artifact-kernel-v1`, rederive closure from the current Goal Contract,
Construction Contract, subject digest, Evidence Ledger material and full heads,
and static Review Contract before rendering. Reject a receipt whose bound input
or deterministic projection no longer matches. Render architecture only from the current
Construction Contract, classified bugs only from registered Counterexample
Sets, and observations only from the referenced Evidence Ledger. Artifact IDs
or event references alone are not enough when the human claim needs source
detail.

For `legacy-actuating-v1`, retain the existing freshness rule: recompute or
reject the decision if the branch, head, live-state fingerprint, run digest, or
resolution digest no longer matches. Render review strategy, lenses,
dispositions, and semantic balance only from bound legacy objects; basis IDs
alone are not enough.

## Output

```markdown
# Proof Patch

## Goal
...

## Artifact
- Protocol:
- Goal Contract / legacy run:
- Construction Contract / legacy closure decision:
- Subject / branch-head-live state:
- Evidence Ledger material/full head / legacy run digest:
- Review Contract / legacy resolution digest:
- Goal outcome:
- Next owner:

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
- Review subject:
- Auxiliary lenses:
- Standard clean streak:
- Request-local recovery:
- Unresolved Counterexamples:

## Retirement and semantic balance
- Added constructs and replacements:
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
```

For a legacy input, map the existing review-resolution and CAS evidence into
the corresponding human sections without pretending those retired artifact
families exist in an Artifact Kernel goal.

## Procedure

1. Select exactly one protocol and require its current terminal receipt with
   `verdict: complete`.
2. For Artifact Kernel input, rederive the closure projection and exact-match
   every bound artifact, subject, Evidence Ledger head, Review Contract, and
   applicable review/publication tuple.
3. For legacy input, enforce the existing closure-decision freshness checks.
4. Bind every reported claim to current source detail, not only a receipt ID.
5. Summarize only goal-relevant changes, Counterexample dispositions, proof
   observations, review convergence, and retirements.
6. Include anti-gaming checks, unavailable checks, and residual risk.

## Guardrails

- Do not emit final proof before current complete closure.
- Do not accept a replayed, hand-edited, stale, or cross-protocol receipt.
- Do not mix legacy and Artifact Kernel control semantics within one goal.
- Do not treat the Proof Patch as closure authority or persist it as peer truth.
- Do not hide failed or unavailable verification.
- Do not treat rejected or proof-only findings as code changes.
- Do not publish, replace `$ship`, or perform public side effects.
