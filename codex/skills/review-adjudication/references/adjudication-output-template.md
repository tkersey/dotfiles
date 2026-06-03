# Adjudication output template

Use this Surface-Budgeted v6 template for real PR review comment sets. It is
designed to prevent downstream selection laundering and to require adversarial
clearance for every selected action.

```md
## Review Basis

artifact_state_id:
  branch:
  base:
  head:
  diff_digest:
  comment_set_digest:
  ci_state:

- branch / PR:
- current artifact evidence:
- tests / CI:
- comments adjudicated:
- limits / unavailable evidence:

## Comment Inventory

- input_comment_count:
- ledger_row_count:
- input_comment_ids:
- ledger_comment_ids:
- missing_comment_ids:
- duplicate_comment_ids:
- synthesized_ids_for_real_comments: yes/no

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

| id/thread | reviewer | location | excerpt | claim | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  | valid/partial/unsupported/unknown | valid/partially-valid/wrong-fix/overbroad/under-specified/not-applicable/validation-only | material-relevant/relevant-nonmaterial/partially-relevant/stale-or-superseded/unsupported/out-of-scope/preference-only | act/rebut/defer/need-evidence | defeated/not-defeated/unresolved |  | current-artifact/current-test/current-ci/current-session-artifact/prior-session-artifact/memory-only/reviewer-only/none |  | none/route-to-accretive-implementer/route-to-fixed-point-driver/route-to-logophile/ask-user/draft-reply |

## Decision Tests

| id/thread | grounded | material | fresh | diagnosis | scope-fit | resolution value | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|
|  | yes/no/unknown | yes/no/user-requested/unknown | current/stale/superseded/unclear | correct/partially-correct/misdiagnosed/unknown | yes/no/partial/unknown | merge-blocking/correctness-critical/review-closure/proof-only/validation-needed/low-value/out-of-lane/blocked | yes/no/unresolved |  |

## No-Change Countercases

- `<id/thread>`:
  - strongest no-change case:
  - status:
  - why defeated / preserved / unresolved:

## Governing Invariant Ledger

| invariant id | invariant | comments | evidence | violated/threatened | minimum fix shape | handoff | why not local fixes |
|---|---|---|---|---|---|---|---|

## Specialist Packet Receipts

Omit this section only when no specialists were used.

| role | packet status | artifact state match | scope match | finding added | route changed | used for | reason |
|---|---|---|---|---|---|---|---|

## Act On

- `<id/thread>`: action, evidence grade/ref, replacement fix shape if reviewer fix is not valid, adversarial clearance, and handoff shape.

## Rebut

- `<id/thread>`: rebuttal basis, evidence, and reply stance.

## Defer / Out of Scope

- `<id/thread>`: scope boundary and future owner.

## Need Evidence

- `<id/thread>`: missing evidence and validation-only handoff, if any.

## Resolve Selection

| id/thread | resolve decision | reason | proof ref | next | route rationale |
|---|---|---|---|---|---|
|  | address/validate-only/resolve-thread-only/do-not-address/blocked |  |  | route-to-fixed-point-driver / validation probe / proof reply or thread resolution / none / blocked | narrow-local/coupled-comments/invariant-level/structural/validation-only/contentious/likely-to-reopen/proof-only-thread/no-change/blocked |

## Resolve Countercases

- `<id/thread>`:
  - proposed resolve decision:
  - strongest alternative resolve decision:
  - why alternative is rejected / preserved / unresolved:

## Adversarial Action Matrix

| id/thread | primary resolve decision | adversarial lanes | parallelism mode | strongest adversarial response | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|---|---|
|  | address/validate-only/resolve-thread-only/do-not-address/blocked | no-change,validation-value,fix-shape,scope,surface-budget | root-equivalent/targeted-parallel/full-fanout/swarm/not-required |  | cleared/preserved-no-change/unresolved/vetoed/blocked/not-required | cleared/preserved/rerouted/downgraded/blocked |  |  |

## Resolution Warrants

| warrant id | claim id | source | claim excerpt | decision | concern validity | proposed fix validity | no-change status | resolution value | route rationale | permitted action | permitted scope | forbidden actions | evidence refs | countercase ref | proof required | expiry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  | github-review/cas/human-review/specialist/root-equivalent |  | address/validate-only/resolve-thread-only/do-not-address/blocked | valid/partial/unsupported/unknown | valid/partially-valid/wrong-fix/overbroad/under-specified/not-applicable/validation-only | defeated/not-defeated/unresolved | merge-blocking/correctness-critical/review-closure/proof-only/validation-needed/low-value/out-of-lane/blocked | narrow-local/coupled-comments/invariant-level/structural/validation-only/contentious/likely-to-reopen/proof-only-thread/no-change/blocked | mutate-code/add-validation-only/resolve-thread/draft-reply/defer/none | files/symbols/threads allowed | actions forbidden outside scope | concrete refs | no-change / resolve / adversarial countercase ref | commands/proofs required | invalid when HEAD/base/diff/comment/thread state changes |

## Surface Budget Ledger

| warrant id | mode | target net loc | max positive loc | max new public symbols | max new files | max new helpers | max new flags/knobs | max new state variants | max new branches | duplicate path budget | subtractive probes required | expansion warrant required | expansion status | proof required | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Invariant-Level Handoff

- invariant:
- affected comments:
- route:
- minimum fix shape:
- proof required:
- adversarial clearance:

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

| check | result | evidence ref | why action still warranted |
|---|---|---|---|
| stale/superseded | pass/fail |  |  |
| unsupported | pass/fail |  |  |
| preference-only | pass/fail |  |  |
| out-of-scope | pass/fail |  |  |
| misdiagnosis | pass/fail |  |  |
| proposed-fix validity | pass/fail |  |  |
| validation-only alternative | pass/fail |  |  |
| shared-invariant | pass/fail |  |  |

## Selection Skew Audit

- resolve decision distribution:
- all-selected pressure checked:
- address over-selection possibilities:
- validate-only over-routing possibilities:
- proof-only thread-resolution alternatives:
- do-not-address alternatives:
- blocked/ask-user alternatives:
- fixed-point over-routing pressure:
- adversarial parallelism pressure:

## All-Selected Justification

Include this section only when every substantive comment is selected as `address` or `validate-only`.

| check | result | evidence ref | why selected resolution is still warranted |
|---|---|---|---|
| stale/already-fixed alternative | pass/fail |  |  |
| proof-only thread-resolution alternative | pass/fail |  |  |
| do-not-address alternative | pass/fail |  |  |
| validate-before-mutation alternative | pass/fail |  |  |
| out-of-scope/defer alternative | pass/fail |  |  |
| fixed-point over-routing check | pass/fail |  |  |

## Adjudication Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass/fail |  |
| comment_inventory_coverage | pass/fail |  |
| identity_coverage | pass/fail |  |
| decision_test_coverage | pass/fail |  |
| no_change_coverage | pass/fail |  |
| disposition_coverage | pass/fail |  |
| proposed_fix_separation | pass/fail |  |
| evidence_ref_coverage | pass/fail |  |
| resolve_selection_coverage | pass/fail |  |
| resolve_countercase_coverage | pass/fail |  |
| adversarial_action_coverage | pass/fail |  |
| parallelism_calibration | pass/fail |  |
| resolution_warrant_coverage | pass/fail |  |
| surface_budget_coverage | pass/fail |  |
| surface_budget_consumption_safety | pass/fail |  |
| warrant_consumption_safety | pass/fail |  |
| handoff_agenda_consistency | pass/fail |  |
| selection_skew_audit | pass/fail |  |
| invariant_pass | pass/fail |  |
| specialist_packet_coverage | pass/fail/not-used |  |
| acceptance_skew_audit | pass/fail |  |
| adjudication_complete | pass/fail |  |
| implementation_handoff_allowed | yes/no |  |
| validation_handoff_allowed | yes/no |  |
| reply_handoff_allowed | yes/no |  |

## Handoff Agenda

- implementation route:
- validation route:
- proof-only thread-resolution route:
- reply route:
- items selected for implementation: # must match address rows and mutate-code warrants
- validation-only items: # must match validate-only rows and add-validation-only warrants
- proof-only thread-resolution items: # must match resolve-thread-only rows and resolve-thread warrants
- items not selected:
- proof:
- surface budget preflight required:
- surface delta receipt required:
- expansion-warrant triggers:
- blocked items:

## Adjudication Bottom Line
```
