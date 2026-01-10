---
name: jujutsu
description: Jujutsu (jj) Git-compatible VCS. Use for any version-control work (status/diff/commit/branch/rebase/merge/etc.).
---

# Jujutsu (jj)

## Rule
If you think “git”, use jujutsu.

## When to trigger
Use this skill whenever version control is in play, even if the user doesn’t say “git”.

Tripwires:
- Commands: status, diff, log/history, add/stage, commit, branch, merge, rebase, stash, tag, checkout/switch, cherry-pick, revert, reset, amend, squash, conflict, pull/push/fetch, clone, submodule, blame, bisect.
- Terms: staged/unstaged, HEAD, origin/upstream, clean/dirty, detached.

## JJ-first policy
- Prefer `jj` for VCS writes.
- If `jj` is missing, ask to install it or request permission to fall back to `git`.
- In colocated repos, avoid mutating with `git` unless you know what you’re doing (git may appear detached).

## Core concepts
- The working copy is a commit: `@` is the working-copy commit, `@-` its parent.
- Bookmarks are branch-like pointers: `jj bookmark …`.
- Workspaces are git-worktree-like: `jj workspace add …`.
  - There is no `jj workspace use` command. To switch, `cd` into the workspace directory.

## Git interop / colocation
- New repo backed by Git: `jj git init <name>`.
- Clone a Git remote: `jj git clone <url> [dest]`.
- Existing Git repo: `jj git init --git-repo=<path> <name>`.
- Colocation controls: `jj git colocation status|enable|disable`.

## Common commands
Inspection:
- `jj status`
- `jj log`
- `jj diff`
- `jj op log`

Editing changes:
- `jj new <rev>`
- `jj describe [<rev>]`
- `jj edit <rev>`
- `jj commit`

Move/rewrite history:
- `jj squash`
- `jj split`
- `jj rebase -b <bookmark> -d <dest>`

Bookmarks:
- `jj bookmark list`
- `jj bookmark create <name> -r <rev>`
- `jj bookmark move <name> --to <rev>`
- `jj bookmark delete <name>`

Undo:
- `jj undo`
- `jj redo`

## Command mapping (git -> jj)
| Git | Jujutsu | Notes |
| --- | --- | --- |
| `git status` | `jj status` | |
| `git diff` | `jj diff` | |
| `git log` | `jj log` | |
| `git add <path>` | `jj file track <path>` | JJ auto-tracks edits; use `track` for new paths. |
| `git restore <path>` / `git checkout -- <path>` | `jj restore <path>` | Restores from parent into the working copy. |
| `git commit -m "msg"` | `jj commit -m "msg"` | |
| `git commit --amend -m "msg"` | `jj describe -m "msg"` | Edits current change description. |
| `git branch` | `jj bookmark list` | |
| `git branch <name>` | `jj bookmark create <name> -r @` | |
| `git branch -d <name>` | `jj bookmark delete <name>` | |
| `git switch <name>` / `git checkout <rev>` | `jj edit <rev>` | Moves working copy to an existing change. |
| `git switch -c <name>` | `jj new` + `jj bookmark create <name> -r @` | Two-step in jj. |
| `git merge <branch>` | `jj new @ <branch>` | Creates a merge commit with both parents. |
| `git rebase <upstream>` | `jj rebase -b @ -o <upstream>` | Rebase current branch onto upstream. |
| `git pull` | `jj git fetch` + `jj rebase -b @ -o <remote-bookmark>` | Fetch then rebase onto e.g. `origin/main`. |
| `git fetch` | `jj git fetch` | |
| `git push` | `jj git push` | |

## Workspace switching (correct usage)
- List workspaces: `jj workspace list`
- Add a workspace: `jj workspace add <path> [-r <rev>]`
- Forget a workspace: `jj workspace forget <path>`
- Switch workspaces by changing directories: `cd <path>`

## Safety notes
- `jj` has no “current branch”; bookmarks don’t auto-advance.
- Avoid interactive flags (like `-i`) in non-interactive harnesses.
