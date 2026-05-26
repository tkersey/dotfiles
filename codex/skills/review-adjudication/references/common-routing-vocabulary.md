# Common routing vocabulary

Use routing terms consistently across adjudication, orchestration, and closure.

## Evidence grades

Use exactly one per comment:

- `current-artifact`
- `current-test`
- `current-ci`
- `current-session-artifact`
- `prior-session-artifact`
- `memory-only`
- `reviewer-only`
- `none`

## Relevance classes

Use exactly one per comment:

- `material-relevant`
- `relevant-nonmaterial`
- `partially-relevant`
- `stale-or-superseded`
- `unsupported`
- `out-of-scope`
- `preference-only`

## Concern validity

Use exactly one per comment:

- `valid`
- `partial`
- `unsupported`
- `unknown`

## Dispositions

Use exactly one per comment:

- `act`
- `rebut`
- `defer`
- `need-evidence`

## No-change countercase status

Use exactly one per comment:

- `defeated`
- `not-defeated`
- `unresolved`

## Resolve decisions

Use exactly one per comment in `Resolve Selection`:

- `address`
- `validate-only`
- `resolve-thread-only`
- `do-not-address`
- `blocked`

## Proposed-fix validity

Use exactly one per comment:

- `valid`
- `partially-valid`
- `wrong-fix`
- `overbroad`
- `under-specified`
- `not-applicable`
- `validation-only`

## Decision tests

- `grounded`: `yes` / `no` / `unknown`
- `material`: `yes` / `no` / `user-requested` / `unknown`
- `fresh`: `current` / `stale` / `superseded` / `unclear`
- `diagnosis`: `correct` / `partially-correct` / `misdiagnosed` / `unknown`
- `scope-fit`: `yes` / `no` / `partial` / `unknown`
- `no-change defeated`: `yes` / `no` / `unresolved`

## Diagnosis quality

Use exactly one per comment:

- `correct`
- `partially-correct`
- `misdiagnosed`
- `unknown`

## Freshness

Use exactly one per comment:

- `current`
- `stale`
- `superseded`
- `unclear`

## Reframe type

Use exactly one per comment:

- `none`
- `governing-invariant`
- `source-of-truth-rule`
- `ownership-boundary`
- `soundness-obligation`
- `api-contract`
- `validation-only`

## Remediation posture

Use exactly one per comment:

- `no-change`
- `rebut`
- `validating-check-only`
- `accretive-remediation`
- `structural-remediation`

## Reply stance

Use exactly one when a reply stance is useful:

- `acknowledge-and-fix`
- `acknowledge-and-bound`
- `rebut-with-evidence`
- `defer-with-scope`
- `ask-for-evidence`

## Resolve decision

Use exactly one per comment in the Resolve Selection map:

- `address`
- `validate-only`
- `resolve-thread-only`
- `do-not-address`
- `blocked`

## Handoff action

Use exactly one per comment:

- `none`
- `route-to-accretive-implementer`
- `route-to-fixed-point-driver`
- `route-to-logophile`
- `ask-user`
- `draft-reply`

## Gate values

Gate fields use:

- `pass`
- `fail`

`specialist_packet_coverage` may also use:

- `not-used`

Handoff permission fields use:

- `yes`
- `no`

## Compact-Gated v2 gate fields

- `artifact_state_coverage`
- `comment_inventory_coverage`
- `identity_coverage`
- `decision_test_coverage`
- `no_change_coverage`
- `disposition_coverage`
- `proposed_fix_separation`
- `evidence_ref_coverage`
- `resolve_selection_coverage`
- `invariant_pass`
- `specialist_packet_coverage`
- `acceptance_skew_audit`
- `adjudication_complete`
- `implementation_handoff_allowed`
- `validation_handoff_allowed`
- `reply_handoff_allowed`

## Workflow states

- `ready`
- `conditionally-ready`
- `needs-remediation`
- `needs-decision`
- `blocked`

## Agreement pressure

- `aligned`
- `mixed`
- `conflicting`
- `unknown`
