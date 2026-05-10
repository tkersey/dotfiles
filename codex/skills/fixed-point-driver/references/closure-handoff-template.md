# Example Closure Handoff Packet

```md
### Closure Handoff Packet

#### Handoff Kind
final-closure

#### Artifact State Label
loop-03-post-review

#### Artifact State ID
- branch: feature/session-refresh-fix
- revision: abc1234
- diff_hash: auth-session-rotated-secret-v3
- touched_paths:
  - auth/session.ts
  - auth/session.test.ts
- phase: closure-candidate

#### Objective
- requested_outcome: Eliminate the session refresh regression without changing the public API.
- claimed_behavior_change: The refresh path should re-issue a valid token only when the stored refresh secret is still current.
- current_phase_state: final closure candidate after remediation and de novo review.

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
  - negative evidence closure gate is satisfied

#### Companion Skill Ledger
- companion: review-adjudication
  status: used
  evidence: reviewer comment F-03 accepted as material validation work
  limitations: none
- companion: accretive-implementer
  status: root-equivalent
  evidence: root applied narrow remediation and direct regression test
  limitations: no distinct implementer packet
- companion: adversarial-reviewer
  status: root-equivalent
  evidence: root ran de novo post-remediation review
  limitations: no distinct reviewer packet
- companion: verification-closure
  status: used
  evidence: this packet requests final closure
  limitations: closure not yet run
- companion: negative-ledger
  status: handoff
  evidence: preflight query/map and pre-closure handoff completed
  limitations: repo history not searched
- companion: learnings
  status: recalled
  evidence: lrn-auth-refresh-cache-fast-path considered as candidate negative evidence
  limitations: only matching learning was current enough to inspect

#### Routing and Budget Ledger
- task_shape: remediation
- fixed_point_lane: targeted
- subagent_mode: targeted
- specialist_budget_planned: 2
- specialist_budget_actual: 1
- budget_exceptions: none
- lane_change_history:
  - direct-closure -> targeted because prior cache-fast-path negative evidence could change route

#### Artifact Set
- changed_files:
  - auth/session.ts
  - auth/session.test.ts
- changed_symbols:
  - refreshSession
  - validateRefreshSecret
  - rejects stale refresh secret test
- implicated_untouched_surfaces:
  - auth/token-store.ts

#### Diagnosis Ledger
- primary_mechanism: The refresh path previously trusted a cached secret snapshot during token rotation.
- confidence: plausible
- supporting_evidence:
  - failing rotated-secret retry test before remediation
  - passing direct regression test after remediation
  - negative evidence showed cache-fast-path had failed this same invariant before
- superseded_diagnoses:
  - transient clock skew hypothesis

#### Change Ledger
- pass_id: neg-01
  pass_type: negative-ledger
  rationale: Query prior failures before selecting remediation route.
  touched_surfaces: none
  status: completed
- pass_id: build-01
  pass_type: build
  rationale: Narrow fix for stale secret lookup and direct regression test.
  touched_surfaces:
    - auth/session.ts
    - auth/session.test.ts
  status: completed
- pass_id: review-01
  pass_type: review
  rationale: Full de novo review after remediation.
  touched_surfaces:
    - auth/session.ts
    - auth/session.test.ts
    - auth/token-store.ts
  status: completed

#### Findings Ledger
- finding_id: F-03
  materiality: material
  severity: major
  category: stale-state regression
  status: remediated
  remediation_posture: validating-check-only
  evidence:
    - direct rotated-secret retry test now passes
  why_it_matters: The fix could pass happy-path tests while still minting a token against stale state.
  implicated_surfaces:
    - auth/session.ts
    - auth/token-store.ts
  impacted_invariants:
    - INV-02
  next_action: final closure gate

#### Invariant Ledger
- invariant_id: INV-02
  name: Refresh uses the current persisted secret, not cached pre-rotation state.
  tier: critical
  status: preserved
  confidence: plausible
  blast_radius: module
  supporting_evidence:
    - direct rotated-secret retry test exercises post-rotation persisted secret
  open_question: none

#### Foot-Gun Register
- hazard_id: H-01
  trigger: Retry refresh immediately after token rotation under cached store state.
  impact: Incorrect token issuance on an operational edge path.
  ease_of_misuse: medium
  status: bounded
  evidence:
    - direct retry-after-rotation test fails under stale snapshot behavior and passes after remediation
  narrowest_bounding_action: preserve direct regression test

#### Complexity Ledger
- overall_delta: neutral
- materiality: non-material
- drivers:
  - one extra persisted-secret lookup
  - one focused regression test
- evidence:
  - no new public surface
  - no new branching outside refresh path
- bounded_by:
  - localized helper call and direct test

#### Verification Ledger
- direct_changed_path: satisfied
- claimed_failure_mechanism: satisfied
- regression_surface: satisfied
- checks_run:
  - check_id: T-01
    target: auth/session.test.ts::rejects_stale_refresh_secret_after_rotation
    result: pass
    what_it_proves: Changed path rejects stale rotated secret.
    limitations: Uses test adapter rather than production token store.
  - check_id: T-02
    target: auth/session.test.ts existing refresh suite
    result: pass
    what_it_proves: Basic refresh behavior still succeeds.
    limitations: Does not prove all production adapter behavior.

#### Negative Ledger Pass
- phase: pre-closure
- mode: handoff
- artifact_state_id: branch=feature/session-refresh-fix head=abc1234 diff=auth-session-rotated-secret-v3 phase=closure-candidate
- topical_query: auth refresh rotated-secret cache fast-path regression
- sources_checked:
    current_run: yes
    fixed_point_ledgers: yes
    learnings: yes
    repo_history: no
    review_comments: yes
    user_context: no
- result:
    active_exclusions:
      - NEG-01
    stale_or_superseded: none
    reopened_candidates: none
    need_evidence: none
    no_applicable_negative_evidence_reason: n/a
    safest_next_frontier: keep persisted-secret read and direct rotated-secret proof; do not optimize through cache snapshot
- durable_capture: duplicate-skip

#### Negative Evidence Ledger
- neg_id: NEG-01
  hypothesis: Reuse cached store snapshots during token refresh to avoid the extra store read.
  attempted_change: Prior fast-path prototype skipped the post-rotation store read.
  source_refs:
    - kind: learning
      ref: lrn-auth-refresh-cache-fast-path
      summary: Prior fast path regressed rotated-secret retry coverage.
    - kind: failing-test
      ref: auth/session.test.ts::rejects_stale_refresh_secret_after_rotation
      summary: Fails when refresh depends on stale snapshot.
  learning_source_ids:
    - lrn-auth-refresh-cache-fast-path
  evidence:
    - Prior fast path passed happy-path refresh but failed rotated-secret retry coverage.
  observed_outcome: Removed a read but reopened stale-secret token issuance.
  failure_class: unsound
  applicability_conditions:
    - applies while refresh correctness depends on reading the current persisted secret after rotation
  current_status: active
  exclusion_rule: Do not select a cache-snapshot refresh optimization unless it proves post-rotation secret freshness directly.
  reopening_criteria:
    - store snapshot semantics are replaced with a current-secret witness
    - direct rotated-secret retry test passes under the new design
  confidence: medium
  next_search_hint: Prefer validating the persisted-secret read rather than optimizing it away.

#### Negative Ledger Handoff
- active_exclusions:
    - NEG-01: cache-snapshot fast path remains excluded
- stale_or_superseded: none
- reopened: none
- need_evidence: none
- safest_next_frontier: proceed with closure; maintain persisted-secret read and regression test
- learnings_source_ids:
    - lrn-auth-refresh-cache-fast-path
- durable_capture: duplicate-skip
- closure_effect:
    blocks_closure: no
    changes_one_change_challenge: yes
    changes_verification_plan: yes

#### Specialist Briefing Ledger
- role: verification_auditor
  artifact_state_id:
    branch: feature/session-refresh-fix
    revision: abc1234
    diff_hash: auth-session-rotated-secret-v3
    touched_paths:
      - auth/session.ts
      - auth/session.test.ts
    phase: closure-candidate
  artifact_state_label: loop-03-post-review
  scope: direct path and regression coverage
  top_material_signals:
    - direct rotated-secret retry path now exercised
  unresolved_signals:
    - production adapter semantics not directly exercised
  agreement_pressure: aligned
  stale: no
  packet_status: accepted
  used_for: verification planning
  rejection_reason: none

#### Specialist Value Receipts
- role: verification_auditor
  packet_status: accepted
  artifact_state_id_match: yes
  scope_match: yes
  uncertainty_class: verification
  route_changed: no
  finding_added: no
  proof_changed: yes
  risk_retired: yes
  value: positive
  used_for: verification-planning
  reason: Identified the direct rotated-secret retry test as the decisive changed-path proof.

#### Closure Gate Preview
- direct_changed_path: satisfied
- claimed_failure_mechanism: satisfied
- regression_surface: satisfied
- critical_invariants: preserved
- material_foot_guns: bounded
- material_complexity_hazards: bounded
- negative_evidence_closure_gate: satisfied
- briefing_agreement: aligned
- external_blockers: none

#### Requested Closure Questions
- Does the changed path now directly prove post-rotation secret correctness?
- Is INV-02 bounded or still open?
- Is NEG-01 still active, and if so, does it block the current route?
- Are any `learnings` hits being used as exclusions without current-state applicability?

#### Residual Uncertainty
- The production token-store adapter is represented indirectly by the test adapter.
```
