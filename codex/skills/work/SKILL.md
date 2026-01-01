---
name: work
description: Finish the in-progress bead; validate via $close-the-loop; open a PR (do not merge). Explicit-only.
---

# Work (WK)

## Intent
Finish the active bead, ship PR-ready changes, and close the loop with at least one validation signal.

## Workflow
1. Identify the in-progress bead; restate what “done” means.
2. Anchor on `bd`; treat chat context as hints.
3. Clarify until requirements are complete.
4. Audit the working tree; keep only bead-aligned changes.
5. Implement the smallest correct change (surgeon’s principle).
6. Run formatters/build/tests as appropriate.
7. Invoke `$close-the-loop` and record at least one signal.
8. Open a PR; do not merge.

## Principles
- Source of truth: `bd` wins.
- Safety nets: prefer compile-time/construction-time invariants; else a focused test; else a minimal guard/log.
- Heuristics:
  - Bug: reproduce if possible; else speculative fix + safety net.
  - Feature: smallest end-to-end slice that proves the requirement.
  - Refactor: preserve behavior; add a characterization test or invariant first.

## Deliverable
- PR-ready changes (formatted, built, tested where applicable).
- Handoff includes: assumptions, proof (signals), and deliberate non-scope.

## Guardrails
- Explicit-only; never auto-trigger.
- If validation fails, fix and re-run before opening the PR.
- Don’t split into multiple PRs unless asked.
- Don’t merge.
