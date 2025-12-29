---
name: work
description: Finish the current in-progress bead and hand off PR-ready changes with build/test/format completed; explicit invocation only for the WK (Work) workflow (complete the bead, validate, open a PR, do not merge).
---

# Work (WK)

## Overview

Finish the active bead and deliver a PR-ready change set with validation complete.

## Workflow

1. Identify the current in-progress bead and resume it.
2. Continue until the work is complete.
3. Run build, tests, and formatters before wrapping.
4. Open a PR with the changes; do not merge it.

## Deliverable

Provide PR-ready changes with build/test/format completed.

## Examples

- Finish an "add CSV export" bead, run `uv run pytest` and formatters, then open a PR titled "Add CSV export (bd-123)".
- Complete a lint-fix bead, ensure `npm test` passes, and push a PR without merging.

## Guardrails

- Treat this as explicit-only; do not auto-trigger.
- If validation fails, fix and re-run the relevant checks before opening the PR.
