# Adjudication Gate contract v6

The v6 gate is the automation boundary between review analysis and any
implementation, validation, proof-only thread cleanup, or reply handoff. It must
fail closed when authority coverage, direction coverage, severity acceptance,
mutation approval, veto handling, or resolve-selection coverage is incomplete.

## Required gate fields

| field | value | pass condition |
|---|---|---|
| artifact_state_coverage | pass/fail | branch/head/diff/comment set identity recorded |
| direction_context_coverage | pass/fail | direction state identity recorded or missing fields named |
| comment_inventory_coverage | pass/fail | every input id appears exactly once |
| identity_coverage | pass/fail | raw id/source/reviewer/location/excerpt/claim preserved |
| decision_test_coverage | pass/fail | Decision Tests cover every row |
| direction_fit_coverage | pass/fail | Direction Tests cover every row |
| severity_claim_coverage | pass/fail | Severity Tests cover every row |
| mutation_approval_coverage | pass/fail | Mutation Approval Tests cover every row |
| p2_plus_acceptance_coverage | pass/fail | P2+ labels accepted/downgraded/rejected/unresolved with proof |
| no_change_coverage | pass/fail | every row has a no-change countercase |
| disposition_coverage | pass/fail | every row has one allowed disposition |
| proposed_fix_separation | pass/fail | concern and fix validity are independent |
| evidence_ref_coverage | pass/fail | `act` rows have current evidence refs |
| validation_value_coverage | pass/fail | validate-only rows have route-changing validation value |
| resolve_selection_coverage | pass/fail | every row has one resolve decision |
| resolve_countercase_coverage | pass/fail | every row challenges the selected route |
| handoff_agenda_consistency | pass/fail | agenda buckets exactly match Resolve Selection |
| source_pressure_audit | pass/fail | automated/current finding pressure audited |
| selection_skew_audit | pass/fail | all-selected pressure audited |
| p2_plus_severity_audit | pass/fail | P2+ pressure audited |
| direction_fit_audit | pass/fail | direction distribution and stale-plan pressure audited |
| invariant_pass | pass/fail | invariant clustering checked |
| authority_fanout_required | pass/fail | required authority lanes launched or root-equivalent packets emitted |
| authority_packet_coverage | pass/fail | all six authority roles have accepted/root-equivalent receipts |
| authority_clearance_coverage | pass/fail | every row has an Authority Clearance Matrix row |
| authority_veto_coverage | pass/fail | every preserved veto is recorded and respected |
| permissive_override_absent | pass/fail | no `address` row overrides veto/unresolved/missing authority |
| acceptance_skew_audit | pass/fail | all-action pressure audited |
| adjudication_complete | pass/fail | all required preceding fields pass |
| implementation_handoff_allowed | yes/no | yes only for authority-cleared `address` rows |
| validation_handoff_allowed | yes/no | yes only for validation/proof tasks selected as such |
| reply_handoff_allowed | yes/no | yes only for proof/reply/defer/rebut work |

## Authority rules

`address` is legal only when the row is `act`, mutation-approved, A-class,
direction-aligned or direction-overriding, implementation-critical, and the
Authority Clearance Matrix says `cleared-for-address`. Any row in the Authority
Veto Ledger forbids `address` for that id.

`validate-only` requires `authority status: cleared-for-validation` and
`validation-value: validate-first`.

`resolve-thread-only` requires `authority status: proof-only`.

`do-not-address` requires `authority status: no-change` or `defer`.

`blocked` requires `authority status: blocked`.
