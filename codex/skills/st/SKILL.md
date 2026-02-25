---
name: st
description: Manage persistent task plans in repo-committed JSONL (`.step/st-plan.jsonl`) so state survives turns/sessions and stays reviewable in git. Use when users ask to "use $st", "resume the plan", "export/import plan state", "checkpoint milestones", "track dependencies/blocked work", "show ready next tasks", "keep shared TODO status on disk", "map a `$select` plan into durable execution state", "prove `$st` works for implementation tracking", or diagnose/repair `st-plan.jsonl` concerns (for example append-only vs mutable semantics, lock-file gitignore policy, or seq/checkpoint integrity).
---

# st

## Overview

Maintain a durable plan file in the repo (default: `.step/st-plan.jsonl`) using in-place JSONL v3 persistence with dual lanes:

- `event` lane for mutations
- `checkpoint` lane for periodic full-state snapshots

Plan items use typed dependency edges (`deps: [{id,type}]`) plus `notes` and `comments`, and render deterministically through `show`/read views.

## Workflow

1. Resolve repository root and plan path.
2. If the run has 3+ dependent steps, likely spans turns, or already uses `update_plan`, adopt `$st` as the durable source of truth before editing.
3. If the plan came from `$select`, map selected units into stable `$st` IDs and dependency edges before execution starts.
4. Initialize plan storage with `scripts/st_plan.py init` if missing.
5. Rehydrate current state with `scripts/st_plan.py show` (or focused views via `ready` / `blocked`).
6. Run `doctor` when ingesting an existing plan file or when integrity is in doubt.
7. Apply plan mutations through script subcommands (`add`, `set-status`, `set-deps`, `set-notes`, `add-comment`, `remove`, `import-plan`); do not hand-edit existing JSONL lines.
8. After each mutation command, consume the emitted `update_plan: {...}` payload and publish `update_plan` in the same turn.
9. Use `emit-update-plan` to regenerate the payload from durable state when needed.
10. Export/import snapshots when cross-session handoff is needed.

## Commands

Run commands from the target repository root.

```bash
CODEX_SKILLS_HOME="${CODEX_HOME:-$HOME/.codex}"
CLAUDE_SKILLS_HOME="${CLAUDE_HOME:-$HOME/.claude}"
ST_PLAN="$CODEX_SKILLS_HOME/skills/st/scripts/st_plan.py"
[ -f "$ST_PLAN" ] || ST_PLAN="$CLAUDE_SKILLS_HOME/skills/st/scripts/st_plan.py"
ST_QUERY="$CODEX_SKILLS_HOME/skills/st/scripts/st_query_fast.sh"
[ -f "$ST_QUERY" ] || ST_QUERY="$CLAUDE_SKILLS_HOME/skills/st/scripts/st_query_fast.sh"

uv run "$ST_PLAN" init --file .step/st-plan.jsonl
uv run "$ST_PLAN" add --file .step/st-plan.jsonl --id st-001 --step "Reproduce failing test" --deps ""
uv run "$ST_PLAN" add --file .step/st-plan.jsonl --id st-002 --step "Patch core logic" --deps "st-001"
uv run "$ST_PLAN" set-status --file .step/st-plan.jsonl --id st-001 --status in_progress
uv run "$ST_PLAN" set-deps --file .step/st-plan.jsonl --id st-002 --deps "st-001:blocks,st-003:blocks"
uv run "$ST_PLAN" set-notes --file .step/st-plan.jsonl --id st-002 --notes "Need benchmark evidence"
uv run "$ST_PLAN" add-comment --file .step/st-plan.jsonl --id st-002 --text "Pausing until CI clears" --author tk
uv run "$ST_PLAN" ready --file .step/st-plan.jsonl --format markdown
uv run "$ST_PLAN" blocked --file .step/st-plan.jsonl --format json
uv run "$ST_PLAN" show --file .step/st-plan.jsonl --format markdown
uv run "$ST_PLAN" doctor --file .step/st-plan.jsonl
uv run "$ST_PLAN" doctor --file .step/st-plan.jsonl --repair-seq
uv run "$ST_PLAN" emit-update-plan --file .step/st-plan.jsonl
uv run "$ST_PLAN" export --file .step/st-plan.jsonl --output .step/st-plan.snapshot.json
uv run "$ST_PLAN" import-plan --file .step/st-plan.jsonl --input .step/st-plan.snapshot.json --replace
```

