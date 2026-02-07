---
name: st
description: Manage persistent task plans in a repository-committed JSONL log so plan state survives turns and sessions and stays reviewable in git. Use when users ask to export/import Codex plans, keep TODO state on disk, resume a plan across sessions, checkpoint milestones, or maintain shared task status in repo files.
---

# st

## Overview

Maintain a durable plan file in the repo (default: `.codex/st-plan.jsonl`) using an append-only JSONL event log plus deterministic state rendering.

## Workflow

1. Resolve repository root and plan path.
2. Initialize plan storage with `scripts/st_plan.py init` if missing.
3. Rehydrate current state with `scripts/st_plan.py show`.
4. Apply plan mutations through script subcommands; do not hand-edit existing JSONL lines.
5. Export/import snapshots when cross-session handoff is needed.

## Commands

Run commands from the target repository root.

```bash
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py init --file .codex/st-plan.jsonl
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py add --file .codex/st-plan.jsonl --step "Reproduce failing test"
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py set-status --file .codex/st-plan.jsonl --id st-001 --status in_progress
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py show --file .codex/st-plan.jsonl --format markdown
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py export --file .codex/st-plan.jsonl --output .codex/st-plan.snapshot.json
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py import-plan --file .codex/st-plan.jsonl --input .codex/st-plan.snapshot.json --replace
```

## Operating Rules

- Keep exactly one `in_progress` item unless `--allow-multiple-in-progress` is explicitly used.
- Normalize user status terms before writing:
  - `open`, `queued` -> `pending`
  - `active`, `doing` -> `in_progress`
  - `done`, `closed` -> `completed`
- Preserve history by appending events; use `import-plan --replace` to atomically reset state while retaining an auditable log.
- Prefer concise, stable item IDs (`st-001`, `st-002`, ...).

## References

- Read `references/jsonl-format.md` for event schema, status vocabulary, and snapshot import/export shapes.
