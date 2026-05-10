# Canonical Closure Handoff Packet

Use this packet whenever `fixed-point-driver` hands work to `verification-closure`.

The packet is a **canonical, ledgerized, schema-disciplined handoff**. Its job is to move the latest state across the phase boundary without collapsing important distinctions into prose. It must preserve negative evidence, rejected specialist packets, value receipts, and closure gates so the closure pass can audit readiness rather than reconstruct the campaign.

## Packet rules

- Use the headings in the exact order below.
- If a field is unknown, write `unknown`. Do not omit it.
- If a section has no entries, write `none`.
- Preserve stable IDs for findings, invariants, hazards, checks, passes, and negative-evidence entries when the same item survives multiple loops.
- Never silently drop a previously open material issue. Change its `status` with evidence.
- Mark specialist briefings `stale: yes` if their `artifact_state_id` or `artifact_state_label` does not match the packet's current state.
- Treat specialist outputs as high-signal input, not proof; root-owned verification commands remain authoritative.
- Validate packets against `../../references/specialist-packet-contract.md` before using them as evidence.
- Record accepted, rejected, stale, superseded, timeout, wrong-scope, transport-invalid, and low-value specialist packets instead of silently dropping them.
- Include a Specialist Value Receipt for every specialist packet.
- Include the pre-closure Negative Ledger Handoff even when no active exclusions exist.
- A `learnings` hit is candidate evidence only; closure must still decide whether its witness and applicability bind the current artifact state.

## Required headings

1. **Handoff Kind**
   - `targeted-validation`
   - `final-closure`

2. **Artifact State Label**
   - A stable state label such as `loop-03-post-review`.

3. **Artifact State ID**
   - branch or comparable workspace identity
   - `HEAD` or comparable revision
   - diff hash or changed-file digest
   - touched path set
   - phase label

4. **Objective**
   - requested outcome
   - claimed behavior change
   - current phase state

5. **Scope and Constraints**
   - in-scope artifacts
   - explicit constraints
   - done condition

6. **Companion Skill Ledger**
   - one entry per companion with:
     - `companion`
     - `status`: `used` | `root-equivalent` | `not-needed` | `unavailable` | `queried` | `mapped` | `captured` | `handoff` | `no-applicable-evidence` | `recalled` | `not-material`
     - `evidence`
     - `limitations`

7. **Routing and Budget Ledger**
   - `task_shape`
   - `fixed_point_lane`: `direct-closure` | `targeted` | `expanded-targeted` | `swarm`
   - `subagent_mode`: `off` | `targeted` | `swarm`
   - `specialist_budget_planned`
   - `specialist_budget_actual`
   - `budget_exceptions`
   - `lane_change_history`

8. **Artifact Set**
   - changed files
   - changed symbols
   - implicated untouched surfaces

9. **Diagnosis Ledger**
   - `primary_mechanism`
   - `confidence`: `proven` | `plausible` | `speculative`
   - `supporting_evidence`
   - `superseded_diagnoses`

10. **Change Ledger**
   - one entry per pass with:
     - `pass_id`
     - `pass_type`: `build` | `validation` | `review` | `closure` | `negative-ledger` | `capture`
     - `rationale`
     - `touched_surfaces`
     - `status`: `completed` | `partial` | `blocked`

11. **Findings Ledger**
   - one entry per finding with:
     - `finding_id`
     - `materiality`: `material` | `non-material`
     - `severity`: `blocker` | `major` | `minor` | `info`
     - `category`
     - `status`: `open` | `disproved` | `remediated` | `needs-decision` | `blocked` | `accepted-risk`
     - `remediation_posture`: `validating-check-only` | `accretive-remediation` | `structural-remediation`
     - `evidence`
     - `why_it_matters`
     - `implicated_surfaces`
     - `impacted_invariants`
     - `next_action`

12. **Invariant Ledger**
   - one entry per invariant with:
     - `invariant_id`
     - `name`
     - `tier`: `critical` | `major` | `supporting`
     - `status`: `preserved` | `strained` | `broken` | `unknown`
     - `confidence`: `proven` | `plausible` | `speculative`
     - `blast_radius`: `local` | `module` | `cross-cutting`
     - `supporting_evidence`
     - `open_question`

