---
name: meta-orchestrator
description: Use this skill to coordinate iterative execution across rigor-doctrine, adversarial-reviewer, and verification-closure when a coding task needs exhaustive discovery of material issues, full de novo re-litigation after every validation or remediation step, and explicit routing based on reviewer remediation posture (validating-check-only, accretive-remediation, structural-remediation) until the in-scope artifact set reaches a material fixed point. Trigger for requests like harden this patch exhaustively, keep re-reviewing from scratch after every check or fix, find all impactful changes, take this through build-review-verify until nothing materially new emerges, or route reviewer findings intelligently instead of treating every issue as code change. Do not trigger for trivial one-step tasks or when the user explicitly wants only a single narrow phase.
---

# Meta Orchestrator

This skill coordinates three narrow companion skills:

- `rigor-doctrine` for diagnosis and implementation
- `adversarial-reviewer` for skeptical full-scope review
- `verification-closure` for targeted evidence checks and final readiness decisions

Default posture: drive the in-scope artifact set to an evidence-backed **material fixed point** through repeated **de novo adversarial re-litigation**, explicit **remediation-posture routing**, and **accretive remediation by default**. When exhaustive mode is requested, do not substitute delta review for full review.

## Global doctrine

Every phase inherits **UNSOUND**, **MECHANISTIC**, **ACCRETIVE**, and **TRACEABLE** standards.

- **UNSOUND**: reject unsupported conclusions and label unknowns instead of guessing.
- **MECHANISTIC**: reason through failure mechanisms, contracts, state transitions, blast radius, and side effects.
- **ACCRETIVE**: prefer the narrowest additive change that resolves the real issue without speculative redesign.
- **TRACEABLE**: tie major claims to files, symbols, tests, diffs, commands, logs, or outputs.

Additional orchestration pressures:

- **EXHAUSTIVE**: re-examine the entire in-scope state, not just changed lines or previously flagged surfaces.
- **DE NOVO**: each review pass re-adjudicates from the current artifact state rather than inheriting prior conclusions by default.
- **ADVERSARIAL**: actively try to falsify the diagnosis, break the patch, expose hidden assumptions, and find second-order regressions.
- **SATURATING**: assume later loops may surface new material issues; continue until a full pass adds nothing materially new.
- **MATERIAL**: focus on correctness, safety, security, reliability, compatibility, performance regressions, verification sufficiency, and consequential maintainability risks; do not let low-consequence style nits drive the loop.
- **FIXED-POINT**: stop only when the current in-scope artifact set yields no new material findings under full de novo review and closure verification.

## When to use which phase

1. Start with **`rigor-doctrine`** when the task involves implementation, diagnosis, bug fixing, refactoring, or no patch exists yet.
2. Start with **`adversarial-reviewer`** when a diagnosis, plan, or patch already exists and the user wants exhaustive challenge, re-litigation, or red-teaming.
3. Use **`verification-closure`** in two ways:
   - **targeted validation subpass** for material `validating-check-only` findings
   - **final closure pass** for readiness on the current stabilized artifact set
4. Run the **full chain** when the request implies end-to-end completion, merge readiness, exhaustive hardening, or full-scope iterative review.

## Entry-state detection

Before choosing a phase path, classify the task into one of these states:

- **no patch yet**
- **patch in progress**
- **patch exists**
- **review only**
- **verify only**

If the user explicitly asks for the whole workflow, exhaustive hardening, or full re-litigation, do not collapse the request to a single phase even if one phase appears sufficient at first glance.

## Handoff protocol

Before switching phases, carry forward:

- objective and requested behavior
- scope and constraints
- likely diagnosis or current design rationale
- changed files, symbols, commands run, and relevant outputs
- invariants and contracts that must still hold
- verification evidence already collected
- prior findings and their status
- residual uncertainty

When carrying findings from `adversarial-reviewer`, preserve this ledger per finding:

- materiality
- severity
- category
- evidence
- why it matters
- implicated surfaces
- remediation posture: `validating-check-only` | `accretive-remediation` | `structural-remediation`
- narrowest remediation or validating check
- current status: open | disproved | remediated | needs-decision | blocked

Later phases should reuse grounded evidence, but **review judgments must be re-derived de novo from the current state** rather than merely rubber-stamping earlier conclusions.

## Remediation-posture routing

Consume `adversarial-reviewer` findings explicitly.

### `validating-check-only`
Route to a targeted validation subpass using **`verification-closure` discipline**.

Use this route when the reviewer says the next highest-value action is evidence collection rather than code change.

Rules:
- perform the narrowest high-signal check that can confirm or falsify the concern
- do not edit code before the validating check unless the user explicitly requests immediate remediation despite incomplete evidence
- if the check disproves the concern, mark the finding `disproved`
- if the check confirms a material issue or reveals a stronger failure mode, update the evidence ledger and re-run **full-scope de novo `adversarial-reviewer`** before deciding whether the issue is now `accretive-remediation` or `structural-remediation`
- do not skip re-review after a targeted validation subpass

### `accretive-remediation`
Route to **`rigor-doctrine`** constrained to the narrowest consequential remediation.

Rules:
- batch compatible findings only when they share a mechanism or surface and the bundle remains reviewable
- preserve contracts unless the task explicitly changes behavior
- after remediation, record what changed and what was re-verified
- then re-run **full-scope de novo `adversarial-reviewer`**

### `structural-remediation`
Route to **`rigor-doctrine`** with an explicit structural-remediation brief.

Use this route only when the reviewer has justified why accretive remediation is insufficient.

