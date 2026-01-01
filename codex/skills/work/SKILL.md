---
name: work
description: Finish the in-progress bead; validate via $close-the-loop; open a PR (do not merge). Explicit-only for WK.
---

# Work (WK)

## Overview

Finish the active bead; ship PR-ready changes; validate via $close-the-loop.

## Workflow

1. Identify the in-progress bead; restate what “done” means.
2. Anchor on `bd`; treat session context as hints.
3. Clarify until requirements are complete, then proceed.
4. Audit the working tree; keep only bead-aligned changes.
5. Implement the smallest correct change (surgeon’s principle).
6. Run formatters, build, and tests.
7. Run $close-the-loop and capture at least one signal.
8. Open a PR; do not merge.

## Principles

- **Source of truth:** `bd` wins.
- **Surgeon’s principle:** maximize correctness per byte of change.
- **Safety nets:** prefer the strongest available invariant (compile-time > construction-time > runtime); else the smallest unit test; else a minimal guard/log.
- **Heuristics:**
  - Bug: reproduce if possible; else speculative fix + safety net.
  - Feature: smallest end-to-end slice that proves the requirement.
  - Refactor: preserve behavior; add a characterization test or invariant first.

## Deliverable

- PR-ready changes with formatting/build/tests complete and $close-the-loop satisfied.
- Final handoff message includes:
  - **Assumptions:** what was inferred
  - **Proof:** $close-the-loop signal(s)
  - **Scope:** what was intentionally not done

## Examples

- Finish an "add CSV export" bead, run `uv run pytest` + formatters, invoke $close-the-loop, then open a PR titled "Add CSV export (bd-123)".
- Complete a lint-fix bead, ensure `npm test` passes, invoke $close-the-loop, then open a PR (no merge).

## Guardrails

- Explicit-only; never auto-trigger.
- If validation fails, fix and re-run before opening the PR.
- Do not split work into multiple PRs unless asked.
- Do not merge.
