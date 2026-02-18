---
name: fix
description: Review+fix protocol with safety guardrails (unsoundness, invariants, footguns, incidental complexity). Use when prompts say "$fix this PR", "fix current branch", "fix this diff", "repair CI red", or "apply a minimal patch", and when crash/corruption/invariant-break issues need correction with a validation signal.
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

## Skill composition (required)
- `$invariant-ace`: default invariant/protocol engine for `fix`; run it before invariant-affecting edits.
- `$complexity-mitigator`: default complexity analysis engine; use it for risk-driven complexity judgments before reshaping code.
- `$refine`: default path when the task is to improve `fix` itself (or other skills); apply `$refine` workflow and `quick_validate`.
- Delegation order when both are needed: `$invariant-ace` first, then `$complexity-mitigator`.

## Inputs
- User request text.
- Repo state (code + tests + scripts).
- Validation signal (failing test/repro/log) OR a proof hook you create.

## Outputs (chat)
- Emit the exact sections in `Deliverable format (chat)`.
- Use section headings verbatim (for example, `**Findings (severity order)**`, not `Findings`).
- During execution, emit one-line pass progress updates at pass start and pass end using:
  `Pass <n>/<total_planned>: <name> — <start|done>; edits=<yes|no|n/a>; signal=<cmd|n/a>; result=<ok|fail|n/a>`.

### Embedded mode (when $fix is invoked inside another skill)
- You may emit a compact **Fix Record** instead of the full deliverable.
- If another skill requires a primary artifact (for example patch-only diff), append **Fix Record** immediately after that artifact in the same assistant message.
- Do not mention “Using $fix” without emitting either the full deliverable or a Fix Record.

## Hard rules (MUST / MUST NOT)
- MUST default to review + implement (unless review-only is requested).
- MUST triage and present findings in severity order: security > crash > corruption > logic.
- MUST NOT claim done without a passing validation signal.
- MUST NOT do product/feature work.
- MUST NOT do intentional semantic changes without clarifying, except correctness tightening.
- MUST resolve trade-offs using `Default policy (non-interactive)`.
- MUST emit pass progress updates while running the multi-pass loop.
- MUST include a final `Pass trace` section in the deliverable/Fix Record with executed pass count and per-pass outcomes.
- MUST use the exact heading names from `Deliverable format (chat)` / `Fix Record`; do not alias or shorten heading labels.
- MUST produce a complete finding record for every acted-on issue:
  - counterexample
  - invariant_before
  - invariant_after
  - fix
  - proof
- MUST follow the delegation contract in `Skill composition (required)` (including order: `$invariant-ace` -> `$complexity-mitigator`).
- MUST route skill-self edits (for example `codex/skills/fix`) through `$refine` and run `quick_validate`.
- MUST NOT put fixable items in `Residual risks / open questions`; if it is fixable under the autonomy gate + guardrails, treat it as a finding and fix it.
- When paired with `$tk` in wave execution, MUST treat `$fix` as the final mutating pass before artifactization:
  - `commit_first`: hand off immediately to `$commit` after passing validation.
  - `patch_first`: hand off immediately to `$patch` after passing validation.

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
    - Docs/README/examples/CHANGELOG/config examples describe or demonstrate the token/behavior.
    - Repo callsites use the token (non-test, non-doc).
3. IF any evidence exists, THEN mark PROVEN_USED; ELSE mark NON_PROVEN_USED.

Evidence scan procedure (repo-local):
- Tests: search `tests/`, `test/`, `__tests__/`, `spec/`, and files matching `*test*` / `*.spec.*`.
- Docs/examples: search `README*`, `docs/`, `examples/`, `CHANGELOG*`, `config.example*`, and `*.md`.
- Callsites: search remaining source files.
- CI/config surfaces: also scan `.github/workflows/` for env vars, flags, and script entrypoints.

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
    - scoped + rate-limited diagnostic log tied to ONE invariant (never log secrets/PII)

### PR/diff scope guardrail (default in review mode)
- Default slice = changed lines/paths (git diff/PR diff) + at most one boundary seam (parse/construct/API edge) required to make the fix sound.
- Do not fix pre-existing issues outside the slice unless:
  - severity is security/crash/corruption AND
  - the fix is localized and provable without widening the slice.
