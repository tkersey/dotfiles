---
name: fix
description: Review+fix protocol with safety guardrails (unsoundness, invariants, footguns, incidental complexity); requires a validation signal.
---

# Fix

## Intent
Make risky or unclear code safe with a small, validated change.

## When to use
- Crash/corruption risk; lifetime hazards.
- “Resolve/fix” with a repro or credible signal.
- “Should never happen”, null surprises, validation sprawl.
- Misuse-prone APIs, confusing params, silent failures.
- Deep nesting/branch soup/cross-file hops when risk reduction is the goal.

## Default posture
- Default: review + fix (unless review-only).
- Smallest sound fix; widen only to reduce future incidents (tests, invariants, footguns, complexity).
- Treat stricter/tighter behavior as correctness: apply minimal strictness/tightening upgrades, not optional suggestions.
- No product/semantic changes without clarifying, except minimal strictness/correctness tightening (reject invalid inputs, hard-fail invalid data vs warn+fallback, clearer errors) that reduces risk.

## Autonomy (conviction)
Proceed without asking only if all are true:
- Local repro or tight signal.
- Invariant stated.
- Minimal diff.
- At least one validation signal passes.

Otherwise: clarify before editing.

## Autonomy defaults (to satisfy the gate)
When the fix is localized and semantics-preserving, assume:
- Ownership/lifetime: the scope owns allocations it creates until transfer; all error paths release them. Arena free is OK (no-op), so adding frees is safe.
- Validation: if no command is given, infer the cheapest local signal (no network). Prefer README/QUICKSTART command, `scripts/` (`scripts/check`/`scripts/test`), or repo task files (`Makefile`, `justfile`, `Taskfile.yml`). If none, add a boundary assertion or characterization test as the proof hook; ask only if expected behavior is unclear.

## Clarify before changes
- Expected behavior missing/contradictory/product-sensitive.
- The fix crosses subsystems, needs migrations, or breaks APIs.
- Repro/validation unknown and no default can be inferred.
- Risk tolerance undefined (performance/compat/security).
- Don’t pause just to ask for stricter/tighter behavior when the minimal upgrade is clearly safer and localized.

## Workflow
1. Establish expected behavior + current signal (repro, failing test, or diagnostic log).
2. Triage failure modes: crash > corruption > logic.
3. Unsoundness scan (below): trace lifetimes/nullables/concurrency; give a counterexample.
4. Strengthen invariants (below): construction/compile-time > runtime.
5. Defuse footguns (below): safer surfaces + tests/assertions.
6. Apply minimal strictness/tightening upgrades that reduce silent failure or ambiguity (hard-fail invalid inputs, stricter parsing, clearer errors).
7. Reduce incidental complexity (below): flatten → rename → extract.
8. Apply the smallest sound fix.
9. Close the loop: run at least one validation signal and record outcomes.
10. Report findings/fixes in severity order with file:line references.

## Unsoundness scan (expanded)
For each hazard, give a concrete counterexample input/timeline and the smallest sound fix.

- Nullability surprises: refine type, guard, or construction-time validation.
- Resource lifetimes: release handles/locks/memory on all paths (success/error/early return).
- Concurrency/time: surface shared state, ordering assumptions, retries/timeouts, blocking; make coupling explicit.
- Bounds/overflows: guard indexing/slicing/arithmetic; prefer checked ops with explicit errors.
- Error handling: avoid silent failures; preserve context; don’t swallow errors without a compensating signal.

## Invariants (expanded)
Name the invariant; enforce the strongest option that fits:
- Compile-time/typestate (best).
- Construction-time (parsers/smart constructors).
- Runtime boundary checks.
- Last resort: assertions/logs (only when stronger options are impractical).

Always add a proof hook when feasible:
- Focused regression/characterization test, or
- Boundary assertion that fails loudly on violation.

## Footgun defusal (expanded)
Treat APIs as hostile; prevent misuse.

- Inventory misuse paths (likelihood × severity).
- Show a minimal misuse snippet + surprising behavior.
- Prefer safer surfaces: options structs/named params, split boolean flags, explicit units/encodings, richer returns vs sentinels.
- Lock down with a regression test or assertion.

## Incidental complexity reduction (expanded)
Reduce cognitive load only if it reduces risk or improves correctness.

- Separate essential vs incidental (keep essential).
- Sequence: flatten → rename → extract.
- Replace branch soup with data (enums/tables) when it improves auditability.
- Avoid premature abstraction; duplication is cheaper than a bad abstraction.

## Deliverable format
- Findings (severity order): file:line, failure mode (crash/corruption/logic), issue, fix.
- Changes applied (files + rationale).
- Validation signal(s) run + outcome.
- Residual risks, open questions, tests added (or why skipped).

## Pitfalls
- Vague advice without locations.
- “Nice-to-have” refactors that don’t reduce risk.
- Feature creep without clarifying.
- Offering stricter/tighter fixes as optional suggestions instead of applying minimal safe upgrades.

## Activation cues
- "resolve" / "fix" / "crash" / "data corruption"
- "footgun" / "misuse" / "should never happen"
- "invariant" / "lifetime" / "nullable surprise"
- "too complex" / "branch soup" / "cross-file hops"
