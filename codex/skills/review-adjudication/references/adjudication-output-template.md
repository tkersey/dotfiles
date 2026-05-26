# Adjudication output template

Use this template for real PR review comment sets.

```md
## Review Basis

- branch / PR:
- current artifact evidence:
- tests / CI:
- comments adjudicated:
- limits / unavailable evidence:

## PR Why Ledger

- intended_change:
- explicit_constraints:
- non_goals:
- governing_invariants:
- evidence_source:
- rationale_freshness:
- staleness_source:
- confidence:

## Comment Ledger

| id/thread | reviewer | location | claim | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  | valid/partial/unsupported/unknown | valid/partially-valid/wrong-fix/overbroad/under-specified/not-applicable/validation-only | material-relevant/relevant-nonmaterial/partially-relevant/stale-or-superseded/unsupported/out-of-scope/preference-only | act/rebut/defer/need-evidence | defeated/not-defeated/unresolved |  |  | none/route-to-accretive-implementer/route-to-fixed-point-driver/route-to-logophile/ask-user/draft-reply |

## No-Change Countercases

- `<id/thread>`:
  - strongest no-change case:
  - status:
  - why defeated / preserved / unresolved:

## Governing Invariant Ledger

| invariant id | invariant | comments | evidence | violated/threatened | minimum fix shape | handoff | why not local fixes |
|---|---|---|---|---|---|---|---|

## Act On

- `<id/thread>`: action, evidence, and handoff shape.

## Rebut

- `<id/thread>`: rebuttal basis, evidence, and reply stance.

## Defer / Out of Scope

- `<id/thread>`: scope boundary and future owner.

## Need Evidence

- `<id/thread>`: missing evidence and validation-only handoff, if any.

## Resolve Selection

| id/thread | resolve decision | reason | next |
|---|---|---|---|
|  | address/validate-only/resolve-thread-only/do-not-address/blocked |  | route-to-fixed-point-driver / validation probe / proof reply or thread resolution / none / blocked |

## Invariant-Level Handoff

- invariant:
- affected comments:
- route:
- minimum fix shape:
- proof required:

## Acceptance Skew Audit

- disposition distribution:
- acceptance pressure checked:
- stale/superseded possibilities:
- unsupported possibilities:
- preference-only possibilities:
- out-of-scope possibilities:
- validation-only alternatives:
- shared-invariant pressure:

## All-Action Justification

Include this section only when every substantive comment is `act`.

- stale/superseded check:
- unsupported check:
- preference-only check:
- out-of-scope check:
- misdiagnosis check:
- proposed-fix validity check:
- validation-only alternative:
- shared-invariant check:

## Adjudication Gate

| field | value | basis |
|---|---|---|
| identity_coverage | pass/fail |  |
| no_change_coverage | pass/fail |  |
| disposition_coverage | pass/fail |  |
| proposed_fix_separation | pass/fail |  |
| evidence_coverage | pass/fail |  |
| invariant_pass | pass/fail |  |
| acceptance_skew_audit | pass/fail |  |
| handoff_allowed | yes/no |  |

## Handoff Agenda

- route:
- items selected for implementation:
- validation-only items:
- proof-only thread-resolution items:
- items not selected:
- proof:
- blocked items:

## Adjudication Bottom Line

- `Proceed: ...`
- or `Blocked: incomplete adjudication. Do not implement yet.`
```
