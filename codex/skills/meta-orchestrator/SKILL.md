---
name: meta-orchestrator
description: Use this skill to coordinate staged execution across rigor-doctrine, adversarial-reviewer, and verification-closure when a coding task needs an end-to-end path from diagnosis and implementation through skeptical review to final readiness. Trigger for debugging and fix workflows, PR hardening, migration closure, release gating, patch shepherding, and requests phrased as run the whole workflow, take this to merge, implement then review then verify, or determine if a change is truly done. Do not trigger for trivial one-step tasks that only need a single skill, rote formatting, or purely informational questions.
---

# Meta Orchestrator

This skill coordinates three narrow companion skills:

- `rigor-doctrine` for diagnosis and implementation
- `adversarial-reviewer` for skeptical second-pass audit
- `verification-closure` for final readiness decisions

Default posture: choose the smallest phase set that satisfies the task, but use the full chain when the user wants end-to-end confidence.

## Global doctrine

Every phase inherits **UNSOUND**, **MECHANISTIC**, **ACCRETIVE**, and **TRACEABLE** standards.

- **UNSOUND**: reject unsupported conclusions and label unknowns instead of guessing.
- **MECHANISTIC**: reason through failure mechanisms, contracts, state transitions, and blast radius.
- **ACCRETIVE**: prefer the narrowest additive change or check that resolves the real issue.
- **TRACEABLE**: tie major claims to files, symbols, tests, diffs, commands, logs, or outputs.

Additional phase overlays:
- Review adds **ADVERSARIAL** pressure.
- Verification adds **DETERMINISTIC** evidence discipline.

## When to use which phase

1. Start with **`rigor-doctrine`** when the task involves implementation, diagnosis, bug fixing, refactoring, or no patch exists yet.
2. Start with **`adversarial-reviewer`** when a diagnosis, plan, or patch already exists and the user wants critique, challenge, risk discovery, or red-teaming.
3. Start with **`verification-closure`** when the user mainly wants readiness, merge confidence, release confidence, or proof that a patch is actually done.
4. Run the **full chain** when the request implies end-to-end completion, merge readiness, high confidence, or “take this all the way through.”

## Entry-state detection

Before choosing a phase path, classify the task into one of these states:

- **no patch yet**
- **patch in progress**
- **patch exists**
- **review only**
- **verify only**

If the user explicitly asks for the whole workflow, do not collapse the request to a single phase even if one phase appears sufficient at first glance.

## Handoff protocol

Before switching phases, carry forward:

- objective and requested behavior
- scope and constraints
- likely diagnosis or current design rationale
- changed files, symbols, commands run, and relevant outputs
- invariants and contracts that must still hold
- verification evidence already collected
- residual uncertainty

Never make a later phase rediscover grounded facts that an earlier phase already established.

## Orchestration algorithm

1. Establish the entry state.
2. Choose the minimum required phase path:
   - implement only: `rigor-doctrine`
   - review only: `adversarial-reviewer`
   - verify only: `verification-closure`
   - implement + confidence: `rigor-doctrine` -> `adversarial-reviewer` -> `verification-closure`
   - review + verify: `adversarial-reviewer` -> `verification-closure`
3. Execute the selected phases:
   - During `rigor-doctrine`, produce a grounded diagnosis, minimal patch, and first-pass verification.
   - During `adversarial-reviewer`, pressure-test the diagnosis, patch, and verification record.
   - If review finds material issues and the task is end-to-end, return to `rigor-doctrine` for minimal remediation, then re-review the changed surface.
   - During `verification-closure`, decide `ready`, `conditionally ready`, or `not ready`.
4. Stop when one of these states is justified:
   - **blocked**: hard external blocker or missing prerequisite evidence
   - **needs remediation**: material issues remain unresolved
   - **conditionally ready**: core behavior is verified, but named gaps or risks remain
   - **ready**: core behavior is verified, review concerns are resolved or bounded, and no material unexplained failures remain

## Companion skill invocation

When supported in the current Codex client, explicitly use these companion skills by name:

- `$rigor-doctrine`
- `$adversarial-reviewer`
- `$verification-closure`

If explicit nested skill invocation is not available in the current environment, follow the same phase contracts directly inside this workflow rather than skipping a phase.

## Phase rules

### Build phase (`rigor-doctrine`)
- Diagnose before editing.
- Prefer the smallest accretive fix.
- Preserve existing contracts unless the task explicitly changes behavior.
- Produce a clear first-pass verification record.

### Review phase (`adversarial-reviewer`)
- Pressure-test the diagnosis, patch, and verification.
- Flag unsound assumptions, invariant breaks, regression risk, hidden blast radius, and missing negative checks.
- Report severity, evidence, and minimal remediation or validation.

### Closure phase (`verification-closure`)
- Verify the changed behavior directly.
- Check at least one plausible regression or contract surface.
- Classify readiness using evidence, not tone.
- Name residual risks, environment gaps, or flaky surfaces.

## Hard rules

- Never skip a necessary phase just to save time or context.
- Never treat passing tests as proof when the changed path was not directly exercised.
- Never ignore material reviewer findings; either remediate them, bound them, or downgrade readiness.
- Never conclude `ready` when unresolved critical or high-severity issues remain.
- Never let the orchestrator become a monolith; each phase should stay narrow and explicit.

## Definition of done

The workflow is done only when:

1. the necessary phase path has been completed or a concrete blocker is identified,
2. evidence has been carried forward across phases,
3. the final state is one of `blocked`, `needs remediation`, `conditionally ready`, or `ready`,
4. the final report states why that state was chosen.

## Final report shape

Use concise sections:

- Workflow
- Entry State
- Phase Path
- Findings / Changes
- Evidence
- Final Readiness
- Remaining Actions
