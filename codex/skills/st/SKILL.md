---
name: st
description: Manage persistent task plans in a repository-committed JSONL log so plan state survives turns and sessions and stays reviewable in git. Use when users ask to export/import Codex plans, keep TODO state on disk, resume a plan across sessions, checkpoint milestones, track task dependencies, or maintain shared task status in repo files.
---

# st

## Overview

Maintain a durable plan file in the repo (default: `.codex/st-plan.jsonl`) using an append-only JSONL event log with first-class dependency edges (`deps`) and deterministic state rendering.

## Workflow

1. Resolve repository root and plan path.
2. Initialize plan storage with `scripts/st_plan.py init` if missing.
3. Rehydrate current state with `scripts/st_plan.py show` to see lifecycle status and dependency state.
4. Apply plan mutations through script subcommands (`add`, `set-status`, `set-deps`, `remove`); do not hand-edit existing JSONL lines.
5. Export/import snapshots when cross-session handoff is needed.

## Commands

Run commands from the target repository root.

```bash
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py init --file .codex/st-plan.jsonl
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py add --file .codex/st-plan.jsonl --id st-001 --step "Reproduce failing test" --deps ""
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py add --file .codex/st-plan.jsonl --id st-002 --step "Patch core logic" --deps "st-001"
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py set-status --file .codex/st-plan.jsonl --id st-001 --status in_progress
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py set-deps --file .codex/st-plan.jsonl --id st-002 --deps "st-001,st-003"
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py show --file .codex/st-plan.jsonl --format markdown
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py export --file .codex/st-plan.jsonl --output .codex/st-plan.snapshot.json
uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py import-plan --file .codex/st-plan.jsonl --input .codex/st-plan.snapshot.json --replace
```

## Operating Rules

- Keep exactly one `in_progress` item unless `--allow-multiple-in-progress` is explicitly used.
- Track prerequisites in each item's `deps` array; dependencies are part of the canonical JSONL schema.
- Require dependency integrity:
  - dependency IDs must exist in the current plan,
  - no self-dependencies,
  - no dependency cycles.
- Allow `in_progress` and `completed` only when all dependencies are `completed`.
- Normalize user status terms before writing:
  - `open`, `queued` -> `pending`
  - `active`, `doing` -> `in_progress`
  - `done`, `closed` -> `completed`
- Preserve history by appending events; use `import-plan --replace` to atomically reset state while retaining an auditable log.
- Prefer concise, stable item IDs (`st-001`, `st-002`, ...).
- Prefer `show --format markdown` for execution: it groups steps into `Ready`, `Waiting on Dependencies`, `In Progress`, and terminal/manual buckets.

## Sync Checklist (`$st` -> `update_plan`)

- After each `$st` mutation (`add`, `set-status`, `set-deps`, `remove`, `import-plan --replace`), run:
  - `uv run ~/.dotfiles/codex/skills/st/scripts/st_plan.py show --file .codex/st-plan.jsonl --format json`
- Publish `update_plan` in the same turn using the same item order as `$st`.
- Map statuses:
  - `in_progress` -> `in_progress`
  - `completed` -> `completed`
  - `pending`, `blocked`, `deferred`, `canceled` -> `pending`
- Keep dependency edges only in `$st` (`deps`); do not encode dependencies in `update_plan`.
- If an item has `dep_state=waiting_on_deps`, never publish that step as `in_progress` in `update_plan`.
- Before final response on turns that mutate `$st`, re-check no-drift by comparing `show --format json` against the latest `update_plan` payload.

## Validation

- Run sync smoke test:
  - `uv run ~/.dotfiles/codex/skills/st/scripts/smoke_sync.py`

## References

- Read `references/jsonl-format.md` for event schema, status/dependency state vocabulary, and snapshot import/export shapes.
