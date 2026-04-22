# Canonical Closure Handoff Packet

Use this packet whenever `fixed-point-driver` hands work to `verification-closure`. The packet is a **canonical, ledgerized, schema-disciplined handoff**. Its job is to move the latest state across the phase boundary without collapsing important distinctions into prose.

## Packet rules

- Use the headings in the exact order below.
- If a field is unknown, write `unknown`. Do not omit it.
- If a section has no entries, write `none`.
- Preserve stable IDs for findings, soundness claims, invariants, hazards, checks, and passes when the same item survives multiple loops.
- Never silently drop a previously open material issue. Change its `status` with evidence.
- Include the current escalation level and the active or resolved escalation triggers.
- Mark specialist briefings `stale: yes` if their `artifact_state_label` does not match the packet's current `artifact_state_label`.
- Treat specialist outputs as high-signal input, not proof.
- For final closure, include the latest applicable one-change challenge result.
- If unchanged-state reuse is used, identify the reused state and the fresh stale-assumption recheck.

## Required headings

1. **Handoff Kind**
   - `targeted-validation`
   - `final-closure`

2. **Artifact State Label**
   - A stable state label such as `loop-03-post-review`.

3. **Closure Freshness**
   - `freshness_mode`: `fresh` | `unchanged-state-reuse`
   - `unchanged_since`: prior packet or state label, or `none`
   - `reuse_basis`: artifact state, diff, evidence, ledgers, specialist freshness, and requested questions unchanged, or `none`
   - `stale_assumption_recheck`: the fresh re-review just performed, or `none`
   - `missing_focused_witnesses`: any witness still missing, or `none`

4. **Escalation Ledger**
   - `level`: `0-local` | `1-focused` | `2-exhaustive`
   - `active_triggers`
   - `resolved_triggers`
   - `why_this_level_is_sufficient_or_required`
   - `last_escalation_decision`

5. **Objective**
   - requested outcome
   - claimed behavior change
   - current phase state

6. **Scope and Constraints**
   - in-scope artifacts
   - explicit constraints
   - done condition

7. **Artifact Set**
   - changed files
   - changed symbols
   - implicated untouched surfaces

8. **Diagnosis Ledger**
   - `primary_mechanism`
   - `confidence`: `proven` | `plausible` | `speculative`
   - `supporting_evidence`
   - `superseded_diagnoses`

9. **Change Ledger**
   - one entry per pass with:
     - `pass_id`
     - `pass_type`: `build` | `validation` | `review` | `closure`
     - `rationale`
     - `touched_surfaces`
     - `status`: `completed` | `partial` | `blocked`
   - record the most recent pre-closure one-change challenge as a `review` pass even when it results in no code change

10. **Findings Ledger**
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

11. **Soundness Ledger**
    - one entry per soundness claim with:
      - `claim_id`
      - `claim_or_obligation`
      - `kind`: `missing-witness` | `stale-witness` | `contradictory-witness` | `preservation-break` | `stuck-state` | `impossible-state` | `partial-elimination` | `overclaim`
      - `witness_required`
      - `witness_status`: `present` | `partial` | `stale` | `missing` | `contradictory`
      - `preservation`: `preserved` | `strained` | `broken` | `unknown`
      - `progress`: `safe` | `stuck` | `unknown`
      - `inhabitance`: `bounded` | `impossible-state-admitted` | `unknown`
      - `evidence`
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

16. **One-Change Challenge Ledger**
    - `question`
    - `status`: `not-run` | `run`
    - `outcome`: `unknown` | `implemented` | `no-impactful-change` | `needs-decision` | `blocked`
    - `acceptance`: `unknown` | `accepted-now` | `deferred-adjacent` | `rejected-scope` | `rejected-nonmaterial`
    - `candidate_change`
    - `why_this_one`
    - `routed_to`
    - `evidence`
    - `artifact_state_before`
    - `artifact_state_after`
    - final closure packets must not leave `outcome` or `acceptance` as `unknown`

