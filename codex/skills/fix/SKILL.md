---
name: fix
description: Review+fix protocol with optional pre-core git diff review and safety guardrails (unsoundness, invariants, footguns, incidental complexity). Use when prompts say "$fix this PR", "fix current branch", "fix this diff", "repair CI red", or "apply a minimal patch", and when crash/corruption/invariant-break issues need correction with a validation signal. Stop only after self-review exhausts actionable changes and the post-self-review rerun is clean.
---

# Fix

## Intent
Make risky or unclear code safe with the smallest sound, validated change, then keep listening to the final self-review until no actionable self-review change remains.
When the validated changeset survives the post-self-review rerun, `$fix` stops at that boundary; broader architecture, product, or roadmap analysis belongs to another skill.
Skill-artifact refinement belongs to `$refine`; `$fix` stays focused on code/diff repair turns.

## Execution spine
- `Preflight`
- `Diff review loop`
- `Core passes`
- `Residual risk sweep`
- `Agent-directed self-review loop`
- `Post-self-review rerun`
- `Output / handoff`

## Double Diamond fit
`fix` spans the full Double Diamond, but keeps divergence mostly internal to stay autonomous:
- Discover: reproduce/characterize + collect counterexamples.
- Define: state the contract and invariants (before/after).
- Develop: (internal) consider 2-3 plausible fix strategies; pick the smallest sound one per default policy.
- Deliver: implement + prove with a real validation signal.

If a fix requires a product-sensitive choice (cannot be derived or characterized safely), stop and ask (or invoke `$creative-problem-solver` when multiple viable strategies exist).

## Auxiliary skills (conditional)
- `$invariant-ace`: use it when the slice touches stateful boundaries (parse/construct/API/DB/lock/txn/retry ordering), ownership/lifetime, or any "should never happen" claim.
- `$complexity-mitigator`: use it when auditability is at risk (for example: branch soup, deep nesting, cross-file reasoning, or unclear ownership/control flow).
- If both triggers fire, run `$invariant-ace` first, then `$complexity-mitigator`.

## Inputs
- User request text.
- Repo state (code + tests + scripts).
- Optional git review context: `base_branch` + `comparison_sha`.
- Validation signal (failing test/repro/log) OR a proof hook you create.

## Outputs (chat)
- Emit the exact sections in `Deliverable format (chat)`.
- Use section headings verbatim (for example, `**Findings (severity order)**`, not `Findings`).
- During execution, emit one-line pass progress updates at pass start and pass end using:
  `Pass <n>/<total_planned>: <name> — <start|done>; edits=<yes|no|n/a>; signal=<cmd|n/a>; result=<ok|fail|n/a>`.
- In `Validation`, include a machine-checkable JSON object with keys:
  `baseline_cmd`, `baseline_result`, `proof_hook`, `final_cmd`, `final_result`.
- Keep review/self-review transcript shapes aligned with `references/self_review_loop_examples.md` when editing this contract.

### Embedded mode (when $fix is invoked inside another skill)
- You may emit a compact **Fix Record** instead of the full deliverable.
- If another skill requires a primary artifact (for example patch-only diff), append **Fix Record** immediately after that artifact in the same assistant message.
- Do not mention “Using $fix” without emitting either the full deliverable or a Fix Record.

## Hard rules (MUST / MUST NOT)
- MUST default to review + implement (unless review-only is requested).
- MUST triage and present findings in severity order: security > crash > corruption > logic.
- MUST NOT claim done without a passing validation signal.
- MUST NOT edit when no local signal/proof hook can be found or created under `Validation signal selection`; fail fast and report blocker.
- MUST NOT do product/feature work.
- MUST NOT do intentional semantic changes without clarifying, except correctness tightening.
- MUST resolve trade-offs using `Default policy (non-interactive)`.
- MUST emit pass progress updates while running the multi-pass loop.
- MUST include a final `Pass trace` section in the deliverable/Fix Record with executed pass count and per-pass outcomes.
- MUST include machine-checkable validation evidence keys in `Validation`: `baseline_cmd`, `baseline_result`, `proof_hook`, `final_cmd`, `final_result`.
- MUST use the exact heading names from `Deliverable format (chat)` / `Fix Record`; do not alias or shorten heading labels.
- MUST produce a complete finding record for every acted-on issue:
  - counterexample
  - invariant_before
  - invariant_after
  - fix
  - proof
  - proof_strength
  - compatibility_impact
