---
name: work
description: Finish the in-progress bead; validate via $close-the-loop; open a PR (do not merge). Explicit-only.
---

# Work (WK)

## Intent
Ship one bead end-to-end with proof (≥1 validation signal). Shipping protocol: constrain scope, define "done," require evidence.

## Definition of Done (WK)
Done when:
- Bead criteria met.
- Formatter/lint-typecheck/build/tests run (or **N/A**).
- ≥1 validation *signal* recorded (see "Proof").
- PR opened (do not merge).

## Workflow

### 0) Preflight (don't skip)
- Confirm beads repo + explicit `work` invocation; if blocked (missing requirements/no bead), stop.

### 1) Identify the active bead (source of truth)
1. Anchor on `bd`.
2. Find the in-progress bead; if none, invoke `$select` and mark it in progress.
3. Restate "done" for this bead (1 sentence + acceptance criteria).

### 2) Clarify until requirements are implementable
- Ask only judgment calls; everything else is in repo/bead.
- If ambiguity appears mid-implementation, stop and re-clarify.

### 3) Audit the working tree (scope containment)
- Audit early/often; keep bead changes surgical.

### 4) Do the work (how the work is accomplished)

#### 4.1) Mandatory TRACE mini-pass
Before first incision, run a small `$fix` pass:
1. **Heat map**: hotspots + surprises.
2. **Failure triage**: crash > corruption > logic.
3. **Invariant**: what must remain true after the change?
4. **Footgun scan**: any misuse-prone surface?
5. **Incidental complexity**: flatten/rename/extract only if risk drops.

#### 4.2) Complexity gate (pause and invoke CPS)
If complex (multi-constraint, cross-subsystem, high uncertainty, multiple viable designs), stop and invoke `$creative-problem-solver`: produce a five-tier portfolio (signals + escape hatches), ask for selection, resume after choice.

#### 4.3) Surgeon loop (execution)
Tight loop:
1. **Hypothesis**: what change likely satisfies the bead?
2. **Smallest incision**: smallest change that could be correct.
3. **Observable**: test/invariant/log.
4. **Implement**: minimal collateral.
5. **Re-check**: rerun closest fast signal.
6. Repeat until acceptance criteria pass.

Autonomy gate (borrowed from `$fix`): proceed without further clarification only when all are true:
- Local repro (or a tight, credible signal).
- Invariant stated.
- Minimal diff.
- At least one validation signal passes.

Otherwise, clarify before widening scope.

Heuristics by bead type:
- **Bug**: reproduce if possible; otherwise add a characterization test or diagnostic signal, then fix.
- **Feature**: smallest end-to-end slice (vertical slice > layered scaffolding).
- **Refactor**: preserve behavior; add a characterization test/invariant first.

Refactor hygiene (within bead scope):
- Limit simplification to bead-touched code unless explicitly asked.
- Cleanup must preserve behavior beyond bead changes.
- Prefer explicit, readable code; avoid nested ternaries (use if/else/switch).
- Remove redundant comments; keep clarifying ones.
- Keep helpful abstractions; don't flatten at the cost of clarity.

### 5) Validation (all musts)
Run all: **Formatter**, **Lint/typecheck**, **Build**, **Tests** (unit/integration).
Order: formatter + lint/typecheck + focused tests, then build + full suites. PR is blocked until *all* categories run.
Entry points: prefer canonical (`make`, `just`, `task`, `npm run`, `cargo`, `go test`, etc.); if multiple, run *all* or justify the skip.
If a category doesn't exist: record **N/A** with a 1-line reason and run the nearest substitute.

### 6) Invoke `$close-the-loop` (minimum one signal)
`$close-the-loop` is the forcing function: record ≥1 signal (see "Proof") after changes + validations.

### 7) Record proof (make results auditable)
Record proof in:
- **PR description** (recommended): full command list + outcomes.
- **Bead comment** (when feasible): short proof summary + PR link.

"Feasible" = no extra auth friction and no secret leakage.
Include: **Signals**, **Decision** (if CPS ran), **Notes** (N/A validations, limits, follow-ups), **Simplification** (only significant refactors).
Signal strength (prefer higher): tests > build > lint/typecheck > formatter > runtime log/manual repro.

### 8) Open a PR (do not merge)
- Open a single PR.
- Do not merge.
- Do not split into multiple PRs unless explicitly asked.

## Principles
- Source of truth: `bd` wins.
- Safety nets: compile/construction-time invariants > focused test > minimal guard/log.
- Surgeon's principle: smallest correct change.

## Failure Paths
- **No in-progress bead**: invoke `$select`, mark it in progress, proceed.
- **Unclear requirements**: stop and ask; don't guess.
- **Unrelated diffs**: ignore; don't touch or stage; continue. If the task would touch the same lines/hunks, stop and ask.
- **Validation fails**: fix and rerun before opening the PR.
- **Bug can't be reproduced**: add instrumentation or a characterization test; state limits in proof.

## Deliverable
- PR-ready changes (formatted, linted/typechecked, built, tested).
- Handoff includes: assumptions, proof (signals), and deliberate non-scope.

## Examples (calibration)

### Bug bead
1. `bd` shows bead `X`; restate done + acceptance criteria.
2. TRACE mini-pass (heat map, failure modes, invariant).
3. Reproduce or characterize.
4. Smallest fix.
5. Fast checks (format + lint/typecheck + focused tests).
6. Slow checks (build + full suites).
7. Record proof (PR body + bead comment w/ link).
8. Open PR; do not merge.

### Feature bead
1. `bd` shows bead `Y`; restate done + acceptance criteria.
2. TRACE mini-pass (heat map, failure modes, invariant).
3. If complex, invoke `$creative-problem-solver`; pause for selection.
4. Smallest vertical slice users can exercise.
5. Add/extend tests.
6. Fast checks (format + lint/typecheck + focused tests).
7. Slow checks (build + full suites).
8. Record proof (PR body + bead comment w/ link).
9. Open PR; do not merge.

## Guardrails
- Explicit-only; never auto-trigger.
- Don't split into multiple PRs unless asked.
- Don't merge.
