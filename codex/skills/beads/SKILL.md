---
name: beads
description: Beads (bd) issue-tracking workflow and repo deltas; use when creating/claiming/updating/closing beads, managing dependencies/epics/subtasks, or coordinating work in bd.
---

# Beads

## Canonical reference
- Use `.beads/BD_GUIDE.md` for the full bd workflow and command catalog.
- If missing or stale, regenerate it:
  ```bash
  bd onboard --output .beads/BD_GUIDE.md
  ```

## Repo deltas (must follow)
- Start the daemon and keep it running for the session:
  ```bash
  bd daemon start --auto-commit --auto-push
  ```
- Confirm the metadata sync branch is `beads-metadata`:
  ```bash
  bd config get sync.branch
  bd config set sync.branch beads-metadata --json
  ```
- Save Closure Notes in `notes` (exported), not comments; comments are scratch only.
- Never create docs-only beads; embed doc updates in each bead's description/design/acceptance.
- Warm-start memory in new sessions:
  ```bash
  bd list --status closed --sort closed --reverse --limit 10 --json
  bd show <id> --json
  ```
