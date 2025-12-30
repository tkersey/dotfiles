---
name: trace-guard
description: TRACE (Type-Readability-Atomic-Cognitive-Essential) review + resolve lens with safety guardrails; apply minimal fixes, validate, and ask clarifying questions when blocked.
---

# TRACE Guard

## When to use
- Review or refactor code for clarity, maintainability, or cognitive load.
- Explain confusing control flow or hidden side effects.
- Crash risk, data corruption risk, or resource lifetime hazards.
- "Should never happen" comments, nullable surprises, or validation sprawl.
- Misuse-prone APIs, confusing parameters, or silent failure paths.
- Tangled control flow, deep nesting, or cross-file hop fatigue.

## Resolution posture
- Default: review **and resolve** unless asked for review-only.
- Prefer the smallest sound fix; expand scope only when it meaningfully reduces future-incident risk (tests, invariants, footgun defusal, incidental-complexity reduction).
- Do not make intentional semantic/product behavior changes without clarifying.
- Ask before editing only when requirements or constraints are unknown.
- Default to a regression/behavior test for bugfixes that change determinism, ordering, invariants, or error handling; skip only if the harness is missing, prohibitive to set up, or requires product decisions.

## Autonomy principles (spirit-level)
- Auto-advance on strong conviction: fix → validate → report; ask only if behavior changes or a guardrail trips.
- Strong conviction requires all: local repro, explicit invariant, minimal diff, and at least one passing validation signal.
- Scope/complexity guardrail: if either rises, invoke the Complexity Mitigator playbook and ask before crossing subsystem boundaries.
- Explicit skills: invoke `$close-the-loop` for any code change; use `$jujutsu` for VCS actions; invoke Complexity Mitigator when the guardrail triggers.

## Conviction examples (canonical)
- Strong conviction: single-file fix, invariant stated, repro confirmed, tests pass; proceed.
- Weak conviction: no repro, invariant unclear, or multi-subsystem change; ask.

## Clarify before changes
- Expected behavior is missing, contradictory, or product-sensitive.
- The change would alter product behavior (feature change) rather than fix a bug or tighten an invariant.
- The fix needs cross-service changes, schema migrations, or API breakage decisions.
- Repro steps or validation commands are unknown.
- Risk tolerance (performance, compatibility, security) is undefined.
- Test harness is unknown, or the only feasible test needs heavy scaffolding or product decisions (otherwise add tests by default).
- Conviction is weak (missing repro, invariant, minimal diff, or validation signal).
- Scope/complexity guardrail trips or a subsystem boundary would be crossed.

## Quick start
1. Build a cognitive heat map (mark hotspots and surprises).
2. Check the conviction gate; auto-advance if strong, otherwise clarify.
3. Triage failure modes (crash > corruption > logic).
4. Run Unsoundness scan; produce a concrete counterexample.
5. Strengthen invariants (construction-time > runtime checks).
6. Defuse footguns with safer signatures and tests.
7. Reduce incidental complexity; report via TRACE.
8. Run the TRACE checklist (Type, Readability, Atomic, Cognitive, Essential).
9. Choose the smallest sound fix.
10. Decide risk-based scope expansion (only if it reduces future-incident risk).
11. Apply changes (fix + scoped expansion).
12. Validate with at least one signal (tests, lint, logs).
13. Report findings + fixes (severity order, file:line), include scope expansion justification, then close with residual risks or testing gaps.

## Heat map (quick scan)
- Mark smooth flow as OK; hotspots as HOT.
- Record surprise events: misleading names, implicit state, sneaky side effects.
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
- Avoid “nice-to-have” refactors that don’t reduce future-incident risk.
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