- Otherwise: record as `Residual risks / open questions`.

### Generated / third-party code guardrail
- If a file appears generated or is under third-party/build output, do not edit it directly.
- Prefer to locate the source-of-truth + regeneration step; apply fixes there and regenerate as needed.
- Common no-edit zones (examples): `dist/`, `build/`, `vendor/`, `node_modules/`.

### Proof discipline for passing baselines
When the baseline signal is ok:
- For every acted-on finding, prefer a proof hook that fails before the fix (focused regression/characterization test).
- If you cannot produce a failing proof hook, do not edit; attempt to create one first by:
  - turning the counterexample into a focused regression/characterization test
  - enforcing the invariant at a single boundary seam (parse/refine once) and testing the new error
  - reducing effects to a pure helper and unit-testing it
  - using an existing fuzzer/property test harness if present
- Only if you still cannot create a proof hook without product ambiguity, record the blocker as residual risk.

### Residual risks / open questions policy (last resort)

Residual risks are a record of what you could not safely fix (not a to-do list).

Rules:
- Before emitting a residual item, attempt to convert it into an actionable finding:
  - produce a concrete counterexample
  - attach a proof hook (test/assert) that fails before the fix
  - apply the smallest localized fix within guardrails
  - re-run the validation signal
- Only emit residual items that are truly blocked by one of these blockers:
  - `product_ambiguity` (semantics cannot be derived/characterized safely)
  - `breaking_change` (no additive path; fix would be breaking)
  - `no_repro_or_proof` (cannot create a repro/proof hook locally)
  - `scope_guardrail` (outside diff slice and not severe enough to widen)
  - `generated_output` (generated/third-party output; need source-of-truth + regen)
  - `external_dependency` (needs network/creds/services/hardware)
  - `perf_unmeasurable` (impact plausible; no local measurement)
- Every residual bullet MUST include: a location or token, `blocked_by=<...>`, and `next=<one action>`.
- If there are no residual items, output `- None`.

## Multi-pass loop (default)

Goal: reduce missed issues in PR/diff reviews without widening scope.

Run 3 core passes (mandatory). Run 2 additional delta passes only if pass 3 edits code.

Pass 1) Safety (highest severity)
- Scope: diff-driven slice + required boundary seams.
- Focus: security/crash/corruption hazards, unsafe tightening, missing error propagation.
- Change budget: smallest sound fix only.

Pass 2) Surface (compat + misuse)
- Scope: externally-used surfaces touched by the diff (exports/CLI/config/format/docs).
- Focus: additive compatibility, defuse top footguns, clearer errors.
- Change budget: additive/wrapper/adapter preferred; breaking change => stop and ask.

Pass 3) Audit (invariants + ownership + proof quality)
- Scope: final diff slice.
- Focus: invariants enforced at strongest cheap boundary; ownership release-on-all-paths; proof strength.
- Delegation: run `$invariant-ace` first for invariant framing, then `$complexity-mitigator` for complexity verdicts that affect auditability.
- Change budget: no refactors unless they directly reduce risk/auditability of invariants.

Early exit (stop after pass 3):
- If pass 3 applies no edits, stop (after running/confirming the primary validation signal).

Delta passes (only if pass 3 applied edits)

Pass 4) Safety delta rescan
- Scope: ONLY lines/paths changed by passes 1-3 and their immediate boundaries.
- Focus: new security/crash/corruption hazards introduced by the fixes.

Pass 5) Surface + proof delta rescan
- Re-enumerate behavior tokens from the FINAL diff (including newly introduced errors/flags/exports/config keys).
- Re-run PROVEN_USED/external-surface checks for newly introduced tokens.
- Ensure proof is still strong for the final diff.

Rules:
- After any pass that edits code, run a local signal before continuing.
- Do not edit on suspicion: every edit must have a concrete counterexample, invariant_before/after, and a proof hook.
- Merge/de-duplicate findings across passes; final output format stays unchanged.
- Emit pass progress updates in real time at pass start/end; these updates are required and do not replace the final `Pass trace` section.

## Clarify before changes
Stop and ask ONLY if any is true:
- Behavior is contradictory/product-sensitive AND cannot be derived from tests/docs/callsites AND cannot be characterized safely.
- A breaking API change or irreversible migration is unavoidable (no backward-compatible path).
- No local signal/proof hook can be found or created without product ambiguity.