- MUST follow the delegation contract in `Auxiliary skills (conditional)` (including order: `$invariant-ace` -> `$complexity-mitigator`).
- MUST NOT put fixable items in `Residual risks / open questions`; if it is fixable under the autonomy gate + guardrails, treat it as a finding and fix it.
- MUST include a final `Review loop trace` section in the deliverable/Fix Record.
- MUST use the exact diff review prompt from `Diff review loop`, with only `base_branch` and `comparison_sha` substituted.
- MUST verify `comparison_sha` resolves to a commit before activating the diff review loop.
- MUST keep the diff review loop separate from `Pass trace`; report it in `Review loop trace`.
- MUST close the diff review loop only when a review round yields `local_findings=0`.
- MUST carry blocked diff-review findings into `Residual risks / open questions`; they do not keep the diff review loop open.
- MUST suppress a repeated diff-review finding only when its normalized fingerprint and implicated path set did not change across consecutive review rounds.
- MUST include a final `Self-review loop trace` section in the deliverable/Fix Record.
- MUST run the final agent-directed self-review loop only after at least one change is applied and validation is passing.
- MUST run the self-review loop against the final validated changeset only.
- MUST invalidate and rerun the self-review loop if any non-self-review edit occurs after a self-review round.
- MUST ask internally exactly: `If you could change one thing about this changeset what would you change?`
- MUST treat the final agent-directed self-review phase as current-worktree scoped once the first validated changeset exists; do not reject a self-review suggestion solely because it broadens the diff.
- MUST treat a self-review answer as actionable whenever it identifies a concrete compatible/provable improvement on the current validated changeset, even if the improvement is ergonomic, structural, or API-shaping rather than a baseline bug fix.
- MUST answer that question internally, apply at most one new actionable self-review change per self-round, re-run validation, and repeat until a self-round yields no new actionable self-review change or only blocked changes.
- MUST NOT reject a self-review suggestion solely because the baseline is already green, the concern sounds architectural, or the change would reshape a public/API seam; if it can stay backward-compatible and be revalidated locally, implement it.
- MUST, when a self-review critique is broader than the smallest bug repair, apply the narrowest compatible/provable slice that materially addresses the critique before considering broader follow-up skills.
- MUST rerun the non-self-review `$fix` passes once after the self-review loop reaches `no_new_actionable_changes` or `blocked`.
- MUST NOT use `scope_guardrail` as the reason to reject a self-review suggestion once the self-review phase has started.
- MUST NOT report a self-review answer that was already applied before the final self-review round; record `finding=none` only when the current final validated changeset yields no concrete compatible/provable self-review change.
- MUST NOT emit `If you could change one thing about this changeset what would you change?` as a user-facing terminal line during normal successful completion.
- MUST stop `$fix` once no new actionable self-review change remains and the post-self-review rerun is clean; do not continue under `$fix` into broader architecture, product, roadmap, or conceptual analysis.
- MUST, if the user asks for broader or bolder analysis after a clean or closed `$fix` pass, close the `$fix` deliverable first and recommend the next skill explicitly (`$grill-me`, `$parse`, `$plan`, or `$creative-problem-solver`) instead of continuing under `$fix`.
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
Deterministic scan command template (run in this order):
- `rg -n "<token>" tests test __tests__ spec --glob '*test*' --glob '*.spec.*'`
- `rg -n "<token>" README* docs examples CHANGELOG* config.example* --glob '*.md'`
- `rg -n "<token>" .github/workflows`
- `rg -n "<token>" .`

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

No-signal fail-fast (deterministic):
- If no signal/proof hook is available after executing the selection algorithm once, stop before editing.
- Return one blocker with `blocked_by=no_repro_or_proof` and include the exact commands you attempted.

### PR/diff scope guardrail (default in review mode)
- Default slice = changed lines/paths (git diff/PR diff) + at most one boundary seam (parse/construct/API edge) required to make the fix sound.
- Do not fix pre-existing issues outside the slice unless:
  - severity is security/crash/corruption AND
  - the fix is localized and provable without widening the slice.
