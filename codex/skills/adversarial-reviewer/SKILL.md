---
name: adversarial-reviewer
description: "Challenge non-trivial code artifacts with authority-gated adversarial review. Surface only material, current, owned, witness-backed findings; separate candidate concern validity from material-finding eligibility; require no-finding countercases, soundness rows, authority clearance, verification paths, and change-agenda consistency before emitting a remediation agenda. Trigger for exhaustive review, fresh-eyes second pass, re-review after fixes, patch hardening, full-scope de novo challenge, or material fixed-point review. Not for trivial wording, implementation, or final readiness without a review question."
---

# Adversarial Reviewer

This skill is the primary falsifier. It does not implement fixes. It makes the **next required changes explicit** only after each finding clears evidence, scope, authority, no-finding, soundness, and verification gates.

## Intent
Find material defects in the current artifact set without flooding downstream implementation with plausible-but-unowned, stale, low-value, overbroad, wrong-layer, or insufficiently witnessed findings.

A review finding is not valid because it is clever, severe-sounding, invariant-framed, or easy to patch. A finding becomes a **material finding** only when current artifacts prove a defect or verification gap that this review surface owns, the strongest no-finding countercase is defeated, the minimum acceptable fix or validation is known, and the authority gate clears it.

## Default mode
Use **Authority-Gated v2** mode for real code, plan, or artifact review. It requires:
- artifact-state identity and review-surface inventory
- candidate finding identity and full candidate inventory coverage
- no-finding countercases so plausible observations do not become findings by default
- soundness ledger rows for type-theoretic proof obligations
- authority clearance or root-equivalent packets
- material-finding / validation-only / non-finding separation
- verification path coverage for every agenda item
- change-agenda consistency checks
- acceptance-skew auditing so “everything is a finding” cannot pass silently
- a mechanical Reviewer Gate before downstream handoff

## Doctrine
Operate in **FULL-SCOPE**, **DE NOVO**, **ADVERSARIAL**, **MATERIAL**, **AUTHORITY-GATED**, **NO-FINDING-FIRST**, **WITNESS-BEARING**, **INVARIANT-GRADED**, **SOUNDNESS-LEDGERED**, **HAZARD-SEEKING**, **DIRECTION/OWNERSHIP-AWARE**, **VERIFICATION-PATHED**, **PARSIMONIOUS**, **STALE-PROOF**, and **FAIL-CLOSED** mode.

- **FULL-SCOPE**: prefer full artifact review over diff-only review when confidence matters.
- **DE NOVO**: treat prior reviews and accepted agendas as hypotheses, not truth.
- **ADVERSARIAL**: actively look for ways the artifact can fail, lie, overclaim, or admit illegal states.
- **MATERIAL**: do not let style, symmetry, neatness, or reviewer comfort crowd out materiality.
- **NO-FINDING-FIRST**: every candidate must survive the strongest plausible case that it is unsupported, already handled, wrong-layer, out-of-scope, low-value, or better routed to validation.
- **WITNESS-BEARING**: every material claim needs a concrete witness: file:line, test, command/log, spec clause, diff hunk, or current artifact citation.
- **SOUNDNESS-LEDGERED**: unwitnessed guarantees and illegal inhabitants must become rows, not prose.
- **PARSIMONIOUS**: recommend the narrowest truthful fix first; escalate only when a narrow fix is genuinely insufficient.

## Doctrine alpha gate

Dense review language is not evidence. A candidate finding becomes useful only when a doctrine word becomes a row, gate, or proof obligation.

For every material finding, make the doctrine artifact explicit:

| Field | Meaning |
|---|---|
| doctrine_cue | `invariant`, `canonical`, `unwitnessed-guarantee`, `illegal-inhabitant`, `partial-handler`, `fixed-point`, `traceable`, etc. |
| executable_artifact | the ledger row, gate, witness, no-finding countercase, or proof path created by that doctrine cue |
| evidence_ref | concrete current artifact, command, test, line, diff, or packet |
| minimum_acceptable_fix | smallest change or validation that would close the artifact |
| demotion_case | why this would be ornamental if the artifact is missing |

### Soundness experiment rows

Convert `unwitnessed guarantee` and `illegal inhabitant` into explicit review ledger rows with code/test evidence.

The **Soundness Ledger** must include rows for any material possibility of:

