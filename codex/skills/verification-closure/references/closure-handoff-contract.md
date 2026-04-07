# Canonical Closure Handoff Packet

Use this packet whenever `meta-orchestrator` hands work to `verification-closure`.
The packet is a canonical, ledgerized phase-boundary object.

## Packet rules

- Use the headings in the exact order below.
- If a field is unknown, write `unknown`. Do not omit it.
- If a section has no entries, write `none`.
- Preserve stable IDs for findings, invariants, hazards, checks, and passes when the same item survives multiple loops.
- Never silently drop a previously open material issue. Change its `status` with evidence.
- Mark specialist briefings `stale: yes` if their `artifact_state_label` does not match the packet's current `artifact_state_label`.
- Treat specialist outputs as high-signal input, not proof.

## Required headings

1. **Handoff Kind**
   - `targeted-validation`
   - `final-closure`

2. **Artifact State Label**
   - a stable state label such as `loop-03-post-review`

3. **Objective**
   - requested outcome
   - claimed behavior change
   - current phase state

4. **Scope and Constraints**
   - in-scope artifacts
   - explicit constraints
   - done condition

5. **Artifact Set**
   - changed files
   - changed symbols
   - implicated untouched surfaces

6. **Diagnosis Ledger**
   - `primary_mechanism`
   - `confidence`: `proven` | `plausible` | `speculative`
   - `supporting_evidence`
   - `superseded_diagnoses`

7. **Change Ledger**
   - one entry per pass with:
     - `pass_id`
     - `pass_type`: `build` | `review` | `validation` | `closure`
     - `rationale`
     - `touched_surfaces`
     - `status`: `completed` | `partial` | `blocked`

8. **Findings Ledger**
   - one entry per finding with:
     - `finding_id`
     - `materiality`: `material` | `non-material`
     - `severity`: `blocker` | `major` | `moderate` | `minor` | `info`
     - `category`
     - `status`: `open` | `disproved` | `remediated` | `needs-decision` | `blocked` | `accepted-risk`
     - `remediation_posture`: `validating-check-only` | `accretive-remediation` | `structural-remediation`
     - `evidence`
     - `why_it_matters`
     - `implicated_surfaces`
     - `impacted_invariants`
     - `next_action`

9. **Invariant Ledger**
   - one entry per invariant with:
     - `invariant_id`
     - `name`
     - `tier`: `critical` | `major` | `supporting`
     - `status`: `preserved` | `strained` | `broken` | `unknown`
     - `confidence`: `proven` | `plausible` | `speculative`
     - `blast_radius`: `local` | `module` | `cross-cutting`
     - `supporting_evidence`
     - `open_question`

10. **Foot-Gun Register**
    - one entry per hazard with:
      - `hazard_id`
      - `trigger`
      - `impact`
      - `ease_of_misuse`: `high` | `medium` | `low`
      - `status`: `bounded` | `unbounded` | `unknown` | `accepted-risk`
      - `evidence`
      - `narrowest_bounding_action`

11. **Complexity Ledger**
    - `overall_delta`: `reduces` | `neutral` | `increases` | `indeterminate`
    - `materiality`: `material` | `non-material` | `unknown`
    - `drivers`
    - `evidence`
    - `bounded_by`

12. **Verification Ledger**
    - `direct_changed_path`: `satisfied` | `open` | `blocked` | `conflicting`
    - `claimed_failure_mechanism`: `satisfied` | `open` | `blocked` | `conflicting`
    - `regression_surface`: `satisfied` | `open` | `blocked` | `conflicting`
    - `checks_run`: one entry per check with:
      - `check_id`
      - `target`
      - `result`: `pass` | `fail` | `flaky` | `blocked` | `not-run`
      - `what_it_proves`
      - `limitations`

13. **Specialist Briefing Ledger**
    - one entry per specialist with:
      - `role`
      - `artifact_state_label`
      - `scope`
      - `top_material_signals`
      - `unresolved_signals`
      - `agreement_pressure`: `aligned` | `mixed` | `conflicting`
      - `stale`: `yes` | `no`

14. **Closure Gate Preview**
    - `critical_invariants`: `preserved` | `strained` | `broken` | `unknown`
    - `material_foot_guns`: `bounded` | `unbounded` | `unknown` | `accepted-risk`
    - `material_complexity_hazards`: `bounded` | `unbounded` | `unknown` | `residual-design-risk`
    - `briefing_agreement`: `aligned` | `mixed` | `conflicting`
    - `external_blockers`: `none` | `present`

15. **Requested Closure Questions**
    - the specific questions `verification-closure` must answer

16. **Residual Uncertainty**
    - assumptions
    - environment limits
    - known unknowns
