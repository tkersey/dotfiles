---
name: verification-closure
description: "Decide final readiness after material coding work by checking closure gates, current-head proof, soundness rows, invariant witnesses, stale handoffs, and residual risk. Trigger for final readiness, closure gates, fixed-point claims, proof receipts, or 'is this ready?' after material work. Not the initial reviewer or implementer."
---

# Verification Closure

This skill is the final proof gate. It does not redesign, adjudicate, or implement. It decides whether the current artifact state is ready, conditionally ready, not ready, or indeterminate.

## Doctrine closure check

Closure must verify the artifact created by doctrine, not the doctrine prose.

For any doctrine cue used upstream, require the corresponding closure evidence:

| Doctrine cue | Closure evidence |
|---|---|
| `fixed-point` | current-head fixed-point test and no open material gate |
| `invariant` | test/check/proof defending the named invariant |
| `canonical` | single owner/representation remains, or shadow owner is explicitly justified |
| `witness` / `traceable` | proof receipt tied to current artifact state |
| `unwitnessed guarantee` | witness now exists, or claim is downgraded/removed |
| `illegal inhabitant` | constructor/producer no longer admits it, or boundary rejects it deliberately |
| `partial handler` | eliminator/consumer is total over the intended domain or partiality is explicit and safe |

Distinguish `absence_of_evidence` from `evidence_of_absence`. A search that found nothing is not proof unless the checked surface is exhaustive or targeted enough to exclude the bad state/path.

## Handoff intake
Accept handoff from `fixed-point-driver`, `adversarial-reviewer`, or direct user request. Treat all upstream packets as inputs, not proof.

If a handoff packet is stale, incomplete, or contradicted by current artifacts, set `Handoff Contract Status: stale | incomplete | contradicted` and reopen rather than closing.

Expected specialist inputs may include:
- `evidence_mapper`
- `soundness_auditor` or `adv_review_soundness_authority`
- `invariant_auditor` or `adv_review_invariant_scope_authority`
- `hazard_hunter` or `adv_review_hazard_footgun_authority`
- `complexity_auditor` or `adv_review_complexity_remediation_authority`
- `verification_auditor` or `adv_review_verification_authority`

## Closure Gate Ledger
Use exact gate names when relevant:
- `current_artifact_state`
- `material_findings_closed`
- `soundness_rows_closed`
- `critical_invariants_witnessed`
- `canonical_owner_preserved`
- `illegal_inhabitants_rejected`
- `partial_handlers_total_or_safe`
- `verification_receipts_current`
- `public_surface_intentional`
- `residual_risk_bounded`

Each gate status must be exactly one of:
- `closed`
- `open`
- `blocked`
- `not-applicable`
- `indeterminate`

Use exactly one readiness value:
- `ready`
- `conditionally-ready`
- `not-ready`
- `indeterminate`

## Evidence standard
Prefer proof in this order:
1. targeted reproducer or invariant test
2. direct command/check output
3. current diff + static inspection
4. accepted authority packet with concrete refs
5. reasoned claim with explicit uncertainty

A closure claim cannot rest on authority packet prose alone.

## Output contract
Use tail-weighted sections:

1. Verification Target
2. Handoff Contract Status
3. Evidence Inputs
4. Closure Gate Ledger
5. Evidence Run
6. Results
7. Fixed-Point Test
8. Readiness
9. Residual Risks
10. Reopen Trigger
11. Closure Bottom Line

`Closure Bottom Line` must be final and include:
- readiness
- strongest proof
- highest open gate
- exact next action

## Resources
- [tail-proof.md](references/tail-proof.md)
- [closure-gates.md](references/closure-gates.md)