## Finding record schema (internal)
For every issue you act on, construct this record before editing:
- id: `F<number>`
- location: `file:line`
- severity: `security|crash|corruption|logic`
- issue: <one sentence>
- tokens: <affected behavior tokens; empty if none>
- proven_used: <yes/no + evidence if yes>
- external_surface: <yes/no + why>
- diff_touch: <yes/no>
- counterexample: <input/timeline>
- invariant_before: <what is allowed/assumed today>
- invariant_after: <what becomes guaranteed/rejected>
- fix: <smallest sound fix that removes the bug-class>
- proof: <test/assert/log + validation command + result>

## Workflow (algorithm)

### 0) Preflight
1. Determine mode: review-only vs fix.
2. If the requested target is this skill (or another skill), route through `$refine`:
   - follow `$refine` Discover -> Define -> Develop -> Deliver,
   - apply minimal skill diffs,
   - run `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/<skill-name>`.
   - Return to the rest of `fix` only if the request also includes code/runtime defects.
3. Define slice:
   - If in a git repo and there is a diff, derive slice/tokens from the diff (paths, changed symbols/strings).
   - Otherwise: entrypoint, inputs, outputs, state.
4. If the request is PR-scoped (for example "`$fix this PR`", "`$fix current branch`", CI failure on a PR), anchor the slice to PR diff/base and keep the work PR-local unless severity widening is required.
5. Apply `PR/diff scope guardrail` for review mode.
6. Apply `Generated / third-party code guardrail` before editing.
7. Select validation signal (or create proof hook).

### 1) Contract + baseline
1. Determine PROVEN_USED behavior:
    - Apply `PROVEN_USED evidence checklist` to the behavior tokens affected by the slice.
2. Derive contract without asking (in this order):
    - tests that exercise the slice
    - callsites in the repo
    - docs/README/examples
    - if none: add a characterization test for current behavior
3. Write contract (1 sentence): "Working means …".
4. Run baseline signal once; record result.
5. If baseline signal is ok, apply `Proof discipline for passing baselines`.

### 2) Create initial findings
1. Enumerate candidate failure modes for the slice.
2. Rank security > crash > corruption > logic.
3. For each issue you will act on, create a finding record.

### 3) Mandatory scans (multi-pass)
Run the `Multi-pass loop (default)` for the touched slice.

#### 3a) Unsoundness scan
For each hazard class that applies:
- Identify the first failure point.
- Provide a concrete counterexample (input/timeline).
- Specify the smallest sound fix that removes the bug-class.

Hazard classes:
- Security boundaries: authz/authn, injection, path traversal, SSRF, unsafe deserialization, secrets/PII handling.
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
Delegate to `$invariant-ace` and import its artifacts into `fix`.

Default execution:
1. Run `$invariant-ace` Compact Mode first.
2. Capture at minimum:
   - `Counterexample`
   - `Invariants`
   - `Owner and Scope`
   - `Enforcement Boundary`
   - `Seam (Before -> After)`
   - `Verification`
3. Map these to `fix` finding fields:
   - `invariant_before` from broken trace + prior scope,
   - `invariant_after` from chosen predicate(s) + holds scope,
   - `fix` from seam,
   - `proof` from verification signal.
4. Escalate to full `$invariant-ace` protocol if Compact Mode does not yield an inductive predicate.

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
Delegate to `$complexity-mitigator` for analysis; implement only via `fix`.

Rule: reshape only when it reduces risk and improves auditability of invariants/ownership.

Algorithm:
1. Run `$complexity-mitigator` on the touched slice (heat read + essential/incidental verdict + ranked options + TRACE).
2. Select the smallest viable cut that directly supports a finding (safety/surface/invariant ownership/proof quality).
3. If simplification depends on an unstated invariant, run/refresh `$invariant-ace` first.
4. Keep complexity-only cleanup out of scope unless it closes a concrete risk.

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
4. If you cannot make progress after 3 repair cycles, stop and ask with:
   - the last failing output (key lines/stack),
   - what you tried,
   - the smallest remaining decision that blocks you.

