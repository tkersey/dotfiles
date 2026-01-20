---
name: fix
description: Review+fix protocol with safety guardrails (unsoundness, invariants, footguns, incidental complexity); requires a validation signal.
---

# Fix

## Overview
- Default action: review + implement the smallest sound fix (unless review-only).
- Triage order: crash > corruption > logic.
- Proof requirement: run at least one validation signal and record the outcome.
- Reporting requirement: every finding MUST include:
  - Counterexample (input/timeline).
  - Invariant (before).
  - Invariant (after).
  - Proof hook (test/assert/log) and validation signal result.

## When to use
- Crash/corruption risk; resource lifetime hazards.
- "resolve" / "fix" with a repro or credible signal.
- "should never happen", null surprises, validation sprawl.
- Misuse-prone APIs, confusing params, silent failures.
- Deep nesting/branch soup/cross-file hops when risk reduction is the goal.

## Guardrails
- No product/feature work.
- No intentional semantic changes without clarifying, except correctness tightening (below).
- Prefer the smallest diff that removes the bug-class.
- Do not claim done without a passing signal.

## Autonomy gate (conviction)
Proceed without asking only when all are true:
- A local repro or tight signal exists (or can be created without product ambiguity).
- Expected behavior is clear and not product-sensitive.
- At least one invariant can be stated (before + after).
- The fix is reviewable and localized (minimal diff for the chosen strategy).
- At least one validation signal passes after changes.

Otherwise: clarify before editing.

## Correctness tightening (apply by default)
Treat stricter/tighter behavior as correctness: apply minimal tightening upgrades; do not offer them as optional suggestions.

Tightening is allowed without asking only when it:
- Affects invalid/ambiguous inputs or states (including previously undefined behavior), and
- Reduces silent failure, data loss, or unsafe continuation.

Common tightening moves (language-agnostic; examples in parentheses):
- Parsing/coercion: replace implicit coercion/partial parse with explicit parse + error (JS implicit string->number; Python permissive parsing; Rust `parse().ok()` used as fallback).
- Silent fallback: replace warn+fallback/default-without-signal with explicit error or an explicit "unknown"/"invalid" result.
- Lossy conversion: replace truncation/clamping/wraparound with checked conversion + error (Rust `as`; C casts; Go int conversions).
- Partial updates: replace partial writes/multi-step mutations with an atomic/transactional boundary, or return an explicit partial result.
- Swallowed errors: propagate with context; if intentionally ignored, add a compensating signal (assert/test/metric/log) that makes the ignore auditable.
- Sentinel values: replace sentinels (`-1`, `0`, `""`, `None`) with richer returns (result/option/enum) so callers must handle the case.

Clarify before tightening if it could change behavior for valid inputs, break callers, or a fallback is known product behavior.

## Autonomy defaults (to satisfy the gate)
When the fix is localized and intended to be semantics-preserving for valid inputs, assume:

### Ownership / lifetimes (tightened)
- Inventory all resources acquired in the slice (allocations, file handles, sockets, locks, DB transactions, temp files).
- For each resource, record:
  - Acquisition site.
  - Owner.
  - Release action.
- Ensure every exit path releases resources exactly once.
- Only free/release using the same owner/allocator/handle that acquired it.
  - Do not assume a "free" is safe without proving allocator/ownership.
  - Arena/bump allocators: treat per-object `free` as safe only if the API explicitly documents it as a no-op or otherwise permitted.

### Validation signal selection
- If a command is provided, use it.
- Otherwise infer the cheapest local signal (no network):
  1. README/QUICKSTART documented command.
  2. `scripts/` (`scripts/check`, `scripts/test`).
  3. Task entrypoints (`Makefile`, `justfile`, `Taskfile.yml`).
- If no command exists, create a proof hook in this order:
  1. Focused regression/characterization test in the existing harness.
  2. Boundary assertion that fails loudly.
  3. Diagnostic log that is (a) rate-limited/scoped and (b) tied to a specific invariant.

Ask only if expected behavior is unclear.

## Clarify before changes
- Expected behavior missing/contradictory/product-sensitive.
- The fix crosses subsystems, needs migrations, or breaks APIs.
- Repro/validation unknown and no default can be inferred or created.
- Risk tolerance undefined (performance/compat/security) and the change affects those axes.
- Do not pause just to ask for correctness tightening when the minimal upgrade is clearly safer and localized.

## Workflow

### 0) Preflight
1. Confirm whether the user requested review-only.
2. Identify the slice: entrypoint, inputs, outputs, and state.
3. Identify (or create) the validation signal you will run.

### 1) Establish contract + baseline signal
1. Write the contract as 1 sentence: "Working means …".
2. Capture the current signal:
   - A failing test, repro steps, or diagnostic log.
   - If none exists, create a proof hook (see defaults) and run it once to establish baseline behavior.

