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

## Quick Start (Zig CLI Bootstrap)

```bash
run_st_tool() {
  install_st_direct() {
    local repo="${SKILLS_ZIG_REPO:-$HOME/workspace/tk/skills-zig}"
    if ! command -v zig >/dev/null 2>&1; then
      echo "zig not found. Install Zig from https://ziglang.org/download/ and retry." >&2
      return 1
    fi
    if [ ! -d "$repo" ]; then
      echo "skills-zig repo not found at $repo." >&2
      echo "clone it with: git clone https://github.com/tkersey/skills-zig \"$repo\"" >&2
      return 1
    fi
    if ! (cd "$repo" && zig build -Doptimize=ReleaseSafe); then
      echo "direct Zig build failed in $repo." >&2
      return 1
    fi
    if [ ! -x "$repo/zig-out/bin/st" ]; then
      echo "direct Zig build did not produce $repo/zig-out/bin/st." >&2
      return 1
    fi
    mkdir -p "$HOME/.local/bin"
    install -m 0755 "$repo/zig-out/bin/st" "$HOME/.local/bin/st"
  }

  local os="$(uname -s)"
  if command -v st >/dev/null 2>&1 && st --help 2>&1 | grep -q "st.zig"; then
    st "$@"
    return
  fi

  if [ "$os" = "Darwin" ]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "homebrew is required on macOS: https://brew.sh/" >&2
      return 1
    fi
    if ! brew install tkersey/tap/st; then
      echo "brew install tkersey/tap/st failed." >&2
      return 1
    fi
  elif ! (command -v st >/dev/null 2>&1 && st --help 2>&1 | grep -q "st.zig"); then
    if ! install_st_direct; then
      return 1
    fi
  fi

  if command -v st >/dev/null 2>&1 && st --help 2>&1 | grep -q "st.zig"; then
    st "$@"
    return
  fi

  echo "st binary missing or incompatible after install attempt." >&2
  if [ "$os" = "Darwin" ]; then
    echo "expected install path: brew install tkersey/tap/st" >&2
  else
    echo "expected direct path: SKILLS_ZIG_REPO=<skills-zig-path> zig build -Doptimize=ReleaseSafe" >&2
  fi
  return 1
}

run_st_tool --help
```

## Workflow

1. Define `run_st_tool` once per shell session to bootstrap/install `st`.
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

Run commands from the target repository root. Commands below use `st` directly; use `run_st_tool` first when bootstrapping.

```bash
st init --file .step/st-plan.jsonl
st add --file .step/st-plan.jsonl --id st-001 --step "Reproduce failing test" --deps ""
st add --file .step/st-plan.jsonl --id st-002 --step "Patch core logic" --deps "st-001"
st set-status --file .step/st-plan.jsonl --id st-001 --status in_progress
st set-deps --file .step/st-plan.jsonl --id st-002 --deps "st-001:blocks,st-003:blocks"
st set-notes --file .step/st-plan.jsonl --id st-002 --notes "Need benchmark evidence"
st add-comment --file .step/st-plan.jsonl --id st-002 --text "Pausing until CI clears" --author tk
st ready --file .step/st-plan.jsonl --format markdown
st blocked --file .step/st-plan.jsonl --format json
st show --file .step/st-plan.jsonl --format markdown
st doctor --file .step/st-plan.jsonl
st doctor --file .step/st-plan.jsonl --repair-seq
st emit-update-plan --file .step/st-plan.jsonl
st export --file .step/st-plan.jsonl --output .step/st-plan.snapshot.json
st import-plan --file .step/st-plan.jsonl --input .step/st-plan.snapshot.json --replace
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
  - `st emit-update-plan --file .step/st-plan.jsonl`
- Preserve item ordering from `$st` in `update_plan`.
- Map statuses:
  - `in_progress` -> `in_progress`
  - `completed` -> `completed`
  - `pending`, `blocked`, `deferred`, `canceled` -> `pending`
- Keep dependency edges only in `$st` (`deps`); do not encode dependencies in `update_plan`.
- If an item has `dep_state=waiting_on_deps`, never publish that step as `in_progress` in `update_plan`.
- Before final response on turns that mutate `$st`, re-check no drift by comparing:
  - `st show --file .step/st-plan.jsonl --format json`
  - the latest emitted `update_plan` payload.

## Validation

- Run lightweight CLI sanity checks:
  - `run_st_tool --help`
  - `st doctor --file .step/st-plan.jsonl`
  - `st emit-update-plan --file .step/st-plan.jsonl`
  - `st show --file .step/st-plan.jsonl --format json`

## References

- Read `references/jsonl-format.md` for event schema, status/dependency state vocabulary, and snapshot import/export shapes.
