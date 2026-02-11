---
name: xit
description: "Use when a repo has `.xit/` or the user asks for xit: translate git-like intents to non-interactive `xit` CLI commands (`status/diff/log --cli`, add/commit/branch/merge/cherry-pick), avoid the TUI, and do not use git unless explicitly requested."
---

# Xit (xit)

## Rule (when to trigger)
Use `xit` instead of `git` when either is true:
- A `.xit/` directory exists in this repo (including in a parent directory).
- The user explicitly asks for xit (e.g. “use xit”, “.xit repo”, “xit status”).

If the repo is not a xit repo and the user didn’t ask for xit, do not force this skill.

## Non-interactive defaults
- Never run bare `xit` (it launches the TUI).
- Always use `--cli` for `status`, `diff`, `diff-added`, and `log` (their default is TUI).
- Avoid TUI entrypoints (e.g. `xit config`); use `xit config list|add|rm ...` instead.
- Prefer `--cli` whenever it’s available; check `xit <cmd> --help` if unsure.

## Preflight
1. Confirm `xit` is available: `command -v xit`.
   - If missing, ask the user to install/provide `xit`.
   - If they decline, do not attempt to “fake it” with `git`; ask how they want to proceed.
2. Confirm you’re in a xit repo:
   - Prefer: `xit status --cli` (it should discover `.xit/` from subdirectories).

## Top mapping (git-like intent → xit)
| Intent | xit | Notes |
| --- | --- | --- |
| status | `xit status --cli` | Text output for agents. |
| diff (working tree) | `xit diff --cli` | Changes not added to index. |
| diff --cached | `xit diff-added --cli` | Index vs last commit. |
| add / stage | `xit add <path>` | Stage file contents. |
| unstage | `xit unadd <path>` | Like `git reset HEAD <path>`. |
| restore (work dir) | `xit restore <path>` | Discard local changes for a path. |
| rm --cached | `xit untrack <path>` | Stop tracking but keep the file. |
| rm | `xit rm <path>` | Stop tracking and delete the file. |
| commit | `xit commit -m "msg"` | Use a quoted message. |
| log | `xit log --cli` | Text output for agents. |
| branch list / create / delete | `xit branch list` / `xit branch add <name>` / `xit branch rm <name>` |  |
| switch / checkout | `xit switch <name-or-oid>` | Updates index + working dir. |
| merge | `xit merge <branch-or-oid>` | Patch-based merge by default. |
| cherry-pick | `xit cherry-pick <oid>` | Apply an existing commit. |

For a more complete mapping and workflows, see `references/cli.md`.

## Common workflows

### Inspect changes
- `xit status --cli`
- `xit diff --cli`
- `xit diff-added --cli`

### Commit cycle
- `xit status --cli`
- `xit diff --cli`
- `xit add <paths...>`
- `xit diff-added --cli`
- `xit commit -m "<message>"`

### Merge / cherry-pick (conflicts)
- Start: `xit merge <branch-or-oid>` or `xit cherry-pick <oid>`.
- Inspect: `xit status --cli` and `xit diff --cli`.
- If conflicts:
  - Resolve conflicts in the working tree.
  - Stage resolutions: `xit add <resolved-paths...>` then `xit diff-added --cli`.
  - Continue: `xit merge --continue` or `xit cherry-pick --continue`.
- To abandon the operation: `xit merge --abort` or `xit cherry-pick --abort`.

### Reset semantics (git reset equivalents)
- Move branch pointer, index only: `xit reset <ref-or-oid>` (like `git reset --mixed`).
- Move branch pointer + working dir: `xit reset-dir <ref-or-oid>` (like `git reset --hard`).
- Move branch pointer only: `xit reset-add <ref-or-oid>` (like `git reset --soft`).

### Remotes (pull is not implemented)
- Manage remotes: `xit remote add|rm|list ...`
- Pull equivalent:
  - `xit fetch <remote>`
  - `xit merge refs/remotes/<remote>/<branch>` (choose `<branch>` by inspecting refs or `xit log --cli` after fetch)
- Push:
  - `xit push <remote> <branch>`

## Guardrails
- **Require explicit user confirmation before running**: `xit rm <path>` (deletes file), `xit restore <path>` / `xit reset-dir <ref-or-oid>` (discard local changes), or `xit push ... -f` / `xit push <remote> :<branch>` (force push / delete remote branch).
- Prefer `xit untrack <path>` when the user wants to stop tracking but keep the file.
- Do not run `git` inside a `.xit` repo unless the user explicitly requests git.

## If a command seems missing
- Check `xit --help` and `xit <cmd> --help`.
- If it isn’t available, explain the limitation and ask for direction.

## Notes
- Patch-based merge controls: `xit patch on|off|all`.