### 2) Triage + create finding records
1. List candidate failure modes for the slice.
2. Rank them: crash > corruption > logic.
3. For each candidate you intend to act on, create a finding record with:
   - Location (`file:line`).
   - Failure mode.
   - Counterexample (input/timeline).
   - Invariant (before).
   - Invariant (after) (stronger).

### 3) Mandatory scans (update findings)
Run all scans below for the touched slice; add findings if any hazard applies.

#### 3a) Unsoundness scan
For each hazard class:
- Identify the first failure point.
- Provide a concrete counterexample input/timeline.
- Choose the smallest sound fix that removes the bug-class.

Hazard classes:
- Nullability/uninitialized state (null/undefined/None/optional; sentinel values).
- Ownership/lifetime (leaks; double-free; use-after-close; lock not released).
- Concurrency/order/time (races; lock ordering; reentrancy; timeouts/retries; TOCTOU).
- Bounds/arithmetic (indexing/slicing; overflow/underflow; signedness).
- Persistence/atomicity (partial writes; torn updates; non-transactional multi-step state changes).
- Encoding/units (bytes vs chars; timezone/locale; unit mismatches; lossy normalization).
- Error handling (swallowed errors; missing context; silent fallback).

Language-specific cues (examples only):
- Rust: `unsafe`, `unwrap/expect`, `as` casts, `mem::*`.
- JS/TS: `any`, implicit coercions, `undefined` flows.
- Python: bare `except`, `None` defaulting, truthiness checks.
- C/C++: raw pointers, unchecked casts, manual `malloc/free`.

#### 3b) Invariant strengthening
1. Name the invariant.
2. Identify where it is (and is not) enforced today.
3. Enforce at the strongest level that fits:
   - Compile-time/typestate.
   - Construction-time (parser/smart constructor that returns the refined value).
   - Runtime boundary checks.
   - Last resort: assertions/logs.
4. Prefer "parse/refine once at the boundary" over scattered validation.
5. Add a proof hook that fails loudly on violation.

Invariant discovery cues:
- Repeated validation in multiple places.
- Comments like "should never happen".
- Silent fallbacks/defaulting.
- Boolean/flag combinations that only make sense in certain states.

#### 3c) Footgun defusal
1. Inventory misuse paths; rank by likelihood × severity.
2. For top-ranked hazards, show a minimal misuse snippet + surprising behavior.
3. Make misuse hard:
   - Options struct/named params.
   - Split boolean flags into enums or separate functions.
   - Make units/encodings explicit.
   - Replace sentinel returns with richer results.
   - Separate side effects from pure computation.
4. Lock down with a regression test or boundary assertion.

#### 3d) Incidental complexity reduction (risk-driven)
Reshaping is allowed when it reduces risk and makes invariants/ownership easier to audit.

1. Identify hotspots (nesting, branch soup, cross-file hops, mixed responsibilities).
2. Separate essential vs incidental complexity.
3. Apply in this order:
   - Flatten (guard clauses; early returns).
   - Rename (names match behavior/invariants).
   - Extract (small, single-responsibility units).
   - Replace branch soup with data (enums/tables/normal forms).
4. If simplification depends on a missing invariant, strengthen the invariant first.
5. Avoid premature abstraction; duplication is cheaper than a bad abstraction.

### 4) Apply the smallest sound fix
1. Implement the fix that removes the bug-class (not just the symptom).
2. Apply correctness tightening where applicable.
3. Ensure ownership/invariants hold on all paths.
4. Keep the diff reviewable.

### 5) Close the loop (required)
1. Run at least one validation signal.
2. If it fails, fix and re-run the same signal until it passes.
3. Record commands and outcomes.

## Deliverable format (chat)
Output exactly these sections.

**Contract**
- <one sentence>

**Findings (severity order)**
For each finding:
- `<file:line>` — `<crash|corruption|logic>` — <issue>
  - Counterexample: <input/timeline>
  - Invariant (before): <what was assumed/allowed>
  - Invariant (after): <what is now guaranteed/rejected>
  - Fix: <smallest sound fix summary>
  - Proof: <test/assert/log + validation command> -> <ok/fail>

**Changes applied**
- <file> — <rationale>

**Validation**
- <cmd> -> <ok/fail>

**Residual risks / open questions**
- <bullets>

## Pitfalls
- Vague advice without locations.
- "Nice-to-have" refactors that don’t reduce risk.
- Feature creep without clarifying.
- Tightening behavior presented as optional.
- Ownership fixes without proven allocator/owner.

## Activation cues
- "resolve" / "fix" / "crash" / "data corruption"
- "footgun" / "misuse" / "should never happen"
- "invariant" / "lifetime" / "nullable surprise"
- "too complex" / "branch soup" / "cross-file hops"
