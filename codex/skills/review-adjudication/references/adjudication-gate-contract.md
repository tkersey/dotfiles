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
| direction_context_coverage | pass | direction_state_id recorded and same-objective/freshness evaluated |
| comment_inventory_coverage | pass | input comments match ledger rows; no dropped or duplicate real comments |
| identity_coverage | pass | every raw comment has id/thread, reviewer, location, excerpt, and claim |
| decision_test_coverage | pass | every row has grounding/materiality/freshness/diagnosis/scope/resolution/no-change tests |
| direction_fit_coverage | pass | every row has direction fit, direction ref, source freshness, and same-objective test |
| severity_claim_coverage | pass | every row splits reviewer severity claim from accepted criticality |
| p2_plus_acceptance_coverage | pass | every P2+ row has accepted/downgraded/rejected/unresolved status and proof/reason |
| no_change_coverage | pass | every comment has a countercase and status |
| disposition_coverage | pass | every comment has exactly one allowed disposition |
| proposed_fix_separation | pass | concern validity and proposed-fix validity are separate |
| evidence_ref_coverage | pass | every action has current evidence grade and concrete evidence ref |
| validation_value_coverage | pass | every validate-only route has validation-material mutation value |
| resolve_selection_coverage | pass | every ledger row has one valid downstream resolve decision, proof ref, and route rationale |
| resolve_countercase_coverage | pass | every ledger row has a resolve countercase challenging the selected downstream action |
| handoff_agenda_consistency | pass | Handoff Agenda is a subset-preserving projection of Resolve Selection |
| selection_skew_audit | pass | resolve-selection distribution audited; all-selected outputs justified |
| p2_plus_severity_audit | pass | P2+ severity distribution audited; all-accepted outputs justified |
| direction_fit_audit | pass | direction-fit distribution audited |
| invariant_pass | pass | invariant clustering checked or named |
| invariant_ace_coverage | pass/not-required | `$invariant-ace` checked accepted current invariant-framed findings, or no such findings exist |
| specialist_packet_coverage | not-used | specialists were not used, or pass if receipts exist |
| acceptance_skew_audit | pass | disposition distribution audited |
| adjudication_complete | pass | all required gate fields pass |
| implementation_handoff_allowed | yes/no | yes only for artifact-backed, direction-aligned `act` rows selected as `address` |
| validation_handoff_allowed | yes/no | yes only for validation/proof tasks |
| reply_handoff_allowed | yes/no | yes only for reply/drafting/thread-cleanup tasks |
```

## Direction Context block

Every real PR review adjudication must include a direction state:

```md
## Direction Context Ledger

direction_state_id:
  source:
  source_ref:
  source_freshness:
  same_objective:
  active_frontier:
  locked_decisions:
  non_goals:
  compatibility_posture:
  ownership_boundaries:
  direction_confidence:
```

`$st` is canonical only when current and same-objective. Built-in update plans are
projection evidence and must not override `$st`, explicit user instruction, or
current artifacts.

## Resolve Selection block

Every real PR review adjudication must include a downstream selection map:

```md
## Resolve Selection

