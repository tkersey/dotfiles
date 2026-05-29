# Adversarial Review Gate contract

The Reviewer Gate is the automation boundary between adversarial review and downstream validation or remediation.

Required fields:

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass/fail | artifact state recorded |
| review_surface_coverage | pass/fail | reviewed artifacts and limits recorded |
| candidate_inventory_coverage | pass/fail | candidates/material/non-findings match ledgers |
| finding_eligibility_coverage | pass/fail | every material finding has eligibility tests |
| authority_packet_coverage | pass/fail | required authority packets or root-equivalent packets present |
| authority_clearance_coverage | pass/fail | every candidate has clearance status |
| authority_veto_coverage | pass/fail | vetoes are represented and respected |
| evidence_ref_coverage | pass/fail | material findings have concrete evidence refs |
| non_finding_coverage | pass/fail | rejected candidates are visible |
| verification_path_coverage | pass/fail | every agenda item has proof/validation path |
| change_agenda_consistency | pass/fail | agenda matches eligible material/validation items |
| acceptance_skew_audit | pass/fail | all-candidate acceptance justified if needed |
| fixed_point_judgment_coverage | pass/fail | fixed-point judgment present |
| reviewer_complete | pass/fail | all required fields pass |
| change_agenda_allowed | yes/no | yes only when reviewer_complete passes and agenda is consistent |
| implementation_handoff_allowed | yes/no | must be no |
| validation_handoff_allowed | yes/no | yes only for validation-first agenda items |

If any required field fails, emit: `Blocked: incomplete adversarial review. Do not route remediation yet.`
