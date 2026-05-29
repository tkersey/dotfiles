# Adversarial review output template

```md
## Review Basis

artifact_state_id:
  branch:
  base:
  head:
  diff_digest:
  review_surface_digest:
  ci_state:

## Review Surface Inventory

- artifact_state_id:
- review_surface_id:
- artifact_set:
- changed_files:
- nearby_files_checked:
- proof_surfaces_checked:
- direction_sources_checked:
- limits_or_unavailable_evidence:

## Candidate Finding Inventory

- candidate_count:
- material_finding_count:
- non_finding_count:
- validation_item_count:
- proof_only_count:
- candidate_ids:
- material_finding_ids:
- non_finding_ids:
- validation_item_ids:
- proof_only_ids:
- missing_candidate_ids:
- duplicate_candidate_ids:

## Material Findings
| id | severity | finding class | claim | agenda decision | evidence of defect | evidence of remedy | confidence | minimum acceptable fix | do not broaden into | remediation posture |
|---|---|---|---|---|---|---|---|---|---|---|

## Finding Eligibility Tests
| id | grounded | material | current | ownership | remedy-shaped | verification-path | no-finding defeated | eligible | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|---|

## Authority Packet Receipts
| role | packet status | artifact state match | scope match | candidates covered | finding added | veto added | used for | reason |
|---|---|---|---|---|---|---|---|---|

## Authority Clearance Matrix
| id | evidence | soundness | invariant/scope | hazard/footgun | complexity/remediation | verification | finding skeptic | authority status | packet refs |
|---|---|---|---|---|---|---|---|---|

## Authority Veto Ledger
| id | veto source | veto class | veto claim | evidence ref | required to clear | final route |
|---|---|---|---|---|---|---|

## Soundness Ledger
## Complexity Delta
## Invariant Ledger
## Foot-Gun Register
## Non-Finding Ledger
## Verification Gaps
## Residual Uncertainty

## Change Agenda
| id | agenda decision | change | proof or validation required | next | remediation posture |
|---|---|---|---|---|---|

## Acceptance Skew Audit
## All-Candidate Accepted Justification
## Fixed-Point Judgment
## Reviewer Gate
## Reviewer Bottom Line
```