### 6) Residual risk sweep (required)
1. Re-check `Residual risks / open questions policy`.
2. Any item without a valid blocker becomes a finding and is fixed (with proof) or dropped.

### 7) Output lock (required)
Before sending the final message, verify all are true:
1. Heading set is exact and complete (`Contract`, `Findings (severity order)`, `Changes applied`, `Pass trace`, `Validation`, `Residual risks / open questions`).
2. `Pass trace` includes planned/executed counts and P1/P2/P3 lines (plus P4/P5 when executed).
3. Runtime pass updates (`Pass <n>/<total_planned>: ...`) were emitted during execution.
4. If embedded mode was used, include **Fix Record** in the same assistant message (after any required artifact).

## Deliverable format (chat)
Output exactly these sections.

If no findings:
- **Findings (severity order)**: `None`.
- **Changes applied**: `None`.
- **Residual risks / open questions**: `- None`.
- Still include **Pass trace** and **Validation**.

**Contract**
- <one sentence>

**Findings (severity order)**
For each finding:
- `F#` `<file:line>` — `<security|crash|corruption|logic>` — <issue>
  - Surface: Tokens=<...>; PROVEN_USED=<yes/no + evidence>; External=<yes/no>; Diff_touch=<yes/no>
  - Counterexample: <input/timeline>
  - Invariant (before): <what was assumed/allowed>
  - Invariant (after): <what is now guaranteed/rejected>
  - Fix: <smallest sound fix summary>
  - Proof: <test/assert/log + validation command> -> <ok/fail>

**Changes applied**
- <file> — <rationale>

**Pass trace**
- Core passes planned: `3`; core passes executed: `<3>`
- Delta passes planned: `<0|2>`; delta passes executed: `<0|2>`
- Total passes executed: `<3|5>`
- `P1 Safety` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`
- `P2 Surface` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`
- `P3 Audit` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`
- If delta passes executed, also include `P4` and `P5` lines in the same format.

**Validation**
- <cmd> -> <ok/fail>

**Residual risks / open questions**
- If none: `- None`
- Otherwise: `- <file:line or token> — blocked_by=<blocker> — next=<one action>`

### Fix Record (embedded mode only)
Use only when $fix is invoked inside another skill.

**Findings (severity order)**
For each finding:
- `F#` `<file:line>` — `<security|crash|corruption|logic>` — <issue>
  - Surface: Tokens=<...>; PROVEN_USED=<yes/no + evidence>; External=<yes/no>; Diff_touch=<yes/no>
  - Counterexample: <input/timeline>
  - Invariant (before): <what was assumed/allowed>
  - Invariant (after): <what is now guaranteed/rejected>
  - Fix: <smallest sound fix summary>
  - Proof: <test/assert/log + validation command> -> <ok/fail>

**Changes applied**
- <file> — <rationale>

**Pass trace**
- Core passes planned: `3`; core passes executed: `<3>`
- Delta passes planned: `<0|2>`; delta passes executed: `<0|2>`
- Total passes executed: `<3|5>`
- `P1 Safety` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`
- `P2 Surface` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`
- `P3 Audit` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`
- If delta passes executed, also include `P4` and `P5` lines in the same format.

**Validation**
- <cmd> -> <ok/fail>

**Residual risks / open questions**
- If none: `- None`
- Otherwise: `- <file:line or token> — blocked_by=<blocker> — next=<one action>`

## Pitfalls
- Vague advice without locations.
- "Nice-to-have" refactors that don’t reduce risk.
- Feature creep.
- Asking for risk tolerance instead of applying the default policy.
- Tightening presented as optional.
- Ownership fixes without proven allocator/owner.
- Editing generated/third-party outputs instead of source-of-truth.
- Code edits without a failing proof hook when baseline was ok.
- Using `Residual risks / open questions` as a substitute for fixable findings.

## Activation cues
- "resolve" / "fix" / "crash" / "data corruption"
- "$fix this PR" / "$fix current branch" / "fix this branch"
- "CI failed" / "fix the red checks" / "repair failing PR"
- "footgun" / "misuse" / "should never happen"
- "invariant" / "lifetime" / "nullable surprise"
- "too complex" / "branch soup" / "cross-file hops"
- "refine $fix" / "improve fix skill workflow" / "update fix skill docs"
