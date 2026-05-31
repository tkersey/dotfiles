# Adjudication Gate contract

The Adjudication Gate is the automation boundary between review analysis and
implementation, validation, proof-only thread resolution, or reply handoff. It
must be emitted for every real PR review adjudication.

## Required block

```md
## Adjudication Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass | branch/head/diff/comment-set identity recorded or explicitly unavailable |
| comment_inventory_coverage | pass | input comments match ledger rows; no dropped or duplicate real comments |
| identity_coverage | pass | every raw comment has id/thread, reviewer, location, excerpt, and claim |
| decision_test_coverage | pass | every row has grounding/materiality/freshness/diagnosis/scope/resolution/no-change tests |
| no_change_coverage | pass | every comment has a countercase and status |
| disposition_coverage | pass | every comment has exactly one allowed disposition |
| proposed_fix_separation | pass | concern validity and proposed-fix validity are separate |
| evidence_ref_coverage | pass | every action has current evidence grade and concrete evidence ref |
| resolve_selection_coverage | pass | every ledger row has one valid downstream resolve decision, proof ref, and route rationale |
| resolve_countercase_coverage | pass | every ledger row has a resolve countercase challenging the selected downstream action |
| handoff_agenda_consistency | pass | Handoff Agenda is a subset-preserving projection of Resolve Selection |
| selection_skew_audit | pass | resolve-selection distribution audited; all-selected outputs justified |
| invariant_pass | pass | invariant clustering checked or named |
| specialist_packet_coverage | not-used | specialists were not used, or pass if receipts exist |
| acceptance_skew_audit | pass | disposition distribution audited |
| adjudication_complete | pass | all required gate fields pass |
| implementation_handoff_allowed | yes/no | yes only for artifact-backed `act` rows selected as `address` |
| validation_handoff_allowed | yes/no | yes only for validation/proof tasks |
| reply_handoff_allowed | yes/no | yes only for reply/drafting/thread-cleanup tasks |
```

## Resolution Warrants block

Every real PR review adjudication must issue downstream permission warrants:

```md
## Resolution Warrants

| warrant id | claim id | source | claim excerpt | decision | concern validity | proposed fix validity | no-change status | resolution value | route rationale | permitted action | permitted scope | forbidden actions | evidence refs | countercase ref | proof required | expiry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rw-c1 | c1 | github-review | retry writes twice | address | valid | valid | defeated | correctness-critical | narrow-local | mutate-code | files=src/a.py,tests/test_a.py | mutate outside permitted_scope | src/a.py:10 | c1 no-change defeated | pytest tests/test_a.py::test_retry_idempotent | invalid when HEAD/base/diff/comment-set changes |
```

Allowed `permitted action` values are `mutate-code`,
`add-validation-only`, `resolve-thread`, `draft-reply`, `defer`, and `none`.
A downstream skill must consume a matching active warrant before acting.

## Resolve Selection block

Every real PR review adjudication must include a downstream selection map:

```md
## Resolve Selection

| id/thread | resolve decision | reason | proof ref | next | route rationale |
|---|---|---|---|---|---|
| c1 | address | act row with defeated no-change case | src/a.py:10 | route-to-accretive-implementer | narrow-local |
| c2 | validate-only | failure mode is plausible but unproven | thread:c2 | validation probe only | validation-only |
| c3 | resolve-thread-only | already fixed on latest HEAD | tests/retry.test.ts::case | reply with proof and resolve thread | proof-only-thread |
| c4 | do-not-address | preference-only no-change case preserved | src/a.py:1 | none | no-change |
| c5 | blocked | missing artifact state or identity | missing | blocked | blocked |
```

Allowed `resolve decision` values are `address`, `validate-only`,
`resolve-thread-only`, `do-not-address`, and `blocked`.

Allowed `route rationale` values are `narrow-local`, `coupled-comments`,
`invariant-level`, `structural`, `validation-only`, `contentious`,
`likely-to-reopen`, `proof-only-thread`, `no-change`, and `blocked`.

Rules:

- `address` means implementation is selected and is legal only for `act` rows
  with defeated no-change cases and current evidence refs.
- `validate-only` means the next workflow may create proof but must not
  implement the requested fix yet; it is legal only for `need-evidence` rows.
- `resolve-thread-only` means the review thread can be answered or resolved with
  current proof without changing code.
- `do-not-address` means no implementation handoff; the reason must preserve the
  no-change case.
- `blocked` means selection evidence is incomplete and must force
  `adjudication_complete: fail` with all handoff permissions set to `no`.
- `route-to-fixed-point-driver` requires route rationale `coupled-comments`,
  `invariant-level`, `structural`, `validation-only`, `contentious`, or
  `likely-to-reopen`.
