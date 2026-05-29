# Invariant Ace output template

```md
## Review Basis

artifact_state_id:
  branch:
  base:
  head:
  diff_digest:
  proof_state:

direction_state_id:
  source:
  source_ref:
  same_objective:

## Candidate Invariant Inventory

- candidate_count:
- accepted_count:
- validate_only_count:
- proof_only_count:
- defer_or_no_change_count:
- blocked_count:
- candidate_ids:
- accepted_ids:
- validate_only_ids:
- proof_only_ids:
- defer_or_no_change_ids:
- blocked_ids:
- missing_candidate_ids:
- duplicate_candidate_ids:

## Counterexample Ledger
## Invariant Ledger
| id | predicate | owner | scope | holds when | source of truth | acceptance status | enforcement boundary | verification signal | evidence ref | route |
|---|---|---|---|---|---|---|---|---|---|---|

## Owner and Scope Ledger
## Transition / Induction Matrix
## Enforcement Boundary Decision
## Policy / Exception Ledger
## Witness and Fixture Parity Ledger
## Verification Plan
## Authority Packet Receipts
| role | packet status | artifact state match | scope match | candidates covered | clearances added | vetoes added | used for | reason |
|---|---|---|---|---|---|---|---|---|

## Authority Clearance Matrix
| id | counterexample | owner/scope | induction | boundary | witness/parity | verification | skeptic | authority status | packet refs |
|---|---|---|---|---|---|---|---|---|---|

## Authority Veto Ledger
| id | veto source | veto class | veto claim | evidence ref | required to clear | final route |
|---|---|---|---|---|---|---|

## Accepted Invariants
## Validate Only
## Proof Only
## Defer / No Change
## Change Agenda
| id | route | change | proof or validation required | next | owner |
|---|---|---|---|---|---|

## Acceptance Skew Audit
## All-Invariant Accepted Justification
## Invariant Gate
| field | value | basis |
|---|---|---|

## Ace Bottom Line
```
