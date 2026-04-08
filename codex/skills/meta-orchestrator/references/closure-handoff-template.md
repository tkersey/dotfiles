# Example Closure Handoff Packet

```md
### Closure Handoff Packet

#### Handoff Kind
targeted-validation

#### Artifact State Label
loop-02-post-review

#### Objective
- requested_outcome: Eliminate the session refresh regression without changing the public API.
- claimed_behavior_change: The refresh path should re-issue a valid token only when the stored refresh secret is still current.
- current_phase_state: targeted validation before any additional remediation.

#### Scope and Constraints
- in_scope_artifacts:
  - auth/session.ts
  - auth/session.test.ts
  - auth/token-store.ts
- constraints:
  - preserve the current public API
  - keep remediation accretive unless structural evidence proves otherwise
- done_condition:
  - root cause is bounded
  - changed path is directly verified
  - no unresolved material finding remains

#### Artifact Set
- changed_files:
  - auth/session.ts
- changed_symbols:
  - refreshSession
  - validateRefreshSecret
- implicated_untouched_surfaces:
  - auth/token-store.ts

#### Diagnosis Ledger
- primary_mechanism: The refresh path reads a stale secret from a cached store snapshot during token rotation.
- confidence: plausible
- supporting_evidence:
  - failing CI log on token rotation scenario
  - reviewer finding F-03
- superseded_diagnoses:
  - transient clock skew hypothesis

#### Change Ledger
- pass_id: build-01
  pass_type: build
  rationale: Narrow fix for stale secret lookup
  touched_surfaces:
    - auth/session.ts
  status: completed
- pass_id: review-01
  pass_type: review
  rationale: Full de novo adversarial review
  touched_surfaces:
    - auth/session.ts
    - auth/session.test.ts
    - auth/token-store.ts
  status: completed
- pass_id: challenge-01
  pass_type: review
  rationale: Pre-closure one-change challenge found no remaining impactful accretive improvement.
  touched_surfaces:
    - none
  status: completed

#### Findings Ledger
- finding_id: F-03
  materiality: material
  severity: major
  category: stale-state regression
  status: open
  remediation_posture: validating-check-only
  evidence:
    - reviewer observed missing direct exercise of rotated-secret path
  why_it_matters: The fix may pass happy-path tests while still minting a token against stale state.
  implicated_surfaces:
    - auth/session.ts
    - auth/token-store.ts
  impacted_invariants:
    - INV-02
  next_action: Add a direct rotated-secret validation check.

#### Invariant Ledger
- invariant_id: INV-02
  name: Refresh uses the current persisted secret, not cached pre-rotation state.
  tier: critical
  status: unknown
  confidence: plausible
  blast_radius: module
  supporting_evidence:
    - no direct rotated-secret check yet
  open_question: Does refreshSession re-read the store after rotation?

#### Foot-Gun Register
- hazard_id: H-01
  trigger: Retry a refresh immediately after token rotation under cached store state.
  impact: Incorrect token issuance on an operational edge path.
  ease_of_misuse: medium
  status: unknown
  evidence:
    - inferred from missing direct exercise of the edge path
  narrowest_bounding_action: Add a direct retry-after-rotation test.

#### Complexity Ledger
- overall_delta: neutral
- materiality: non-material
- drivers:
  - one extra helper call
- evidence:
  - localized change only
- bounded_by:
  - no new public surface or branching beyond the existing refresh path

#### Verification Ledger
- direct_changed_path: open
- claimed_failure_mechanism: open
- regression_surface: satisfied
- checks_run:
  - check_id: T-01
    target: auth/session.test.ts existing refresh happy-path suite
    result: pass
    what_it_proves: Basic refresh flow still succeeds.
    limitations: Does not exercise rotated-secret state.

#### Specialist Briefing Ledger
- role: invariant_auditor
  artifact_state_label: loop-02-post-review
  scope: refreshSession + token-store contract
  top_material_signals:
    - INV-02 remains unknown
  unresolved_signals:
    - need direct proof of post-rotation store read
  agreement_pressure: aligned
  stale: no
- role: verification_auditor
  artifact_state_label: loop-02-post-review
  scope: direct path and regression coverage
  top_material_signals:
    - changed path not directly exercised
  unresolved_signals:
    - rotated-secret retry path untested
  agreement_pressure: aligned
  stale: no

#### Closure Gate Preview
- critical_invariants: unknown
- material_foot_guns: unknown
- material_complexity_hazards: bounded
- briefing_agreement: aligned
- external_blockers: none

#### Requested Closure Questions
- Does the changed path now directly prove post-rotation secret correctness?
- Is INV-02 bounded or still open?

#### Residual Uncertainty
- The store implementation may cache snapshots differently under production adapters.
```