| id/thread | resolve decision | reason | proof ref | next | route rationale |
|---|---|---|---|---|---|
| c1 | address | act row with defeated no-change case, accepted criticality, and direction fit | src/a.py:10 | route-to-accretive-implementer | narrow-local |
| c2 | validate-only | failure mode is plausible, route-changing, and unproven | thread:c2 | validation probe only | validation-only |
| c3 | resolve-thread-only | already fixed on latest HEAD | tests/retry.test.ts::case | reply with proof and resolve thread | proof-only-thread |
| c4 | do-not-address | preference-only no-change case preserved | src/a.py:1 | none | no-change |
| c5 | blocked | missing artifact state, direction state, severity proof, or identity | missing | blocked | blocked |
```

Allowed `resolve decision` values are `address`, `validate-only`,
`resolve-thread-only`, `do-not-address`, and `blocked`.

Allowed `route rationale` values are `narrow-local`, `coupled-comments`,
`invariant-level`, `structural`, `validation-only`, `contentious`,
`likely-to-reopen`, `proof-only-thread`, `no-change`, and `blocked`.

Rules:

- `address` means implementation is selected and is legal only for `act` rows
  with defeated no-change cases, current evidence refs, direction fit, and
  implementation-grade accepted criticality.
- `validate-only` means the next workflow may create proof but must not
  implement the requested fix yet; it is legal only for `need-evidence` rows with
  `mutation_value: validation-material`.
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
- direction-conflict alternative
- review-closure-only alternative
- fixed-point over-routing check

Each row must have `result=pass`, a concrete evidence ref, and a specific
explanation for why selected resolution is still warranted. Generic language like
"all are worth resolving" is insufficient.

## P2+ skew rule

If every P2+ row is accepted, the gate may pass only when the output contains a
structured All-P2+ Accepted Justification table covering:

- independent artifact proof
- implementation-grade criticality
- direction alignment
- review-closure-only rejection
- downgrade alternative
- validation alternative

Each row must have `result=pass`, a concrete evidence ref, and a specific
explanation for why accepted severity is still warranted.

## Pass conditions

- `artifact_state_coverage`: branch/head/diff/comment-set identity was recorded,
  or unavailable fields were explicitly named.
- `direction_context_coverage`: direction state was recorded, including source,
  source ref, freshness, and same-objective status.
- `comment_inventory_coverage`: every input comment appears exactly once in the
  ledger, with no missing or duplicate raw IDs.
- `identity_coverage`: every real review comment has stable raw identity.
- `decision_test_coverage`: every comment has required Decision Tests fields,
  including `resolution value`.
- `direction_fit_coverage`: every comment has Direction Tests plus direction fit
  and direction ref in the ledger.
- `severity_claim_coverage`: every comment has reviewer severity claim, accepted
  criticality, and severity acceptance status.
- `p2_plus_acceptance_coverage`: every P2+ row has accepted/downgraded/rejected/
  unresolved status, proof if accepted, and reason if not accepted.
- `no_change_coverage`: every comment has a strongest no-change countercase and
  one allowed status.
- `disposition_coverage`: every comment has exactly one disposition from the
  allowed set.
- `proposed_fix_separation`: every comment separates concern validity from
  proposed-fix validity.
- `evidence_ref_coverage`: every `act` row has current evidence grade and a
  concrete evidence reference.
- `validation_value_coverage`: every `validate-only` row has
  `mutation_value: validation-material`.
- `resolve_selection_coverage`: every ledger row has exactly one Resolve
  Selection row, no unknown selection IDs exist, and selection decisions are
  consistent with disposition, direction, severity, proof ref, next action, and
  route rationale.
- `resolve_countercase_coverage`: every ledger row has a resolve countercase.
- `handoff_agenda_consistency`: downstream handoff buckets match Resolve
  Selection exactly.
- `selection_skew_audit`: selection distribution is audited; all-selected
  outputs have structured justification.
- `p2_plus_severity_audit`: P2+ severity distribution is audited; all-accepted
  P2+ outputs have structured justification.
- `direction_fit_audit`: direction fit distribution is audited.
- `invariant_pass`: invariant clustering was performed; shared invariants are
  named, or absence is justified.
- `invariant_ace_coverage`: `pass` when any accepted current invariant-framed
  finding selected for `address` has `$invariant-ace` coverage; `not-required`
  only when no accepted current invariant-framed finding is selected.
- `specialist_packet_coverage`: `not-used` if no specialists were used; otherwise
  every accepted or rejected specialist packet has a receipt and rejected packets
  are not used as evidence.
- `acceptance_skew_audit`: disposition skew was audited; all-action outputs have
  a structured All-Action Justification table.
- `adjudication_complete`: `pass` only when all required gate fields pass.
- `implementation_handoff_allowed`: `yes` only when the gate passes and at least
  one `address` item has artifact-backed, direction-aligned `act` evidence.
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

Do not route to `$accretive-implementer` from an incomplete adjudication. Do not
route to `$fixed-point-driver` as implementation from an incomplete adjudication.
A complete validation-only adjudication may route validation tasks to
`$fixed-point-driver` while keeping `implementation_handoff_allowed: no`.

## Checker integration

The checker in `tools/review_adjudication_gate.py` validates the mechanical parts
of this contract. It cannot prove semantic correctness, but it blocks incomplete,
stale-prone, direction-conflicting, severity-laundered, or over-selected ledgers
before downstream routing.
