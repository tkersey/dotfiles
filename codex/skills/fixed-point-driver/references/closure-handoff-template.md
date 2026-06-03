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
  - no unresolved adversarial veto remains
  - negative evidence closure gate is satisfied

#### Warrant Intake / Parallelism Plan
| warrant id | claim id | permitted action | permitted scope | expiry check | surface budget | adversarial plan | parallelism mode | intake status |
|---|---|---|---|---|---|---|---|---|
| rw-F03 | F-03 | mutate-code | auth/session.ts,auth/session.test.ts | current head abc1234 | max +8 LOC, no public symbols | challenge stale-state route, proof, and surface | targeted-parallel | consumed |

#### Companion Skill Ledger
- companion: review-adjudication
  status: used
  evidence: reviewer comment F-03 accepted as material validation/mutation work with adversarial clearance
  limitations: none
- companion: accretive-implementer
  status: root-equivalent
  evidence: root applied narrow remediation and direct regression test inside warrant scope
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

#### Parallelism Plan
- mode: targeted-parallel
- read_only_lanes:
  - stale-state proof challenger
  - surface-budget / duplicate-owner challenger
- write_owner: root-equivalent implementation only
- reason: two independent risk classes could be checked before final closure without serial delay

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

#### Adversarial Action Ledger
| action id | phase | target | challenger lanes | parallelism mode | strongest adversarial finding | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|---|---|---|
| A-01 | route-selection | F-03 stale-secret remediation | no-change,validate-first,negative-evidence | targeted-parallel | cache-fast-path optimization remains excluded; direct persisted-secret read is warranted | cleared | cleared | auth/session.test.ts::rejects_stale_refresh_secret_after_rotation | route retained |
| A-02 | closure | INV-02 proof | proof freshness,surface-budget | root-equivalent | production adapter not directly exercised but changed path proof is sufficient for scoped PR | cleared | preserved | local test receipt T-01 | closure packet asks verification to inspect adapter limitation |

#### Findings Ledger
- finding_id: F-03
  materiality: material
  severity: major
  category: stale-state regression
  status: remediated
  remediation_posture: validating-check-only -> mutate-code after proof
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

#### Surface Delta Receipts
| receipt id | warrant id | patch/pass | production insertions | production deletions | net production loc | public symbols added | helpers added | duplicate paths added | budget status | proof ref |
|---|---|---|---|---|---|---|---|---|---|---|
| SDR-01 | rw-F03 | build-01 | 6 | 2 | +4 | 0 | 0 | 0 | within-budget | auth/session.test.ts::rejects_stale_refresh_secret_after_rotation |

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

#### Fixed-Point Gate Preview
- direct_changed_path: satisfied
- claimed_failure_mechanism: satisfied
- regression_surface: satisfied
- critical_invariants: preserved
- material_foot_guns: bounded
- material_complexity_hazards: bounded
- negative_evidence_closure_gate: satisfied
- adversarial_action_coverage: satisfied
- unresolved_adversarial_vetoes: none
- surface_budget_status: within-budget
- briefing_agreement: aligned
- external_blockers: none

#### Requested Closure Questions
- Does the changed path now directly prove post-rotation secret correctness?
- Is INV-02 bounded or still open?
- Are all adversarial vetoes cleared, preserved, or explicitly accepted as risk?
- Is NEG-01 still active, and if so, does it block the current route?
- Are any `learnings` hits being used as exclusions without current-state applicability?

#### Residual Uncertainty
- The production token-store adapter is represented indirectly by the test adapter.
```