13. **Foot-Gun Register**
    - one entry per hazard with:
      - `hazard_id`
      - `trigger`
      - `impact`
      - `ease_of_misuse`: `high` | `medium` | `low`
      - `status`: `bounded` | `unbounded` | `unknown` | `accepted-risk`
      - `evidence`
      - `narrowest_bounding_action`

14. **Complexity Ledger**
    - `overall_delta`: `reduces` | `neutral` | `increases`
    - `materiality`: `material` | `non-material` | `unknown`
    - `drivers`
    - `evidence`
    - `bounded_by`

15. **Verification Ledger**
    - `direct_changed_path`: `satisfied` | `open` | `blocked` | `conflicting`
    - `claimed_failure_mechanism`: `satisfied` | `open` | `blocked` | `conflicting`
    - `regression_surface`: `satisfied` | `open` | `blocked` | `conflicting`
    - `checks_run`: one entry per check with:
      - `check_id`
      - `target`
      - `result`: `pass` | `fail` | `flaky` | `blocked` | `not-run`
      - `what_it_proves`
      - `limitations`

16. **Negative Ledger Pass**
    - latest root-owned negative-ledger pass with:
      - `phase`: `preflight` | `post-remediation` | `post-review` | `pre-closure` | `capture` | `handoff`
      - `mode`: `query` | `map` | `capture` | `reopen` | `handoff` | `none`
      - `artifact_state_id`
      - `topical_query`
      - `sources_checked`
      - `result`
      - `durable_capture`

17. **Negative Evidence Ledger**
    - one entry per currently material negative-evidence signal with:
      - `neg_id`
      - `hypothesis`
      - `attempted_change`
      - `source_refs`
      - `learning_source_ids` when sourced from `.learnings.jsonl` or `learnings recall/query`
      - `evidence`
      - `observed_outcome`
      - `failure_class`: `no-effect` | `local-regression` | `global-regression` | `unsound` | `too-complex` | `stale` | `unknown`
      - `applicability_conditions`
      - `current_status`: `active` | `stale` | `superseded` | `reopened` | `unknown` | `need-evidence`
      - `exclusion_rule`
      - `reopening_criteria`
      - `confidence`: `high` | `medium` | `low` | `unknown`
      - `next_search_hint`

18. **Negative Ledger Handoff**
    - `active_exclusions`
    - `stale_or_superseded`
    - `reopened`
    - `need_evidence`
    - `safest_next_frontier`
    - `learnings_source_ids`
    - `durable_capture`
    - `closure_effect`:
      - `blocks_closure`: `yes` | `no`
      - `changes_one_change_challenge`: `yes` | `no`
      - `changes_verification_plan`: `yes` | `no`

19. **Specialist Briefing Ledger**
    - one entry per specialist with:
      - `role`
      - `artifact_state_id`
      - `artifact_state_label`
      - `scope`
      - `top_material_signals`
      - `unresolved_signals`
      - `agreement_pressure`: `aligned` | `mixed` | `conflicting` | `unknown`
      - `stale`: `yes` | `no` | `unknown`
      - `packet_status`: `accepted` | `stale` | `transport-invalid` | `wrong-scope` | `timeout` | `superseded` | `low-value`
      - `used_for`: evidence mapping | negative-evidence pruning | soundness pressure | invariant pressure | hazard pressure | complexity pressure | verification planning | none
      - `rejection_reason`: reason or `none`

20. **Specialist Value Receipts**
    - one entry per specialist packet with:
      - `role`
      - `packet_status`: `accepted` | `stale` | `transport-invalid` | `wrong-scope` | `timeout` | `superseded` | `low-value`
      - `artifact_state_id_match`: `yes` | `no` | `unknown`
      - `scope_match`: `yes` | `no` | `unknown`
      - `uncertainty_class`: `evidence` | `soundness` | `invariant` | `hazard` | `complexity` | `verification` | `negative-evidence` | `other`
      - `route_changed`: `yes` | `no`
      - `finding_added`: `yes` | `no`
      - `proof_changed`: `yes` | `no`
      - `risk_retired`: `yes` | `no`
      - `value`: `positive` | `neutral` | `negative`
      - `used_for`
      - `reason`