## Operating Rules

- Keep exactly one `in_progress` item unless `--allow-multiple-in-progress` is explicitly used.
- Track prerequisites in each item's typed `deps` array; dependencies are part of the canonical JSONL schema.
- Parse CLI deps as comma-separated `id` or `id:type` tokens; missing type normalizes to `blocks`, and type must be kebab-case.
- Require dependency integrity:
  - dependency IDs must exist in the current plan,
  - no self-dependencies,
  - no dependency cycles.
- Allow `in_progress` and `completed` only when all dependencies are `completed`.
- Normalize user status terms before writing:
  - `open`, `queued` -> `pending`
  - `active`, `doing` -> `in_progress`
  - `done`, `closed` -> `completed`
- Mutation commands (`add`, `set-status`, `set-deps`, `set-notes`, `add-comment`, `remove`, `import-plan`) automatically print an `update_plan:` payload line after durable write.
- Lock sidecar policy: mutating commands require the lock file (`<plan-file>.lock`, for example `.step/st-plan.jsonl.lock`) to be gitignored when inside a git repo; add it to `.gitignore` before first mutation.
- Storage model: not append-only growth. Mutations rewrite the JSONL file atomically (`temp` + `fsync` + `os.replace`) and compact to a canonical `replace` event plus checkpoint snapshot at the current seq watermark.
- `doctor` is the first-line integrity check for seq/checkpoint contract issues; use `doctor --repair-seq` only when repair is explicitly needed.
- `import-plan --replace` atomically resets state in the same in-place write model.
- Prefer concise, stable item IDs (`st-001`, `st-002`, ...).
- Prefer `show --format markdown` for execution: it groups steps into `Ready`, `Waiting on Dependencies`, `In Progress`, and terminal/manual buckets.

## Fast Query Helper (`jq` + `rg`)

- Use `scripts/st_query_fast.sh` for low-latency read-only queries against large logs.
- Requires both `jq` and `rg` on `PATH`.
- Examples:
  - `"$ST_QUERY" --file .step/st-plan.jsonl ready`
  - `"$ST_QUERY" --file .step/st-plan.jsonl blocked`
  - `"$ST_QUERY" --file .step/st-plan.jsonl show`
  - `"$ST_QUERY" --file .step/st-plan.jsonl show st-002`

## Sync Checklist (`$st` -> `update_plan`)

- After each `$st` mutation (`add`, `set-status`, `set-deps`, `set-notes`, `add-comment`, `remove`, `import-plan`), parse the emitted `update_plan: {...}` line and publish `update_plan` in the same turn.
- If no emitted payload is available (for example after `init` or shell piping), run:
  - `uv run "$ST_PLAN" emit-update-plan --file .step/st-plan.jsonl`
- Preserve item ordering from `$st` in `update_plan`.
- Map statuses:
  - `in_progress` -> `in_progress`
  - `completed` -> `completed`
  - `pending`, `blocked`, `deferred`, `canceled` -> `pending`
- Keep dependency edges only in `$st` (`deps`); do not encode dependencies in `update_plan`.
- If an item has `dep_state=waiting_on_deps`, never publish that step as `in_progress` in `update_plan`.
- Before final response on turns that mutate `$st`, re-check no drift by comparing:
  - `uv run "$ST_PLAN" show --file .step/st-plan.jsonl --format json`
  - the latest emitted `update_plan` payload.

## Validation

- Run lightweight CLI sanity checks:
  - `uv run "$ST_PLAN" --help`
  - `uv run "$ST_PLAN" doctor --file .step/st-plan.jsonl`
  - `uv run "$ST_PLAN" emit-update-plan --file .step/st-plan.jsonl`
  - `uv run "$ST_PLAN" show --file .step/st-plan.jsonl --format json`

## References

- Read `references/jsonl-format.md` for event schema, status/dependency state vocabulary, and snapshot import/export shapes.
