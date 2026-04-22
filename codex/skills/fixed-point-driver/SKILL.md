---
name: fixed-point-driver
description: Use this skill to drive build-review-improve-verify workflows toward a material fixed point across accretive-implementer, adversarial-reviewer, and verification-closure with progressive saturation by default, automatic escalation to exhaustive de novo re-litigation when evidence warrants it, optional read-only specialist subagents, signal-aware routing by soundness invariants foot-guns and complexity, a mandatory late pre-closure one-change challenge, unchanged-state closure reuse, and a canonical closure handoff packet that always carries the latest ledgers into verification-closure.
---

# Fixed-Point Driver

This skill drives the changeset toward a material fixed point by coordinating three narrow companion skills:

- `accretive-implementer` for diagnosis and implementation
- `adversarial-reviewer` for skeptical review and re-litigation
- `verification-closure` for targeted evidence checks and final readiness decisions

It optionally uses a read-only specialist subagent swarm for parallel evidence gathering. The fixed-point driver remains the decider and root synthesizer. Specialists supply ledgers and pressure signals; they do not replace direct review or closure judgment.

Default posture: drive the in-scope artifact set to an evidence-backed material fixed point through **progressive saturation**. Start with the narrowest sound closure path that can expose material risk, then automatically escalate to exhaustive saturation whenever the artifact state produces broad, stale, cross-cutting, suspicious, or under-witnessed signals. The user does not have to ask for exhaustion when the evidence warrants it.

## CLI-tail-weighted reporting

Assume the user may only see the last screenful of terminal output.

- Keep intermediate ledgers terse.
- End the final report with **Final State** and **Do Next**.
- **Do Next** must be the last section and name the exact next phase, owning skill, or stop condition.
- When specialists are asked for output, require a one-line routing call at the end.

## Global doctrine

Every phase inherits **UNSOUND**, **WITNESS-BEARING**, **PRESERVATION-AWARE**, **PROGRESS-AWARE**, **REFINEMENT-AWARE**, **MECHANISTIC**, **ACCRETIVE**, and **TRACEABLE** standards.

- **UNSOUND**: reject unsupported conclusions and label unknowns instead of guessing.
- **WITNESS-BEARING**: require a concrete witness for every material claim; tests only witness the specific behavior they exercise.
- **PRESERVATION-AWARE**: route on whether critical guarantees survive transformations, retries, persistence hops, and boundary crossings.
- **PROGRESS-AWARE**: treat stuck, half-valid, or impossible states as material soundness pressure.
- **REFINEMENT-AWARE**: prefer boundaries that narrow raw values early and keep validated states explicit.
- **MECHANISTIC**: reason through failure mechanisms, contracts, state transitions, blast radius, and side effects.
- **ACCRETIVE**: prefer the narrowest additive change that resolves the real issue without speculative redesign.
- **TRACEABLE**: tie major claims to files, symbols, tests, diffs, commands, logs, or outputs.

Additional orchestration pressures:

- **PROGRESSIVELY SATURATING**: use the cheapest sound closure path first, but escalate automatically as evidence demands.
- **EXHAUSTIVE WHEN TRIGGERED**: re-examine the entire in-scope state, not just changed lines, whenever escalation triggers require saturation.
- **DE NOVO**: each review pass re-adjudicates from the current artifact state rather than inheriting prior conclusions.
- **ADVERSARIAL**: actively try to falsify the diagnosis, break the patch, expose hidden assumptions, and find second-order regressions.
- **MATERIAL**: focus on correctness, safety, security, reliability, compatibility, performance regressions, verification sufficiency, and consequential maintainability risk.
- **FIXED-POINT**: stop only when the current artifact set yields no unresolved material issue under the required review and closure verification for its escalation state.
- **PARSIMONIOUS**: treat incidental complexity growth as a first-class signal when it creates fragility, coupling, operational burden, or future hazard.
- **INVARIANT-GRADED**: grade invariants by tier, status, confidence, and blast radius, and route unresolved critical invariants explicitly.
- **HAZARD-SEEKING**: search for foot-guns, misuse paths, unsafe defaults, and silent failure modes even when the happy path works.
- **CANONICAL**: use one stable handoff schema instead of ad hoc summaries.
- **LEDGERIZED**: normalize findings, soundness claims, invariants, hazards, complexity, verification, one-change results, and specialist signals into explicit ledgers with durable statuses.

