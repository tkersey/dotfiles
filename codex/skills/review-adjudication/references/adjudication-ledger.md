# Comment Ledger schema

Use one row per review comment.

Fields:
- `comment_id`
- `summary`
- `relevance_class`
- `disposition`
- `grounding`
- `rationale_match`
- `diagnosis_quality`
- `materiality`
- `freshness`
- `remediation_posture`
- `minimum_evidence_to_change_mind`
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

Allowed `remediation_posture` values:
- `no-change`
- `rebut`
- `validating-check-only`
- `accretive-remediation`
- `structural-remediation`

Tail-weight requirement:
The full ledger may appear above, but the final visible section must collapse it into:
- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Handoff Agenda
- Adjudication Bottom Line
