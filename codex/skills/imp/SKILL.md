---
name: imp
description: Unified shipping + TRACE self-review protocol (beads, proof, PR). Explicit-only.
---

# IMP

## Intent
Ship bead-scoped changes end-to-end with proof, then immediately self-review the resulting PR using TRACE and fix what you find.

IMP is a combined *execution + review + closure* protocol:
- Write code with strong invariants and minimal incision.
- Validate with a full check suite.
- Open a PR.
- Review that PR right away and resolve findings.
- Select the next bead (so bead state is committed).
- Update/monitor/merge/cleanup (CL).

## Definition of Done (IMP)
An `imp` run is done when:
- The bead’s acceptance criteria are satisfied.
- The working tree contains only bead-aligned changes.
- Format + lint/typecheck + build + tests have run (or are explicitly recorded as unavailable).
- `$close-the-loop` is invoked and at least one signal is recorded.
- The worked bead is marked `done` before PR creation.
- A PR is opened.
- A TRACE self-review is produced (in chat) and all 🔥 + 🟡 items are resolved.
- `$select` is run once (to pick exactly one next bead), and resulting bead state changes (e.g. `issues.jsonl`) are committed into the PR.
- The PR is updated and squash-merged when either:
  - CI is green, or
  - CI is billing-blocked (`billing` appears in CI failure text), `zig build ci` passes, and the PR is squash-mergeable.
- Local state is cleaned up.
- A bead comment exists with PR link + proof summary.

## Guardrails
- Explicit-only; never auto-trigger.
- Source of truth: `bd` wins.
- Surgeon’s principle: smallest correct change.
- No intentional product/semantic changes without clarifying.
- Don’t split into multiple PRs unless explicitly asked.
- Don’t merge until the final CL step.

## Autonomy gate (conviction)
Proceed without asking only when all are true:
- Local repro (or a tight, credible signal).
- Invariant stated.
- Minimal diff.
- At least one validation signal passes.

Otherwise: clarify before editing.

## Core doctrine (canonical)
This section is the single source of truth for how we write and review code.

### Surgeon’s principle
- Prefer the smallest change that could be correct.
- Make progress legible and reversible.
- Trade breadth for certainty: keep diffs bead-scoped.

### TRACE checklist
- Type: make invalid states unrepresentable.
- Readability: understandable in 30 seconds.
- Atomic: one responsibility; explicit side effects.
- Cognitive: minimize branching/hidden deps/cross-file hops.
- Essential: keep only domain-required complexity.

### Complexity Mitigator (CM)
- Keep essential complexity; vaporize incidental.
- Default sequence: flatten → rename → extract.
- If simplification requires new invariants, strengthen them first.

### Invariant Ace (IA)
- Name the invariant at risk and current protection level.
- Prefer construction-time/compile-time guarantees.
- If that’s not viable, add the tightest test/assertion that locks the invariant.

### Universalist (UN)
- Prefer the smallest algebra that fits: product/coproduct/monoid before higher abstractions.
- Name the laws (identity/associativity/composition) and add a lightweight check when feasible.

## Workflow

### 0) Preflight (don’t skip)
- Confirm the repo uses beads (a `.beads/` directory exists).
- Confirm `imp` was explicitly invoked.
- If anything blocks progress (missing requirements, no bead, unrelated diffs), stop and resolve before coding.

### 1) Identify the active bead (source of truth)
1. Anchor on `bd` (not chat context).
2. Find the in-progress bead.
3. If no bead is in progress: invoke `$select` to pick the next `bd ready` bead, then mark it in progress.
4. Restate what “done” means for this bead (1 sentence + acceptance criteria).

### 2) Clarify until requirements are implementable
- Ask only judgment calls (preferences, tradeoffs, acceptance thresholds).
- Everything else should be discovered in-repo (code, tests, conventions) or in the bead.
- If you encounter ambiguity mid-implementation, stop and re-clarify.

### 3) Audit the working tree (scope containment)
- Audit changes early and often.
- Keep only bead-aligned diffs.
- Do not smuggle in drive-by refactors.

If you find unrelated work:
- Revert/stash it (or split it only if explicitly asked).

### 4) Mandatory TRACE mini-pass (before first incision)
Before changing code, do a small `$fix` pass:
1. Cognitive heat map: note hotspots + surprises.
2. Triage failure modes: crash > corruption > logic.
3. State the invariant: what must remain true after the change?
4. Footgun scan: any misuse-prone surface being touched?
5. Incidental complexity: plan to flatten/rename/extract only if it reduces risk.

### 5) Complexity gate (invoke CPS)
If you identify a *complex problem* (multi-constraint, cross-subsystem, high uncertainty, or multiple viable designs), invoke `$creative-problem-solver`.

CPS autonomy rule:
- If a clear **Advantage Play** or **Moonshot** emerges, pick one and proceed.
- Otherwise, ask for human selection before implementation.

Record (in chat and later in proof): chosen tier + rationale + escape hatch.

### 6) Surgeon loop (implement + re-check)
Use a tight loop so progress stays legible and reversible:
1. Form a hypothesis: what change likely satisfies the bead?
2. Choose the smallest incision: smallest change that could be correct.
3. Make it observable: add/adjust a test, invariant, or log to prove/diagnose.
4. Implement: modify code with minimal collateral.
5. Re-check locally: re-run the closest fast signal (focused test, typecheck, repro script).
6. Repeat until acceptance criteria pass.

