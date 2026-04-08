---
name: st
description: Manage persistent task plans in `.step/st-plan.jsonl`, with an explicit first-use choice between repo-committed storage and local-only ignore via `.git/info/exclude`, so state survives turns/sessions and can stay reviewable in git when desired. Use when users ask to "use $st", "resume the plan", "export/import plan state", "checkpoint milestones", "track dependencies/blocked work", "show ready next tasks", "keep shared TODO status on disk", "store backlog tasks on disk without loading them into `update_plan` yet", "select which durable tasks enter the mirrored plan", "map a `$select` plan into durable execution state", "prove `$st` works for implementation tracking", mirror the durable plan into Codex `update_plan` or OpenCode `TodoWrite`, or diagnose/repair `st-plan.jsonl` concerns (for example append-only vs mutable semantics, lock-file ignore policy, or seq/checkpoint integrity).
---

# st

## Overview

Maintain a durable task inventory in the repo worktree (default: `.step/st-plan.jsonl`) using in-place JSONL v3 persistence with dual lanes:

- `event` lane for mutations
- `checkpoint` lane for periodic full-state snapshots

Items use typed dependency edges (`deps: [{id,type}]`) plus `notes`, `comments`, `in_plan`, and optional execution metadata (`related_to`, `scope`, `location`, `validation`, `source`, `claim`, `runtime`, `proof`).
`in_plan=true` projects an item into the mirrored Codex/OpenCode plan; `in_plan=false` keeps it on disk as durable backlog only.

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
2. If the run has 3+ dependent steps, likely spans turns, or already uses a native task surface (`update_plan` in Codex or `TodoWrite` in OpenCode), adopt `$st` as the durable source of truth before editing.
3. Before the first `st init` or mutation in a repo, determine the plan-file storage policy.
   - If `.step/st-plan.jsonl` is already tracked, or already ignored by repo policy, respect that existing choice and do not re-ask.
   - If the repo has not yet made the choice obvious, ask one targeted question: should `.step/st-plan.jsonl` be committed to the repo, or kept local by adding it to `.git/info/exclude`?
   - Shared mode: keep `.step/st-plan.jsonl` tracked and make sure only the lock sidecar is ignored.
   - Local mode: add both `.step/st-plan.jsonl` and `.step/st-plan.jsonl.lock` to `.git/info/exclude` before first mutation.
4. If the plan came from `$select`, import the OrchPlan into `$st` and claim the first safe wave before execution starts.
   - `st import-orchplan --file .step/st-plan.jsonl --input .step/orchplan.yaml`
   - `st claim --file .step/st-plan.jsonl --wave w1 --executor teams`
   - For OrchPlan-backed claims, `--wave` is the canonical selector and there is no public same-turn non-`$st` handoff.
5. Initialize plan storage with `st init` if missing.
6. Rehydrate current state with `st show` (or focused views via `ready` / `blocked`).
   - Default surface is `plan`.
   - Use `--surface all` to inspect the full durable inventory.
   - Use `--surface backlog` to inspect durable tasks not currently mirrored into the plan.
7. Run `doctor` when ingesting an existing plan file or when integrity is in doubt.
8. Apply plan mutations through subcommands (`add`, `select`, `deselect`, `set-status`, `set-deps`, `set-notes`, `add-comment`, `remove`, `import-plan`, `import-orchplan`, `claim`, `heartbeat`, `set-runtime`, `set-proof`, `release`, `reclaim-stale`, `import-mesh-results`); do not hand-edit existing JSONL lines.
   - Use `add --backlog-only` or `import-plan --backlog-only` to update the durable inventory without loading those items into the mirrored plan yet.
   - Use `select` to add backlog items into the mirrored plan.
   - Use `deselect` to remove items from the mirrored plan without deleting them from disk.
9. After each mutation command, consume the emitted `plan_sync: {...}` payload and mirror it into the native runtime tool in the same turn.
10. Use `emit-plan-sync` to regenerate the payload from durable state when needed.
11. If `emit-plan-sync` is unavailable because the installed binary is older, fall back:
   - Codex: use `emit-update-plan`.
   - OpenCode: use `show --format json`, map `content=item.step`, normalize `blocked`/`deferred` to `pending`, normalize `canceled` to `cancelled`, and default missing priority to `medium`.
