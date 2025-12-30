---
name: beads
description: Issue tracking workflow using bd (beads). Use when a repo uses bd/beads for issue tracking (for example, when a `.beads/` directory exists) or when asked to run bd commands like `bd ready`, `bd create`, `bd close`, or `bd sync`.
---

# Beads

## Overview

Use `bd` for issue tracking and workflow context. Run `bd prime` to learn the full process, then use the commands below for day-to-day work.

## Workflow

1. Run `bd prime` to load workflow context.
2. Install hooks if needed: `bd hooks install`.

## Quick reference

- `bd ready` - Find unblocked work
- `bd create "Title" --type task --priority 2` - Create issue
- `bd close <id>` - Complete work
- `bd sync` - Sync with git (run at session end)

## Notes

- For full workflow details, run `bd prime`.
