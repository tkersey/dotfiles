---
name: trace-guard
description: TRACE (Type/Readability/Atomic/Cognitive/Essential) review+resolve lens with safety guardrails.
---

# TRACE Guard

## When to use
- Review/refactor for clarity or cognitive load.
- Explain confusing control flow or hidden side effects.
- Crash/corruption risk; resource lifetime hazards.
- “Should never happen”, nullable surprises, validation sprawl.
- Misuse-prone APIs, confusing params, silent failures.
- Deep nesting, branch soup, cross-file hop fatigue.

## Default posture
- Default: review and resolve (unless asked for review-only).
- Prefer the smallest sound fix; widen scope only to reduce future-incident risk (tests, invariants, footgun defusal, incidental-complexity reduction).
- No intentional product/semantic changes without clarifying.

## Autonomy (conviction)
Proceed without asking only when all are true:
- Local repro (or a tight, credible signal).
- Invariant stated.
- Minimal diff.
- At least one validation signal passes.

Otherwise: clarify before editing.

## Clarify before changes
- Expected behavior is missing/contradictory/product-sensitive.
- The fix crosses subsystems, needs migrations, or breaks APIs.
- Repro/validation commands are unknown.
- Risk tolerance is undefined (performance/compat/security).

## Workflow
1. Build a cognitive heat map (hotspots + surprises).
2. Triage failure modes: crash > corruption > logic.
3. Unsoundness scan: trace nullables/lifetimes/concurrency; give a concrete counterexample.
4. Strengthen invariants (construction-time > runtime).
5. Defuse footguns (safer signatures, clearer names, tests/assertions).
6. Reduce incidental complexity (flatten → rename → extract).
7. Apply the smallest sound fix.
8. Close the loop: run at least one validation signal and record outcomes.
9. Report findings/fixes in severity order with file:line references.

## TRACE checklist
- Type: make invalid states unrepresentable.
- Readability: understandable in 30 seconds.
- Atomic: one responsibility; explicit side effects.
- Cognitive: minimize branching/hidden deps/cross-file hops.
- Essential: keep only domain-required complexity.

## Deliverable format
- Findings (severity order): file:line, issue, violated TRACE letters, fix.
- Changes applied (files + rationale).
- Validation signal(s) run + outcome.
- Residual risks, open questions, and tests added (or why skipped).

## Pitfalls
- Vague advice without concrete locations.
- “Nice-to-have” refactors that don’t reduce risk.
- Feature creep without clarifying.

## Activation cues
- "review" / "refactor" / "readability" / "cognitive load"
- "what is this doing" / "trace it"
- "resolve this"
- "crash" / "data corruption"
- "footgun" / "misuse"
- "invariant" / "too complex"