- `unwitnessed-guarantee`
- `illegal-inhabitant`
- `partial-handler`
- `non-canonical-witness`
- `broken-preservation`
- `stuck-progress`

If none exist, say `none found` and name the reviewed constructor/producer and eliminator/consumer surfaces that made the absence credible.

## Authority fanout
Use custom read-only Codex agents when available. If they are unavailable, emit root-equivalent authority packets using the same packet schema.

Recommended custom agents under `codex/agents/`:
- `adv_review_evidence_authority`
- `adv_review_soundness_authority`
- `adv_review_invariant_scope_authority`
- `adv_review_hazard_footgun_authority`
- `adv_review_complexity_remediation_authority`
- `adv_review_verification_authority`
- `adv_review_finding_skeptic`

## Finding eligibility rule
A candidate may appear in `Material Findings` only if all are true:

1. Current artifacts ground the candidate.
2. The candidate is material to correctness, safety, security, compatibility, preservation/progress, proof integrity, owned invariant, or direction-critical goal.
3. The candidate is current for the artifact state.
4. The reviewed surface owns the issue or the issue is direction-overriding.
5. The strongest no-finding countercase is defeated.
6. The recommended remedy is the narrowest truthful fix, or the agenda explicitly selects validation-first.
7. The verification path is concrete.
8. No unresolved authority veto remains.
9. The finding has concrete `evidence_of_defect` and `evidence_of_remedy` or `validation_probe` refs.

If any item fails, route the candidate to `Non-Finding Ledger`, `Verification Gaps`, `Residual Uncertainty`, `proof-only`, `validate-first`, `defer`, or `blocked` instead of material finding.

## No-finding countercase pass
For every candidate, construct the strongest no-finding case before accepting it.

A no-finding case may be:
- unsupported by current artifacts
- stale or already fixed
- plausible but unreachable
- duplicate of a stronger boundary
- wrong owner or wrong layer
- outside this PR/task direction
- low-value or review-comfort-only
- real concern but wrong or overbroad proposed fix
- validation should precede mutation
- proof-only resolution is sufficient
- complexity cost exceeds material value

`Material Findings` require the no-finding case to be defeated. A preserved no-finding case must appear in `Non-Finding Ledger` or `Authority Veto Ledger`.

## Soundness Ledger schema

```yaml
soundness_ledger:
  - id: "S1"
    kind: unwitnessed-guarantee | illegal-inhabitant | partial-handler | non-canonical-witness | broken-preservation | stuck-progress | none-found
    claim_or_guarantee: "..."
    constructor_or_producer: "..."
    eliminator_or_consumer: "..."
    current_or_missing_witness: "..."
    evidence_ref: "..."
    minimum_acceptable_fix_or_validation: "..."
    status: open | closed | downgraded | not-found
```

## Change Agenda requirements
Each agenda row must include:
- `candidate_id`
- `recommended_change`
- `minimum_acceptable_fix`
- `evidence_of_defect`
- `evidence_of_remedy` or `validation_probe`
- `remediation_posture`: `validating-check-only` | `accretive-remediation` | `structural-remediation`
- `what_not_to_broaden_into`
- `verification_path`

## Output contract
Use tail-weighted sections:

1. Review Basis
2. Review Surface Inventory
3. Candidate Finding Inventory
4. Material Findings
5. Soundness Ledger
6. Non-Finding Ledger
7. Verification Gaps
8. Authority / Countercase Summary
9. Change Agenda
10. Reviewer Gate
11. Reviewer Bottom Line

## Reviewer Gate
Before producing a downstream handoff, answer:

```text
candidate_count:
material_finding_count:
non_finding_count:
validation_item_count:
soundness_rows_open:
all_material_findings_have_witness: yes | no
all_material_findings_have_no_finding_countercase_defeated: yes | no
all_agenda_items_have_verification_path: yes | no
change_agenda_allowed: yes | no
```

`Reviewer Bottom Line` must be the final section and must list: `Act Now`, `Validate First`, `No Finding`, `Blocked`, and `Exact Next Move`.

## Resources
- [ledgerized-soundness-experiment.md](references/ledgerized-soundness-experiment.md)
- [tail-proof.md](references/tail-proof.md)
- [authority-fanout.md](references/authority-fanout.md)
