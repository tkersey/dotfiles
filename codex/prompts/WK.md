# Work (WK)
- **Purpose:** Finish the current in-progress bead and hand off a ready-for-review change.
- **Process:**
  - Pick up the in-progress bead and continue until the work is complete.
  - Run build, tests, and formatters before wrapping.
  - Open a PR with the changes; do not merge it.
- **Deliverable:** PR-ready changes with build/test/format completed.
- **Examples:**
  - Finish an "add CSV export" bead, run `uv run pytest` and formatters, then open a PR titled "Add CSV export (bd-123)".
  - Complete a lint-fix bead, ensure `npm test` passes, and push a PR without merging.
