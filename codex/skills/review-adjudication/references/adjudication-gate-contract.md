# Adjudication Gate contract

The Adjudication Gate is the automation boundary between review analysis and
implementation, validation, proof-only thread resolution, reply/defer handoff, or
blocked closure. It must be emitted for every real PR review adjudication.

Surface-Budgeted v6 adds adversarial action coverage and parallelism calibration
to the v5 contract. A selected downstream action is not licensed merely because
it appears in `Resolve Selection`; it must also have adversarial clearance and a
matching Resolution Warrant.

## Required block

```md
## Adjudication Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass/fail | branch/head/diff/comment-set identity recorded or explicitly unavailable |
| comment_inventory_coverage | pass/fail | input comments match ledger rows; no dropped or duplicate real comments |
| identity_coverage | pass/fail | every raw comment has id/thread, reviewer, location, excerpt, and claim |
| decision_test_coverage | pass/fail | every row has grounding/materiality/freshness/diagnosis/scope/resolution/no-change tests |
| no_change_coverage | pass/fail | every comment has a countercase and status |
| disposition_coverage | pass/fail | every comment has exactly one allowed disposition |
| proposed_fix_separation | pass/fail | concern validity and proposed-fix validity are separate |
| evidence_ref_coverage | pass/fail | every action has current evidence grade and concrete evidence ref |
| resolve_selection_coverage | pass/fail | every ledger row has one valid downstream resolve decision, proof ref, and route rationale |
| resolve_countercase_coverage | pass/fail | every ledger row has a resolve countercase challenging the selected downstream action |
| adversarial_action_coverage | pass/fail | every Resolve Selection row has an adversarial action row with clearance consistent with the selected decision |
| parallelism_calibration | pass/fail | rows use root-equivalent, targeted-parallel, full-fanout, swarm, or not-required according to materiality/coupling |
| resolution_warrant_coverage | pass/fail | every selected row has a matching warrant with the exact permitted action |
| surface_budget_coverage | pass/fail | every mutate-code warrant has a matching surface-budget row |
| surface_budget_consumption_safety | pass/fail | downstream diff/symbol growth is inside budget or blocked |
| warrant_consumption_safety | pass/fail | downstream changed files/resolved threads are inside active warrant scope |
| handoff_agenda_consistency | pass/fail | Handoff Agenda is a subset-preserving projection of Resolve Selection, Adversarial Action Matrix, and warrants |
| selection_skew_audit | pass/fail | resolve-selection distribution audited; all-selected outputs justified |
| invariant_pass | pass/fail | invariant clustering checked or named |
| specialist_packet_coverage | pass/fail/not-used | specialists were not used, or pass if receipts exist |
| acceptance_skew_audit | pass/fail | disposition distribution audited |
| adjudication_complete | pass/fail | all required gate fields pass |
| implementation_handoff_allowed | yes/no | yes only for artifact-backed `act` rows selected as `address` and adversarially cleared |
| validation_handoff_allowed | yes/no | yes only for validation/proof tasks |
| reply_handoff_allowed | yes/no | yes only for reply/drafting/thread-cleanup tasks |
```

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
  with defeated no-change cases, current evidence refs, and adversarial clearance.
- `validate-only` means the next workflow may create proof but must not implement
  the requested fix yet; it is legal only for `need-evidence` rows.
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

## Adversarial Action Matrix

Every `Resolve Selection` row must also receive a permission-level adversarial
challenge:

```md
## Adversarial Action Matrix

| id/thread | primary resolve decision | adversarial lanes | parallelism mode | strongest adversarial response | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|---|---|
| c1 | address | no-change,fix-shape,surface-budget | targeted-parallel | validate-first is weaker because src/a.py:10 proves duplicate write | cleared | cleared | src/a.py:10 | address retained |
```

Allowed `parallelism mode` values are `root-equivalent`, `targeted-parallel`,
`full-fanout`, `swarm`, and `not-required`.

Allowed `veto status` values are `cleared`, `preserved-no-change`, `unresolved`,
`vetoed`, `blocked`, and `not-required`.

Allowed `clearance` values are `cleared`, `preserved`, `rerouted`, `downgraded`,
and `blocked`.