## Progressive saturation

The fixed-point driver must not require the user to explicitly request exhaustion. Its default obligation is material fixed-point closure.

Start with the narrowest sound closure path that can expose material risk: local diagnosis, direct evidence, targeted adversarial review, and focused verification. Escalate without asking the user when any material trigger appears. Do not run full saturation merely because the skill is active.

### Escalation levels

- **Level 0 — local closure pass**
  - Use for narrow, seeded, or already-bounded changes.
  - Run local diagnosis, direct proof, targeted checks, and a focused de novo adversarial review of the implicated surfaces.
  - Do not spawn a full specialist swarm.
- **Level 1 — focused adversarial closure**
  - Use when material uncertainty exists but the affected surface is still bounded.
  - Add one or two focused read-only lenses, update ledgers, and re-review the implicated surfaces de novo.
  - Use targeted validation for specific missing witnesses before broad remediation.
- **Level 2 — exhaustive saturation**
  - Use when escalation triggers show broad, stale, cross-cutting, suspicious, or unstable risk.
  - Run the full specialist swarm when available, full-scope de novo review, full ledger normalization, one-change challenge, closure handoff packet, and verification-closure loop.

The driver may move upward without user confirmation. The driver may not move downward while an unresolved material escalation trigger remains. Level 0 and Level 1 are cost controls, not rigor opt-outs.

### Automatic escalation triggers

Escalate to Level 1 or Level 2 when any of these signals appears:

- scope is broad, unclear, or touches multiple contracts
- local review finds cross-cutting invariant pressure
- a critical invariant is unknown, strained, stale, or under-witnessed
- verification does not directly exercise the changed behavior or failure mechanism
- a plausible regression surface lacks a direct witness
- a soundness claim depends on stale, partial, contradictory, or missing evidence
- a hazard, foot-gun, or misuse path has meaningful blast radius
- a clean review feels suspicious because evidence is thin, inherited, or mostly indirect
- remediation changes artifact shape enough to stale prior review
- repeated closure attempts reopen material findings
- incidental complexity growth creates concrete fragility, coupling, operational burden, or future hazard
- the user explicitly asks for exhaustive hardening, full re-litigation, subagents, or all impactful changes

Do not ask the user whether to escalate. Escalate when the evidence demands it.

## Phase selection

1. Start with **`accretive-implementer`** when the task involves implementation, diagnosis, bug fixing, refactoring, or no patch exists yet.
2. Start with **`adversarial-reviewer`** when a diagnosis, plan, or patch already exists and the user wants challenge, re-litigation, or review to closure.
3. Use **`verification-closure`** in two ways:
   - **targeted validation subpass** for material evidence gaps or `validating-check-only` findings
   - **final closure pass** for readiness on the current stabilized artifact set
4. Run the **pre-closure one-change challenge** only after a candidate material fixed point and before every final closure attempt.
5. Use focused read-only lenses or the full subagent swarm according to the current escalation level.
6. Keep remediation single-threaded and reviewable. Do not use concurrent write-heavy subagents.

## Entry-state detection

Before choosing a phase path, classify the task into one of these states:

- **no patch yet**
- **patch in progress**
- **patch exists**
- **review only**
- **verify only**

If the user explicitly asks for the full workflow, exhaustive hardening, or full re-litigation, do not collapse the request to a single phase even if one phase appears sufficient at first glance. If the user simply asks for closure, do not require magic words for exhaustion; apply progressive saturation and escalate automatically as triggers appear.

## Canonical ledgers

Maintain these ledgers across the whole workflow and refresh them after every meaningful pass:

1. **Escalation Ledger**
   - `level`: `0-local` | `1-focused` | `2-exhaustive`
   - `active_triggers`
   - `resolved_triggers`
   - `why_this_level_is_sufficient_or_required`
   - `last_escalation_decision`
2. **Findings Ledger**
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
3. **Soundness Ledger**
   - `claim_id`
   - `claim_or_obligation`
   - `kind`
   - `witness_required`
   - `witness_status`
   - `preservation`
   - `progress`
   - `inhabitance`
   - `evidence`
   - `next_action`