- Otherwise: record as `Residual risks / open questions`.

Scope widening trigger (deterministic):
- Widen beyond the diff only when ALL are true:
  - severity is `security`, `crash`, or `corruption`
  - you can show a concrete causal chain from a diff token to the out-of-slice location
  - the widening is limited to one adjacent seam (at most one additional file/module boundary)
  - one local validation signal can prove the widened fix
- If any check fails, keep scope fixed and record `blocked_by=scope_guardrail`.
- This guardrail applies to the core review passes.
- Once the final agent-directed self-review loop starts, scope expands to the current repo/worktree and `scope_guardrail` is not a valid reason to reject the self-review suggestion.

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
- Self-review exception: when the self-review finding is a concrete compatible simplification or auditability improvement on an already-green changeset, a fresh failing hook is preferred but not mandatory; the primary validation bundle may serve as the proof hook if it still proves the improved invariant after the change.

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
- For self-review-originated changes, do not emit `blocked_by=scope_guardrail`; if scope is the only blocker, widen and continue.
- Every residual bullet MUST include: a location or token, `blocked_by=<product_ambiguity|breaking_change|no_repro_or_proof|scope_guardrail|generated_output|external_dependency|perf_unmeasurable>`, and `next=<one action>`.
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
- If pass 3 applies no edits, stop the core-pass phase (after running/confirming the primary validation signal).

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
- During the self-review phase, the counterexample may be an auditability or responsibility-split failure in the current validated changeset; if the change is compatible and locally validated, that is actionable under `$fix` even when the baseline was already green.
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
- proof_strength: `characterization|targeted_regression|property_or_fuzz`
- compatibility_impact: `none|tightening|additive|breaking`

### Canonical finding example (fully-filled)
Use this as the reference shape when writing findings.

```md
F1 `src/config_loader.py:88` — crash — untrusted config type causes uncaught attribute access
  - Surface: Tokens=config.path; PROVEN_USED=yes (tests/config/test_loader.py::test_reads_path); External=yes; Diff_touch=yes
  - Counterexample: `{"path":null}` reaches `cfg.path.strip()` and raises `AttributeError`
  - Invariant (before): loader assumes `path` is a non-empty string
  - Invariant (after): loader accepts only non-empty string `path`; invalid type returns explicit error
  - Fix: add boundary validation in `parse_config()` and reject invalid `path` before use
  - Proof: `uv run pytest tests/config/test_loader.py::test_rejects_null_path` -> ok
  - Proof strength: `targeted_regression`
  - Compatibility impact: `tightening`

Residual risks / open questions
- `vendor/generated/config_schema.py` — blocked_by=generated_output — next=edit source schema and regenerate artifact
```

## Workflow (algorithm)

### 0) Preflight
1. Determine mode: review-only vs fix.
2. Define slice:
   - If in a git repo and there is a diff, derive slice/tokens from the diff (paths, changed symbols/strings).
   - Otherwise: entrypoint, inputs, outputs, state.
3. If the request is PR-scoped (for example "`$fix this PR`", "`$fix current branch`", CI failure on a PR), anchor the slice to PR diff/base and keep the work PR-local unless severity widening is required.
4. Apply `PR/diff scope guardrail` for review mode.
5. Apply `Generated / third-party code guardrail` before editing.
6. Determine review-loop activation:
   - If `git rev-parse --is-inside-work-tree` fails, set `Review loop trace` to `- None (skip_not_git_repo)` and continue.
   - If the repo is git-backed but `base_branch` or `comparison_sha` is missing, set `Review loop trace` to `- None (skip_missing_base_context)` and continue.
   - Otherwise verify `comparison_sha` with `git rev-parse --verify <comparison_sha>^{commit}` and freeze the canonical commit for the rest of the run.
   - If that verification fails, stop before editing and report the failed command as a blocker.
7. Select validation signal (or create proof hook).
8. If signal/proof creation fails, stop before editing and return `blocked_by=no_repro_or_proof` with attempted commands.

