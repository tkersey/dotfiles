---
name: work
description: Finish the in-progress bead; validate via $close-the-loop; open a PR (do not merge). Explicit-only.
---

# Work (WK)

## Intent
Finish one bead end-to-end, ship PR-ready changes, and attach proof via at least one validation signal.

This skill is a *shipping protocol*: it constrains scope, makes “done” explicit, and requires evidence.

## Definition of Done (WK)
A `work` run is done when:
- The bead’s acceptance criteria are satisfied.
- The working tree contains only bead-aligned changes.
- Format + lint/typecheck + build + tests have run (or are explicitly recorded as unavailable).
- At least one validation *signal* is recorded (see “Proof”).
- A PR is opened (do not merge).

## Workflow

### 0) Preflight (don’t skip)
- Confirm the repo uses beads (a `.beads/` directory exists).
- Confirm `work` was explicitly invoked.
- If anything blocks progress (missing requirements, no bead, unrelated diffs), stop and resolve before coding.

### 1) Identify the active bead (source of truth)
1. Anchor on `bd` (not chat context).
2. Find the in-progress bead.
3. If no bead is in progress: invoke `$select` to pick the next `bd ready` bead, then mark it in progress.
4. Restate what “done” means for this bead (1 sentence + acceptance criteria).

### 2) Clarify until requirements are implementable
- Ask only judgment calls (preferences, tradeoffs, acceptance thresholds).
- Everything else should be discovered in-repo (code, tests, existing conventions) or in the bead.
- If you encounter ambiguity mid-implementation, stop and re-clarify.

### 3) Audit the working tree (scope containment)
- Audit changes early and often.
- Keep only bead-aligned diffs.
- Do not smuggle in drive-by refactors.

If you find unrelated work:
- Revert/stash it (or split it only if explicitly asked).

### 4) Do the work (how the work is accomplished)

#### 4.1) Mandatory TRACE mini-pass (every bead)
Before the first code incision, do a small `$resolve` pass:
1. **Cognitive heat map**: note hotspots + surprises.
2. **Triage failure modes**: crash > corruption > logic.
3. **State the invariant**: what must remain true after the change?
4. **Footgun scan**: any misuse-prone surface being touched?
5. **Incidental complexity**: plan to flatten/rename/extract only if it reduces risk.

#### 4.2) Complexity gate (pause and invoke CPS)
If you identify a *complex problem* (multi-constraint, cross-subsystem, high uncertainty, or multiple viable designs), stop implementation and explicitly invoke `$creative-problem-solver`.
- Generate the five-tier portfolio with expected signals + escape hatches.
- Ask for human selection.
- Resume only after a choice is made.

#### 4.3) Surgeon loop (execution)
Use a tight loop so progress stays legible and reversible:
1. **Form a hypothesis**: what change likely satisfies the bead?
2. **Choose the smallest incision**: smallest change that could be correct.
3. **Make it observable**: add/adjust a test, invariant, or log to prove/diagnose.
4. **Implement**: modify code with minimal collateral.
5. **Re-check locally**: re-run the closest fast signal (focused test, typecheck, repro script).
6. Repeat until acceptance criteria pass.

Autonomy gate (borrowed from `$resolve`): proceed without further clarifying only when all are true:
- Local repro (or a tight, credible signal).
- Invariant stated.
- Minimal diff.
- At least one validation signal passes.

Otherwise: clarify before widening scope.

Heuristics by bead type:
- **Bug**: reproduce if possible; otherwise create a characterization test or diagnostic signal, then fix.
- **Feature**: implement the smallest end-to-end slice that proves the requirement (vertical slice > layered scaffolding).
- **Refactor**: preserve behavior; add a characterization test/invariant first.

Refactor hygiene (within bead scope):
- Limit simplification to code touched by this bead unless explicitly asked.
- Favor explicit, readable code over clever compactness.
- Avoid nested ternaries for multi-branch logic; use if/else or switch equivalents.
- Remove redundant comments; keep clarifying ones.
- Keep helpful abstractions; don’t flatten at the cost of clarity.

