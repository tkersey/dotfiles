# Comment Ledger schema

Use one row per review comment.

Fields:
- `comment_id`
- `reviewer`
- `short_excerpt`
- `file_or_thread`
- `summary`
- `relevance_class`
- `disposition`
- `grounding`
- `rationale_match`
- `diagnosis_quality`
- `materiality`
- `freshness`
- `proposed_fix_validity`
- `strongest_no_change_countercase`
- `no_change_countercase_status`
- `governing_invariant`
- `reframe_type`
- `remediation_posture`
- `minimum_evidence_to_change_mind`
- `evidence_basis`
- `reply_stance`
- `handoff_action`
- `notes`

Allowed `relevance_class` values:
- `material-relevant`
- `relevant-nonmaterial`
- `partially-relevant`
- `stale-or-superseded`
- `unsupported`
- `out-of-scope`
- `preference-only`

Allowed `disposition` values:
- `act`
- `rebut`
- `defer`
- `need-evidence`

Allowed `diagnosis_quality` values:
- `correct`
- `partially-correct`
- `misdiagnosed`

Allowed `freshness` values:
- `current`
- `stale`
- `superseded`
- `unclear`

Allowed `proposed_fix_validity` values:
- `valid`
- `partially-valid`
- `wrong-fix`
- `overbroad`
- `under-specified`
- `not-applicable`

Allowed `no_change_countercase_status` values:
- `defeated`
- `not-defeated`
- `unresolved`

Allowed `reframe_type` values:
- `none`
- `governing-invariant`
- `source-of-truth-rule`
- `ownership-boundary`
- `soundness-obligation`
- `api-contract`
- `validation-only`

Allowed `remediation_posture` values:
- `no-change`
- `rebut`
- `validating-check-only`
- `accretive-remediation`
- `structural-remediation`

Allowed `reply_stance` values:
- `acknowledge-and-fix`
- `acknowledge-and-bound`
- `rebut-with-evidence`
- `defer-with-scope`
- `ask-for-evidence`

Allowed `handoff_action` values:
- `none`
- `route-to-accretive-implementer`
- `route-to-fixed-point-driver`
- `ask-user`
- `draft-reply`

## Governing Invariant Ledger schema

Use one row per inferred invariant cluster.

Fields:
- `invariant_id`
- `invariant_statement`
- `comments`
- `evidence_basis`
- `violated_or_threatened`
- `minimum_fix_shape`
- `handoff_action`
- `why_not_local_fixes`

Allowed `violated_or_threatened` values:
- `violated`
- `threatened`
- `not-proven`
- `not-applicable`

## Tail-weight requirement
The full ledger may appear above, but the final visible section must collapse it into:
- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Invariant-Level Handoff
- Acceptance Skew Audit
- Handoff Agenda
- Adjudication Bottom Line