12. Export/import snapshots when cross-session handoff is needed.

## Commands

Run commands from the target repository root. Commands below use `st` directly; use `run_st_tool` first when bootstrapping.

```bash
st init --file .step/st-plan.jsonl
st add --file .step/st-plan.jsonl --id st-001 --step "Reproduce failing test" --priority high --deps ""
st add --file .step/st-plan.jsonl --id st-002 --step "Investigate optional follow-up" --deps "" --backlog-only
st select --file .step/st-plan.jsonl --ids "st-002"
st add --file .step/st-plan.jsonl --id st-003 --step "Patch core logic" --deps "st-001"
st set-status --file .step/st-plan.jsonl --id st-001 --status in_progress
st set-priority --file .step/st-plan.jsonl --id st-003 --priority medium
st set-deps --file .step/st-plan.jsonl --id st-003 --deps "st-001:blocks"
st set-notes --file .step/st-plan.jsonl --id st-003 --notes "Need benchmark evidence"
st add-comment --file .step/st-plan.jsonl --id st-003 --text "Pausing until CI clears" --author tk
st ready --file .step/st-plan.jsonl --format markdown
st show --file .step/st-plan.jsonl --surface all --format json
st blocked --file .step/st-plan.jsonl --surface backlog --format json
st show --file .step/st-plan.jsonl --format markdown
st doctor --file .step/st-plan.jsonl
st doctor --file .step/st-plan.jsonl --repair-seq
st emit-plan-sync --file .step/st-plan.jsonl
st emit-update-plan --file .step/st-plan.jsonl
st export --file .step/st-plan.jsonl --output .step/st-plan.snapshot.json
st import-plan --file .step/st-plan.jsonl --input .step/st-plan.snapshot.json --replace
st import-orchplan --file .step/st-plan.jsonl --input .step/orchplan.yaml --replace
st claim --file .step/st-plan.jsonl --wave w1 --executor teams
st heartbeat --file .step/st-plan.jsonl --id st-001
st set-runtime --file .step/st-plan.jsonl --id st-001 --substrate spawn_agent --thread-id thread-123 --agent-id agent-1
st set-proof --file .step/st-plan.jsonl --id st-001 --proof-state pass --command "zig build test-st" --evidence-ref .step/proof.log
st release --file .step/st-plan.jsonl --id st-001 --reason proof_complete
st reclaim-stale --file .step/st-plan.jsonl --now 2026-03-12T00:00:00Z
st import-mesh-results --file .step/st-plan.jsonl --input .step/mesh-output.csv
```

## Operating Rules

- Keep exactly one `in_progress` item unless `$st` can prove a safe parallel wave.
- Safe parallel `in_progress` is allowed automatically when every active item has `claim.state=held`, a non-empty `claim.wave_id`, `claim.executor=teams|mesh`, and pairwise non-overlapping `claim.lock_roots`.
- First-use plan-file policy: if `.step/st-plan.jsonl` is not yet tracked and not already ignored, ask whether the repo wants shared tracked state or local-only state via `.git/info/exclude` before the first mutation.
- For OrchPlan-backed durable execution, `claim.wave_id` is authoritative and should be derived from the imported wave, not reconstructed from ad hoc `--ids`.
- `in_plan=true` is the mirrored-plan membership flag. Missing legacy values normalize to `true`.
- Terminal statuses (`completed`, `deferred`, `canceled`) auto-demote items out of the mirrored plan while keeping them on disk.
- Track prerequisites in each item's typed `deps` array; dependencies are part of the canonical JSONL schema.
- Priorities are canonical in `$st`: allowed values are `high`, `medium`, and `low`; missing legacy values normalize to `medium`.
- Parse CLI deps as comma-separated `id` or `id:type` tokens; missing type normalizes to `blocks`, and type must be kebab-case.
- Require dependency integrity:
  - dependency IDs must exist in the current plan,
  - no self-dependencies,
  - no dependency cycles.
