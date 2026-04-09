---
name: meta-orchestrator
description: Use this skill to coordinate exhaustive build-review-improve-verify workflows across accretive-implementer, adversarial-reviewer, and verification-closure when a coding task needs full de novo re-litigation, optional read-only specialist subagents, signal-aware routing by invariants foot-guns and complexity, a mandatory pre-closure one-change challenge, and a canonical closure handoff packet that always passes the latest ledgers into verification-closure. Trigger for requests like harden this patch exhaustively, address PR reviews to closure, use subagents for broad review, keep re-reviewing from scratch, find all impactful changes, ask what one thing should still change before merge, or take this to closure with a fixed handoff schema. Do not trigger for trivial one-step tasks or when the user explicitly wants only a single narrow phase.
---

# Meta Orchestrator

This skill coordinates three narrow companion skills:

- `accretive-implementer` for diagnosis and implementation
- `adversarial-reviewer` for skeptical full-scope review
- `verification-closure` for targeted evidence checks and final readiness decisions

It optionally uses a **read-only specialist subagent swarm** for parallel evidence gathering. The orchestrator remains the decider. Specialists supply ledgers and pressure signals; they do not replace the final review or closure judgment.

Default posture: drive the in-scope artifact set to an evidence-backed **material fixed point** through repeated **de novo adversarial re-litigation**, **signal-aware routing**, **accretive remediation by default**, a mandatory **pre-closure one-change challenge**, and a **canonical closure handoff packet** that is refreshed before every validation or closure pass.

## CLI-tail-weighted reporting

Assume the user may only see the last screenful of terminal output.

- Keep intermediate ledgers terse.
- End the final report with **Final State** and **Do Next**.
- **Do Next** must be the last section and name the exact next phase, owning skill, or stop condition.
- When specialists are asked for output, require a one-line routing call at the end.
- Specialist outputs are internal packets, not user-facing final reports: do not ask for or preserve `Echo:`, instruction acknowledgements, or progress-only chatter in specialist results.

## Global doctrine

Every phase inherits **UNSOUND**, **MECHANISTIC**, **ACCRETIVE**, and **TRACEABLE** standards.

- **UNSOUND**: reject unsupported conclusions and label unknowns instead of guessing.
- **MECHANISTIC**: reason through failure mechanisms, contracts, state transitions, blast radius, and side effects.
- **ACCRETIVE**: prefer the narrowest additive change that resolves the real issue without speculative redesign.
- **TRACEABLE**: tie major claims to files, symbols, tests, diffs, commands, logs, or outputs.

Additional orchestration pressures:

- **EXHAUSTIVE**: re-examine the entire in-scope state, not just changed lines.
- **DE NOVO**: each review pass re-adjudicates from the current artifact state rather than inheriting prior conclusions.
- **ADVERSARIAL**: actively try to falsify the diagnosis, break the patch, expose hidden assumptions, and find second-order regressions.
- **SATURATING**: assume later loops may still surface new material issues.
- **MATERIAL**: focus on correctness, safety, security, reliability, compatibility, performance regressions, verification sufficiency, and consequential maintainability risk.
- **FIXED-POINT**: stop only when the current artifact set yields no unresolved material issue under full review and closure verification.
- **PARSIMONIOUS**: treat incidental complexity growth as a first-class signal when it creates fragility, coupling, operational burden, or future hazard.
- **INVARIANT-GRADED**: grade invariants by tier, status, confidence, and blast radius, and route unresolved critical invariants explicitly.
- **HAZARD-SEEKING**: search for foot-guns, misuse paths, unsafe defaults, and silent failure modes even when the happy path works.
- **CANONICAL**: use one stable handoff schema instead of ad hoc summaries.
- **LEDGERIZED**: normalize findings, invariants, hazards, complexity, verification, and specialist signals into explicit ledgers with durable statuses.

## Phase selection

1. Start with **`accretive-implementer`** when the task involves implementation, diagnosis, bug fixing, refactoring, or no patch exists yet.
2. Start with **`adversarial-reviewer`** when a diagnosis, plan, or patch already exists and the user wants exhaustive challenge or re-litigation.
3. Use **`verification-closure`** in two ways:
   - **targeted validation subpass** for material evidence gaps or `validating-check-only` findings
   - **final closure pass** for readiness on the current stabilized artifact set
4. Run the **pre-closure one-change challenge** after a candidate material fixed point and before every final closure attempt.
5. Use the **subagent swarm** when the next work is primarily read-heavy: exploration, evidence collection, invariant audit, hazard hunt, complexity grading, or verification audit.
6. Keep remediation single-threaded and reviewable. Do not use concurrent write-heavy subagents.

## Entry-state detection

Before choosing a phase path, classify the task into one of these states:

- **no patch yet**
- **patch in progress**
- **patch exists**
- **review only**
- **verify only**

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

