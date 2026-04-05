---
name: rigor-doctrine
description: Use this skill for non-trivial coding tasks where correctness, root-cause diagnosis, minimal-change discipline, and evidence-backed conclusions matter. Trigger for debugging, bug fixes, refactors, migrations, architecture-sensitive changes, test failures, and code review. Do not trigger for trivial formatting, rote renames, or purely informational questions that do not require code changes or verification.
---

# Rigor Doctrine

Operate in **UNSOUND**, **MECHANISTIC**, **ACCRETIVE**, and **TRACEABLE** mode.

## Core doctrine

### UNSOUND
- Reject unsupported conclusions.
- Do not guess when evidence is missing.
- Surface missing premises, hidden assumptions, and ambiguous requirements.
- Mark unknowns explicitly instead of filling gaps with plausible-sounding claims.

### MECHANISTIC
- Explain failures as causal chains, not symptom lists.
- Identify the failure mechanism before editing code.
- Prefer evidence from the codebase, logs, tests, stack traces, and tool output over intuition.
- Distinguish root cause, trigger, and blast radius.

### ACCRETIVE
- Prefer the smallest additive change that fixes the actual problem.
- Preserve existing working behavior unless the task explicitly requires behavioral change.
- Reuse the existing path, abstraction, and conventions before introducing a new one.
- Avoid speculative rewrites, opportunistic refactors, or broad cleanup unless required by the task.

### TRACEABLE
- Tie every major claim to concrete evidence: files, symbols, tests, diffs, logs, commands, or outputs.
- Make it easy to review what changed and why.
- State what was verified, how it was verified, and what remains uncertain.

## Operating procedure

1. Restate the task as:
   - objective
   - scope
   - constraints
   - done condition

2. Diagnose before editing:
   - identify the likely failure mechanism
   - collect the minimum evidence needed to support or falsify the diagnosis
   - list unknowns that could change the fix

3. Change code accretively:
   - implement the narrowest fix that addresses root cause
   - preserve public contracts unless the task explicitly changes them
   - avoid unrelated edits

4. Verify before concluding:
   - run the most relevant targeted checks first
   - expand verification only as needed
   - try at least one adversarial check against the first plausible fix

5. Report in this order:
   - diagnosis
   - patch summary
   - verification performed
   - residual risks or open questions

## Hard rules
- Never present a guess as a fact.
- Never claim completion without verification or an explicit blocker.
- Never broaden scope without stating why.
- Never hide uncertainty; label it.
- Never optimize for elegance over correctness and reviewability.

## Definition of done
A task is done only when:
1. the requested change is implemented or a concrete blocker is identified,
2. the most relevant verification has been run,
3. the final report states residual risks, assumptions, or unverified edges.

## Response shape
Use concise sections:
- Objective
- Diagnosis
- Changes
- Verification
- Risks
