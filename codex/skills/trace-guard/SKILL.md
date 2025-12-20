---
name: trace-guard
description: TRACE plus safety guardrails (unsoundness, invariants, footguns, complexity); use when code may crash, corrupt data, hide invalid states, invite misuse, or become hard to reason about.
---

# TRACE Guard

## When to use
- Crash risk, data corruption risk, or resource lifetime hazards.
- "Should never happen" comments, nullable surprises, or validation sprawl.
- Misuse-prone APIs, confusing parameters, or silent failure paths.
- Tangled control flow, deep nesting, or cross-file hop fatigue.

## Quick start
1. Triage failure modes (crash > corruption > logic).
2. Run Unsoundness scan and produce a concrete counterexample.
3. Strengthen invariants (construction-time > runtime checks).
4. Defuse footguns with safer signatures and tests.
5. Reduce incidental complexity and report via TRACE.

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

## TRACE report
Deliverables:
- Findings ordered by severity with file:line references.
- Violated TRACE letters for each finding.
- Minimal fix or mitigation and the new invariant (if any).
- Open questions and required tests.

## Activation cues
- "crash"
- "data corruption"
- "should never happen"
- "footgun"
- "misuse"
- "invariant"
- "hard to reason about"
- "too complex"