4. **Invariant Ledger**
   - `invariant_id`
   - `name`
   - `tier`
   - `status`
   - `confidence`
   - `blast_radius`
   - `supporting_evidence`
   - `open_question`
5. **Foot-Gun Register**
   - `hazard_id`
   - `trigger`
   - `impact`
   - `ease_of_misuse`
   - `status`
   - `evidence`
   - `narrowest_bounding_action`
6. **Complexity Ledger**
   - `overall_delta`
   - `materiality`
   - `drivers`
   - `evidence`
   - `bounded_by`
7. **Verification Ledger**
   - `direct_changed_path`
   - `claimed_failure_mechanism`
   - `regression_surface`
   - `checks_run`
8. **One-Change Challenge Ledger**
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
9. **Specialist Briefing Ledger**
   - `role`
   - `artifact_state_label`
   - `scope`
   - `top_material_signals`
   - `unresolved_signals`
   - `agreement_pressure`
   - `stale`
10. **Residual Uncertainty**
    - assumptions
    - environment limits
    - known unknowns

Use durable statuses. Do not silently drop or rename fields between phases.

Record the most recent pre-closure one-change challenge in the **One-Change Challenge Ledger** and also mirror it into the **Change Ledger** as a `review` pass for handoff traceability, even when it yields no code changes.

## Canonical Closure Handoff Packet

Before **every** call to `verification-closure`—both targeted validation and final closure—you must compile a **Closure Handoff Packet** using the exact schema in `references/closure-handoff-contract.md`.

Required rules:

- Use the required headings in the required order.
- Pass the latest version of all ledgers, not free-form prose.
- Include the current escalation level and active or resolved escalation triggers.
- Include the one-change challenge ledger for final closure packets.
- If the artifact set changed after a specialist briefing, mark that briefing `stale: yes`.
- If a previously open material issue is no longer open, change its `status` and include the evidence that changed it.
- Include the exact `Requested Closure Questions` for the next closure pass.
- If a field is unknown, write `unknown`; do not omit it.
- Treat unchanged-state reuse as a freshness mode, not as permission to use stale evidence.

Treat the packet as the canonical phase boundary object.

## Unchanged-state closure reuse

If `artifact_state_label`, diff, relevant evidence, ledgers, specialist freshness, and requested closure questions are unchanged since the last closure attempt, do not rerun the whole ritual merely to refresh ceremony.

Unchanged-state reuse requires all of the following:

- no artifact changes since the previous packet
- no new material finding, invariant pressure, foot-gun, complexity hazard, or verification gap
- no stale specialist briefing that is being used as current evidence
- no open requested closure question whose answer would change under the current evidence
- one clean re-review for stale assumptions
- any missing focused witness that was already identified must either be supplied or remain an explicit gate

When reuse is valid, compile a packet with `Closure Freshness` set to `unchanged-state-reuse`, include the reused state label, and name the stale-assumption recheck that was just performed. Do not rerun the full specialist swarm solely because a handoff packet is required.

## Specialist subagent swarm

Use specialist agents as evidence lenses, not as a mandatory ritual. Match the agent pattern to the escalation level.

- **Level 0**: no full swarm; direct local review is expected.
- **Level 1**: use one or two focused read-only lenses when they can materially reduce uncertainty.
- **Level 2**: run the full read-only swarm when custom agents or built-in subagents are available.

When Level 2 subagent mode is active and custom agents are available, prefer this parallel read-only swarm:

- `evidence_mapper`: maps the true execution path, affected surfaces, and artifact set
- `soundness_auditor`: audits witnesses, preservation, progress, impossible states, partial elimination, and overclaim risk
- `invariant_auditor`: enumerates and grades critical, major, and supporting invariants
- `hazard_hunter`: searches for foot-guns, misuse paths, dangerous defaults, and silent hazards
- `complexity_auditor`: grades incidental complexity, coupling, and surface-area growth
- `verification_auditor`: audits whether the verification record directly exercises the changed behavior, failure mechanism, regression surfaces, and critical invariants

Swarm rules:

