# Closure handoff template

```md
### Closure Handoff Packet

#### Handoff Kind
final-closure

#### Artifact State Label
loop-03-post-review

#### Objective
- requested_outcome: ...
- claimed_behavior_change: ...
- current_phase_state: ...

#### Scope and Constraints
- in_scope_artifacts: ...
- constraints: ...
- done_condition: ...

#### Artifact Set
- changed_files: ...
- changed_symbols: ...
- implicated_untouched_surfaces: ...

#### Diagnosis Ledger
- primary_mechanism: ...
- confidence: plausible
- supporting_evidence: ...
- superseded_diagnoses: none

#### Change Ledger
- pass_id: build-03
  pass_type: build
  rationale: ...
  touched_surfaces: ...
  status: completed

#### Findings Ledger
- finding_id: F-01
  materiality: material
  severity: major
  category: verification
  status: open
  remediation_posture: validating-check-only
  evidence: ...
  why_it_matters: ...
  implicated_surfaces: ...
  impacted_invariants: ...
  next_action: ...

#### Invariant Ledger
- invariant_id: INV-01
  name: ...
  tier: critical
  status: unknown
  confidence: plausible
  blast_radius: module
  supporting_evidence: ...
  open_question: ...

#### Foot-Gun Register
- hazard_id: H-01
  trigger: ...
  impact: ...
  ease_of_misuse: medium
  status: unknown
  evidence: ...
  narrowest_bounding_action: ...

#### Complexity Ledger
- overall_delta: neutral
- materiality: non-material
- drivers: ...
- evidence: ...
- bounded_by: ...

#### Verification Ledger
- direct_changed_path: open
- claimed_failure_mechanism: open
- regression_surface: satisfied
- checks_run:
  - check_id: T-01
    target: ...
    result: pass
    what_it_proves: ...
    limitations: ...

#### Specialist Briefing Ledger
- role: verification_auditor
  artifact_state_label: loop-03-post-review
  scope: ...
  top_material_signals:
    - changed path not directly exercised
  unresolved_signals:
    - ...
  agreement_pressure: aligned
  stale: no

#### Closure Gate Preview
- critical_invariants: unknown
- material_foot_guns: unknown
- material_complexity_hazards: bounded
- briefing_agreement: aligned
- external_blockers: none

#### Requested Closure Questions
- Does the changed path now directly prove the claimed behavior?
- Is INV-01 still open?

#### Residual Uncertainty
- ...
```
