---
name: fix
description: Review+fix protocol with safety guardrails (unsoundness, invariants, footguns, incidental complexity); requires a validation signal.
---

# Fix

## Intent
Make risky or unclear code safe with the smallest sound, validated change.

## Double Diamond fit
`fix` spans the full Double Diamond, but keeps divergence mostly internal to stay autonomous:
- Discover: reproduce/characterize + collect counterexamples.
- Define: state the contract and invariants (before/after).
- Develop: (internal) consider 2-3 plausible fix strategies; pick the smallest sound one per default policy.
- Deliver: implement + prove with a real validation signal.

If a fix requires a product-sensitive choice (cannot be derived or characterized safely), stop and ask (or invoke `$creative-problem-solver` when multiple viable strategies exist).

## Inputs
- User request text.
- Repo state (code + tests + scripts).
- Validation signal (failing test/repro/log) OR a proof hook you create.

## Outputs (chat)
- Emit the exact sections in `Deliverable format (chat)`.

## Hard rules (MUST / MUST NOT)
- MUST default to review + implement (unless review-only is requested).
- MUST triage and present findings in severity order: crash > corruption > logic.
- MUST NOT claim done without a passing validation signal.
- MUST NOT do product/feature work.
- MUST NOT do intentional semantic changes without clarifying, except correctness tightening.
- MUST resolve trade-offs using `Default policy (non-interactive)`.
- MUST produce a complete finding record for every acted-on issue:
  - counterexample
  - invariant_before
  - invariant_after
  - fix
  - proof

## Default policy (non-interactive)
Use these defaults to maximize autonomy (avoid asking).

Priority order (highest first):
1. correctness + data safety + security
2. compatibility for PROVEN_USED behavior
3. performance

Definitions:
- PROVEN_USED = behavior with evidence (see checklist below).
- NON_PROVEN_USED = everything else.

### PROVEN_USED evidence checklist (deterministic)
Goal: classify behavior as PROVEN_USED vs NON_PROVEN_USED without asking.

Algorithm:
1. Enumerate affected behavior tokens:
   - API symbols (functions/types/methods).
   - CLI flags/commands.
   - config keys / env vars.
   - file/wire formats (field names, JSON keys).
   - error codes/messages consumed by callers.
2. Collect evidence in this order (stop at first match):
   - User repro/signal references the token.
   - Tests assert on the token/behavior.
   - Docs/README/examples describe or demonstrate the token/behavior.
   - Repo callsites use the token (non-test, non-doc).
3. IF any evidence exists, THEN mark PROVEN_USED; ELSE mark NON_PROVEN_USED.

Evidence scan procedure (repo-local):
- Tests: search `tests/`, `test/`, `__tests__/`, `spec/`, and files matching `*test*` / `*.spec.*`.
- Docs/examples: search `README*`, `docs/`, `examples/`, and `*.md`.
- Callsites: search remaining source files.

Tooling hint: prefer `rg -n "<token>"` with `--glob` filters.

### Externally-used surface checklist (deterministic)
Treat a surface as external if ANY is true:
- Token appears in docs/README/examples.
- Token is a CLI flag/command, config key, env var, or file format field.
- Token is exported/public API (examples: Rust `pub`, TS/JS `export`, Python in `__all__`, Go exported identifier).

If external use is plausible but uncertain:
- Prefer an additive compatibility path (wrapper/alias/adapter) if small.
- Ask only if a breaking change is unavoidable.

Compatibility rules:
- MUST preserve PROVEN_USED behavior unless it is unsafe (crash/corruption/security). If unsafe, tighten and return a clear error.
- For NON_PROVEN_USED behavior, treat it as undefined; tightening is allowed.

API/migration rules:
- IF a fix touches an externally-used surface (use `Externally-used surface checklist`),
  THEN prefer additive/backward-compatible changes (new option/new function/adapter) over breaking changes.
- IF a breaking change is unavoidable, THEN stop and ask.

Performance rules:
- MUST avoid obvious asymptotic regressions in hot paths.
- IF performance impact is plausible but unmeasurable locally,
  THEN choose the smallest correctness-first fix and record the risk in `Residual risks / open questions` (do not ask).

## Autonomy gate (conviction)
Proceed without asking only if ALL are true:
- SIGNAL: you have (or can create) a local repro/signal without product ambiguity.
- CONTRACT: you can derive contract from repo evidence OR characterize current behavior without product ambiguity.
- INVARIANT: you can state invariant_before and invariant_after.
- DIFF: the change is localized and reviewable for the chosen strategy.
- PROOF: at least one validation signal passes after changes.

If ANY gate fails:
- Apply Defaults + contract derivation.
- Ask only if still blocked.

## Correctness tightening (default)
Definition: tightening = rejecting invalid/ambiguous states earlier, removing silent failure paths, or making undefined behavior explicit.

Rule:
- IF tightening prevents crash/corruption/security issue,
  THEN apply it (even if PROVEN_USED), return a clear error, and record the compatibility impact.
- ELSE IF tightening affects only NON_PROVEN_USED inputs/states,
  THEN apply it without asking.
- ELSE (tightening might change PROVEN_USED behavior):
  - prefer a backward-compatible shape (adapter/additive API), OR
  - lock current behavior with a characterization test,
  - ask only if compatibility cannot be preserved.

