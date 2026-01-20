---
name: fix
description: Review+fix protocol with safety guardrails (unsoundness, invariants, footguns, incidental complexity); requires a validation signal.
---

# Fix

## Intent
Make risky or unclear code safe with a minimal, validated change.

## Non-negotiables
- Default action: review + implement (unless review-only).
- Triage: crash > corruption > logic.
- No "done" claim without a passing validation signal.
- Every finding MUST include: counterexample, invariant (before), invariant (after), proof.

## When to use
- Crash/corruption risk; resource lifetime hazards.
- "resolve" / "fix" with a repro or credible signal.
- "should never happen", null surprises, validation sprawl.
- Misuse-prone APIs, confusing params, silent failures.
- Deep nesting/branch soup/cross-file hops when risk reduction is the goal.

## Guardrails
- No product/feature work.
- No intentional semantic changes without clarifying, except correctness tightening.
- Prefer the smallest diff that removes the bug-class.

## Autonomy gate (conviction)
Proceed without asking only when all are true:
- Signal: a local repro exists (or can be created without product ambiguity).
- Contract: expected behavior is clear and not product-sensitive.
- Invariant: you can state before + after.
- Diff: reviewable and localized for the chosen strategy.
- Proof: at least one validation signal passes after changes.

If any gate fails: clarify before editing.

## Correctness tightening (default)
Treat stricter behavior as correctness: apply minimal tightening upgrades; do not offer them as optional.

Tighten without asking only when it:
- Acts on invalid/ambiguous inputs or states (incl. previously undefined behavior), and
- Reduces silent failure, data loss, or unsafe continuation.

Common tightening moves (language-agnostic; examples only):
- Parse/coerce: replace implicit coercion/partial parse with explicit parse + error (JS implicit string->number; Rust `parse().ok()` fallback).
- Fallbacks: replace warn+fallback/default-without-signal with explicit error or explicit "unknown"/"invalid".
- Lossy conversion: replace truncation/clamping/wraparound with checked conversion + error (Rust `as`; C casts; Go int conversions).
- Partial updates: replace multi-step mutation with an atomic/transactional boundary, or return an explicit partial result.
- Ignored errors: propagate with context; if intentionally ignored, add a compensating signal (assert/test/metric/log).
- Sentinels: replace `-1`/`0`/`""`/`None` with richer returns so callers must handle the case.

Clarify before tightening if it could affect valid inputs, break callers, or preserve an intentionally permissive fallback.

## Defaults (to satisfy the gate)
Use these defaults only for localized, semantics-preserving fixes on valid inputs.

### Ownership / lifetimes
- Inventory resources in-slice: allocations, handles, sockets, locks, txns, temp files.
- For each resource, record: acquire site, owner, release action.
- Ensure every exit releases exactly once.
- Free/release ONLY via the proven owner/allocator/handle.
  - Do not assume a "free" is safe without proving allocator/ownership.
  - Arena/bump allocators: per-object `free` is safe only if explicitly documented as permitted/no-op.

### Validation signal selection
- If a command is provided, use it.
- Else infer the cheapest local signal (no network):
  1. README/QUICKSTART.
  2. `scripts/check` / `scripts/test`.
  3. `Makefile` / `justfile` / `Taskfile.yml`.
- If no command exists, create a proof hook:
  1. Focused regression/characterization test.
  2. Boundary assertion that fails loudly.
  3. Scoped, rate-limited diagnostic log tied to a single invariant.

## Clarify before changes
- Expected behavior missing/contradictory/product-sensitive.
- Fix crosses subsystems, needs migrations, or breaks APIs.
- No repro/signal and no safe default signal can be inferred or created.
- Risk tolerance unclear (perf/compat/security) and the change affects those axes.

## Workflow

### 0) Preflight
1. Confirm review-only vs fix.
2. Define the slice: entrypoint, inputs, outputs, state.
3. Choose the validation signal (or create a proof hook).

### 1) Contract + baseline
1. Write the contract (1 sentence): "Working means …".
2. Capture baseline:
   - failing test / repro steps / diagnostic log.
   - if none: add the smallest proof hook and run it once.

### 2) Findings (start a record per issue)
1. Enumerate candidate failure modes; rank crash > corruption > logic.
2. For each issue you will act on, record:
   - Location (`file:line`).
   - Failure mode.
   - Counterexample (input/timeline).
   - Invariant (before).
   - Invariant (after).

### 3) Mandatory scans (update findings)
Run all scans below for the touched slice; add findings when applicable.

#### 3a) Unsoundness scan
For each applicable hazard:
- First failure point.
- Counterexample input/timeline.
- Smallest sound fix that removes the bug-class.

Hazard classes:
- Nullability/uninitialized state; sentinel values.
- Ownership/lifetime: leaks, double-free, use-after-close, lock not released.
- Concurrency/order/time: races, lock ordering, reentrancy, timeouts/retries, TOCTOU.
- Bounds/arithmetic: indexing/slicing, overflow/underflow, signedness.
- Persistence/atomicity: partial writes, torn updates, non-transactional multi-step updates.
- Encoding/units: bytes vs chars, timezone/locale, unit mismatches, lossy normalization.
- Error handling: swallowed errors, missing context, silent fallback.

Language cues (examples only):
- Rust: `unsafe`, `unwrap/expect`, `as` casts.
- JS/TS: `any`, implicit coercions, `undefined` flows.
- Python: bare `except`, truthiness-based branching.
- C/C++: raw pointers, unchecked casts, manual `malloc/free`.

#### 3b) Invariant strengthening
1. Name the invariant.
2. Identify where it is (and is not) enforced.
3. Enforce at the strongest feasible level:
   - compile-time/typestate
   - construction-time parser/smart constructor (return refined value)
   - runtime boundary checks
   - assertions/logs (last resort)
4. Prefer "parse/refine once at the boundary" over scattered validation.
5. Add a proof hook that fails loudly on violation.

Discovery cues:
- Same check duplicated across sites.
- "should never happen" comments.
- Silent defaulting/fallback.
- Flag/boolean combinations that only make sense in some states.

#### 3c) Footgun defusal
1. Inventory misuse paths; rank likelihood × severity.
2. For top hazards, show a minimal misuse snippet + surprising behavior.
3. Make misuse hard:
   - options structs / named params
   - split booleans into enums or separate functions
   - explicit units/encodings
   - richer returns (no sentinels)
   - separate pure computation from effects
4. Lock with a regression test or boundary assertion.

#### 3d) Incidental complexity (risk-driven)
Reshape only when it reduces risk and makes invariants/ownership easier to audit.

1. Identify hotspots: nesting, branch soup, cross-file hops, mixed responsibilities.
2. Separate essential vs incidental.
3. Apply in order: flatten → rename → extract → replace branches with data.
4. If simplification depends on a missing invariant, strengthen the invariant first.
5. Avoid premature abstraction; duplication is cheaper than the wrong abstraction.

### 4) Apply the smallest sound fix
1. Remove the bug-class (not just the symptom).
2. Apply correctness tightening where applicable.
3. Ensure invariants + ownership hold on all paths.
4. Keep the diff reviewable.

### 5) Close the loop (required)
1. Run the chosen validation signal.
2. If it fails: fix and re-run the same signal until it passes.
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
- Feature creep.
- Tightening presented as optional.
- Ownership fixes without proven allocator/owner.

## Activation cues
- "resolve" / "fix" / "crash" / "data corruption"
- "footgun" / "misuse" / "should never happen"
- "invariant" / "lifetime" / "nullable surprise"
- "too complex" / "branch soup" / "cross-file hops"
