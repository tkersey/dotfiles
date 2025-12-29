---
name: work
description: Finish the current in-progress bead and hand off PR-ready changes; $close-the-loop validation required; explicit invocation only for the WK workflow (complete the bead, validate, open a PR, do not merge).
---

# Work (WK)

## Overview

Finish the active bead and deliver a PR-ready change set with validation complete via $close-the-loop.

## Workflow

1. Identify the in-progress bead and resume it.
2. Complete the work.
3. Run build, tests, and formatters.
4. Invoke $close-the-loop and obtain at least one feedback signal.
5. Open a PR; do not merge it.

## Deliverable

Provide PR-ready changes with build/test/format completed and $close-the-loop satisfied.

## Examples

- Finish an "add CSV export" bead, run `uv run pytest` and formatters, invoke $close-the-loop, then open a PR titled "Add CSV export (bd-123)".
- Complete a lint-fix bead, ensure `npm test` passes, invoke $close-the-loop, and push a PR without merging.

## Guardrails

- Treat this as explicit-only; do not auto-trigger.
- If validation fails, fix and re-run the relevant checks before opening the PR.
- Do not skip $close-the-loop; it is required for final validation.
