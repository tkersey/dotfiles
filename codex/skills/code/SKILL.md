---
name: code
description: Finish one slice; run full validations; deliver an apply_patch diff + proof. Patch-only. Explicit-only.
---

# Code (CD)

## Intent
Finish one slice end-to-end with proof (≥1 validation signal). Constrain scope, define "done," require evidence. Deliver an `apply_patch` diff (no PR).

## Definition of Done (CD)
Done when:
- Slice acceptance criteria met.
- Formatter/lint-typecheck/build/tests run (or **N/A**).
- ≥1 validation *signal* recorded (see "Proof").
- Handoff includes an `apply_patch` diff + notes.

## Double Diamond mapping
- Discover: anchor on the slice brief + establish a baseline signal.
- Define: restate done + acceptance criteria; name the invariant.
- Develop: if there are real trade-offs, stop and ask (or use `$creative-problem-solver`) for a tier choice.
- Deliver: smallest incision + validations + proof + `apply_patch` diff.

## Workflow

### 0) Preflight (don't skip)
- Confirm slice brief (source of truth) + explicit `code` invocation.
- If missing requirements (acceptance criteria or full validation command list), stop and ask.

### 1) Identify the slice (source of truth)
1. Anchor on the slice brief (issue/ticket description + slice text).
2. Restate "done" for this slice (1 sentence + acceptance criteria).
3. Confirm the exact full validation command list to run; if missing, stop and ask.

### 2) Clarify until requirements are implementable
- Ask only judgment calls; everything else is in repo/slice brief.
- If ambiguity appears mid-implementation, stop and re-clarify.

### 3) Audit the working tree (scope containment)
- Audit early/often; keep diffs surgical.

### 4) Do the work (how the work is accomplished)

#### 4.1) Mandatory TRACE mini-pass
Before first incision, run a small TRACE mini-pass (do not invoke `$fix` unless explicitly instructed):
1. **Heat map**: hotspots + surprises.
2. **Failure triage**: crash > corruption > logic.
3. **Invariant**: what must remain true after the change?
4. **Footgun scan**: any misuse-prone surface?
5. **Incidental complexity**: flatten/rename/extract only if risk drops.

#### 4.2) Complexity gate (stop and ask)
If complex (multi-constraint, cross-subsystem, high uncertainty, multiple viable designs), stop and ask.
Provide a five-tier portfolio (Quick Win, Strategic Play, Advantage Play, Transformative Move, Moonshot), each with an expected signal + escape hatch. Ask for a selection, then resume.
If available, you may use `$creative-problem-solver` to generate the portfolio, but still present it explicitly.

#### 4.3) Surgeon loop (execution)
Tight loop:
1. **Hypothesis**: what change likely satisfies the slice?
2. **Smallest incision**: smallest change that could be correct.
3. **Observable**: test/invariant/log.
4. **Implement**: minimal collateral.
5. **Re-check**: rerun closest fast signal.
6. Repeat until acceptance criteria pass.

Autonomy gate: proceed without further clarification only when all are true:
- Local repro (or a tight, credible signal).
- Invariant stated.
- Minimal diff.
- At least one validation signal passes.

Otherwise, clarify before widening scope.

Heuristics by slice type:
- **Bug**: reproduce if possible; otherwise add a characterization test or diagnostic signal, then fix.
- **Feature**: smallest end-to-end slice (vertical slice > layered scaffolding).
- **Refactor**: preserve behavior; add a characterization test/invariant first.

Refactor hygiene (within slice scope):
- Limit simplification to slice-touched code unless explicitly asked.
- Cleanup must preserve behavior outside the slice.
- Prefer explicit, readable code; avoid nested ternaries (use if/else/switch).
- Remove redundant comments; keep clarifying ones.
- Keep helpful abstractions; don't flatten at the cost of clarity.

### 5) Validation (all musts)
Run all: **Formatter**, **Lint/typecheck**, **Build**, **Tests** (unit/integration).
Order: formatter + lint/typecheck + focused tests, then build + full suites. Patch handoff is blocked until *all* categories run.
Entry points: prefer canonical (`make`, `just`, `task`, `npm run`, `cargo`, `go test`, etc.); if multiple, run *all* or justify the skip.
If a category doesn't exist: record **N/A** with a 1-line reason and run the nearest substitute.

### 6) Collect ≥1 validation signal (minimum one)
After changes + validations, explicitly record ≥1 signal (see "Proof"). Prefer higher-strength signals: tests > build > lint/typecheck > formatter > runtime log/manual repro.

### 7) Record proof (make results auditable)
Record proof in the handoff:
- Commands run + outcomes.
- Signals (≥1; include the strongest).
- Decision (portfolio selection, if used).
- Notes (N/A validations, limits, follow-ups).
- Simplification (only significant refactors).

### 8) Deliver a patch (no PR)
- Deliver an `apply_patch` diff that applies cleanly.
- Stop: no PR/push/commit unless explicitly asked.

## Principles
- Source of truth: the slice brief wins.
- Safety nets: compile/construction-time invariants > focused test > minimal guard/log.
- Surgeon's principle: smallest correct change.

## Failure Paths
- **No slice brief**: stop and request one.
- **Unclear requirements**: stop and ask; don't guess.
- **Unrelated diffs**: ignore; don't touch or stage; continue. If the task would touch the same lines/hunks, stop and ask.
- **Validation fails**: fix and rerun before delivering the patch.
- **Bug can't be reproduced**: add instrumentation or a characterization test; state limits in proof.

## Deliverable
- Patch-ready changes (formatted, linted/typechecked, built, tested).
- Handoff includes: `apply_patch` diff, assumptions, proof (signals), and deliberate non-scope.

## Examples (calibration)

### Bug slice
1. Slice brief shows bug `X`; restate done + acceptance criteria.
2. TRACE mini-pass (heat map, failure modes, invariant).
3. Reproduce or characterize.
4. Smallest fix.
5. Fast checks (format + lint/typecheck + focused tests).
6. Slow checks (build + full suites).
7. Record proof (handoff).
8. Deliver `apply_patch` diff.

### Feature slice
1. Slice brief shows feature `Y`; restate done + acceptance criteria.
2. TRACE mini-pass (heat map, failure modes, invariant).
3. If complex, stop and ask (portfolio); pause for selection.
4. Smallest vertical slice users can exercise.
5. Add/extend tests.
6. Fast checks (format + lint/typecheck + focused tests).
7. Slow checks (build + full suites).
8. Record proof (handoff).
9. Deliver `apply_patch` diff.

## Guardrails
- Explicit-only; never auto-trigger.
- Patch-only: no PR/push/commit unless explicitly asked.
