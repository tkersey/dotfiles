# Adjudication Output Template v9

```md
## Review Basis

artifact_state_id:
  branch:
  base:
  head:
  diff_digest:
  claim_set_digest:
  ci_state:

## Claim Decision Kernel

| id/thread | claim | current-state truth | route | warrant id | proof ref | status |
|---|---|---|---|---|---|---|

## Resolution Warrants

| warrant id | claim id | source | selected route | permitted action | permitted scope | forbidden actions | evidence refs | countercase ref | proof required | expiry |
|---|---|---|---|---|---|---|---|---|---|---|

## Route Countercases

| id/thread | selected route | strongest alternative route | countercase status | evidence ref | route impact |
|---|---|---|---|---|---|

## Adversarial Action Matrix

| id/thread | selected route | adversarial challenge | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|

## Ablative Counterproposal Ledger

| id/thread | additive proposal | delete candidate | collapse/reuse candidate | canonical owner candidate | privatization/decommission candidate | clone classification | abstraction-ladder check | lower-surface route | why insufficient or selected | ablative clearance | proof ref |
|---|---|---|---|---|---|---|---|---|---|---|---|

## Ablative Isomorphism Cards

| id/thread | surface | proposed action | behavior preserved | public contract preserved | error/order/side effects preserved | compatibility risk | proof signal | card status |
|---|---|---|---|---|---|---|---|---|

## Surface Budget Ledger

| warrant id | mode | target net loc | max positive loc | max new public symbols | max new files | max new helpers | max new flags/knobs | max new state variants | max new branches | duplicate path budget | subtractive probes required | expansion warrant required | expansion status | proof required | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Act On
## Validate Only
## Delete / Collapse / Canonicalize
## Rebut / Do Not Address
## Need Evidence / Blocked

## Warrant / Budget Summary

| warrant id | claim id | route | permitted action | surface budget status | ablation status | implementation allowed |
|---|---|---|---|---|---|---|

## Adjudication Gate

| field | value | basis |
|---|---|---|
| claim_kernel_complete | pass/fail |  |
| artifact_state_bound | pass/fail |  |
| warrant_coverage | pass/fail |  |
| route_annexes_complete | pass/fail/not-required |  |
| surface_budget_coverage | pass/fail/not-applicable |  |
| fixed_point_handoff_complete | pass/fail/not-applicable |  |
| handoff_agenda_consistency | pass/fail |  |
| adjudication_complete | pass/fail |  |
| implementation_handoff_allowed | yes/no |  |
| validation_handoff_allowed | yes/no |  |
| reply_handoff_allowed | yes/no |  |

## Handoff Agenda

- implementation items:
- delete/collapse/canonicalize items:
- validation-only items:
- proof-only thread-resolution items:
- reply/defer/no-change items:
- blocked items:
- bounded mutation receipts required: yes/no/not-applicable
- proof:

## Adjudication Bottom Line
```
