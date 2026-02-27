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

## Zig CLI Iteration Repos

When iterating on the Zig-backed `st` helper CLI path, use these two repos:

- `skills-zig` (`/Users/tk/workspace/tk/skills-zig`): source for the `st` Zig binary, build/test wiring, and release tags.
- `homebrew-tap` (`/Users/tk/workspace/tk/homebrew-tap`): Homebrew formula updates/checksum bumps for released `st` binaries.

## Quick Start (Automatic Zig Binary + Brew Bootstrap)

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
RUN_ST_SCRIPT="$REPO_ROOT/codex/skills/st/scripts/run_st.sh"
if [ ! -x "$RUN_ST_SCRIPT" ]; then
  echo "run_st bootstrap script missing or not executable: $RUN_ST_SCRIPT" >&2
  exit 1
fi

# Always invoke st through RUN_ST_SCRIPT; it auto-installs tkersey/tap/st on macOS when needed.
"$RUN_ST_SCRIPT" --help
```

## Workflow

1. Resolve repository root and set `RUN_ST_SCRIPT` to `codex/skills/st/scripts/run_st.sh`; use `"$RUN_ST_SCRIPT"` for all commands (do not call `st` directly).
2. If the run has 3+ dependent steps, likely spans turns, or already uses `update_plan`, adopt `$st` as the durable source of truth before editing.
3. If the plan came from `$select`, map selected units into stable `$st` IDs and dependency edges before execution starts.
4. Initialize plan storage with `st init` if missing.
5. Rehydrate current state with `st show` (or focused views via `ready` / `blocked`).
6. Run `doctor` when ingesting an existing plan file or when integrity is in doubt.
7. Apply plan mutations through subcommands (`add`, `set-status`, `set-deps`, `set-notes`, `add-comment`, `remove`, `import-plan`); do not hand-edit existing JSONL lines.
8. After each mutation command, consume the emitted `update_plan: {...}` payload and publish `update_plan` in the same turn.
9. Use `emit-update-plan` to regenerate the payload from durable state when needed.
10. Export/import snapshots when cross-session handoff is needed.

## Commands

Run commands from the target repository root.

```bash
"$RUN_ST_SCRIPT" init --file .step/st-plan.jsonl
"$RUN_ST_SCRIPT" add --file .step/st-plan.jsonl --id st-001 --step "Reproduce failing test" --deps ""
"$RUN_ST_SCRIPT" add --file .step/st-plan.jsonl --id st-002 --step "Patch core logic" --deps "st-001"
"$RUN_ST_SCRIPT" set-status --file .step/st-plan.jsonl --id st-001 --status in_progress
"$RUN_ST_SCRIPT" set-deps --file .step/st-plan.jsonl --id st-002 --deps "st-001:blocks,st-003:blocks"
"$RUN_ST_SCRIPT" set-notes --file .step/st-plan.jsonl --id st-002 --notes "Need benchmark evidence"
"$RUN_ST_SCRIPT" add-comment --file .step/st-plan.jsonl --id st-002 --text "Pausing until CI clears" --author tk
"$RUN_ST_SCRIPT" ready --file .step/st-plan.jsonl --format markdown
"$RUN_ST_SCRIPT" blocked --file .step/st-plan.jsonl --format json
"$RUN_ST_SCRIPT" show --file .step/st-plan.jsonl --format markdown
"$RUN_ST_SCRIPT" doctor --file .step/st-plan.jsonl
"$RUN_ST_SCRIPT" doctor --file .step/st-plan.jsonl --repair-seq
"$RUN_ST_SCRIPT" emit-update-plan --file .step/st-plan.jsonl
"$RUN_ST_SCRIPT" export --file .step/st-plan.jsonl --output .step/st-plan.snapshot.json
"$RUN_ST_SCRIPT" import-plan --file .step/st-plan.jsonl --input .step/st-plan.snapshot.json --replace
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
- Storage model: not append-only growth. Mutations rewrite the JSONL file atomically (`temp` + `fsync` + replace) and compact to a canonical `replace` event plus checkpoint snapshot at the current seq watermark.
- `doctor` is the first-line integrity check for seq/checkpoint contract issues; use `doctor --repair-seq` only when repair is explicitly needed.
- `import-plan --replace` atomically resets state in the same in-place write model.
- Prefer concise, stable item IDs (`st-001`, `st-002`, ...).
- Prefer `show --format markdown` for execution: it groups steps into `Ready`, `Waiting on Dependencies`, `In Progress`, and terminal/manual buckets.

## Sync Checklist (`$st` -> `update_plan`)

- After each `$st` mutation (`add`, `set-status`, `set-deps`, `set-notes`, `add-comment`, `remove`, `import-plan`), parse the emitted `update_plan: {...}` line and publish `update_plan` in the same turn.
- If no emitted payload is available (for example after `init` or shell piping), run:
  - `"$RUN_ST_SCRIPT" emit-update-plan --file .step/st-plan.jsonl`
- Preserve item ordering from `$st` in `update_plan`.
- Map statuses:
  - `in_progress` -> `in_progress`
  - `completed` -> `completed`
  - `pending`, `blocked`, `deferred`, `canceled` -> `pending`
- Keep dependency edges only in `$st` (`deps`); do not encode dependencies in `update_plan`.
- If an item has `dep_state=waiting_on_deps`, never publish that step as `in_progress` in `update_plan`.
- Before final response on turns that mutate `$st`, re-check no drift by comparing:
  - `"$RUN_ST_SCRIPT" show --file .step/st-plan.jsonl --format json`
  - the latest emitted `update_plan` payload.

## Validation

- Run lightweight CLI sanity checks:
  - `"$RUN_ST_SCRIPT" --help`
  - `"$RUN_ST_SCRIPT" doctor --file .step/st-plan.jsonl`
  - `"$RUN_ST_SCRIPT" emit-update-plan --file .step/st-plan.jsonl`
  - `"$RUN_ST_SCRIPT" show --file .step/st-plan.jsonl --format json`

## References

- Read `references/jsonl-format.md` for event schema, status/dependency state vocabulary, and snapshot import/export shapes.
