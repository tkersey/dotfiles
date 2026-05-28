# Adjudication output template v6

```md
## Review Basis

artifact_state_id:
  branch:
  base:
  head:
  diff_digest:
  comment_set_digest:
  ci_state:

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

## Comment Ledger

| id/thread | reviewer | review source | location | excerpt | claim | reviewer severity claim | accepted criticality | severity acceptance status | direction fit | direction ref | approval class | mutation value | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | severity proof ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Decision Tests
| id/thread | grounded | material | fresh | diagnosis | scope-fit | resolution value | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|

## Direction Tests
| id/thread | direction source | source freshness | same objective | direction fit | direction ref | active frontier | non-goal conflict | direction override | min evidence to change direction |
|---|---|---|---|---|---|---|---|---|---|

## Severity Tests
| id/thread | reviewer severity claim | accepted criticality | severity acceptance status | severity proof ref | downgrade/reject reason | p2+ accepted | min evidence to accept severity |
|---|---|---|---|---|---|---|---|

## Mutation Approval Tests
| id/thread | concern approved | fix approved | mutation approved | approval class | why now | why not alternative | proof after fix |
|---|---|---|---|---|---|---|---|

## No-Change Countercases
## Governing Invariant Ledger
## Act On
## Rebut
## Defer / Out of Scope
## Need Evidence

## Authority Packet Receipts
| role | packet status | artifact state match | direction state match | scope match | scoped comment ids | clearance added | veto added | used for | reason |
|---|---|---|---|---|---|---|---|---|---|

## Authority Clearance Matrix
| id/thread | evidence | direction/ownership | criticality | no-change | validation-value | fix-shape | authority status | packet refs |
|---|---|---|---|---|---|---|---|---|

## Authority Veto Ledger
| id/thread | veto source | veto class | veto claim | evidence ref | required to clear | final route |
|---|---|---|---|---|---|---|

## Resolve Selection
| id/thread | resolve decision | reason | proof ref | next | route rationale |
|---|---|---|---|---|---|

## Resolve Countercases
## Invariant-Level Handoff
## Acceptance Skew Audit
## All-Action Justification
## P2+ Severity Audit
## All-P2+ Accepted Justification
## Direction Fit Audit
## Source Pressure Audit
## All-Current-Finding Selected Justification
## Selection Skew Audit
## All-Selected Justification
## Adjudication Gate
## Handoff Agenda
## Adjudication Bottom Line
```