6. **One-Change Challenge Ledger**
   - `question`
   - `status`
   - `candidate_change`
   - `why_this_one`
   - `routed_to`
   - `evidence`
   - `resulting_state_label`

7. **Specialist Briefing Ledger**
   - `role`
   - `artifact_state_label`
   - `scope`
   - `top_material_signals`
   - `unresolved_signals`
   - `agreement_pressure`
   - `stale`

8. **Residual Uncertainty**
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
- If the artifact set changed after a specialist briefing, mark that briefing `stale: yes`.
- If a previously open material issue is no longer open, change its `status` and include the evidence that changed it.
- Include the exact `Requested Closure Questions` for the next closure pass.
- If a field is unknown, write `unknown`; do not omit it.

Treat the packet as the canonical phase boundary object.

## Specialist subagent swarm

When subagent mode is active and custom agents are available, prefer this parallel read-only swarm:

- `evidence_mapper`: maps the true execution path, affected surfaces, and artifact set
- `invariant_auditor`: enumerates and grades critical, major, and supporting invariants
- `hazard_hunter`: searches for foot-guns, misuse paths, dangerous defaults, and silent hazards
- `complexity_auditor`: grades incidental complexity, coupling, and surface-area growth
- `verification_auditor`: audits whether the verification record directly exercises the changed behavior, failure mechanism, regression surfaces, and critical invariants

Swarm rules:
- Spawn specialists only for read-heavy work.
- Wait for all relevant results before synthesis.
- Ask each specialist for concise ledger-shaped findings that end with a one-line routing call, not essays.
- Treat specialist turns as machine-to-machine handoffs: require packet-native briefing output only, with no `Echo:`, no repo-instructions acknowledgement, and no progress-only commentary.
- If a specialist returns only an instruction acknowledgement, `Echo:`, malformed packet, or other non-briefing output, mark that result invalid, exclude it from evidence, and do not surface it to the user verbatim.
- Normalize every specialist result into the **Specialist Briefing Ledger**.
- Treat specialists as lenses, not authorities.
- If specialist transport is noisy or unreliable, reduce or skip the swarm and continue locally rather than rerunning broad fanout just to restate the same failure.
- In exhaustive subagent mode, after each material validation or remediation, rerun the full-scope swarm over the current artifact set rather than restricting the next pass to the diff.

If custom agents are unavailable, continue single-threaded under the same phase contracts.

## Signal-aware routing

Consume `adversarial-reviewer` outputs explicitly, including:

- remediation posture
- invariant ledger
- foot-gun register
- complexity delta
- verification gaps

Routing rules:

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

Before every **final** `verification-closure` attempt, ask exactly:

> If you could change one thing about this changeset what would you change?

Challenge rules:

- Answer from the perspective of the whole current artifact set, not just the last diff.
- Choose **one** candidate change at most.
- A candidate counts as worth routing only when it is **impactful**: it meaningfully improves correctness, misuse resistance, invariant clarity, verification strength, or consequential maintainability at acceptable churn.
- Cosmetic, preference-only, or merely novel changes do not qualify.
- If the best remaining change is an accretive implementation, route it to **`accretive-implementer`**.
- If the best remaining change requires structural redesign beyond current constraints, record `needs-decision` or `blocked` instead of pretending it is accretive.
- If no remaining change is clearly worth the churn, record `no-impactful-change` and proceed to closure.
- After any implemented one-change improvement, rerun the full de novo review loop; do not jump straight to closure.


## Orchestration algorithm

1. Establish the entry state.
2. Choose the initial phase path:
   - implement only: `accretive-implementer`
   - review only: `adversarial-reviewer`
   - verify only: `verification-closure`
   - implement + exhaustive confidence: `accretive-implementer` -> saturation loop -> pre-closure one-change challenge -> `verification-closure`
   - review + exhaustive verify: saturation loop -> pre-closure one-change challenge -> `verification-closure`
3. Optionally run an initial read-only specialist swarm when the scope is broad or unclear.
4. Run the **saturation loop**:
   - During `accretive-implementer`, produce a grounded diagnosis or integration rationale, the narrowest appropriate remediation or implementation, and first-pass verification.
   - Before each full review pass in subagent mode, run the full-scope specialist swarm, wait for all relevant results, and normalize them into the **Specialist Briefing Ledger**.
   - In subagent mode, fail closed on transport junk: invalid specialist outputs do not count as evidence, and repeated instruction-ack/no-briefing returns are a signal to fall back to local review or a narrower swarm.
   - During `adversarial-reviewer`, perform a **full-scope de novo adversarial review** of the current artifact set. Do not restrict attention to the changed surface.
   - Normalize material findings by remediation posture: `validating-check-only`, `accretive-remediation`, `structural-remediation`.
   - Route the highest-value next action using findings, invariants, foot-guns, complexity, and verification gaps.
   - After any targeted validation or remediation, rerun full-scope review; in subagent mode, rerun the full-scope swarm first.
   - Continue looping until the artifact set reaches a **candidate material fixed point**: no unresolved material finding remains, no unbounded critical invariant remains `broken`, `unknown`, or materially `strained`, no unresolved material foot-gun remains, no unresolved material complexity hazard remains, and no material validation gap would reasonably reopen remediation.
