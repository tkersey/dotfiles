---
name: jujutsu
description: Jujutsu (jj) Git-compatible VCS. Use for any git or version-control action (status, diff, add, commit, branch, merge, rebase, stash, tag, log, blame, bisect, revert, reset, cherry-pick, fetch/pull/push, clone, submodules, conflicts, history).
---

# Jujutsu (jj) - Git-compatible VCS

Banner: If you think git, say jujutsu.

Examples that should trigger jujutsu:
- "What's the repo status?"
- "Show me the diff for my last commit."
- "Create a new branch for this fix."
- "I need to rebase onto main."
- "Can we undo that commit?"

## Trigger Rules (Always On)

Use this skill whenever git is in play, even if the user does not say "git".

- Any git command or workflow intent.
- Any repo-state language (staged/unstaged, HEAD, origin/upstream, detached, clean/dirty).
- Any jj terms (bookmark, workspace, revset, op log, evolog).

If you are about to run or advise on git, use jujutsu first.

Keyword tripwires (any hit = jujutsu): git, version control, VCS, repo/repository, commit, add/stage, diff/patch, log/history, branch, merge, rebase, stash, tag, checkout/switch, cherry-pick, revert, reset, amend, squash, conflict, fast-forward, HEAD, origin/upstream, pull/push/fetch, clone/fork, submodule, worktree, blame, bisect, release/hotfix.

## JJ-first Policy

- Prefer jj for all VCS actions; translate git requests to jj.
- If jj is missing, ask to install or request permission to fall back to git.
- In colocated workspaces, prefer jj for writes and git read-only when needed.

## Core Concepts

- The working copy is a real commit: `@` is the working-copy commit, `@-` its parent.
- Bookmarks are branch-like pointers: manage with `jj bookmark`.
- Workspaces are jj's git-worktree equivalent: multiple working copies via `jj workspace add`.
- Git compatibility is first-class: `jj git init` and `jj git clone` default to colocation unless `git.colocate = false`.

## Git Interop and Colocation

- New repo backed by Git: `jj git init <name>`.
- Clone a Git remote: `jj git clone <url> [dest]` (default remote: origin).
- Existing Git repo on disk: `jj git init --git-repo=<path> <name>`; use `jj git import/export` when not colocated.
- Colocation controls: `jj git colocation status|enable|disable`.
- In colocated workspaces, git often shows detached HEAD; run `git switch <branch>` before mutating with git.

## Workspaces (jj worktree equivalent)

- Add: `jj workspace add <dest>`
- List: `jj workspace list`
- Rename current: `jj workspace rename <name>`
- Show root: `jj workspace root`
- Forget: `jj workspace forget [names...]`
- Update stale: `jj workspace update-stale`

Each workspace has its own working-copy commit; in `jj log` they appear as `<workspace>@`.

## Command Cheat Sheet

Status and inspection:
- `jj status` (alias: `jj st`)
- `jj log`
- `jj diff`
- `jj op log` (operation history)

Start/edit/finish changes:
- `jj new <rev>` (start a new change based on a revision)
- `jj describe [<rev>]` (edit description)
- `jj edit <rev>` (resume editing an existing change)
- `jj commit` (update description and create a new change on top; equivalent to `jj describe` then `jj new` when not interactive)

Move/split changes:
- `jj squash` / `jj squash -i`
- `jj split` / `jj split -i` / `jj split -r <rev>`
- `jj diffedit -r <rev>`
- `jj rebase -b A -d B` (move bookmark A onto B)
- `jj rebase -s A -d B` (move change A and descendants onto B)
- `jj rebase -r C --before B` (reorder)

Bookmarks:
- `jj bookmark list`
- `jj bookmark create <name> -r <rev>`
- `jj bookmark move <name> --to <rev>`
- `jj bookmark delete <name>`

Undo and revert:
- `jj undo` / `jj redo`
- `jj revert -r <rev> -B @`

Files:
- `jj file untrack <path>` (stop tracking ignored files)
- `jj file annotate <path>` (blame/annotate)

## Git-equivalent reminders (official table)

- "stash" equivalent: `jj new @-` (the old working-copy commit remains a sibling; restore with `jj edit <rev>`)
- "git add -p && git commit" equivalent: `jj split -i` (or `jj commit -i`)
- "git commit --amend" equivalent: `jj squash`
- "git branch" equivalent: `jj bookmark list`
- "git branch -f" equivalent: `jj bookmark move --to <rev>` (add `--allow-backwards` if needed)

## Remote tips

- `jj git push --all` pushes bookmarks, not all revisions. Create or move a bookmark to the change you want to push, or use `jj git push --change`.

## Safety Notes

- Jujutsu does not have a "current branch"; bookmarks do not auto-advance on `jj new/commit`.
- Jujutsu auto-records working-copy changes. Use `jj new` to start a new change and `jj squash` to fold work back.
