# Common routing vocabulary

Use routing terms consistently across adjudication, orchestration, and closure.

## Evidence grades

- `current-artifact`
- `current-test`
- `current-ci`
- `current-session-artifact`
- `prior-session-artifact`
- `memory-only`
- `reviewer-only`
- `none`

## Direction source

- `user-current-instruction`
- `proposed-plan`
- `st-plan`
- `update-plan`
- `PR-body`
- `issue`
- `design-doc`
- `repo-convention`
- `seq-recovered`
- `current-artifact`
- `unknown`

## Source freshness

- `current`
- `stale`
- `off-target`
- `unknown`

## Same objective

- `yes`
- `no`
- `unknown`

## Direction fit

- `aligned`
- `direction-overriding`
- `neutral`
- `conflicting`
- `unknown`

## Reviewer severity claim

- `P0`
- `P1`
- `P2`
- `P3`
- `P4`
- `unlabeled`
- `unknown`

## Accepted criticality

Implementation-grade:

- `blocker`
- `security-critical`
- `safety-critical`
- `data-loss-critical`
- `correctness-critical`
- `compatibility-critical`
- `direction-critical`

Not implementation-grade:

- `review-closure-only`
- `low-value`
- `out-of-lane`
- `unknown`

## Severity acceptance status

- `accepted`
- `downgraded`
- `rejected`
- `unresolved`

## Mutation value

- `codebase-material`
- `validation-material`
- `proof-only`
- `reply-only`
- `no-change`
- `blocked`

## Relevance classes

- `material-relevant`
- `relevant-nonmaterial`
- `partially-relevant`
- `stale-or-superseded`
- `unsupported`
- `out-of-scope`
- `preference-only`
- `direction-conflicting`
- `review-closure-only`

## Concern validity

- `valid`
- `partial`
- `unsupported`
- `unknown`

## Proposed-fix validity

- `valid`
- `partially-valid`
- `wrong-fix`
- `overbroad`
- `under-specified`
- `not-applicable`
- `validation-only`

## Dispositions

- `act`
- `rebut`
- `defer`
- `need-evidence`
- `blocked`

## No-change countercase status

- `defeated`
- `not-defeated`
- `unresolved`

## Decision tests

- `grounded`: `yes` / `no` / `unknown`
- `material`: `yes` / `no` / `user-requested` / `unknown`
- `fresh`: `current` / `stale` / `superseded` / `unclear`
- `diagnosis`: `correct` / `partially-correct` / `misdiagnosed` / `unknown`
- `scope-fit`: `yes` / `no` / `partial` / `unknown`
- `resolution value`: `merge-blocking` / `correctness-critical` /
  `direction-critical` / `review-closure` / `proof-only` /
  `validation-needed` / `low-value` / `out-of-lane` / `blocked`
- `no-change defeated`: `yes` / `no` / `unresolved`

## Resolve decisions

- `address`
- `validate-only`
- `resolve-thread-only`
- `do-not-address`
- `blocked`

## Handoff action

- `none`
- `route-to-accretive-implementer`
- `route-to-fixed-point-driver`
- `route-to-logophile`
- `ask-user`
- `draft-reply`

## Route rationale

- `narrow-local`
- `coupled-comments`
- `invariant-level`
- `structural`
- `validation-only`
- `contentious`
- `likely-to-reopen`
- `proof-only-thread`
- `no-change`
- `blocked`

## Gate values

Gate fields use:

- `pass`
- `fail`

`specialist_packet_coverage` may also use:

- `not-used`

Handoff permission fields use:

- `yes`
- `no`

## Compact-Gated v4 gate fields

- `artifact_state_coverage`
- `direction_context_coverage`
- `comment_inventory_coverage`
- `identity_coverage`
- `decision_test_coverage`
- `direction_fit_coverage`
- `severity_claim_coverage`
- `p2_plus_acceptance_coverage`
- `no_change_coverage`
- `disposition_coverage`
- `proposed_fix_separation`
- `evidence_ref_coverage`
- `validation_value_coverage`
- `resolve_selection_coverage`
- `resolve_countercase_coverage`
- `handoff_agenda_consistency`
- `selection_skew_audit`
- `p2_plus_severity_audit`
- `direction_fit_audit`
- `invariant_pass`
- `invariant_ace_coverage`
- `specialist_packet_coverage`
- `acceptance_skew_audit`
- `adjudication_complete`
- `implementation_handoff_allowed`
- `validation_handoff_allowed`
- `reply_handoff_allowed`
