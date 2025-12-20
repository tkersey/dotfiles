---
name: trace
description: TRACE (Type-Readability-Atomic-Cognitive-Essential) code review lens; use for reviews, refactors, readability audits, and explaining confusing code paths with concrete file/line findings.
---

# TRACE Lens

## When to use
- Review or refactor code for clarity, maintainability, or cognitive load.
- Explain confusing control flow or hidden side effects.
- Produce structured feedback with concrete file:line references.
- Prioritize the smallest fixes that improve readability and safety.

## Quick start
1. Build a cognitive heat map (mark hotspots and surprises).
2. Run the TRACE checklist (Type, Readability, Atomic, Cognitive, Essential).
3. Report findings ordered by severity, with file:line + violated letters.
4. Close with residual risks or testing gaps.

## TRACE checklist
- Type-first: types and invariants should make invalid states unrepresentable.
- Readability: should be understandable in 30 seconds with minimal backtracking.
- Atomic: functions do one thing; side effects are explicit.
- Cognitive: minimize hidden dependencies, branching, and cross-file hops.
- Essential: keep only the complexity that is required by the domain.

## Heat map (quick scan)
- Mark smooth flow as OK and hotspots as HOT.
- Record surprise events: misleading names, implicit state, sneaky side effects.
- Note the first place a reader must simulate state across files.

## Deliverable format
- Findings list first, ordered by severity (file:line, issue, violated TRACE letters, fix).
- Open questions or assumptions.
- Brief change summary.
- Residual risks or missing tests.

## Pitfalls
- Avoid vague advice; tie every critique to a concrete location.
- Avoid broad refactors; open a follow-up bead when scope balloons.

## Activation cues
- "review this code"
- "refactor"
- "readability"
- "cognitive load"
- "what is this doing"
- "trace it"
