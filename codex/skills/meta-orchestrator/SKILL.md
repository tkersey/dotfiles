---
name: meta-orchestrator
description: Use this skill to coordinate iterative execution across rigor-doctrine, adversarial-reviewer, and verification-closure when a coding task needs exhaustive discovery of material issues, full de novo re-litigation after each remediation, and readiness only at a material fixed point. Trigger for requests like harden this patch exhaustively, keep iterating until no new material issues emerge, take this all the way to adversarial closure, or do the whole build-review-verify loop with full re-review each time. Do not trigger for trivial one-step tasks or when the user explicitly wants only a single narrow phase.
---

# Meta Orchestrator

This skill coordinates three narrow companion skills:

- `rigor-doctrine` for diagnosis and implementation
- `adversarial-reviewer` for skeptical full-scope review
- `verification-closure` for final readiness decisions

Default posture: drive the in-scope artifact set to an evidence-backed **material fixed point** through repeated **de novo adversarial re-litigation** and **accretive remediation**. When exhaustive mode is requested, do not substitute delta review for full review.

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
- **MATERIAL**: focus on correctness, safety, reliability, compatibility, performance regressions, verification sufficiency, and consequential maintainability risks; do not let low-consequence style nits drive the loop.
- **FIXED-POINT**: stop only when the current in-scope artifact set yields no new material findings under full de novo review and closure verification.

## When to use which phase

1. Start with **`rigor-doctrine`** when the task involves implementation, diagnosis, bug fixing, refactoring, or no patch exists yet.
2. Start with **`adversarial-reviewer`** when a diagnosis, plan, or patch already exists and the user wants exhaustive challenge, re-litigation, or red-teaming.
3. Start with **`verification-closure`** only when the user wants proof of readiness for an already-stabilized patch.
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

Later phases should reuse grounded evidence, but **review judgments must be re-derived de novo from the current state** rather than merely rubber-stamping earlier conclusions.

## Orchestration algorithm

1. Establish the entry state.
2. Choose the initial phase path:
   - implement only: `rigor-doctrine`
   - review only: `adversarial-reviewer`
   - verify only: `verification-closure`
   - implement + exhaustive confidence: `rigor-doctrine` -> iterative hardening loop -> `verification-closure`
   - review + exhaustive verify: iterative hardening loop -> `verification-closure`
3. Run the **iterative hardening loop**:
   - During `rigor-doctrine`, produce a grounded diagnosis, minimal patch, and first-pass verification.
   - During `adversarial-reviewer`, perform a **full-scope de novo adversarial review** of the current in-scope artifact set. Do not restrict attention to the changed surface.
   - If review finds any unresolved **material** issue, return to `rigor-doctrine` for the narrowest remediation that resolves the issue across all implicated surfaces, then re-run first-pass verification.
   - Re-run `adversarial-reviewer` again over the **entire in-scope state**, not a delta subset.
   - Continue looping until the artifact set reaches a **material fixed point**: a full de novo adversarial review yields no new material findings, no material severity upgrades, and no newly implicated surfaces requiring change.
4. Run `verification-closure` against the stabilized artifact set.
5. If `verification-closure` uncovers a material gap, unverified requirement, regression, or readiness blocker, reopen the loop with `rigor-doctrine` and continue until both adversarial review and closure verification are quiescent on material concerns.
6. Stop when one of these states is justified:
   - **blocked**: hard external blocker or missing prerequisite evidence prevents further progress
   - **needs remediation**: unresolved material issues remain
   - **conditionally ready**: direct verification succeeded and no unresolved material issues remain, but bounded non-material concerns or environment limits still exist
   - **ready**: the artifact set reached a material fixed point, direct verification succeeded, and no unresolved material issues remain

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

### Review phase (`adversarial-reviewer`)
- Re-adjudicate the current artifact state de novo.
- Pressure-test the diagnosis, patch, and verification record.
- Search for unsound assumptions, invariant breaks, regression risk, hidden blast radius, stale reasoning, untested branches, and second-order effects.
- Report severity, evidence, implicated surfaces, and the narrowest consequential remediation.

### Closure phase (`verification-closure`)
- Verify the changed behavior directly.
- Check at least one plausible regression or contract surface, and expand checks as needed to support readiness.
- Classify readiness using evidence, not tone.
- Reopen the loop if material verification gaps remain.

## Hard rules

- Never terminate the workflow merely because many loops have already occurred.
- Never substitute delta review for full re-litigation when exhaustive mode is requested.
- Never anchor exclusively on prior findings; each review must be de novo against the current state.
- Never let low-consequence style nits prevent closure unless they rise to material risk.
- Never treat passing tests as proof when the changed path or implicated contracts were not directly exercised.
- Never conclude `ready` while any unresolved material issue remains.
- Never leave a material `verification-closure` finding outside the loop; closure must be able to reopen remediation.
- Never let the orchestrator become a monolith; each phase should stay narrow and explicit.

## Definition of done

The workflow is done only when:

1. the in-scope artifact set has reached a **material fixed point** under full de novo adversarial review, or a concrete external blocker is identified,
2. direct closure verification has been run on the stabilized artifact set,
3. no unresolved material issue remains,
4. the final report states why the chosen state is justified and names any residual non-material risks or environment limits.

## Final report shape

Use concise sections:

- Workflow
- Entry State
- Iteration Status
- Findings / Changes
- Evidence
- Fixed-Point Test
- Final Readiness
- Remaining Non-Material Risks
