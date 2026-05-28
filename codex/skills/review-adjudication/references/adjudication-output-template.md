# Adjudication output template

Use this template for real PR review comment sets. This is the Compact-Gated v4
shape. It is designed to prevent downstream selection laundering, severity-label
laundering, and direction-conflicting mutations.

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

| id/thread | reviewer | location | excerpt | claim | reviewer severity claim | accepted criticality | severity acceptance status | direction fit | direction ref | mutation value | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | severity proof ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  | P0/P1/P2/P3/P4/unlabeled/unknown | blocker/security-critical/safety-critical/data-loss-critical/correctness-critical/compatibility-critical/direction-critical/review-closure-only/low-value/out-of-lane/unknown | accepted/downgraded/rejected/unresolved | aligned/direction-overriding/neutral/conflicting/unknown |  | codebase-material/validation-material/proof-only/reply-only/no-change/blocked | valid/partial/unsupported/unknown | valid/partially-valid/wrong-fix/overbroad/under-specified/not-applicable/validation-only | material-relevant/relevant-nonmaterial/partially-relevant/stale-or-superseded/unsupported/out-of-scope/preference-only/direction-conflicting/review-closure-only | act/rebut/defer/need-evidence/blocked | defeated/not-defeated/unresolved |  | current-artifact/current-test/current-ci/current-session-artifact/prior-session-artifact/memory-only/reviewer-only/none |  |  | none/route-to-accretive-implementer/route-to-fixed-point-driver/route-to-logophile/ask-user/draft-reply |

## Decision Tests

| id/thread | grounded | material | fresh | diagnosis | scope-fit | resolution value | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|
|  | yes/no/unknown | yes/no/user-requested/unknown | current/stale/superseded/unclear | correct/partially-correct/misdiagnosed/unknown | yes/no/partial/unknown | merge-blocking/correctness-critical/direction-critical/review-closure/proof-only/validation-needed/low-value/out-of-lane/blocked | yes/no/unresolved |  |

## Direction Tests

| id/thread | direction source | source freshness | same objective | direction fit | direction ref | active frontier | non-goal conflict | direction override | min evidence to change direction |
|---|---|---|---|---|---|---|---|---|---|
|  | user-current-instruction/proposed-plan/st-plan/update-plan/PR-body/issue/design-doc/repo-convention/seq-recovered/current-artifact/unknown | current/stale/off-target/unknown | yes/no/unknown | aligned/direction-overriding/neutral/conflicting/unknown |  |  | yes/no/unknown | yes/no/not-needed |  |

## Severity Tests

| id/thread | reviewer severity claim | accepted criticality | severity acceptance status | severity proof ref | downgrade/reject reason | p2+ accepted | min evidence to accept severity |
|---|---|---|---|---|---|---|---|
|  | P0/P1/P2/P3/P4/unlabeled/unknown | blocker/security-critical/safety-critical/data-loss-critical/correctness-critical/compatibility-critical/direction-critical/review-closure-only/low-value/out-of-lane/unknown | accepted/downgraded/rejected/unresolved |  |  | yes/no/not-p2plus |  |

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

| role | packet status | artifact state match | direction state match | scope match | finding added | route changed | used for | reason |
|---|---|---|---|---|---|---|---|---|

## Act On

- `<id/thread>`: action, evidence grade/ref, direction ref, accepted criticality,
  severity proof ref if P2+, replacement fix shape if reviewer fix is not valid,
  and handoff shape.

## Rebut

- `<id/thread>`: rebuttal basis, evidence, severity downgrade/rejection if any,
  direction basis, and reply stance.

## Defer / Out of Scope

- `<id/thread>`: scope or direction boundary and future owner.

## Need Evidence

- `<id/thread>`: missing evidence and validation-only handoff, if any; state why
  validation would change a material decision.

## Resolve Selection

