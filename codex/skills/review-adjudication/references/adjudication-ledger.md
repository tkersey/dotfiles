# Adjudication Ledger

Use one row per review comment. For real PR comments, the Compact-Gated v3 ledger
is mandatory and must preserve raw identity, input inventory, artifact-state
identity, decision tests, and evidence references.

## Comment Inventory schema

```md
## Comment Inventory

- input_comment_count:
- ledger_row_count:
- input_comment_ids:
- ledger_comment_ids:
- missing_comment_ids:
- duplicate_comment_ids:
- synthesized_ids_for_real_comments: yes/no
```

The inventory is the completeness proof. A ledger with valid-looking rows but a
missing input comment is incomplete.

## Compact Comment Ledger schema

Required columns:

```md
| id/thread | reviewer | location | excerpt | claim | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

Column aliases are acceptable only if they remain unambiguous:

- `id/thread`: `comment_id`, `thread_id`, `review_comment_id`
- `location`: `file_or_thread`, `file`, `thread`, `path:line`
- `excerpt`: `short_excerpt`, `review_excerpt`
- `claim`: `summary`, `review_claim`
- `concern validity`: `concern_validity`
- `proposed fix validity`: `proposed_fix_validity`
- `relevance`: `relevance_class`
- `no-change status`: `no_change_countercase_status`
- `invariant`: `governing_invariant`
- `evidence grade`: `evidence_grade`
- `evidence ref`: `evidence_ref`, `evidence_basis`
- `handoff`: `handoff_action`

Do not collapse multiple raw comments into one row unless they are also listed
individually and the merged invariant cluster references those raw rows.

## Decision Tests schema

```md
| id/thread | grounded | material | fresh | diagnosis | scope-fit | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|
```

Allowed values:

- `grounded`: `yes`, `no`, `unknown`
- `material`: `yes`, `no`, `user-requested`, `unknown`
- `fresh`: `current`, `stale`, `superseded`, `unclear`
- `diagnosis`: `correct`, `partially-correct`, `misdiagnosed`, `unknown`
- `scope-fit`: `yes`, `no`, `partial`, `unknown`
- `no-change defeated`: `yes`, `no`, `unresolved`

Every ledger row must have a matching Decision Tests row.

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
- `evidence_grade`
- `evidence_ref`
- `reply_stance`
- `handoff_action`
- `notes`

## Allowed values

### `evidence_grade`

- `current-artifact`
- `current-test`
- `current-ci`
- `current-session-artifact`
- `prior-session-artifact`
- `memory-only`
- `reviewer-only`
- `none`

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
- Decision Tests row with `grounded=yes`, `fresh=current`, `scope-fit=yes`, and
  `no-change defeated=yes`
- `material=yes` or `material=user-requested`
- evidence grade of `current-artifact`, `current-test`, `current-ci`, or
  `current-session-artifact`
- concrete evidence ref
- proposed-fix validity separated from concern validity
- a handoff action that matches the fix shape

If proposed-fix validity is `wrong-fix`, `overbroad`, `under-specified`, or
`not-applicable`, the handoff must not blindly implement the reviewer's proposed
fix. It must name a replacement fix shape in `Act On` or `Invariant-Level
Handoff`.

If proposed-fix validity is `validation-only`, disposition must be
`need-evidence`; it may not be `act`.

## Resolve Selection schema

Use one row per raw review comment after the adjudication buckets and before the
Handoff Agenda. This is the downstream selection contract for implementation,
validation, proof-only thread cleanup, no-change, or blocked outcomes.

```md
| id/thread | resolve decision | reason | next |
|---|---|---|---|
```

Allowed `resolve decision` values:

- `address`
- `validate-only`
- `resolve-thread-only`
- `do-not-address`
- `blocked`

Rules:

- `address` requires disposition `act` and no-change status `defeated`.
- `validate-only` requires disposition `need-evidence`.
- `resolve-thread-only` must cite current proof that no code change is needed.
- `do-not-address` must name the preserved no-change case.
- `blocked` must name missing evidence and force `adjudication_complete: fail`.
- Every Comment Ledger ID must appear exactly once in Resolve Selection.

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

## Specialist Packet Receipts schema

Emit this section when specialists are used:

```md
| role | packet status | artifact state match | scope match | finding added | route changed | used for | reason |
|---|---|---|---|---|---|---|---|
```

A specialist packet may shape routing only if it is packet-native, scoped,
evidence-bearing, current, and accepted. Rejected packets may be recorded as
negative or neutral receipts but must not be used as evidence.

## Adjudication Gate schema

Emit this block before `Handoff Agenda`:

```md
## Adjudication Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass/fail | ... |
| comment_inventory_coverage | pass/fail | ... |
| identity_coverage | pass/fail | ... |
| decision_test_coverage | pass/fail | ... |
| no_change_coverage | pass/fail | ... |
| disposition_coverage | pass/fail | ... |
| proposed_fix_separation | pass/fail | ... |
| evidence_ref_coverage | pass/fail | ... |
| resolve_selection_coverage | pass/fail | ... |
| invariant_pass | pass/fail | ... |
| specialist_packet_coverage | pass/fail/not-used | ... |
| acceptance_skew_audit | pass/fail | ... |
| adjudication_complete | pass/fail | ... |
| implementation_handoff_allowed | yes/no | ... |
| validation_handoff_allowed | yes/no | ... |
| reply_handoff_allowed | yes/no | ... |
```

`adjudication_complete` may be `pass` only if every other required gate field is
`pass`, except `specialist_packet_coverage`, which may be `not-used`.

## Tail-weight requirement

The full ledger may appear above, but the final visible section must collapse it
into:

- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Resolve Selection
- Invariant-Level Handoff
- Acceptance Skew Audit
- All-Action Justification, if all substantive comments are `act`
- Adjudication Gate
- Handoff Agenda
- Adjudication Bottom Line

## Compact-Gated v3 route-selection fields

Resolve Selection is a downstream routing contract, not a restatement of the
Comment Ledger. Use one row per ledger row:

```md
| id/thread | resolve decision | reason | proof ref | next | route rationale |
|---|---|---|---|---|---|
```

`proof ref` must be concrete for `address`, `validate-only`, and
`resolve-thread-only`. For `blocked`, it may explicitly say `missing`.

The Handoff Agenda must be a subset-preserving projection of this table:

- `address` -> `items selected for implementation`
- `validate-only` -> `validation-only items`
- `resolve-thread-only` -> `proof-only thread-resolution items`
- `do-not-address` -> `items not selected`
- `blocked` -> `blocked items`

Every row also needs a Resolve Countercases entry that challenges the selected
resolve decision with the strongest alternative downstream decision.