- Spawn specialists only for read-heavy work.
- Wait for all relevant results before synthesis.
- Ask each specialist for concise ledger-shaped findings that end with a one-line routing call, not essays.
- Normalize every specialist result into the **Specialist Briefing Ledger**.
- Treat specialists as lenses, not authorities.
- In Level 2 exhaustive subagent mode, after each material validation or remediation that changes the artifact state, rerun the full-scope swarm over the current artifact set unless unchanged-state reuse is valid.

If custom agents are unavailable, continue single-threaded under the same phase contracts.

## Root synthesis contract

Do not invent a separate coordinator topology. The fixed-point driver is the root synthesizer:

- it chooses the current escalation level,
- routes work to companion skills or read-only specialists,
- normalizes outputs into canonical ledgers,
- decides whether escalation is required,
- decides whether the artifact set is at a candidate material fixed point,
- and owns the closure handoff packet.

When a Codex client exposes `spawn_agent` or equivalent primitives, use them only as read-only lenses under this root-synthesis contract.

## Signal-aware routing

Consume `adversarial-reviewer` outputs explicitly, including:

- remediation posture
- soundness ledger
- invariant ledger
- foot-gun register
- complexity delta
- verification gaps

Routing rules:

### Soundness

- A material claim with a missing, stale, partial, or contradictory witness remains open until directly bounded.
- A preservation break across transformation, persistence, retry, boundary crossing, or state transition is material when it can affect correctness, safety, security, reliability, or compatibility.
- Stuck states, half-valid states, impossible admitted states, and partial elimination usually route to `accretive-remediation` when local and `structural-remediation` when inherent to the abstraction.
- Overclaims route to narrower claims, direct witnesses, or explicit residual uncertainty.

### Invariants

- Any **critical** invariant with status `broken` is material and prevents fixed-point closure.
- Any **critical** invariant with status `unknown` or materially `strained` is a material gate unless directly bounded by evidence and judged non-consequential.
- Cross-cutting or contract-level invariant breakage often implies `structural-remediation`.
- Localized invariant breakage with a narrow causal fix usually implies `accretive-remediation`.
- Unknown critical invariants usually route to `validating-check-only` first unless current evidence already proves breakage.

### Foot-guns

- A foot-gun is material when impact is meaningful and misuse is easy, subtle, or silent.
- Public API traps, dangerous defaults, destructive ambiguity, silent fallback, partial-failure traps, retry hazards, reentrancy hazards, and hidden global state often count as material even when happy-path tests pass.
- If the narrowest fix is validation, naming, API guardrails, or direct erroring, route as `accretive-remediation`.
- If the misuse risk is inherent to the current abstraction or contract surface, route as `structural-remediation`.
- If the hazard is plausible but not yet evidenced, route as `validating-check-only`.

### Complexity

- An overall delta of `increases` is material when the increase is primarily incidental and creates concrete fragility, coupling, operational burden, or future hazard.
- Cross-cutting growth in control-flow, hidden state, coupling, API surface, config surface, or operational surface often indicates a structural issue.
- Localized complexity growth that meaningfully improves correctness, invariant preservation, or hazard reduction can remain non-material when justified and bounded.

### Verification

A verification gap is material when:

- the changed behavior was not directly checked,
- the claimed failure mechanism was not exercised,
- a plausible regression surface was not checked,
- or a critical invariant still lacks direct support.

## Pre-closure one-change challenge

Before every **final** `verification-closure` attempt, and only after a candidate material fixed point, ask exactly:

> If you could change one thing about this changeset what would you change?

Late-only gate:

- Do not ask the challenge while material findings, validation gaps, unbounded critical invariants, unresolved material foot-guns, or material complexity hazards are still open.
- Do not use the challenge as early brainstorming.
- Do not repeat the challenge when unchanged-state reuse is valid and the latest challenge already applies to the unchanged artifact state.

Challenge rules:

- Answer from the perspective of the whole current artifact set, not just the last diff.
- Choose **one** candidate change at most.
- A candidate counts as worth routing only when it is **impactful**: it meaningfully improves correctness, misuse resistance, invariant clarity, verification strength, or consequential maintainability at acceptable churn.
- Cosmetic, preference-only, or merely novel changes do not qualify.
- If the best remaining change is an accretive implementation, route it to **`accretive-implementer`**.
- If the best remaining change requires structural redesign beyond current constraints, record `needs-decision` or `blocked` instead of pretending it is accretive.
- If the best remaining change is real but adjacent to this task's scope, record `deferred-adjacent` with evidence instead of reopening the task.
- If no remaining change is clearly worth the churn, record `no-impactful-change` and proceed to closure.
- After any implemented one-change improvement, rerun the required de novo review loop for the current escalation level; do not jump straight to closure.