17. **Specialist Briefing Ledger**
    - one entry per specialist with:
      - `role`
      - `artifact_state_label`
      - `scope`
      - `top_material_signals`
      - `unresolved_signals`
      - `agreement_pressure`: `aligned` | `mixed` | `conflicting`
      - `stale`: `yes` | `no`

18. **Closure Gate Preview**
    - `material_soundness`: `bounded` | `unbounded` | `unknown` | `conflicting`
    - `critical_invariants`: `preserved` | `strained` | `broken` | `unknown`
    - `material_foot_guns`: `bounded` | `unbounded` | `unknown` | `accepted-risk`
    - `material_complexity_hazards`: `bounded` | `unbounded` | `unknown` | `residual-design-risk`
    - `briefing_agreement`: `aligned` | `mixed` | `conflicting`
    - `external_blockers`: `none` | `present`

19. **Requested Closure Questions**
    - the specific questions `verification-closure` must answer

20. **Residual Uncertainty**
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

#### Closure Freshness
- freshness_mode: fresh
- unchanged_since: none
- reuse_basis: none
- stale_assumption_recheck: none
- missing_focused_witnesses: none

#### Escalation Ledger
- level: 1-focused
- active_triggers: none
- resolved_triggers:
  - direct changed-path witness supplied
- why_this_level_is_sufficient_or_required: implicated surface is bounded and no cross-cutting invariant remains open
- last_escalation_decision: remain at Level 1 after focused verification review

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
- pass_id: ...
  pass_type: ...
  rationale: ...
  touched_surfaces: ...
  status: ...

#### Findings Ledger
- finding_id: ...
  materiality: material
  severity: major
  category: ...
  status: open
  remediation_posture: accretive-remediation
  evidence: ...
  why_it_matters: ...
  implicated_surfaces: ...
  impacted_invariants: ...
  next_action: ...

#### Soundness Ledger
- claim_id: S-01
  claim_or_obligation: Refresh reads the current persisted secret after rotation.
  kind: missing-witness
  witness_required: direct rotated-secret exercise on the live read path
  witness_status: missing
  preservation: unknown
  progress: safe
  inhabitance: bounded
  evidence: no direct post-rotation witness yet
  next_action: add one direct rotated-secret validation check

#### Invariant Ledger
- invariant_id: ...
  name: ...
  tier: critical
  status: strained
  confidence: plausible
  blast_radius: module
  supporting_evidence: ...
  open_question: ...

#### Foot-Gun Register
- hazard_id: ...
  trigger: ...
  impact: ...
  ease_of_misuse: high
  status: unbounded
  evidence: ...
  narrowest_bounding_action: ...

#### Complexity Ledger
- overall_delta: neutral
- materiality: non-material
- drivers: ...
- evidence: ...
- bounded_by: ...

#### Verification Ledger
- direct_changed_path: satisfied
- claimed_failure_mechanism: open
- regression_surface: open
- checks_run:
  - check_id: ...
    target: ...
    result: pass
    what_it_proves: ...
    limitations: ...

#### One-Change Challenge Ledger
- question: If you could change one thing about this changeset what would you change?
- status: run
- outcome: no-impactful-change
- acceptance: rejected-nonmaterial
- candidate_change: none
- why_this_one: no remaining change was clearly worth the churn
- routed_to: none
- evidence: candidate material fixed point review found no material reopening signal
- artifact_state_before: loop-03-post-review
- artifact_state_after: loop-03-post-review

#### Specialist Briefing Ledger
- role: invariant_auditor
  artifact_state_label: loop-03-post-review
  scope: ...
  top_material_signals: ...
  unresolved_signals: ...
  agreement_pressure: aligned
  stale: no

#### Closure Gate Preview
- material_soundness: unknown
- critical_invariants: strained
- material_foot_guns: unbounded
- material_complexity_hazards: bounded
- briefing_agreement: mixed
- external_blockers: none

#### Requested Closure Questions
- Is the changed path directly verified?
- Is invariant INV-02 now bounded?

#### Residual Uncertainty
- ...
```