Rules:

- `address` requires `veto status: cleared` and `clearance: cleared`.
- `validate-only` requires `veto status: cleared` and `clearance: cleared` or
  `downgraded`.
- `resolve-thread-only` requires `veto status: cleared` or
  `preserved-no-change`, and `clearance: preserved`.
- `do-not-address` requires `veto status: cleared` or `preserved-no-change`, and
  `clearance: preserved`.
- `blocked` requires `veto status: blocked` or `unresolved`, and
  `clearance: blocked`.
- Any row with `vetoed` or `unresolved` blocks implementation unless rerouted to a
  stricter non-mutating action with a matching warrant.

## Resolution Warrants block

Every real PR review adjudication must issue downstream permission warrants:

```md
## Resolution Warrants

| warrant id | claim id | source | claim excerpt | decision | concern validity | proposed fix validity | no-change status | resolution value | route rationale | permitted action | permitted scope | forbidden actions | evidence refs | countercase ref | proof required | expiry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rw-c1 | c1 | github-review | retry writes twice | address | valid | valid | defeated | correctness-critical | narrow-local | mutate-code | files=src/a.py,tests/test_a.py | mutate outside permitted_scope | src/a.py:10 | c1 no-change defeated | pytest tests/test_a.py::test_retry_idempotent | invalid when HEAD/base/diff/comment-set changes |
```

Allowed `permitted action` values are `mutate-code`, `add-validation-only`,
`resolve-thread`, `draft-reply`, `defer`, and `none`. A downstream skill must
consume a matching active warrant before acting.

## Handoff Agenda consistency

The Handoff Agenda must be a subset-preserving projection of Resolve Selection,
Adversarial Action Matrix, and Resolution Warrants:

- `items selected for implementation` must equal the `address` rows.
- `validation-only items` must equal the `validate-only` rows.
- `proof-only thread-resolution items` must equal the `resolve-thread-only` rows.
- `items not selected` must equal the `do-not-address` rows.
- `blocked items` must equal the `blocked` rows.

The Handoff Agenda must not use broad terms such as `all` when explicit comment
IDs are required.

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
  consistent with disposition, no-change status, proof ref, next action, and route
  rationale.
- `resolve_countercase_coverage`: every ledger row has a resolve countercase.
- `adversarial_action_coverage`: every selected action has an adversarial row, the
  primary decision matches Resolve Selection, and clearance is legal for that
  decision.
- `parallelism_calibration`: high-risk/coupled/material rows use appropriate
  parallel fanout or explain why root-equivalent is sufficient.
- `resolution_warrant_coverage`: every Resolve Selection row has a matching
  warrant with the exact permitted action.
- `surface_budget_coverage`: every mutate-code warrant has a surface budget.
- `handoff_agenda_consistency`: downstream handoff buckets match Resolve
  Selection exactly.
- `selection_skew_audit`: selection distribution is audited; all-selected outputs
  have structured justification.
- `invariant_pass`: invariant clustering was performed; shared invariants are
  named, or absence is justified.
- `specialist_packet_coverage`: `not-used` if no specialists were used; otherwise
  every accepted or rejected specialist packet has a receipt and rejected packets
  are not used as evidence.
- `acceptance_skew_audit`: disposition skew was audited; all-action outputs have
  a structured All-Action Justification table.
- `adjudication_complete`: `pass` only when all required gate fields pass.
- `implementation_handoff_allowed`: `yes` only when the gate passes and at least
  one `address` item has artifact-backed `act` evidence plus adversarial
  clearance.
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
without an active `mutate-code` Resolution Warrant and adversarial clearance. Do
not route to `$fixed-point-driver` as implementation from an incomplete
adjudication or from validation-only/proof-only warrants. A complete
validation-only adjudication may route validation tasks to `$fixed-point-driver`
while keeping `implementation_handoff_allowed: no`.

## Checker integration

The checker in `tools/review_adjudication_gate.py` validates the mechanical parts
of this contract. It cannot prove semantic correctness, but it blocks incomplete,
stale-prone, over-selected, adversarially uncleared, or over-budget ledgers before
downstream routing.