Structured result fields:

- `outcome`: `unknown` | `implemented` | `no-impactful-change` | `needs-decision` | `blocked`
- `acceptance`: `unknown` | `accepted-now` | `deferred-adjacent` | `rejected-scope` | `rejected-nonmaterial`
- `artifact_state_before`
- `artifact_state_after`

For final closure packets, `outcome` and `acceptance` must no longer be `unknown`; targeted-validation packets may use `unknown` while the challenge is legitimately not yet runnable.

## Orchestration algorithm

1. Establish the entry state.
2. Initialize the **Escalation Ledger** at the narrowest sound level that can expose material risk.
3. Choose the initial phase path:
   - implement only: `accretive-implementer`
   - review only: `adversarial-reviewer`
   - verify only: `verification-closure`
   - closure workflow: progressive saturation loop -> pre-closure one-change challenge -> `verification-closure`
   - explicit exhaustive hardening: Level 2 saturation loop -> pre-closure one-change challenge -> `verification-closure`
4. Run the **progressive saturation loop**:
   - During `accretive-implementer`, produce a grounded diagnosis or integration rationale, the narrowest appropriate remediation or implementation, and first-pass verification.
   - During local or focused review, perform de novo adversarial review over the implicated surfaces and any untouched surfaces needed to judge the contract.
   - At each pass, evaluate automatic escalation triggers and update the **Escalation Ledger**.
   - If Level 1 is active, use targeted read-only lenses for the highest-value uncertainty.
   - If Level 2 is active and subagent mode is available, run the full-scope specialist swarm before full review, wait for relevant results, and normalize them into the **Specialist Briefing Ledger**.
   - During `adversarial-reviewer`, perform the required de novo adversarial review for the current escalation level. In Level 2, review the full in-scope artifact set; do not restrict attention to the changed surface.
   - Normalize material findings by remediation posture: `validating-check-only`, `accretive-remediation`, `structural-remediation`.
   - Route the highest-value next action using findings, soundness claims, invariants, foot-guns, complexity, and verification gaps.
   - After any targeted validation or remediation, rerun the required de novo review for the current escalation level; if Level 2 subagent mode is active, rerun the full-scope swarm first unless unchanged-state reuse is valid.
   - Continue looping until the artifact set reaches a **candidate material fixed point**: no unresolved material finding remains, no unbounded critical invariant remains `broken`, `unknown`, or materially `strained`, no unresolved material foot-gun remains, no unresolved material complexity hazard remains, no material soundness claim lacks a direct or explicitly bounded witness, and no material validation gap would reasonably reopen remediation.
5. Run the **pre-closure one-change challenge** on the latest stabilized artifact set unless unchanged-state reuse proves that the previous challenge still applies.
   - Ask the exact challenge question.
   - If the result is an impactful accretive change, route it to `accretive-implementer`, record the result in the **One-Change Challenge Ledger**, then return to the saturation loop after the implementation and its first-pass verification.
   - If the result is `needs-decision` or `blocked`, stop in that state with evidence.
   - If the result is `deferred-adjacent`, `rejected-scope`, `rejected-nonmaterial`, or `no-impactful-change`, record it and continue when no material gate remains.
6. Before **every** `verification-closure` invocation, compile the latest **Closure Handoff Packet** from the current ledgers.
7. Run `verification-closure` against that packet and the current evidence.
8. If `verification-closure` uncovers an open gate:
   - convert the gate into a routed finding or validation task,
   - merge any new gate status back into the ledgers,
   - reevaluate escalation triggers,
   - return to the saturation loop,
   - rerun the pre-closure one-change challenge after the next candidate material fixed point unless unchanged-state reuse applies,
   - then compile a fresh packet before the next closure attempt.