### 1) Diff review loop
This phase runs after preflight and before core passes.

Literal prompts (required):

```text
Review the code changes against the base branch '<base_branch>'. The merge base commit for this comparison is <comparison_sha>. Run `git diff <comparison_sha>` to inspect the changes relative to <base_branch>. Provide prioritized, actionable findings.
```

```text
Address all review findings.
```

Algorithm:
1. If `Review loop trace` already contains a skip line from preflight, continue to phase 2.
2. Run the literal review prompt using the frozen `base_branch` label and canonical `comparison_sha`.
3. Partition the returned findings into:
   - `local_findings`: locally fixable under ordinary `$fix` guardrails
   - `blocked_findings`: findings that are blocked under the existing blocker model
   - `stale_findings`: repeated locally-fixable findings whose normalized fingerprint and implicated path set did not change across consecutive rounds after an address round
4. Emit one `Review loop trace` row per review round.
5. If `local_findings > 0`, run `Address all review findings.`, re-run the chosen validation signal, then repeat from step 2.
6. If a repeated locally-fixable finding is stale, suppress it from loop continuation and count it under `stale_findings`.
7. Close the diff review loop only when a review round yields `local_findings=0`.
8. Carry any `blocked_findings` forward to `Residual risks / open questions`; they do not keep this phase open.

### 2) Core passes
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
6. Enumerate candidate failure modes for the slice.
7. Rank security > crash > corruption > logic.
8. For each issue you will act on, create a finding record.
9. Run the `Multi-pass loop (default)` for the touched slice.

#### 2a) Unsoundness scan
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

#### 2b) Invariant strengthening scan
When invariant triggers fire, delegate to `$invariant-ace` and import its artifacts into `fix`.

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

#### 2c) Footgun scan + defusal
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

#### 2d) Complexity scan (risk-driven)
When complexity triggers fire, delegate to `$complexity-mitigator` for analysis; implement only via `fix`.

Rule: reshape only when it reduces risk and improves auditability of invariants/ownership.

Algorithm:
1. Run `$complexity-mitigator` on the touched slice (heat read + essential/incidental verdict + ranked options + TRACE).
2. Select the smallest viable cut that directly supports a finding (safety/surface/invariant ownership/proof quality).
3. If simplification depends on an unstated invariant, run/refresh `$invariant-ace` first.
4. Keep complexity-only cleanup out of scope unless it closes a concrete risk.

10. Implement fixes (per finding).
For findings in severity order:
1. Implement the smallest sound fix that removes the bug-class.
2. Apply correctness tightening when allowed.
3. Ensure invariants + ownership hold on all paths.
4. Keep diff reviewable; avoid drive-by refactors.

11. Close the core-pass phase.
   - Run the chosen validation signal.
   - If it fails, update findings with the new counterexample, apply the smallest additional fix, and re-run the SAME signal.
   - Repeat until the signal passes.
   - If you cannot make progress after 3 repair cycles, stop and ask with the last failing output, what you tried, and the smallest remaining decision that blocks you.

### 3) Residual risk sweep (required)
1. Re-check `Residual risks / open questions policy`.
2. Any item without a valid blocker becomes a finding and is fixed (with proof) or dropped.

### 4) Agent-directed self-review loop (required final step when a changeset exists)
1. Precondition gate: run this step only when `Changes applied` is not `None` and the latest validation signal result is `ok`.
2. Freeze the self-review baseline as the latest validated changeset.
3. Ask internally exactly: `If you could change one thing about this changeset what would you change?`
4. Summarize the self-round in `Self-review loop trace` with one delta row.
5. If the answer yields one new actionable self-review change:
   - convert it into one concrete finding,
   - treat compatible ergonomic/structural/API-shaping improvements as actionable when they materially improve the current validated changeset and can be proven locally,
   - widen anywhere in the current repo/worktree as needed,
   - apply the smallest sound change that materially addresses the critique,
   - re-run the chosen validation signal and update findings/proof,
   - record the `(validated_changeset_fingerprint, normalized_answer_summary)` pair so repeated suggestions cannot loop forever,
   - repeat from step 2.
