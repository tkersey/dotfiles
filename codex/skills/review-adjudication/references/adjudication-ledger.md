# Adjudication Ledger

Use one row per review comment. For real PR comments, the compact ledger is
mandatory and must preserve raw identity.

## Compact Comment Ledger schema

Required columns:

```md
| id/thread | reviewer | location | claim | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|
```

Column aliases are acceptable only if they remain unambiguous:

- `id/thread`: `comment_id`, `thread_id`, `review_comment_id`
- `location`: `file_or_thread`, `file`, `thread`, `path:line`
- `claim`: `summary`, `review_claim`
- `concern validity`: `concern_validity`
- `proposed fix validity`: `proposed_fix_validity`
- `relevance`: `relevance_class`
- `no-change status`: `no_change_countercase_status`
- `invariant`: `governing_invariant`
- `evidence`: `evidence_basis`
- `handoff`: `handoff_action`

Do not collapse multiple raw comments into one row unless they are also listed
individually and the merged invariant cluster references those raw rows.

## Expanded Comment Ledger fields

Use these fields when Standard mode needs more detail:

- `comment_id`
- `reviewer`
- `short_excerpt`
- `file_or_thread`
- `summary`
- `claim`
- `relevance_class`
- `disposition`
- `grounding`
- `rationale_match`
- `diagnosis_quality`
- `concern_validity`
- `materiality`
- `freshness`
- `scope_fit`
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

## Allowed values

### `relevance_class`

- `material-relevant`
- `relevant-nonmaterial`
- `partially-relevant`
- `stale-or-superseded`
- `unsupported`
- `out-of-scope`
- `preference-only`

### `disposition`

- `act`
- `rebut`
- `defer`
- `need-evidence`

### `concern_validity`

- `valid`
- `partial`
- `unsupported`
- `unknown`

### `diagnosis_quality`

- `correct`
- `partially-correct`
- `misdiagnosed`
- `unknown`

### `freshness`

- `current`
- `stale`
- `superseded`
- `unclear`

### `proposed_fix_validity`

- `valid`
- `partially-valid`
- `wrong-fix`
- `overbroad`
- `under-specified`
- `not-applicable`
- `validation-only`

### `no_change_countercase_status`

- `defeated`
- `not-defeated`
- `unresolved`

### `reframe_type`

- `none`
- `governing-invariant`
- `source-of-truth-rule`
- `ownership-boundary`
- `soundness-obligation`
- `api-contract`
- `validation-only`

### `remediation_posture`

- `no-change`
- `rebut`
- `validating-check-only`
- `accretive-remediation`
- `structural-remediation`

### `reply_stance`

- `acknowledge-and-fix`
- `acknowledge-and-bound`
- `rebut-with-evidence`
- `defer-with-scope`
- `ask-for-evidence`

### `handoff_action`

- `none`
- `route-to-accretive-implementer`
- `route-to-fixed-point-driver`
- `route-to-logophile`
- `ask-user`
- `draft-reply`

## Act row requirements

Every `act` row must have:

- non-empty raw identity fields
- concern validity of `valid` or `partial`
- no-change status of `defeated`
- artifact-backed evidence basis
- proposed-fix validity separated from concern validity
- a handoff action that matches the fix shape

If proposed-fix validity is `wrong-fix`, `overbroad`, `under-specified`,
`not-applicable`, or `validation-only`, the handoff must not blindly implement
the reviewer's proposed fix.

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

If no invariant exists, state `No shared governing invariant found` and explain
why local handling is safe.

## Adjudication Gate schema

Emit this block before `Handoff Agenda`:

```md
## Adjudication Gate

| field | value | basis |
|---|---|---|
| identity_coverage | pass/fail | ... |
| no_change_coverage | pass/fail | ... |
| disposition_coverage | pass/fail | ... |
| proposed_fix_separation | pass/fail | ... |
| evidence_coverage | pass/fail | ... |
| invariant_pass | pass/fail | ... |
| acceptance_skew_audit | pass/fail | ... |
| handoff_allowed | yes/no | ... |
```

`handoff_allowed` may be `yes` only if every other gate field is `pass`.

## Tail-weight requirement

The full ledger may appear above, but the final visible section must collapse it
into:

- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Invariant-Level Handoff
- Acceptance Skew Audit
- All-Action Justification, if all substantive comments are `act`
- Adjudication Gate
- Handoff Agenda
- Adjudication Bottom Line
