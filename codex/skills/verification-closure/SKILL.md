---
name: verification-closure
description: Use this skill for final-pass verification of a diagnosis, patch, or reviewed change when you need deterministic checks, regression proof, explicit merge or release confidence, and a grounded done or not-done decision. Trigger for final validation, CI closure, pre-merge confidence, bug-fix confirmation, migration completion, refactor validation, release gating, flaky-test triage, and tasks phrased as verify, validate, regression-check, close out, readiness, is this done, or is this safe to merge. Do not trigger for initial implementation or broad design review unless the task explicitly asks for verification-first. Do not trigger for trivial formatting, rote renames, or purely informational questions with no artifact or command surface to verify.
---

# Verification Closure

This is a **verification** skill. Default posture: verify claims, close evidence gaps, and decide readiness. Do **not** redesign or re-implement unless the user explicitly asks for changes after the verification pass.

Operate in **UNSOUND**, **MECHANISTIC**, **ACCRETIVE**, and **TRACEABLE** mode, with **DETERMINISTIC** verification discipline.

## Core doctrine

### UNSOUND
- Reject claims of correctness, completion, or safety that are not supported by evidence.
- Separate what was observed, what was inferred, and what remains assumed.
- Treat passing checks as evidence, not proof.
- If the direct behavior was not exercised, do not say the change is verified.

### MECHANISTIC
- Verify through causal paths, state transitions, contracts, and invariants.
- Map each check to the behavior, code path, or failure mechanism it is meant to exercise.
- Distinguish root-cause validation from incidental green tests.
- Prefer checks that directly falsify or support the claimed fix.

### ACCRETIVE
- Start with the smallest high-signal verification that can confirm or falsify the claim.
- Expand verification only as risk, failure, or uncertainty justifies it.
- Prefer existing project scripts, canonical test entry points, and targeted checks before broader suites.
- Avoid verification theater: do not run large, low-signal suites when a smaller direct check is more informative.

### TRACEABLE
- Tie confidence to concrete evidence: commands, test files, outputs, logs, diffs, changed symbols, and user constraints.
- Keep a clear ledger of what was run, why it was run, and what it showed.
- State which surfaces remain unverified.
- Make the final readiness judgment auditable.

### DETERMINISTIC
- Prefer reproducible commands, fixed seeds, stable inputs, and controlled environment assumptions when available.
- Call out checks whose results may vary with time, concurrency, randomness, network state, or external services.
- If a result is flaky or non-deterministic, classify it as instability, not proof.
- When determinism is not possible, name the dependency and bound the uncertainty.

## Operating procedure

1. Establish the closure target:
   - requested behavior or bug fix
   - changed files, symbols, and affected surfaces
   - claimed diagnosis and expected outcome
   - known regression risk and invariants that must still hold
   - current verification evidence and merge or release bar

2. Build a minimal evidence plan:
   - direct check for the changed behavior
   - at least one likely regression or contract check
   - one adversarial or negative-path check when relevant
   - broader integration or end-to-end checks only if the risk profile requires them

3. Execute verification in tiers:
   - Tier 1: direct changed-path checks
   - Tier 2: adjacent regression, contract, or invariant checks
   - Tier 3: broader suite or environment validation only if earlier evidence is insufficient or risk remains material

4. Classify the outcome:
   - **ready**: direct behavior verified, regression surface reasonably checked, no material unexplained failures
   - **conditionally ready**: core behavior verified, but named evidence gaps or environment limits remain
   - **not ready**: direct behavior unverified, failures unexplained, or material risks remain open

5. Report in this order:
   - verification target
   - evidence run
   - results
   - readiness judgment
   - residual risks and exact next checks if needed

## Verification checklist

Challenge the work against these questions:
- Was the changed behavior exercised directly, or only indirectly?
- Does the evidence actually touch the claimed root cause and fix path?
- Are public contracts, data shape, nullability, defaults, timing, retries, cleanup, and persistence still safe?
- Was at least one plausible regression surface checked?
- Are any green results explained by mocks, stale artifacts, caching, or skipped code paths?
- Are external services, clocks, randomness, concurrency, or feature flags hiding uncertainty?
- Is the readiness claim stronger than the evidence supports?

## Hard rules
- Never say "verified" if the direct path was not exercised.
- Never hide failed, flaky, skipped, or blocked checks.
- Never let unrelated green tests substitute for missing direct evidence.
- Never collapse uncertainty into confidence.
- Never broaden into implementation unless explicitly asked.
- Never claim release safety without naming any unverified surfaces.

## Definition of done
A verification pass is done only when:
1. the direct behavior was exercised or a concrete blocker was identified,
2. at least one regression, contract, or invariant check was run or explicitly justified as unnecessary,
3. the final output assigns a readiness state: ready, conditionally ready, or not ready,
4. residual risks, assumptions, and unverified edges are stated plainly.

## Response shape
Use concise sections in this order:
- Verification Target
- Evidence Run
- Results
- Readiness
- Residual Risks
- Next Checks

If evidence is incomplete, say exactly what check would close the gap.
