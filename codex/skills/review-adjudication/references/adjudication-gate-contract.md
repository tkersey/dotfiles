# Adjudication Gate contract

The Adjudication Gate is the automation boundary between review analysis and
implementation, validation, or reply handoff. It must be emitted for every real
PR review adjudication.

## Required block

```md
## Adjudication Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass | branch/head/diff/comment-set identity recorded or explicitly unavailable |
| comment_inventory_coverage | pass | input comments match ledger rows; no dropped or duplicate real comments |
| identity_coverage | pass | every raw comment has id/thread, reviewer, location, excerpt, and claim |
| decision_test_coverage | pass | every row has grounding/materiality/freshness/diagnosis/scope/no-change tests |
| no_change_coverage | pass | every comment has a countercase and status |
| disposition_coverage | pass | every comment has exactly one allowed disposition |
| proposed_fix_separation | pass | concern validity and proposed-fix validity are separate |
| evidence_ref_coverage | pass | every action has current evidence grade and concrete evidence ref |
| resolve_selection_coverage | pass | every ledger row has one valid downstream resolve decision |
| invariant_pass | pass | invariant clustering checked or named |
| specialist_packet_coverage | not-used | specialists were not used, or pass if receipts exist |
| acceptance_skew_audit | pass | disposition distribution audited |
| adjudication_complete | pass | all required gate fields pass |
| implementation_handoff_allowed | yes/no | yes only for artifact-backed `act` rows |
| validation_handoff_allowed | yes/no | yes only for validation/proof tasks |
| reply_handoff_allowed | yes/no | yes only for reply/drafting tasks |
```


## Resolve Selection block

Every real PR review adjudication must include a downstream selection map:

```md
## Resolve Selection

| id/thread | resolve decision | reason | next |
|---|---|---|---|
| c1 | address | act row with defeated no-change case and current evidence | route-to-fixed-point-driver |
| c2 | validate-only | failure mode is plausible but unproven | validation probe only |
| c3 | resolve-thread-only | already fixed on latest HEAD | reply with proof and resolve thread |
| c4 | do-not-address | preference-only no-change case preserved | none |
| c5 | blocked | missing artifact state or identity | blocked |
```

Allowed `resolve decision` values are `address`, `validate-only`,
`resolve-thread-only`, `do-not-address`, and `blocked`.

Rules:

- `address` means implementation is selected and is legal only for `act` rows
  with defeated no-change cases.
- `validate-only` means the next workflow may create proof but must not
  implement the requested fix yet; it is legal only for `need-evidence` rows.
- `resolve-thread-only` means the review thread can be answered or resolved with
  current proof without changing code.
- `do-not-address` means no implementation handoff; the reason must preserve the
  no-change case.
- `blocked` means selection evidence is incomplete and must force
  `adjudication_complete: fail` with all handoff permissions set to `no`.

## Pass conditions

- `artifact_state_coverage`: branch/head/diff/comment-set identity was recorded,
  or unavailable fields were explicitly named.
- `comment_inventory_coverage`: every input comment appears exactly once in the
  ledger, with no missing or duplicate raw IDs.
- `identity_coverage`: every real review comment has stable raw identity.
- `decision_test_coverage`: every comment has required Decision Tests fields.
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
  consistent with disposition and no-change status.
- `invariant_pass`: invariant clustering was performed; shared invariants are
  named, or absence is justified.
- `specialist_packet_coverage`: `not-used` if no specialists were used; otherwise
  every accepted or rejected specialist packet has a receipt and rejected packets
  are not used as evidence.
- `acceptance_skew_audit`: disposition skew was audited; all-action outputs have
  a structured All-Action Justification table.
- `adjudication_complete`: `pass` only when all required gate fields pass.
- `implementation_handoff_allowed`: `yes` only when the gate passes and at least
  one `act` item has current evidence.
- `validation_handoff_allowed`: `yes` only when validation/proof tasks are
  complete enough to route without permitting mutation.
- `reply_handoff_allowed`: `yes` only when reply drafting is complete enough to
  route.

## Fail behavior

If any required field fails, emit:

```md
adjudication_complete: fail
implementation_handoff_allowed: no
Adjudication Bottom Line: Blocked: incomplete adjudication. Do not implement yet.
```

Do not route to `$accretive-implementer` from an incomplete adjudication. Do not
route to `$fixed-point-driver` as implementation from an incomplete adjudication.
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
of this contract. It cannot prove semantic correctness, but it blocks incomplete
or stale-prone ledgers before implementation routing.
