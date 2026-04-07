---
name: meta-orchestrator
description: Use this skill to coordinate exhaustive build-review-verify workflows across accretive-implementer, adversarial-reviewer, and verification-closure when a coding task needs de novo re-litigation, optional read-only specialist subagents, signal-aware routing by invariants foot-guns complexity and verification, packet-native specialist briefings, and a canonical Closure Handoff Packet that always passes the latest ledgers into verification-closure. Trigger for requests like harden this patch exhaustively, use subagents for broad review, keep re-reviewing from scratch, find all impactful changes, or take this to closure with a fixed handoff schema.
---

# Meta Orchestrator

This skill coordinates three narrow companion skills:

- `accretive-implementer` for implementation, adaptation, and remediation
- `adversarial-reviewer` for skeptical full-scope review
- `verification-closure` for targeted evidence checks and final readiness decisions

It optionally uses a **read-only specialist subagent swarm** for parallel evidence gathering.
The orchestrator remains the decider.

Default posture: drive the in-scope artifact set to an evidence-backed **material fixed point** through repeated **de novo adversarial re-litigation**, **signal-aware routing**, **accretive implementation or remediation by default**, **packet-native specialist briefings**, and a **canonical Closure Handoff Packet** refreshed before every validation or closure pass.

## Global doctrine

Every phase inherits **UNSOUND**, **MECHANISTIC**, **ACCRETIVE**, and **TRACEABLE** standards.

- **UNSOUND**: reject unsupported conclusions and label unknowns instead of guessing.
- **MECHANISTIC**: reason through failure mechanisms, contracts, state transitions, blast radius, and side effects.
- **ACCRETIVE**: prefer the narrowest additive change that resolves the real issue without speculative redesign.
- **TRACEABLE**: tie major claims to files, symbols, tests, diffs, commands, logs, or outputs.

Additional orchestration pressures:

- **EXHAUSTIVE**
- **DE NOVO**
- **ADVERSARIAL**
- **SATURATING**
- **MATERIAL**
- **FIXED-POINT**
- **PARSIMONIOUS**
- **INVARIANT-GRADED**
- **HAZARD-SEEKING**
- **CANONICAL**
- **LEDGERIZED**

## Phase selection

1. Start with **`accretive-implementer`** when the task involves implementation, diagnosis, bug fixing, refactoring, or no patch exists yet.
2. Start with **`adversarial-reviewer`** when a diagnosis, plan, or patch already exists and the user wants exhaustive challenge or re-litigation.
3. Use **`verification-closure`** in two ways:
   - **targeted validation subpass** for material evidence gaps or `validating-check-only` findings
   - **final closure pass** for readiness on the current stabilized artifact set
4. Use the **subagent swarm** when the next work is primarily read-heavy: exploration, evidence collection, invariant audit, hazard hunt, complexity grading, or verification audit.
5. Keep remediation single-threaded and reviewable. Do not use concurrent write-heavy subagents.

## Entry-state detection

Before choosing a phase path, classify the task into one of these states:
- no patch yet
- patch in progress
- patch exists
- review only
- verify only

If the user explicitly asks for the full workflow, exhaustive hardening, or full re-litigation, do not collapse the request to a single phase even if one phase appears sufficient at first glance.

## Canonical ledgers

Maintain these ledgers across the whole workflow and refresh them after every meaningful pass:

1. **Findings Ledger**
   - `finding_id`
   - `materiality`
   - `severity`
   - `category`
   - `status`
   - `remediation_posture`
   - `evidence`
   - `why_it_matters`
   - `implicated_surfaces`
   - `impacted_invariants`
   - `next_action`

2. **Invariant Ledger**
   - `invariant_id`
   - `name`
   - `tier`
   - `status`
   - `confidence`
   - `blast_radius`
   - `supporting_evidence`
   - `open_question`

3. **Foot-Gun Register**
   - `hazard_id`
   - `trigger`
   - `impact`
   - `ease_of_misuse`
   - `status`
   - `evidence`
   - `narrowest_bounding_action`

4. **Complexity Ledger**
   - `overall_delta`
   - `materiality`
   - `drivers`
   - `evidence`
   - `bounded_by`

5. **Verification Ledger**
   - `direct_changed_path`
   - `claimed_failure_mechanism`
   - `regression_surface`
   - `checks_run`

6. **Specialist Briefing Ledger**
   - `role`
   - `artifact_state_label`
   - `scope`
   - `top_material_signals`
   - `unresolved_signals`
   - `agreement_pressure`
   - `stale`

7. **Residual Uncertainty**
   - assumptions
   - environment limits
   - known unknowns

Use durable statuses. Do not silently drop or rename fields between phases.

## Packet-native specialist briefings

When subagent mode is active and custom agents are available, require specialist outputs to follow the contract in `references/specialist-briefing-contract.md`.

Rules:
- pass the current `artifact_state_label` into each specialist prompt when possible
- require concise sectioned outputs, not essays
- specialists should emit packet-native fields so the orchestrator mostly reconciles rather than rewrites
- the orchestrator still computes `agreement_pressure` and `stale`
- if a specialist briefing is malformed, repair only the minimum needed and record the repair in the workflow notes

## Specialist subagent swarm

Preferred read-only swarm:
- `evidence_mapper`
- `invariant_auditor`
- `hazard_hunter`
- `complexity_auditor`
- `verification_auditor`

Swarm rules:
- spawn specialists only for read-heavy work
- wait for all relevant results before synthesis
- treat specialists as lenses, not authorities
- after each material validation or remediation, rerun the full-scope swarm in exhaustive subagent mode rather than restricting the next pass to the diff

## Canonical Closure Handoff Packet

Before **every** call to `verification-closure`—both targeted validation and final closure—you must compile a **Closure Handoff Packet** using the exact schema in `references/closure-handoff-contract.md`.

Required rules:
- use the required headings in the required order
- pass the latest version of all ledgers, not free-form prose
- if the artifact set changed after a specialist briefing, mark that briefing `stale: yes`
- if a previously open material issue is no longer open, change its `status` and include the evidence that changed it
- include the exact `Requested Closure Questions` for the next closure pass
- if a field is unknown, write `unknown`; do not omit it

## Signal-aware routing

Use:
- remediation posture
- invariant ledger
- foot-gun register
- complexity ledger
- verification gaps

Routing reference: `references/signal-aware-routing.md`

### Routing intent
- `validating-check-only` -> run the narrowest decisive check first
- `accretive-remediation` -> route to `accretive-implementer` for the narrowest consequential change
- `structural-remediation` -> widen scope only with explicit justification

## Loop rules

- There is **no max-round cap**.
- In exhaustive mode, perform full-scope de novo review, not delta-only review.
- Continue until the artifact set reaches a **material fixed point** or a concrete external blocker makes further progress impossible.
- A material fixed point requires:
  - no unresolved material finding
  - no unresolved critical invariant
  - no unbounded material foot-gun
  - no unresolved material complexity hazard
  - no material verification gap that would reasonably reopen remediation

## Definition of done

The workflow is done only when:
1. the current artifact set reached a material fixed point or a concrete blocker was recorded,
2. the latest ledgers are current,
3. the latest Closure Handoff Packet is canonical and complete enough for closure,
4. `verification-closure` issued a grounded readiness decision.

## Response shape

Use concise sections in this order:
- Workflow
- Current State
- Subagent Mode
- Routing
- Ledgers Updated
- Next Phase
- Closure Handoff
- Fixed-Point Status
- Residual Uncertainty