6. If the answer yields only blocked changes, record `stop_reason=blocked`, carry blockers to `Residual risks / open questions`, and continue to phase 5.
7. If the answer yields no new actionable self-review change, record `stop_reason=no_new_actionable_changes` and continue to phase 5.
   - This check is against the current final validated changeset, not an earlier pre-delta review state.
   - `already green`, `architectural`, `not fix-shaped`, or `no failing proof hook` are not sufficient reasons by themselves when a concrete compatible/provable improvement still exists.
8. Skip gate: if `Changes applied` is `None` or the run is blocked before edits, output `- None (skip_gate)` in `Self-review loop trace` and proceed to phase 6.

### 5) Post-self-review rerun (required)
1. Run the non-self-review core passes once against the full resulting changeset.
2. If that rerun edits code, discard the stale self-review state, revalidate, and restart from phase 4 against the new final validated changeset.
3. If that rerun applies no edits, continue to phase 6.

### 6) Output / handoff (required)
1. If a clean or closed `$fix` pass surfaces broader non-fix opportunities, do not continue exploring them under `$fix`.
2. If the user explicitly asks for broader or deeper follow-up after closure, recommend the next skill explicitly:
   - `$parse` for architecture or purpose analysis
   - `$grill-me` for interrogation, pressure-testing, or narrowing the next move
   - `$plan` for a decision-complete roadmap
   - `$creative-problem-solver` for wider option generation
3. Do not place those broader opportunities in `Residual risks / open questions` unless a valid blocker from the allowed set applies.
4. Output lock (required):
   1. Heading set is exact and complete (`Contract`, `Findings (severity order)`, `Changes applied`, `Review loop trace`, `Pass trace`, `Validation`, `Self-review loop trace`, `Residual risks / open questions`).
   2. `Review loop trace` includes either a skip line or at least one terminal review row with `local_findings=0`.
   3. `Pass trace` includes planned/executed counts and P1/P2/P3 lines (plus P4/P5 when executed) plus `Post-self-review rerun`.
   4. Runtime pass updates (`Pass <n>/<total_planned>: ...`) were emitted during execution.
   5. If embedded mode was used, include **Fix Record** in the same assistant message (after any required artifact).
   6. `Validation` includes machine-checkable keys: `baseline_cmd`, `baseline_result`, `proof_hook`, `final_cmd`, `final_result`.
   7. Every acted-on finding includes `Proof strength` and `Compatibility impact` using the allowed enums.
   8. Every residual `blocked_by` uses only: `product_ambiguity|breaking_change|no_repro_or_proof|scope_guardrail|generated_output|external_dependency|perf_unmeasurable`.
   9. If `Changes applied` is not `None` AND the latest validation result is `ok`, `Self-review loop trace` includes a terminal row with `stop_reason=<no_new_actionable_changes|blocked>` and the user-facing final line is not the question.

## Deliverable format (chat)
Output exactly these sections in this order.

If no findings:
- **Findings (severity order)**: `None`.
- **Changes applied**: `None`.
- **Review loop trace**: either a skip line or one or more `R#` rows.
- **Self-review loop trace**: `- None (skip_gate)`.
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
  - Proof strength: `<characterization|targeted_regression|property_or_fuzz>`
  - Compatibility impact: `<none|tightening|additive|breaking>`

**Changes applied**
- <file> — <rationale>

**Review loop trace**
- If skipped: `- None (skip_not_git_repo|skip_missing_base_context)`
- Otherwise: `R#` base_branch=`<name>`; comparison_sha=`<sha>`; review_cmd=`git diff <sha>`; local_findings=`<N>`; blocked_findings=`<N>`; stale_findings=`<N>`; change_applied=`<yes|no>`; result=`<continue|local_clean>`