### 5) Validation (all musts)
Run these categories every time:
- **Formatters** (autoformat).
- **Lint/typecheck** (static analysis).
- **Build** (compile/package).
- **Tests** (unit/integration as available).

Order (fastest-first):
- Run the fastest local checks first (formatter + lint/typecheck + focused tests).
- Then run the slower checks (build + full test suites).
- A PR is blocked until *all* categories have been run.

Entry points:
- Prefer the repo’s canonical entrypoints (`make`, `just`, `task`, `npm run`, `cargo`, `go test`, etc.).
- If multiple relevant entrypoints exist for a category, run *all* of them (or explicitly justify why one is skipped).

Notes:
- If a category genuinely doesn’t exist in this repo, record it as **N/A** in the proof with a 1-line reason and run the nearest substitute you can.

### 6) Invoke `$close-the-loop` (minimum one signal)
`$close-the-loop` is the forcing function: record at least one signal (see “Proof”) after you’ve made the change and run validations.

### 7) Record proof (make results auditable)
Record proof in both places:
- **PR description** (recommended): full command list + outcomes.
- **Bead comment (when feasible)**: short proof summary + PR link.

“Feasible” means: you can post a bead comment from this environment without extra authentication/permissions friction, and it won’t leak secrets.

A PR template is *not required*, but include:
- **Signals**: command(s) you ran and the outcome.
- **Decision**: if `$creative-problem-solver` was used, record the chosen option/tier + rationale.
- **Notes**: any N/A validations, known limitations, or follow-ups.

Validation signal strength (prefer higher):
1. Tests passing (best).
2. Build succeeded.
3. Lint/typecheck clean.
4. Formatter clean / no diff.
5. Runtime log / manual repro notes (only if tests aren’t viable).

### 8) Open a PR (do not merge)
- Open a single PR.
- Do not merge.
- Do not split into multiple PRs unless explicitly asked.

## Principles
- Source of truth: `bd` wins.
- Safety nets: prefer compile-time/construction-time invariants; else a focused test; else a minimal guard/log.
- Surgeon’s principle: smallest correct change.

## Failure Paths (what to do when things go wrong)
- **No in-progress bead**: invoke `$select`, mark chosen bead in progress, then proceed.
- **Unclear requirements**: stop and ask; do not guess.
- **Unrelated diffs**: revert/stash; do not widen scope.
- **Validation fails**: fix and re-run before opening the PR.
- **Bug can’t be reproduced**: add instrumentation or a characterization test; clearly state limits in proof.

## Deliverable
- PR-ready changes (formatted, linted/typechecked, built, tested).
- Handoff includes: assumptions, proof (signals), and deliberate non-scope.

## Examples (calibration)

### Bug bead (example run)
1. `bd` shows bead `X` is in progress; restate “done”.
2. Mandatory TRACE mini-pass (heat map, failure modes, invariant).
3. Reproduce bug (or add characterization test).
4. Apply smallest fix.
5. Run fastest checks first (format + lint/typecheck + focused tests).
6. Run slower checks next (build + full test suites).
7. Record proof in PR body; add a bead comment with a short proof summary + PR link.
8. Open PR; do not merge.

### Feature bead (example run)
1. `bd` shows bead `Y` is in progress; restate “done”.
2. Mandatory TRACE mini-pass (heat map, failure modes, invariant).
3. If the feature is a complex problem, invoke `$creative-problem-solver` and pause for selection.
4. Implement smallest vertical slice that users can exercise.
5. Add/extend tests.
6. Run fastest checks first (format + lint/typecheck + focused tests).
7. Run slower checks next (build + full test suites).
8. Record proof in PR body; add a bead comment with a short proof summary + PR link.
9. Open PR; do not merge.

## Guardrails
- Explicit-only; never auto-trigger.
- Don’t split into multiple PRs unless asked.
- Don’t merge.
