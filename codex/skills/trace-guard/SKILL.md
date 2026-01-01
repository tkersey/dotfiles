---
name: trace-guard
description: TRACE (Type-Readability-Atomic-Cognitive-Essential) review + resolve lens with safety guardrails; apply minimal fixes, validate, and clarify when blocked.
---

# TRACE Guard

## When to use
- Review/refactor for clarity, maintainability, or cognitive load.
- Explain confusing control flow or hidden side effects.
- Crash or corruption risk; resource lifetime hazards.
- "Should never happen" comments, nullable surprises, validation sprawl.
- Misuse-prone APIs, confusing params, silent failure paths.
- Tangled flow, deep nesting, cross-file hop fatigue.

## Resolution posture
- Default: review **and resolve** unless asked for review-only.
- Prefer the smallest sound fix; expand scope only to reduce future-incident risk (tests, invariants, footgun defusal, incidental-complexity reduction).
- No intentional semantic/product behavior changes without clarifying.
- Ask before editing only if requirements/constraints are unknown.
- Add a regression/behavior test when fixes change determinism, ordering, invariants, or error handling; skip only if the harness is missing, prohibitive, or requires product decisions.

## Autonomy principles (spirit-level)
- Auto-advance on strong conviction: fix -> validate -> report; ask only if behavior changes or a guardrail trips.
- Strong conviction requires all: local repro, explicit invariant, minimal diff, and at least one passing validation signal.
- If scope/complexity rises, invoke the Complexity Mitigator playbook and ask before crossing subsystem boundaries.
- Skills: invoke `$close-the-loop` for any code change; use `$jujutsu` for VCS actions; use Complexity Mitigator when the guardrail triggers.

## Conviction examples (canonical)
- Strong conviction: single-file fix, invariant stated, repro confirmed, tests pass; proceed.
- Weak conviction: no repro, invariant unclear, or multi-subsystem change; ask.

## Clarify before changes
- Expected behavior is missing, contradictory, or product-sensitive.
- The change would alter product behavior (feature) vs fix a bug or tighten an invariant.
- The fix needs cross-service changes, schema migrations, or API break decisions.
- Repro steps or validation commands are unknown.
- Risk tolerance (performance, compatibility, security) is undefined.
- Test harness is unknown, or the only feasible test needs heavy scaffolding or product decisions (otherwise add tests by default).
- Conviction is weak (missing repro, invariant, minimal diff, or validation signal).
- The scope/complexity guardrail trips or a subsystem boundary would be crossed.

## Quick start
1. Build a cognitive heat map (hotspots and surprises).
2. Check conviction; auto-advance if strong, otherwise clarify.
3. Triage failure modes (crash > corruption > logic).
4. Run Unsoundness scan with a concrete counterexample.
5. Strengthen invariants (construction-time > runtime checks).
6. Defuse footguns with safer signatures/tests.
7. Reduce incidental complexity; report via TRACE.
8. Run the TRACE checklist (Type, Readability, Atomic, Cognitive, Essential).
9. Choose the smallest sound fix and any risk-reducing scope expansion.
10. Apply changes, validate with at least one signal, then report findings + fixes (severity order, file:line), scope expansion justification, and residual risks/testing gaps.

## Heat map (quick scan)
- Mark smooth flow as OK; hotspots as HOT.
- Record surprises: misleading names, implicit state, sneaky side effects.
- Note the first place a reader must simulate state across files.

## TRACE checklist
- Type-first: types and invariants should make invalid states unrepresentable.
- Readability: should be understandable in 30 seconds with minimal backtracking.
- Atomic: functions do one thing; side effects are explicit.
- Cognitive: minimize hidden dependencies, branching, and cross-file hops.
- Essential: keep only the complexity that is required by the domain.

## Unsoundness scan
Goal: remove crash/corruption classes, not symptoms.

Steps:
- Trace nullables, lifetimes, concurrency, resource ownership.
- Give a concrete counterexample input/scenario.
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
- Propose flatten -> rename -> extract steps ranked by impact/effort.
- Provide a small code sketch when structural changes are needed.
- Cite violated TRACE letters.

## Resolve loop (apply changes)
- Confirm constraints and a validation command; proceed by default.
- Implement the smallest sound fix.
- If scoped expansion reduces future-incident risk, do it in the same change (tests, assertions, footgun defusal, incidental-complexity reduction).
- Keep intent stable: no intentional semantic/product behavior changes without clarifying.
- Invoke `$close-the-loop` for any code change; run at least one validation signal and record outcomes.
- Add a regression/behavior test by default for fixes that change determinism, ordering, invariants, or error handling; omit only with a brief Residual risks justification.
- Summarize changes, scope expansion justification, and residual risks.

## Deliverable format
- Findings first, ordered by severity (file:line, issue, violated TRACE letters, fix).
- Changes applied (files + rationale).
- Scope Expansion Justification (what expanded, why it reduces future-incident risk, and why it is not a product behavior change).
- Validation signal(s) and outcome.
- Next Steps Taken (actions executed, validations run, skills invoked).
- Open questions or assumptions.
- Tests added (or skipped with a reason) and residual risks.

## TRACE report
Deliverables:
- Findings ordered by severity with file:line references.
- Violated TRACE letters for each finding.
- Fixes applied, including new invariants (if any).
- Scope Expansion Justification (what expanded, why it reduces future-incident risk, and why it is not an intentional product behavior change).
- Validation signal(s) run.
- Next Steps Taken (actions executed, validations run, skills invoked).
- Open questions and required tests.

## Pitfalls
- Avoid vague advice; tie every critique to a concrete location.
- Avoid "nice-to-have" refactors that do not reduce future-incident risk.
- Avoid intentional semantic/product behavior changes (feature creep) without clarifying.
- Avoid leaving fixes as suggestions when resolve is requested.

## Activation cues
- "review this code"
- "refactor"
- "readability"
- "cognitive load"
- "what is this doing"
- "trace it"
- "resolve this"
- "crash"
- "data corruption"
- "should never happen"
- "footgun"
- "misuse"
- "invariant"
- "hard to reason about"
- "too complex"
