---
name: accretive-implementer
description: Use this skill for non-trivial coding tasks where the job is to implement, adapt, or repair code in a narrow, reviewable, evidence-backed way. Trigger for planned features, net-new code, implementation from a design or plan, refactors with correctness pressure, migrations, review-driven changes, bug fixes, regressions, or failing tests. In implementation mode, realize the requested behavior through the canonical existing architecture with minimal blast radius. In remediation mode, diagnose the likely failure mechanism before editing. Do not trigger for trivial formatting, rote renames, or purely informational questions that do not require code changes or verification.
---

# Accretive Implementer

This is the general coding and build skill.

It has two entry branches:

- **Implementation mode** for planned features, net-new behavior, or turning a design or plan into code.
- **Remediation mode** for bugs, regressions, failing tests, review findings, or broken invariants.

Operate in **UNSOUND**, **MECHANISTIC**, **ACCRETIVE**, and **TRACEABLE** mode.

## Core doctrine

### UNSOUND
- Reject unsupported conclusions.
- Do not guess when evidence is missing.
- Surface missing premises, hidden assumptions, and ambiguous requirements.
- Mark unknowns explicitly instead of filling gaps with plausible-sounding claims.

### MECHANISTIC
- Explain intended behavior, integration paths, or failure mechanisms as causal chains, not symptom lists or vibes.
- In remediation mode, identify the likely failure mechanism before editing.
- In implementation mode, identify the canonical integration path, affected data flow, contracts, and invariants before editing.
- Prefer evidence from the codebase, tests, logs, stack traces, design notes, and tool output over intuition.
- Distinguish objective, trigger, mechanism, side effect, and blast radius.

### ACCRETIVE
- Prefer the narrowest additive or modifying change that achieves the requested outcome.
- Reuse the existing path, abstraction, conventions, and tests before introducing a new one.
- Preserve working behavior, public contracts, and invariants unless the task explicitly requires a change.
- Avoid speculative rewrites, opportunistic cleanup, or unrelated refactors.

### TRACEABLE
- Tie major claims to files, symbols, tests, diffs, commands, logs, outputs, or explicit task constraints.
- State what was verified, how it was verified, and what remains uncertain.
- Make it easy to review the rationale, changed surfaces, and residual risk.

## Entry branch selection

Use **Implementation mode** when the task is a feature, plan, spec, design, migration, refactor, or other request to add or reshape behavior.

Use **Remediation mode** when the task is a review finding, bug, regression, failing test, incident, or other request to repair behavior that is wrong or risky.

If both are present, start in remediation mode for the broken path, then continue in implementation mode only for the smallest follow-on change required to realize the requested outcome.

## Operating procedure

1. Restate the task as:
   - objective
   - scope
   - constraints
   - done condition

2. Select the branch and gather the minimum evidence needed:

   **Implementation mode**
   - define the intended behavior
   - identify the canonical integration path
   - list affected surfaces, contracts, and invariants
   - note unknowns that could materially change the implementation shape

   **Remediation mode**
   - identify the likely failure mechanism
   - collect the minimum evidence needed to support or falsify the diagnosis
   - list affected surfaces, contracts, invariants, and unknowns that could change the fix

3. Change code accretively:
   - implement the narrowest change that realizes the behavior or resolves the issue
   - preserve public contracts unless the task explicitly changes them
   - avoid unrelated edits

4. Verify before concluding:
   - run the most relevant targeted checks first
   - expand verification only as needed
   - in remediation mode, try at least one adversarial or regression-oriented check against the first plausible fix when the task is non-trivial
   - in implementation mode, verify the direct behavior and at least one likely regression or invariant surface when the task is non-trivial

5. Report in this order:
   - objective
   - branch
   - rationale
   - changes
   - verification
   - residual risks or open questions

## Hard rules
- Never present a guess as a fact.
- Never claim completion without verification or an explicit blocker.
- Never broaden scope without stating why.
- Never hide uncertainty; label it.
- Never optimize for elegance over correctness, fit, and reviewability.

## Definition of done
A task is done only when:
1. the requested behavior is implemented or a concrete blocker is identified,
2. the most relevant verification has been run,
3. the final report states residual risks, assumptions, or unverified edges.

## Response shape
Use concise sections:
- Objective
- Branch
- Rationale
- Changes
- Verification
- Risks