| id/thread | resolve decision | reason | proof ref | next | route rationale |
|---|---|---|---|---|---|
|  | address/validate-only/resolve-thread-only/do-not-address/blocked |  |  | route-to-fixed-point-driver / validation probe / proof reply or thread resolution / none / blocked | narrow-local/coupled-comments/invariant-level/structural/validation-only/contentious/likely-to-reopen/proof-only-thread/no-change/blocked |

## Resolve Countercases

- `<id/thread>`:
  - proposed resolve decision:
  - strongest alternative resolve decision:
  - why alternative is rejected / preserved / unresolved:

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
- direction-conflicting possibilities:
- review-closure-only possibilities:
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
| direction-conflicting | pass/fail |  |  |
| review-closure-only | pass/fail |  |  |
| misdiagnosis | pass/fail |  |  |
| proposed-fix validity | pass/fail |  |  |
| validation-only alternative | pass/fail |  |  |
| shared-invariant | pass/fail |  |  |

## P2+ Severity Audit

- p2_plus_count:
- accepted_count:
- downgraded_count:
- rejected_count:
- unresolved_count:
- accepted criticality distribution:
- unsupported severity labels:
- review-closure-only downgrades:
- validation-only P2+ rows:
- direction-conflicting P2+ rows:

## All-P2+ Accepted Justification

Include this section only when every P2+ row has `severity_acceptance_status: accepted`.

| check | result | evidence ref | why accepted severity still warranted |
|---|---|---|---|
| independent artifact proof | pass/fail |  |  |
| implementation-grade criticality | pass/fail |  |  |
| direction alignment | pass/fail |  |  |
| review-closure-only rejection | pass/fail |  |  |
| downgrade alternative | pass/fail |  |  |
| validation alternative | pass/fail |  |  |

## Direction Fit Audit

- direction source distribution:
- same-objective proof:
- stale/off-target plan pressure:
- conflicting-direction rows:
- direction-overriding rows:
- rows where `$st`/plan/update-plan changed disposition:
- rows where direction was insufficient and blocked/need-evidence was chosen:

## Selection Skew Audit

- resolve decision distribution:
- all-selected pressure checked:
- address over-selection possibilities:
- validate-only over-routing possibilities:
- proof-only thread-resolution alternatives:
- do-not-address alternatives:
- blocked/ask-user alternatives:
- direction-conflict alternatives:
- review-closure-only alternatives:
- fixed-point over-routing pressure:

## All-Selected Justification

Include this section only when every substantive comment is selected as
`address` or `validate-only`.

| check | result | evidence ref | why selected resolution is still warranted |
|---|---|---|---|
| stale/already-fixed alternative | pass/fail |  |  |
| proof-only thread-resolution alternative | pass/fail |  |  |
| do-not-address alternative | pass/fail |  |  |
| validate-before-mutation alternative | pass/fail |  |  |
| out-of-scope/defer alternative | pass/fail |  |  |
| direction-conflict alternative | pass/fail |  |  |
| review-closure-only alternative | pass/fail |  |  |
| fixed-point over-routing check | pass/fail |  |  |

## Adjudication Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass/fail |  |
| direction_context_coverage | pass/fail |  |
| comment_inventory_coverage | pass/fail |  |
| identity_coverage | pass/fail |  |
| decision_test_coverage | pass/fail |  |
| direction_fit_coverage | pass/fail |  |
| severity_claim_coverage | pass/fail |  |
| p2_plus_acceptance_coverage | pass/fail |  |
| no_change_coverage | pass/fail |  |
| disposition_coverage | pass/fail |  |
| proposed_fix_separation | pass/fail |  |
| evidence_ref_coverage | pass/fail |  |
| validation_value_coverage | pass/fail |  |
| resolve_selection_coverage | pass/fail |  |
| resolve_countercase_coverage | pass/fail |  |
| handoff_agenda_consistency | pass/fail |  |
| selection_skew_audit | pass/fail |  |
| p2_plus_severity_audit | pass/fail |  |
| direction_fit_audit | pass/fail |  |
| invariant_pass | pass/fail |  |
| invariant_ace_coverage | pass/fail/not-required |  |
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
