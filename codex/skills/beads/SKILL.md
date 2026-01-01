---
name: beads
description: bd (beads) issue-tracking workflow; use when `.beads/` exists or when running `bd` commands.
---

# Beads

## When to use
- The repo uses `bd` (a `.beads/` directory exists).
- The user asks for `bd` commands (`bd ready`, `bd create`, `bd close`, `bd sync`, …).

## Quick start
1. Run `bd prime` to load workflow context.
2. Install hooks if needed: `bd hooks install`.

## Command quick reference
- `bd ready` — list unblocked work
- `bd create "Title" --type task --priority 2` — create an issue
- `bd close <id>` — close an issue
- `bd sync` — sync with git (typically end of session)

## Notes
- For the full workflow, run `bd prime`.