5. Run the **pre-closure one-change challenge** on the latest stabilized artifact set.
   - Ask the exact challenge question.
   - If the result is an impactful accretive change, route it to `accretive-implementer`, record the result in the **One-Change Challenge Ledger**, then return to the saturation loop after the implementation and its first-pass verification.
   - If the result is `needs-decision` or `blocked`, stop in that state with evidence.
   - If the result is `no-impactful-change`, record it and continue.
6. Before **every** `verification-closure` invocation, compile the latest **Closure Handoff Packet** from the current ledgers.
7. Run `verification-closure` against that packet and the current evidence.
8. If `verification-closure` uncovers an open gate:
   - convert the gate into a routed finding or validation task,
   - merge any new gate status back into the ledgers,
   - return to the saturation loop,
   - rerun the pre-closure one-change challenge after the next candidate material fixed point,
   - then compile a fresh packet before the next closure attempt.
9. Stop when one of these states is justified:
   - **blocked**: hard external blocker or missing prerequisite evidence prevents further progress
   - **needs-decision**: a material structural issue or non-accretive highest-leverage change remains and task constraints do not permit the necessary change
   - **needs remediation**: unresolved material issues remain and further work is still possible
   - **conditionally ready**: direct verification succeeded, no unresolved material issue remains, and the latest one-change challenge yielded no impactful accretive improvement, but bounded non-material concerns or environment limits still exist
   - **ready**: the artifact set reached a material fixed point, the latest one-change challenge yielded no impactful accretive improvement, direct verification succeeded, and no unresolved material issue remains

## Companion skill invocation

When supported in the current Codex client, explicitly use these companion skills by name:

- `$accretive-implementer`
- `$adversarial-reviewer`
- `$verification-closure`

If explicit nested skill invocation is not available in the current environment, follow the same phase contracts directly inside this workflow rather than skipping a phase.

## Optional custom agents

When the project defines custom agents, prefer these exact names:

- `evidence_mapper`
- `invariant_auditor`
- `hazard_hunter`
- `complexity_auditor`
- `verification_auditor`

If these custom agents do not exist, do not fail the workflow. Fall back to built-in agents and direct analysis.

## Hard rules

- Never impose an arbitrary maximum number of loops.
- Never terminate the workflow merely because many loops have already occurred.
- Never substitute delta review for full re-litigation when exhaustive mode is requested.
- Never anchor exclusively on prior findings; each review must be de novo against the current state.
- Never let low-consequence style nits prevent closure unless they rise to material risk.
- Never treat passing tests as proof when the changed path or implicated contracts were not directly exercised.
- Never conclude `ready` while any unresolved material issue remains.
- Never leave a material `verification-closure` finding outside the loop; closure must be able to reopen remediation.
- Never skip re-review after a targeted validation subpass or a remediation pass.
- Never force an accretive patch when the evidence says the issue is structural.
- Never let subagent summaries replace direct review judgment.
- Never run multiple write-heavy remediations in parallel.
- Never hand off to `verification-closure` without a fresh **Closure Handoff Packet**.
- Never let stale specialist briefings masquerade as current evidence.
- Never rename or reshape canonical ledger fields ad hoc between phases.
- Never skip the pre-closure one-change challenge before a final closure attempt.
- Never promote a cosmetic or preference-only suggestion as the one remaining change worth doing.
- Never bundle more than one discretionary improvement from the one-change challenge unless a tightly coupled follow-on edit is strictly required.
- Never let a one-change improvement bypass full re-review.

## Definition of done

The workflow is done only when:

1. the in-scope artifact set has reached a **material fixed point** under full de novo adversarial review, or a concrete blocker / decision gate is identified,
2. the latest pre-closure one-change challenge has been run on the stabilized artifact set and either its single impactful change was implemented and re-reviewed or it yielded `no-impactful-change`,
3. direct closure verification has been run on the stabilized artifact set,
4. no unresolved material issue remains,
5. no critical invariant remains unboundedly broken, unknown, or materially strained,
6. no unresolved material foot-gun or material complexity hazard remains,
7. the latest **Closure Handoff Packet** was produced and consumed at the final closure boundary,
8. the final report states why the chosen state is justified and names any residual non-material risks or environment limits.

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
- Subagent Mode
- Routing Summary
- One-Change Challenge
- Closure Handoff Packet
- Residual Risks
- Final State
- Do Next
