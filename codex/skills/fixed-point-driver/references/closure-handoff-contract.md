# Canonical Closure Handoff Packet

Use this packet whenever `meta-orchestrator` hands work to `verification-closure`.
The packet is a **canonical, ledgerized, schema-disciplined handoff**. Its job is to move the latest state across the phase boundary without collapsing important distinctions into prose.

## Packet rules

- Use the headings in the exact order below.
- If a field is unknown, write `unknown`. Do not omit it.
- If a section has no entries, write `none`.
- Preserve stable IDs for findings, invariants, hazards, checks, and passes when the same item survives multiple loops.
- Never silently drop a previously open material issue. Change its `status` with evidence.
- Mark specialist briefings `stale: yes` if their `artifact_state_id` or `artifact_state_label` does not match the packet's current state.
- Treat specialist outputs as high-signal input, not proof; root-owned verification commands remain authoritative.
- Record rejected specialist packets instead of silently dropping them.

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

6. **Artifact Set**
   - changed files
   - changed symbols
   - implicated untouched surfaces

7. **Diagnosis Ledger**
   - `primary_mechanism`
   - `confidence`: `proven` | `plausible` | `speculative`
   - `supporting_evidence`
   - `superseded_diagnoses`

8. **Change Ledger**
   - one entry per pass with:
     - `pass_id`
     - `pass_type`: `build` | `validation` | `review` | `closure`
     - `rationale`
     - `touched_surfaces`
     - `status`: `completed` | `partial` | `blocked`

9. **Findings Ledger**
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

10. **Invariant Ledger**
   - one entry per invariant with:
     - `invariant_id`
     - `name`
     - `tier`: `critical` | `major` | `supporting`
     - `status`: `preserved` | `strained` | `broken` | `unknown`
     - `confidence`: `proven` | `plausible` | `speculative`
     - `blast_radius`: `local` | `module` | `cross-cutting`
     - `supporting_evidence`
     - `open_question`

11. **Foot-Gun Register**
    - one entry per hazard with:
      - `hazard_id`
      - `trigger`
      - `impact`
      - `ease_of_misuse`: `high` | `medium` | `low`
      - `status`: `bounded` | `unbounded` | `unknown` | `accepted-risk`
      - `evidence`
      - `narrowest_bounding_action`

12. **Complexity Ledger**
    - `overall_delta`: `reduces` | `neutral` | `increases`
    - `materiality`: `material` | `non-material` | `unknown`
    - `drivers`
    - `evidence`
    - `bounded_by`

13. **Verification Ledger**
    - `direct_changed_path`: `satisfied` | `open` | `blocked` | `conflicting`
    - `claimed_failure_mechanism`: `satisfied` | `open` | `blocked` | `conflicting`
    - `regression_surface`: `satisfied` | `open` | `blocked` | `conflicting`
    - `checks_run`: one entry per check with:
      - `check_id`
      - `target`
      - `result`: `pass` | `fail` | `flaky` | `blocked` | `not-run`
      - `what_it_proves`
      - `limitations`

14. **Specialist Briefing Ledger**
    - one entry per specialist with:
      - `role`
      - `artifact_state_id`
      - `artifact_state_label`
      - `scope`
      - `top_material_signals`
      - `unresolved_signals`
      - `agreement_pressure`: `aligned` | `mixed` | `conflicting`
      - `stale`: `yes` | `no`
      - `packet_status`: `accepted` | `stale` | `transport-invalid` | `wrong-scope` | `timeout` | `superseded`
      - `used_for`: evidence mapping | soundness pressure | invariant pressure | hazard pressure | complexity pressure | verification planning | none
      - `rejection_reason`: reason or `none`

15. **Closure Gate Preview**
    - `critical_invariants`: `preserved` | `strained` | `broken` | `unknown`
    - `material_foot_guns`: `bounded` | `unbounded` | `unknown` | `accepted-risk`
    - `material_complexity_hazards`: `bounded` | `unbounded` | `unknown` | `residual-design-risk`
    - `briefing_agreement`: `aligned` | `mixed` | `conflicting`
    - `external_blockers`: `none` | `present`

16. **Requested Closure Questions**
    - the specific questions `verification-closure` must answer

17. **Residual Uncertainty**
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

#### Specialist Briefing Ledger
- role: invariant_auditor
  artifact_state_id:
    branch: ...
    revision: ...
    diff_hash: ...
    touched_paths: ...
    phase: ...
  artifact_state_label: loop-03-post-review
  scope: ...
  top_material_signals: ...
  unresolved_signals: ...
  agreement_pressure: aligned
  stale: no
  packet_status: accepted
  used_for: invariant pressure
  rejection_reason: none

#### Closure Gate Preview
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
