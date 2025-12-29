---
name: trace-guard
description: TRACE (Type-Readability-Atomic-Cognitive-Essential) code review lens plus safety guardrails (unsoundness, invariants, footguns, complexity); use for reviews, refactors, readability audits, and when code may crash, corrupt data, hide invalid states, invite misuse, or become hard to reason about.
---

# TRACE Guard

## When to use
- Review or refactor code for clarity, maintainability, or cognitive load.
- Explain confusing control flow or hidden side effects.
- Crash risk, data corruption risk, or resource lifetime hazards.
- "Should never happen" comments, nullable surprises, or validation sprawl.
- Misuse-prone APIs, confusing parameters, or silent failure paths.
- Tangled control flow, deep nesting, or cross-file hop fatigue.

## Quick start
1. Build a cognitive heat map (mark hotspots and surprises).
2. Triage failure modes (crash > corruption > logic).
3. Run Unsoundness scan and produce a concrete counterexample.
4. Strengthen invariants (construction-time > runtime checks).
5. Defuse footguns with safer signatures and tests.
6. Reduce incidental complexity and report via TRACE.
7. Run the TRACE checklist (Type, Readability, Atomic, Cognitive, Essential).
8. Prioritize the smallest fixes that improve readability and safety.
9. Report findings ordered by severity with file:line, then close with residual risks or testing gaps.

## Heat map (quick scan)
- Mark smooth flow as OK and hotspots as HOT.
- Record surprise events: misleading names, implicit state, sneaky side effects.
- Note the first place a reader must simulate state across files.

## TRACE checklist
- Type-first: types and invariants should make invalid states unrepresentable.
- Readability: should be understandable in 30 seconds with minimal backtracking.
- Atomic: functions do one thing; side effects are explicit.
- Cognitive: minimize hidden dependencies, branching, and cross-file hops.
- Essential: keep only the complexity that is required by the domain.

## Unsoundness scan
Goal: remove crash/corruption classes, not just symptoms.

Steps:
- Trace nullables, lifetimes, concurrency, and resource ownership.
- Give a concrete counterexample input or scenario.
- Apply the smallest sound fix that removes the class.
- State the new invariant.

## Invariant strengthening
Goal: make illegal states unrepresentable.

Steps:
- Name the at-risk invariant and current protection level.
- Propose stronger construction-time or type-level guardrails.
- Sketch before/after types or parsers.
- Recommend a verification check (property test or assertion).

## Footgun defusal
Goal: reduce misuse probability and impact.

Steps:
- List hazards ordered by likelihood x severity.
- Provide minimal misuse snippets with surprising behavior.
- Offer safer signatures or naming (named params, typestate, richer types).
- Add a test/assertion to lock the edge down.

## Complexity mitigation
Goal: keep essential complexity, remove incidental complexity.

Steps:
- Separate essential vs incidental complexity.
- Propose flatten -> rename -> extract steps, ranked by impact/effort.
- Provide a small code sketch when structural changes are needed.
- Cite violated TRACE letters.

## Deliverable format
- Findings list first, ordered by severity (file:line, issue, violated TRACE letters, fix).
- Open questions or assumptions.
- Brief change summary.
- Residual risks or missing tests.

## TRACE report
Deliverables:
- Findings ordered by severity with file:line references.
- Violated TRACE letters for each finding.
- Minimal fix or mitigation and the new invariant (if any).
- Open questions and required tests.

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
- "crash"
- "data corruption"
- "should never happen"
- "footgun"
- "misuse"
- "invariant"
- "hard to reason about"
- "too complex"