21. **Closure Gate Preview**
    - `direct_changed_path`: `satisfied` | `open` | `blocked` | `conflicting`
    - `claimed_failure_mechanism`: `satisfied` | `open` | `blocked` | `conflicting`
    - `regression_surface`: `satisfied` | `open` | `blocked` | `conflicting`
    - `critical_invariants`: `preserved` | `strained` | `broken` | `unknown`
    - `material_foot_guns`: `bounded` | `unbounded` | `unknown` | `accepted-risk`
    - `material_complexity_hazards`: `bounded` | `unbounded` | `unknown` | `residual-design-risk`
    - `negative_evidence_closure_gate`: `satisfied` | `open` | `blocked` | `unavailable`
    - `briefing_agreement`: `aligned` | `mixed` | `conflicting`
    - `external_blockers`: `none` | `present`

22. **Requested Closure Questions**
    - the specific questions `verification-closure` must answer
    - include at least one negative-evidence question when active, reopened, unknown, or unavailable negative evidence exists

23. **Residual Uncertainty**
    - assumptions
    - environment limits
    - known unknowns

## Minimal template

```md
### Closure Handoff Packet

#### Handoff Kind
final-closure

#### Artifact State Label
loop-03-post-review

#### Artifact State ID
- branch: ...
- revision: ...
- diff_hash: ...
- touched_paths: ...
- phase: ...

#### Objective
- requested_outcome: ...
- claimed_behavior_change: ...
- current_phase_state: ...

#### Scope and Constraints
- in_scope_artifacts: ...
- constraints: ...
- done_condition: ...

#### Companion Skill Ledger
- companion: negative-ledger
  status: handoff
  evidence: pre-closure negative-ledger handoff completed
  limitations: none

#### Routing and Budget Ledger
- task_shape: remediation
- fixed_point_lane: targeted
- subagent_mode: targeted
- specialist_budget_planned: 2
- specialist_budget_actual: 1
- budget_exceptions: none
- lane_change_history: none

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
- pass_id: neg-01
  pass_type: negative-ledger
  rationale: preflight query/map to avoid repeated failed routes
  touched_surfaces: none
  status: completed

#### Findings Ledger
- finding_id: ...
  materiality: material
  severity: major
  category: ...
  status: remediated
  remediation_posture: accretive-remediation
  evidence: ...
  why_it_matters: ...
  implicated_surfaces: ...
  impacted_invariants: ...
  next_action: none

#### Invariant Ledger
- invariant_id: ...
  name: ...
  tier: critical
  status: preserved
  confidence: plausible
  blast_radius: module
  supporting_evidence: ...
  open_question: none

#### Foot-Gun Register
none

#### Complexity Ledger
- overall_delta: neutral
- materiality: non-material
- drivers: ...
- evidence: ...
- bounded_by: ...

#### Verification Ledger
- direct_changed_path: satisfied
- claimed_failure_mechanism: satisfied
- regression_surface: satisfied
- checks_run:
  - check_id: ...
    target: ...
    result: pass
    what_it_proves: ...
    limitations: ...

#### Negative Ledger Pass
- phase: pre-closure
- mode: handoff
- artifact_state_id: ...
- topical_query: ...
- sources_checked:
    current_run: yes
    fixed_point_ledgers: yes
    learnings: yes
    repo_history: no
    review_comments: yes
    user_context: no
- result:
    active_exclusions: none
    stale_or_superseded: none
    reopened_candidates: none
    need_evidence: none
    no_applicable_negative_evidence_reason: no matching failed route found
    safest_next_frontier: proceed with closure proof
- durable_capture: not-material

#### Negative Evidence Ledger
none

#### Negative Ledger Handoff
- active_exclusions: none
- stale_or_superseded: none
- reopened: none
- need_evidence: none
- safest_next_frontier: proceed with closure proof
- learnings_source_ids: none
- durable_capture: not-material
- closure_effect:
    blocks_closure: no
    changes_one_change_challenge: no
    changes_verification_plan: no

#### Specialist Briefing Ledger
none

#### Specialist Value Receipts
none

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
- Is the changed path directly verified?
- Is the negative evidence closure gate satisfied?

#### Residual Uncertainty
- ...
```
