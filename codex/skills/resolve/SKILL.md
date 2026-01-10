---
name: resolve
description: Review+resolve protocol with safety guardrails (unsoundness, invariants, footguns, incidental complexity); requires a validation signal.
---

# Resolve

## Intent
Turn unclear, risky, or failure-prone code into a small, sound, *validated* change.

## When to use
- Crash/corruption risk; resource lifetime hazards.
- “Resolve this” / “fix this” with a repro or credible signal.
- “Should never happen”, nullable surprises, validation sprawl.
- Misuse-prone APIs, confusing params, silent failures.
- Deep nesting, branch soup, cross-file hop fatigue (when risk reduction is the goal).

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

## Autonomy defaults (to satisfy the gate)
When the fix is localized and semantics-preserving, assume these defaults:
- Ownership/lifetime: allocations created in the current scope are owned by that scope until transfer; all error paths must release them. Freeing on an arena allocator is acceptable (no-op), so adding frees is safe.
- Validation: if no command is provided, infer the cheapest local signal from repo conventions (no network). Prefer a documented command in README/QUICKSTART, or a local script in `scripts/` (e.g., `scripts/check`, `scripts/test`), or a repo-level task runner file (`Makefile`, `justfile`, `Taskfile.yml`). If no clear marker exists, ask before editing.

## Clarify before changes
- Expected behavior is missing/contradictory/product-sensitive.
- The fix crosses subsystems, needs migrations, or breaks APIs.
- Repro/validation commands are unknown and no default can be inferred.
- Risk tolerance is undefined (performance/compat/security).

## Workflow
1. Establish expected behavior + current signal (repro, failing test, or diagnostic log).
2. Triage failure modes: crash > corruption > logic.
3. Unsoundness scan (below): trace lifetimes, nullables, concurrency; give a concrete counterexample.
4. Strengthen invariants (below): construction/compile-time > runtime.
5. Defuse footguns (below): safer signatures/surfaces + tests/assertions.
6. Reduce incidental complexity (below): flatten → rename → extract.
7. Apply the smallest sound fix.
8. Close the loop: run at least one validation signal and record outcomes.
9. Report findings/fixes in severity order with file:line references.

## Unsoundness scan (expanded)
For each suspected hazard, give a concrete counterexample input/timeline and the smallest sound fix.

- Nullability surprises: replace “should never be null” with a refined type, explicit guard, or construction-time validation.
- Resource lifetimes: ensure handles/locks/memory are released on *all* paths (success, error, early return).
- Concurrency/time: identify shared state, ordering assumptions, retry/timeouts, and blocking calls; make coupling explicit.
- Bounds/overflows: guard indexing/slicing/arithmetic; prefer checked operations and explicit error paths.
- Error handling: avoid silent failures; preserve context; don’t swallow errors without a compensating signal.

## Invariants (expanded)
Name the invariant explicitly, then choose the strongest enforcement that fits scope:
- Compile-time/typestate (best): make illegal states unrepresentable.
- Construction-time: parsers/smart constructors that only produce valid values.
- Runtime: focused checks at boundaries.
- Last resort: assertions/logs (only when stronger options are impractical).

Always add a “proof hook” when feasible:
- A focused regression/characterization test, or
- A boundary assertion that will fail loudly on violation.

## Footgun defusal (expanded)
Treat APIs as hostile terrain: prevent misuse, don’t just document it.

- Inventory misuse paths (likelihood × severity).
- Show a minimal misuse snippet and the surprising behavior.
- Prefer safer surfaces:
  - options structs / named parameters,
  - separate functions instead of boolean flags,
  - explicit units/encodings,
  - richer return types instead of sentinel values.
- Lock it down with a regression test or assertion.

## Incidental complexity reduction (expanded)
Reduce cognitive load only when it reduces risk or improves correctness.

- Separate essential vs incidental complexity (keep the essential).
- Sequence: flatten → rename → extract.
- Replace branch soup with data (enums/tables) when it makes behavior easier to audit.
- Avoid premature abstraction; duplication is cheaper than a bad abstraction.

## Deliverable format
- Findings (severity order): file:line, failure mode (crash/corruption/logic), issue, fix.
- Changes applied (files + rationale).
- Validation signal(s) run + outcome.
- Residual risks, open questions, and tests added (or why skipped).

## Pitfalls
- Vague advice without concrete locations.
- “Nice-to-have” refactors that don’t reduce risk.
- Feature creep without clarifying.

## Activation cues
- "resolve" / "fix" / "crash" / "data corruption"
- "footgun" / "misuse" / "should never happen"
- "invariant" / "lifetime" / "nullable surprise"
- "too complex" / "branch soup" / "cross-file hops"