- Projected-plan integrity:
  - `select` accepts exact IDs (`--ids`) plus simple field filters (`--status`, `--priority`),
  - selecting an item auto-includes unresolved dependency closure,
  - completed dependencies do not get pulled back into the mirrored plan,
  - `deselect` rejects if it would strand a still-selected dependent on a backlog-only unresolved task.
- Allow `in_progress` and `completed` only when all dependencies are `completed`.
- Normalize user status terms before writing:
  - `open`, `queued` -> `pending`
  - `active`, `doing` -> `in_progress`
  - `done`, `closed` -> `completed`
- Mutation commands (`add`, `select`, `deselect`, `set-status`, `set-priority`, `set-deps`, `set-notes`, `add-comment`, `remove`, `import-plan`, `import-orchplan`, `claim`, `heartbeat`, `set-runtime`, `set-proof`, `release`, `reclaim-stale`, `import-mesh-results`) automatically print a canonical `plan_sync:` payload line plus a legacy `update_plan:` compatibility line after durable write.
- Lock sidecar policy: mutating commands require the lock file (`<plan-file>.lock`, for example `.step/st-plan.jsonl.lock`) to be ignored when inside a git repo. In shared mode, add the lock sidecar to `.gitignore`; in local-only mode, add both the plan file and the lock sidecar to `.git/info/exclude`.
- Storage model: not append-only growth. Mutations rewrite the JSONL file atomically (`temp` + `fsync` + replace) and compact to a canonical `replace` event plus checkpoint snapshot at the current seq watermark.
- `doctor` is the first-line integrity check for seq/checkpoint contract issues; use `doctor --repair-seq` only when repair is explicitly needed.
- `import-plan --replace` atomically resets the full durable inventory in the same in-place write model.
- Prefer concise, stable item IDs (`st-001`, `st-002`, ...).
- Prefer `show --format markdown` for execution: it groups tasks into `Ready`, `Waiting on Dependencies`, `In Progress`, and terminal/manual buckets for the selected surface.

## Sync Checklist (`$st` -> native runtime tools)

- After each `$st` mutation (`add`, `select`, `deselect`, `set-status`, `set-priority`, `set-deps`, `set-notes`, `add-comment`, `remove`, `import-plan`, `import-orchplan`, `claim`, `heartbeat`, `set-runtime`, `set-proof`, `release`, `reclaim-stale`, `import-mesh-results`), prefer the emitted `plan_sync: {...}` line.
- If no emitted payload is available (for example after `init` or shell piping), run:
  - `st emit-plan-sync --file .step/st-plan.jsonl`
- Preserve full inventory order from `$st` in `plan_sync.items`.
- Codex:
  - publish `plan_sync.codex.plan` via `update_plan`.
  - if only a legacy payload is available, use `st emit-update-plan --file .step/st-plan.jsonl`.
- OpenCode:
  - publish `plan_sync.opencode.todos` via `TodoWrite`.
  - if only an older binary is available, use `st show --file .step/st-plan.jsonl --format json` and map `content=item.step`, `status=in_progress|completed|pending|cancelled`, and `priority=item.priority` or `medium` when missing.
- `plan_sync.items` is the full durable inventory. `plan_sync.codex.plan`, `plan_sync.opencode.todos`, and `emit-update-plan` emit only the selected mirrored-plan subset.
- Keep dependency edges only in `$st` (`deps`); do not encode dependencies in `update_plan` or `TodoWrite`.
- If an item has `dep_state=waiting_on_deps`, never mirror that item as `in_progress`.
- Before final response on turns that mutate `$st`, re-check no drift by comparing:
  - `st show --file .step/st-plan.jsonl --format json`
  - the latest emitted `plan_sync` payload.

## Validation

- Run lightweight CLI sanity checks:
  - `run_st_tool --help`
  - `st doctor --file .step/st-plan.jsonl`
  - `st emit-plan-sync --file .step/st-plan.jsonl`
  - `st emit-update-plan --file .step/st-plan.jsonl`
  - `st show --file .step/st-plan.jsonl --surface all --format json`
  - `st show --file .step/st-plan.jsonl --format json`

## References

- Read `references/jsonl-format.md` for event schema, status/dependency state vocabulary, and snapshot import/export shapes.