Rules:
- state the structural reason the narrower fix fails
- bound the broadened scope as tightly as the structural issue allows
- keep redesign limited to what is necessary to close the material finding
- if explicit task constraints forbid the necessary structural change, do not paper over the issue with an inadequate narrow patch; surface `needs-decision` or `blocked` with evidence
- after structural remediation, re-run **full-scope de novo `adversarial-reviewer`**

### Mixed posture findings
If a pass yields multiple material findings with different remediation postures:

1. Resolve `validating-check-only` findings first when they could falsify, narrow, or reprioritize higher-cost remediation.
2. Otherwise remediate the highest-confidence highest-severity material finding first.
3. Bundle compatible `accretive-remediation` findings when that reduces churn without hiding causality.
4. Do not bury a confirmed structural issue behind unrelated accretive cleanup.
5. After any validating check or remediation, re-run **full-scope de novo `adversarial-reviewer`** over the entire in-scope artifact set.

## Orchestration algorithm

1. Establish the entry state.
2. Choose the initial phase path:
   - implement only: `rigor-doctrine`
   - review only: `adversarial-reviewer`
   - verify only: `verification-closure`
   - implement + exhaustive confidence: `rigor-doctrine` -> saturation loop -> `verification-closure`
   - review + exhaustive verify: saturation loop -> `verification-closure`
3. Run the **saturation loop**:
   - During `rigor-doctrine`, produce a grounded diagnosis, the narrowest appropriate remediation, and first-pass verification.
   - During `adversarial-reviewer`, perform a **full-scope de novo adversarial review** of the current in-scope artifact set. Do not restrict attention to the changed surface.
   - Normalize material findings by remediation posture: `validating-check-only`, `accretive-remediation`, `structural-remediation`.
   - If any open `validating-check-only` finding is currently the highest-value next action, run a targeted validation subpass, update the evidence ledger, and then re-run **full-scope de novo `adversarial-reviewer`**.
   - If open `accretive-remediation` findings remain, run `rigor-doctrine` on the narrowest consequential remediation set, then re-run **full-scope de novo `adversarial-reviewer`**.
   - If open `structural-remediation` findings remain, run `rigor-doctrine` with an explicit structural brief or surface `needs-decision` / `blocked` if constraints forbid the required change, then re-run **full-scope de novo `adversarial-reviewer`** if remediation occurred.
   - Continue looping until the artifact set reaches a **material fixed point**: a full de novo adversarial review yields no unresolved material findings, no material severity upgrades, no newly implicated surfaces requiring change, and no material validation gap that would reasonably reopen remediation.
4. Run `verification-closure` against the stabilized artifact set.
5. If `verification-closure` uncovers a material gap, route it the same way:
   - evidence-only gap -> targeted validation subpass -> full de novo re-review
   - fixable narrow defect -> `rigor-doctrine` accretive remediation -> full de novo re-review
   - structural defect -> `rigor-doctrine` structural remediation or `needs-decision` / `blocked`
   - after any closure-triggered action, return to the saturation loop before attempting final closure again
6. Stop when one of these states is justified:
   - **blocked**: hard external blocker or missing prerequisite evidence prevents further progress
   - **needs-decision**: a material structural issue remains and the current task constraints do not permit the necessary change
   - **needs remediation**: unresolved material issues remain and further work is still possible
   - **conditionally ready**: direct verification succeeded and no unresolved material issues remain, but bounded non-material concerns or environment limits still exist
   - **ready**: the artifact set reached a material fixed point, direct verification succeeded, and no unresolved material issue remains

## Companion skill invocation

When supported in the current Codex client, explicitly use these companion skills by name:

- `$rigor-doctrine`
- `$adversarial-reviewer`
- `$verification-closure`

If explicit nested skill invocation is not available in the current environment, follow the same phase contracts directly inside this workflow rather than skipping a phase.

## Phase rules

### Build phase (`rigor-doctrine`)
- Diagnose before editing.
- Prefer the smallest accretive fix that resolves the current material issue without speculative redesign.
- Preserve existing contracts unless the task explicitly changes behavior.
- Produce a clear first-pass verification record after each remediation.
- When invoked for `structural-remediation`, state why the broader change is necessary and keep the redesign bounded.

### Review phase (`adversarial-reviewer`)
- Re-adjudicate the current artifact state de novo.
- Pressure-test the diagnosis, patch, and verification record.
- Search for unsound assumptions, invariant breaks, regression risk, hidden blast radius, stale reasoning, untested branches, and second-order effects.
- Emit findings using the remediation-posture ledger so routing is explicit rather than implied.

### Validation / closure phase (`verification-closure`)
- For targeted validation, run the narrowest high-signal check that can confirm or falsify the open concern.
- For final closure, verify the changed behavior directly and check at least one plausible regression or contract surface.
- Classify readiness using evidence, not tone.
- Reopen the loop if material verification gaps remain.

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
- Never let the orchestrator become a monolith; each phase should stay narrow and explicit.

## Definition of done

The workflow is done only when:

1. the in-scope artifact set has reached a **material fixed point** under full de novo adversarial review, or a concrete external blocker / decision gate is identified,
2. direct closure verification has been run on the stabilized artifact set,
3. no unresolved material issue remains,
4. the final report states why the chosen state is justified and names any residual non-material risks or environment limits.

## Final report shape

Use concise sections:

- Workflow
- Entry State
- Routing
- Iteration Status
- Findings / Changes
- Evidence
- Fixed-Point Test
- Final Readiness
- Remaining Non-Material Risks