Heuristics by bead type:
- Bug: reproduce if possible; otherwise create a characterization test or diagnostic signal, then fix.
- Feature: implement the smallest end-to-end slice that users can exercise (vertical slice > layered scaffolding).
- Refactor: preserve behavior; add a characterization test/invariant first.

### 7) Validation (all musts)
Run these categories every time:
- Formatters (autoformat).
- Lint/typecheck (static analysis).
- Build (compile/package).
- Tests (unit/integration as available).

Order (fastest-first):
- Run the fastest local checks first (formatter + lint/typecheck + focused tests).
- Then run the slower checks (build + full test suites).

Entry points:
- Prefer the repo’s canonical entrypoints (`make`, `just`, `task`, `npm run`, `cargo`, `go test`, etc.).
- If multiple relevant entrypoints exist for a category, run all of them (or explicitly justify why one is skipped).

If a category genuinely doesn’t exist, record it as **N/A** in proof with a 1-line reason and run the nearest substitute.

Billing-only CI substitute (Zig):
- Trigger: hosted CI is blocked (CI failure text contains `billing`).
- Run `zig build ci` before opening the PR.
- If CI is still not green at merge time, run `zig build ci` again immediately before squash-merge.
- If `zig build ci` is unavailable, record **N/A**.

### 8) Invoke `$close-the-loop` (required)
`$close-the-loop` is the forcing function: record at least one signal after you’ve made the change and run validations.

### 9) Close the worked bead (required)
Before creating the PR:
- Mark the worked bead as `done`.

Note: this typically updates bead state files (e.g. `issues.jsonl`). Those changes are part of the workflow and must be included in the PR.

### 10) Open a PR (do not merge yet)
- Open a single PR.
- Do not merge yet.

### 11) Immediate TRACE self-review (required, post-PR)
Review the PR output immediately and resolve findings.

Rules:
- Findings must be in severity order.
- Include `file:line` references.
- Include violated TRACE letters.
- Resolve all 🔥 + 🟡 items (no deferrals).

If fixes are required:
- Apply smallest sound fixes.
- Re-run validations (Step 7).
- Re-invoke `$close-the-loop` (Step 8).
- Repeat review until no 🔥 or 🟡 remain.

### 12) Select the next bead (required, post-review)
Run the `$select` workflow once to choose exactly one next bead.

Intent:
- Pick the next `bd ready` bead via risk-first heuristics.
- Verify dependency/readiness.
- Add missing deps and restart selection when needed.
- Mark the chosen bead `in_progress` and leave a short rationale comment.

Critical requirement:
- The bead state changes produced here (commonly `issues.jsonl` updates) must be committed and included in the current PR.

### 13) CL: update PR → check CI + mergeability → squash → cleanup
Follow `codex/prompts/CL.md`, with a billing-only CI bypass:

1. Update the PR.
2. Confirm the PR is squash-mergeable (no merge conflict). If conflicting, merge/rebase the base branch and resolve conflicts.
3. Check CI status (e.g., `gh pr checks`).
4. If CI is green: squash-merge.
5. If CI is not green:
   - If CI failure text contains `billing`: run `zig build ci` (again, immediately before merge). If it passes and the PR is squash-mergeable, squash-merge.
   - Otherwise: keep fixes minimal, and iterate until CI is green.
6. Cleanup local state.

CI policy:
- Default: treat non-`billing` CI failures as real (fix → re-run validations + `$close-the-loop`).
- Bypass: only skip “wait for green” when CI failure text contains `billing`.

### 14) Record proof (make results auditable)
Record proof in both places:
- PR description: full command list + outcomes.
- Bead comment: short proof summary + PR link.

Proof should include:
- Signals: commands run and outcomes.
- Decision: if CPS was used, record tier + rationale + escape hatch.
- Notes: any N/A validations, known limitations.

## Deliverable format (chat)

### A) Work summary
- Bead: `<id>` + 1-sentence “done means”.
- Change summary: what and why.

### B) TRACE self-review (severity order)
For each finding:
- `file:line` — issue — violated TRACE letters — fix applied.

### C) Proof
- Format: `<cmd>` → `<ok/fail>`
- Lint/typecheck: `<cmd>` → `<ok/fail>`
- Build: `<cmd>` → `<ok/fail>`
- Tests: `<cmd>` → `<ok/fail>`
- CI substitute (if `billing`): `zig build ci` (pre-PR; pre-merge if needed) → `<ok/fail>`
- `$close-the-loop`: `<signal>`
- PR: `<url>`
- Merge: `<squash ok/fail>`
- Bead comment: `<posted/blocked>`

## Failure paths
- No in-progress bead: invoke `$select`, mark chosen bead in progress, then proceed.
- Unclear requirements: stop and ask; do not guess.
- Unrelated diffs: ignore; don't touch or stage; continue. If the requested change would touch the same lines/hunks, stop and ask.
- Validation fails: fix and re-run before opening the PR.
- CI is not green:
  - If CI failure text contains `billing`, run `zig build ci` and treat “squash-mergeable + `zig build ci` ok” as green.
  - Otherwise, keep fixing until CI is green.
- PR is not squash-mergeable (merge conflict): merge/rebase the base branch, resolve conflicts, then re-run validations (Step 7) and retry merge.
- Bug can’t be reproduced: add instrumentation or a characterization test; clearly state limits in proof.

## Activation cues
- "imp"
- "ship this bead"
- "implement then review"
- "PR-ready with proof"