**Pass trace**
- Core passes planned: `3`; core passes executed: `<3>`
- Delta passes planned: `<0|2>`; delta passes executed: `<0|2>`
- Total core/delta passes executed: `<3|5>`
- `P1 Safety` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`
- `P2 Surface` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`
- `P3 Audit` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`
- If delta passes executed, also include `P4` and `P5` lines in the same format.
- `Post-self-review rerun` -> executed=`<yes|no>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`

**Validation**
- <cmd> -> <ok/fail>
- `{"baseline_cmd":"<cmd|n/a>","baseline_result":"<ok|fail|n/a>","proof_hook":"<test/assert/log|n/a>","final_cmd":"<cmd>","final_result":"<ok|fail>"}` (single-line JSON)

**Self-review loop trace**
- If none: `- None (skip_gate)`
- Otherwise: `S#` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=<...>; finding=`<F#|none>`; change_applied=`<yes|no>`; proof=`<cmd|n/a>`; result=`<ok|fail|n/a>`; stop_reason=`<continue|no_new_actionable_changes|blocked>`

**Residual risks / open questions**
- If none: `- None`
- Otherwise: `- <file:line or token> — blocked_by=<product_ambiguity|breaking_change|no_repro_or_proof|scope_guardrail|generated_output|external_dependency|perf_unmeasurable> — next=<one action>`

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
  - Proof strength: `<characterization|targeted_regression|property_or_fuzz>`
  - Compatibility impact: `<none|tightening|additive|breaking>`

**Changes applied**
- <file> — <rationale>

**Review loop trace**
- If skipped: `- None (skip_not_git_repo|skip_missing_base_context)`
- Otherwise: `R#` base_branch=`<name>`; comparison_sha=`<sha>`; review_cmd=`git diff <sha>`; local_findings=`<N>`; blocked_findings=`<N>`; stale_findings=`<N>`; change_applied=`<yes|no>`; result=`<continue|local_clean>`

**Pass trace**
- Core passes planned: `3`; core passes executed: `<3>`
- Delta passes planned: `<0|2>`; delta passes executed: `<0|2>`
- Total core/delta passes executed: `<3|5>`
- `P1 Safety` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`
- `P2 Surface` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`
- `P3 Audit` -> `<done>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`
- If delta passes executed, also include `P4` and `P5` lines in the same format.
- `Post-self-review rerun` -> executed=`<yes|no>`; edits=`<yes|no>`; signal=`<cmd|n/a>`; result=`<ok|fail|n/a>`

**Validation**
- <cmd> -> <ok/fail>
- `{"baseline_cmd":"<cmd|n/a>","baseline_result":"<ok|fail|n/a>","proof_hook":"<test/assert/log|n/a>","final_cmd":"<cmd>","final_result":"<ok|fail>"}` (single-line JSON)

**Self-review loop trace**
- If none: `- None (skip_gate)`
- Otherwise: `S#` prompt=`If you could change one thing about this changeset what would you change?`; answer_summary=<...>; finding=`<F#|none>`; change_applied=`<yes|no>`; proof=`<cmd|n/a>`; result=`<ok|fail|n/a>`; stop_reason=`<continue|no_new_actionable_changes|blocked>`

**Residual risks / open questions**
- If none: `- None`
- Otherwise: `- <file:line or token> — blocked_by=<product_ambiguity|breaking_change|no_repro_or_proof|scope_guardrail|generated_output|external_dependency|perf_unmeasurable> — next=<one action>`

## Pitfalls
- Vague advice without locations.
- "Nice-to-have" refactors that don’t reduce risk.
- Feature creep.
- Continuing broad repo critique or planning under a completed `$fix` label.
- Asking for risk tolerance instead of applying the default policy.
- Treating skill-artifact refinement as in-band `$fix` work instead of using `$refine`.
- Tightening presented as optional.
- Ownership fixes without proven allocator/owner.
- Editing generated/third-party outputs instead of source-of-truth.
- Code edits without a failing proof hook when baseline was ok.
- Recomputing the diff-review comparison or mutating the literal review prompt text.
- Folding the diff review loop into `Pass trace` instead of `Review loop trace`.
- Using `Residual risks / open questions` as a substitute for fixable findings.

## Activation cues
- "resolve" / "fix" / "crash" / "data corruption"
- "$fix this PR" / "$fix current branch" / "fix this branch"
- "Review the code changes against the base branch" / "merge base commit" / "git diff <sha>"
- "CI failed" / "fix the red checks" / "repair failing PR"
- "footgun" / "misuse" / "should never happen"
- "invariant" / "lifetime" / "nullable surprise"
- "too complex" / "branch soup" / "cross-file hops"