- `route-to-accretive-implementer` requires route rationale `narrow-local`.
- `resolve-thread-only` requires route rationale `proof-only-thread`.
- `do-not-address` requires route rationale `no-change`.
- `blocked` requires route rationale `blocked`.

## Resolve Countercases

Every ledger row must be challenged with a resolve-level countercase:

```md
## Resolve Countercases

- c1:
  - proposed resolve decision: address
  - strongest alternative resolve decision: validate-only
  - why alternative is rejected / preserved / unresolved: current failing test already proves the defect.
```

This prevents concern validity from being laundered into "worth resolving now".

## Handoff Agenda consistency

The Handoff Agenda must be a subset-preserving projection of Resolve Selection:

- `items selected for implementation` must equal the `address` rows.
- `validation-only items` must equal the `validate-only` rows.
- `proof-only thread-resolution items` must equal the `resolve-thread-only` rows.
- `items not selected` must equal the `do-not-address` rows.
- `blocked items` must equal the `blocked` rows.

The Handoff Agenda must not use broad terms such as `all` when explicit comment
IDs are required.

## Selection skew rule

If every substantive comment is selected as `address` or `validate-only`, the
gate may pass only when the output contains a structured All-Selected
Justification table covering:

- stale/already-fixed alternative
- proof-only thread-resolution alternative
- do-not-address alternative
- validate-before-mutation alternative
- out-of-scope/defer alternative
- fixed-point over-routing check

Each row must have `result=pass`, a concrete evidence ref, and a specific
explanation for why selected resolution is still warranted. Generic language like
"all are worth resolving" is insufficient.

## Pass conditions

- `artifact_state_coverage`: branch/head/diff/comment-set identity was recorded,
  or unavailable fields were explicitly named.
- `comment_inventory_coverage`: every input comment appears exactly once in the
  ledger, with no missing or duplicate raw IDs.
- `identity_coverage`: every real review comment has stable raw identity.
- `decision_test_coverage`: every comment has required Decision Tests fields,
  including `resolution value`.
- `no_change_coverage`: every comment has a strongest no-change countercase and
  one allowed status.
- `disposition_coverage`: every comment has exactly one disposition from the
  allowed set.
- `proposed_fix_separation`: every comment separates concern validity from
  proposed-fix validity.
- `evidence_ref_coverage`: every `act` row has current evidence grade and a
  concrete evidence reference.
- `resolve_selection_coverage`: every ledger row has exactly one Resolve
  Selection row, no unknown selection IDs exist, and selection decisions are
  consistent with disposition, no-change status, proof ref, next action, and
  route rationale.
- `resolve_countercase_coverage`: every ledger row has a resolve countercase.
- `handoff_agenda_consistency`: downstream handoff buckets match Resolve
  Selection exactly.
- `selection_skew_audit`: selection distribution is audited; all-selected
  outputs have structured justification.
- `invariant_pass`: invariant clustering was performed; shared invariants are
  named, or absence is justified.
- `specialist_packet_coverage`: `not-used` if no specialists were used; otherwise
  every accepted or rejected specialist packet has a receipt and rejected packets
  are not used as evidence.
- `acceptance_skew_audit`: disposition skew was audited; all-action outputs have
  a structured All-Action Justification table.
- `adjudication_complete`: `pass` only when all required gate fields pass.
- `implementation_handoff_allowed`: `yes` only when the gate passes and at least
  one `address` item has artifact-backed `act` evidence.
- `validation_handoff_allowed`: `yes` only when validation/proof tasks are
  complete enough to route without permitting mutation.
- `reply_handoff_allowed`: `yes` only when reply or proof-only thread cleanup is
  complete enough to route.

## Fail behavior

If any required field fails, emit:

```md
adjudication_complete: fail
implementation_handoff_allowed: no
Adjudication Bottom Line: Blocked: incomplete adjudication. Do not implement yet.
```

Do not route to `$accretive-implementer` from an incomplete adjudication or
without an active `mutate-code` Resolution Warrant. Do not route to
`$fixed-point-driver` as implementation from an incomplete adjudication or from
validation-only/proof-only warrants.
A complete validation-only adjudication may route validation tasks to
`$fixed-point-driver` while keeping `implementation_handoff_allowed: no`.

## All-action fail-closed rule

If every substantive comment is `act`, the gate may pass only when the output
contains a structured All-Action Justification table covering:

- stale/superseded
- unsupported
- preference-only
- out-of-scope
- misdiagnosis
- proposed-fix validity
- validation-only alternative
- shared-invariant

Each row must have `result=pass`, a non-empty evidence ref, and a specific
explanation for why action is still warranted. Generic language like "all
comments are valid" is insufficient.

## Checker integration

The checker in `tools/review_adjudication_gate.py` validates the mechanical parts
of this contract. It cannot prove semantic correctness, but it blocks incomplete,
stale-prone, or over-selected ledgers before downstream routing.