Allowed tightening moves (examples only):
- Parse/coerce: implicit coercion/partial parse -> explicit parse + error (JS implicit string->number; Rust `parse().ok()` fallback).
- Fallbacks: warn+fallback/default-without-signal -> explicit error OR explicit "unknown"/"invalid".
- Lossy conversion: truncation/clamp/wrap -> checked conversion + error (Rust `as`; C casts; Go int conversions).
- Partial updates: multi-step mutation -> atomic/transactional boundary OR explicit partial result.
- Ignored errors: ignore -> propagate with context; if intentionally ignored -> compensating signal (assert/test/metric/log).
- Sentinels: `-1`/`0`/`""`/`None` -> richer returns.

## Defaults (use only when semantics-preserving for valid inputs)

### Ownership / lifetimes
- MUST inventory in-slice resources: allocations, handles, sockets, locks, txns, temp files.
- For each resource, record: acquire_site, owner, release_action.
- MUST ensure every exit releases exactly once.
- MUST free/release ONLY via the proven owner/allocator/handle.
  - Never assume a "free" is safe without proving allocator/ownership.
  - Arena/bump allocators: per-object `free` is safe only if explicitly documented as permitted/no-op.

### Validation signal selection
Algorithm:
1. IF the user provided a command, use it.
2. ELSE choose the cheapest local signal (no network) in this order:
   - README/QUICKSTART
   - `scripts/check` / `scripts/test`
   - `Makefile` / `justfile` / `Taskfile.yml`
3. ELSE create a proof hook in this order:
   - focused regression/characterization test
   - boundary assertion that fails loudly
   - scoped + rate-limited diagnostic log tied to ONE invariant

## Clarify before changes
Stop and ask ONLY if any is true:
- Behavior is contradictory/product-sensitive AND cannot be derived from tests/docs/callsites AND cannot be characterized safely.
- A breaking API change or irreversible migration is unavoidable (no backward-compatible path).
- No local signal/proof hook can be found or created without product ambiguity.

## Finding record schema (internal)
For every issue you act on, construct this record before editing:
- location: `file:line`
- severity: `crash|corruption|logic`
- issue: <one sentence>
- counterexample: <input/timeline>
- invariant_before: <what is allowed/assumed today>
- invariant_after: <what becomes guaranteed/rejected>
- fix: <smallest sound fix that removes the bug-class>
- proof: <test/assert/log + validation command + result>

## Workflow (algorithm)

### 0) Preflight
1. Determine mode: review-only vs fix.
2. Define slice: entrypoint, inputs, outputs, state.
3. Select validation signal (or create proof hook).

### 1) Contract + baseline
1. Determine PROVEN_USED behavior:
   - Apply `PROVEN_USED evidence checklist` to the behavior tokens affected by the slice.
2. Derive contract without asking (in this order):
   - tests that exercise the slice
   - docs/README/examples
   - callsites in the repo
   - if none: add a characterization test for current behavior
3. Write contract (1 sentence): "Working means …".
4. Run baseline signal once; record result.

### 2) Create initial findings
1. Enumerate candidate failure modes for the slice.
2. Rank crash > corruption > logic.
3. For each issue you will act on, create a finding record.

### 3) Mandatory scans (add/upgrade findings)
Run all scans for the touched slice.

#### 3a) Unsoundness scan
For each hazard class that applies:
- Identify the first failure point.
- Provide a concrete counterexample (input/timeline).
- Specify the smallest sound fix that removes the bug-class.

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

#### 3b) Invariant strengthening scan
For each invariant you can name:
1. State invariant_before and invariant_after.
2. Choose the strongest enforcement feasible:
   - compile-time/typestate
   - construction-time parser/smart constructor (return refined value)
   - runtime boundary checks
   - assertions/logs (last resort)
3. Prefer "parse/refine once at the boundary" over scattered validation.
4. Attach a proof hook (test/assert/log) that fails loudly on violation.

Discovery cues:
- Same check duplicated across sites.
- "should never happen" comments.
- Silent defaulting/fallback.
- Flag/boolean combos that only make sense in some states.

#### 3c) Footgun scan + defusal
Trigger: you touched an API surface OR a caller can plausibly misuse the code.

For top-ranked misuse paths:
1. Provide minimal misuse snippet + surprising behavior.
2. Defuse by changing the surface:
   - options structs / named params
   - split booleans into enums or separate functions
   - explicit units/encodings
   - richer returns (no sentinels)
   - separate pure computation from effects
3. Lock with a regression test or boundary assertion.

#### 3d) Complexity scan (risk-driven)
Rule: reshape only when it reduces risk and improves auditability of invariants/ownership.

Algorithm:
1. Identify hotspots: nesting, branch soup, cross-file hops, mixed responsibilities.
2. Separate essential vs incidental.
3. Apply in order: flatten → rename → extract → replace branches with data.
4. If simplification requires a missing invariant, strengthen invariants first.
5. Avoid premature abstraction; duplication is cheaper than the wrong abstraction.

### 4) Implement fixes (per finding)
For findings in severity order:
1. Implement the smallest sound fix that removes the bug-class.
2. Apply correctness tightening when allowed.
3. Ensure invariants + ownership hold on all paths.
4. Keep diff reviewable; avoid drive-by refactors.

### 5) Close the loop (required)
1. Run the chosen validation signal.
2. IF it fails:
   - update findings with the new counterexample,
   - apply the smallest additional fix,
   - re-run the SAME signal.
3. Repeat until the signal passes.

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
- Asking for risk tolerance instead of applying the default policy.
- Tightening presented as optional.
- Ownership fixes without proven allocator/owner.

## Activation cues
- "resolve" / "fix" / "crash" / "data corruption"
- "footgun" / "misuse" / "should never happen"
- "invariant" / "lifetime" / "nullable surprise"
- "too complex" / "branch soup" / "cross-file hops"