9. Stop when one of these states is justified:
   - **blocked**: hard external blocker or missing prerequisite evidence prevents further progress
   - **needs-decision**: a material structural issue or non-accretive highest-leverage change remains and task constraints do not permit the necessary change
   - **needs remediation**: unresolved material issues remain and further work is still possible
   - **conditionally ready**: direct verification succeeded, no unresolved material issue remains, the required review level has no unresolved escalation trigger, and the latest applicable one-change challenge yielded no impactful accretive improvement, but bounded non-material concerns or environment limits still exist
   - **ready**: the artifact set reached a material fixed point, the latest applicable one-change challenge yielded no impactful accretive improvement, direct verification succeeded, no unresolved material issue remains, and no escalation trigger remains unresolved

## Companion skill invocation

When supported in the current Codex client, explicitly use these companion skills by name:

- `$accretive-implementer`
- `$adversarial-reviewer`
- `$verification-closure`

If explicit nested skill invocation is not available in the current environment, follow the same phase contracts directly inside this workflow rather than skipping a phase.

## Optional custom agents

When the project defines custom agents, prefer these exact names:

- `evidence_mapper`
- `soundness_auditor`
- `invariant_auditor`
- `hazard_hunter`
- `complexity_auditor`
- `verification_auditor`

If these custom agents do not exist, do not fail the workflow. Fall back to built-in agents and direct analysis.

## Hard rules

- Never require the user to request exhaustive mode when material evidence warrants it.
- Never run full saturation merely because the skill is active; full saturation requires an escalation trigger or explicit user request.
- Never impose an arbitrary maximum number of loops.
- Never terminate the workflow merely because many loops have already occurred.
- Never substitute delta review for full re-litigation when Level 2 is active or exhaustive mode is requested.
- Never anchor exclusively on prior findings; each review must be de novo against the current state.
- Never let low-consequence style nits prevent closure unless they rise to material risk.
- Never treat passing tests as proof when the changed path or implicated contracts were not directly exercised.
- Never conclude `ready` while any unresolved material issue remains.
- Never leave a material `verification-closure` finding outside the loop; closure must be able to reopen remediation.
- Never skip required re-review after a targeted validation subpass or a remediation pass.
- Never force an accretive patch when the evidence says the issue is structural.
- Never let subagent summaries replace direct review judgment.
- Never run multiple write-heavy remediations in parallel.
- Never hand off to `verification-closure` without a current **Closure Handoff Packet**.
- Never use unchanged-state reuse if artifact state, diff, material evidence, ledgers, specialist freshness, or requested closure questions changed.
- Never let stale specialist briefings masquerade as current evidence.
- Never rename or reshape canonical ledger fields ad hoc between phases.
- Never ask the pre-closure one-change challenge before a candidate material fixed point.
- Never skip the pre-closure one-change challenge before a final closure attempt unless unchanged-state reuse proves the latest challenge still applies.
- Never promote a cosmetic or preference-only suggestion as the one remaining change worth doing.
- Never bundle more than one discretionary improvement from the one-change challenge unless a tightly coupled follow-on edit is strictly required.
- Never let a one-change improvement bypass required de novo re-review.

## Definition of done

The workflow is done only when:

1. the in-scope artifact set has reached a **material fixed point** under the required de novo adversarial review level, or a concrete blocker / decision gate is identified,
2. any active escalation trigger has either been resolved, explicitly bounded, or escalated to Level 2 saturation,
3. the latest applicable pre-closure one-change challenge has been run on the stabilized artifact set and either its single impactful change was implemented and re-reviewed or it yielded a non-reopening outcome,
4. direct closure verification has been run on the stabilized artifact set,
5. no unresolved material issue remains,
6. no critical invariant remains unboundedly broken, unknown, or materially strained,
7. no material soundness claim lacks a direct or explicitly bounded witness,
8. no unresolved material foot-gun or material complexity hazard remains,
9. the latest **Closure Handoff Packet** was produced and consumed at the final closure boundary,
10. the final report states why the chosen state is justified and names any residual non-material risks or environment limits.

### Do Next

The final section must say:

- `owner`: skill | user | none
- `action`: exact next phase, stop action, or `none`
- `why`: one sentence
- `state`: ready | conditionally ready | needs remediation | needs-decision | blocked

## Final report shape

Use concise sections:

- Workflow
- Entry State
- Escalation Level
- Subagent Mode
- Routing Summary
- One-Change Challenge
- Closure Handoff Packet
- Residual Risks
- Final State
- Do Next
