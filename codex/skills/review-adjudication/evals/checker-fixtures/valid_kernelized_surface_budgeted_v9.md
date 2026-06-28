## Review Basis

artifact_state_id:
  branch: feature/review
  base: main@abc123
  head: feature@def456
  diff_digest: paths=src/a.py,tests/test_a.py
  claim_set_digest: c1,c2,c3,c4
  ci_state: local tests pass

## Claim Decision Kernel

| id/thread | claim | current-state truth | route | warrant id | proof ref | status |
|---|---|---|---|---|---|---|
| c1 | retry duplicates writes | src/a.py currently lacks idempotence guard | address | rw-c1 | src/a.py:10 | licensed |
| c2 | flake may exist | not proven on current artifacts | validate-only | rw-c2 | thread:c2 | validation-needed |
| c3 | helper rename | no convention supports rename | do-not-address | rw-c3 | src/a.py:1 | no-change |
| c4 | duplicate wrapper path | same contract can be canonicalized | delete-collapse-canonicalize | rw-c4 | src/a.py:20 | delete-collapse-canonicalize |

## Resolution Warrants

| warrant id | claim id | source | selected route | permitted action | permitted scope | forbidden actions | evidence refs | countercase ref | proof required | expiry |
|---|---|---|---|---|---|---|---|---|---|---|
| rw-c1 | c1 | github-review | address | mutate-code | src/a.py, tests/test_a.py | forbid mutate outside permitted scope | src/a.py:10 | no-change defeated at src/a.py:10 | pytest tests/test_a.py::test_retry_idempotent | expires when head/base/diff/comment changes |
| rw-c2 | c2 | github-review | validate-only | add-validation-only | tests/test_a.py | forbid production mutation | thread:c2 | flake unproven | add validation probe only | expires when head/base/diff/comment changes |
| rw-c3 | c3 | github-review | do-not-address | none | none | no mutation | src/a.py:1 | preference-only preserved | none | expires when head/base/diff/comment changes |
| rw-c4 | c4 | github-review | delete-collapse-canonicalize | mutate-code | src/a.py, tests/test_a.py | forbid mutate outside permitted scope | src/a.py:20 | duplicate wrapper dominated | pytest tests/test_a.py::test_retry_idempotent | expires when head/base/diff/comment changes |

## Route Countercases

| id/thread | selected route | strongest alternative route | countercase status | evidence ref | route impact |
|---|---|---|---|---|---|
| c1 | address | validate-only | defeated | src/a.py:10 | mutate allowed under budget |
| c2 | validate-only | address | preserved-validate-first | thread:c2 | validation only |
| c3 | do-not-address | address | preserved-no-change | src/a.py:1 | no implementation |
| c4 | delete-collapse-canonicalize | additive-helper | preserved-ablative | src/a.py:20 | canonicalize not add |

## Adversarial Action Matrix

| id/thread | selected route | adversarial challenge | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|
| c1 | address | validation-first could be enough | cleared | cleared | src/a.py:10 | address preserved |
| c4 | delete-collapse-canonicalize | deletion could lose behavior | cleared | cleared | tests/test_a.py::test_retry_idempotent | canonicalize preserved |

## Ablative Counterproposal Ledger

| id/thread | additive proposal | delete candidate | collapse/reuse candidate | canonical owner candidate | privatization/decommission candidate | clone classification | abstraction-ladder check | lower-surface route | why insufficient or selected | ablative clearance | proof ref |
|---|---|---|---|---|---|---|---|---|---|---|---|
| c1 | add guard | none | reuse retry state | retry state | none | not-applicable | not-needed | none | lower-surface not enough for missing guard | clear-additive | src/a.py:10 |
| c4 | add helper | wrapper path | canonical retry state | retry state | wrapper private | exact-clone | not-needed | canonicalize | canonical owner selected | select-ablative-route | src/a.py:20 |

## Ablative Isomorphism Cards

| id/thread | surface | proposed action | behavior preserved | public contract preserved | error/order/side effects preserved | compatibility risk | proof signal | card status |
|---|---|---|---|---|---|---|---|---|
| c4 | duplicate wrapper | canonicalize | yes | yes | yes | low | tests/test_a.py::test_retry_idempotent | pass |

## Surface Budget Ledger

| warrant id | mode | target net loc | max positive loc | max new public symbols | max new files | max new helpers | max new flags/knobs | max new state variants | max new branches | duplicate path budget | subtractive probes required | expansion warrant required | expansion status | proof required | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rw-c1 | ablative-first | small-positive | 20 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | yes | yes | not-needed | pytest tests/test_a.py::test_retry_idempotent | narrow guard only |
| rw-c4 | ablative-first | negative | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | yes | yes | not-needed | pytest tests/test_a.py::test_retry_idempotent | canonicalize wrapper |

## Act On

- c1: mutate within rw-c1 scope only.

## Validate Only

- c2: add validation probe only.

## Delete / Collapse / Canonicalize

- c4: canonicalize duplicate wrapper.

## Rebut / Do Not Address

- c3: no-change.

## Need Evidence / Blocked

- none.

## Warrant / Budget Summary

| warrant id | claim id | route | permitted action | surface budget status | ablation status | implementation allowed |
|---|---|---|---|---|---|---|
| rw-c1 | c1 | address | mutate-code | within-budget | clear-additive | yes |
| rw-c4 | c4 | delete-collapse-canonicalize | mutate-code | within-budget | select-ablative-route | yes |

## Adjudication Gate

| field | value | basis |
|---|---|---|
| claim_kernel_complete | pass | four raw claims represented |
| artifact_state_bound | pass | artifact_state_id recorded |
| warrant_coverage | pass | every kernel row has matching warrant |
| route_annexes_complete | pass | mutation/delete annexes present |
| surface_budget_coverage | pass | mutation warrants budgeted |
| fixed_point_handoff_complete | pass | handoff requests surface handshake |
| handoff_agenda_consistency | pass | agenda ids match routes |
| adjudication_complete | pass | all required fields pass |
| implementation_handoff_allowed | yes | c1 and c4 have mutate-code warrants |
| validation_handoff_allowed | yes | c2 has add-validation-only warrant |
| reply_handoff_allowed | yes | c3 has no-change/reply route |

## Handoff Agenda

- implementation items: c1
- delete/collapse/canonicalize items: c4
- validation-only items: c2
- proof-only thread-resolution items: none
- reply/defer/no-change items: c3
- blocked items: none
- bounded mutation receipts required: yes
- proof: pytest tests/test_a.py::test_retry_idempotent

## Adjudication Bottom Line

Proceed: c1 and c4 may route to implementation under scoped surface budgets; c2 is validation-only; c3 is no-change.
