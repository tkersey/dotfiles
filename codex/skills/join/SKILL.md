---
name: join
description: "PR autopilot: create/manage PRs, enforce CI gates, apply surgical fixes, and squash-merge via `gh`."
---

# Join

## Intent
Run a continuous PR operator: keep PRs created, green, reviewed, and squash-merged (via `gh`) with minimal-incision fixes.

## Quick start
1. Ensure `gh auth status` succeeds.
2. Ensure labels exist: `auto:manage`, `auto:hold`.
3. (Optional) Add `.github/auto-merge.yml` from `assets/auto-merge.yml`.
4. Start the monitor loop.

## Label contract
- `auto:manage`: opt-in to automation.
- `auto:hold`: pause automation.

Contributor guidance:
- Add `auto:manage` to opt in.
- Add `auto:hold` to stop the operator.

## PR creation policy
- For every non-default branch without an open PR, create a PR.
- Use the repo PR template if present; else use `assets/pr-template.md`.
- Prefer `gh pr create --fill` and apply `auto:manage`.
- Default to ready-for-review (no drafts unless configured).

## Operating modes
Mode is per-PR and determined by the current checkout:
- Local checkout (VCS): the PR `headRefName` matches the currently checked-out branch/bookmark. Name match is sufficient; no upstream requirement. jj detached checkouts still count as local when they point at the PR head.
- Remote-only (`gh` only): no clean local checkout/branch is available. Keep operations `gh`-only. Post-merge cleanup may still run if a local worktree is clean (see below).

Local is preferred when available or when a local branch exists and the worktree is clean enough to switch. If local mode is selected and the PR branch is checked out, dirty changes are committed and pushed into the PR before CI. If the PR branch is not checked out and the worktree is dirty, apply `auto:hold` (cannot switch safely); do not fall back to remote-only for that PR.

Mode detection (git):
- Current checkout: `git branch --show-current` (empty means detached).
- Dirty state: `git status --porcelain` (non-empty means dirty).
- Local branch exists: `git show-ref --verify --quiet refs/heads/<headRefName>`.
- Local if `git branch --show-current` equals `headRefName`.
- If not on the PR branch but a local branch exists and the worktree is clean, checkout `headRefName` and treat as local.
- If a local branch exists but the worktree is dirty, apply `auto:hold` (cannot switch safely).
- If detached in git, treat as remote-only for operations; still eligible for safe local cleanup when the worktree is clean. JJ handling is delegated to the JJ skill.

## Monitor loop
Process PRs sequentially (blocking per PR on CI):
1. List open PRs: `gh pr list --state open --json number,title,headRefName,labels,isDraft`.
2. For each PR:
   - Skip if `auto:hold`.
   - Skip if not `auto:manage` and not agent-created.
   - If draft, mark ready: `gh pr ready <num>`.
   - Select mode for this PR (local if current checkout matches `headRefName` or a clean local branch exists; otherwise remote-only).
   - If local and not on `headRefName`, checkout the branch (requires a clean worktree). If dirty, apply `auto:hold`, leave a comment (template below), and skip.
   - If local, run the local sync gate (below) before CI.
   - Ensure branch is up to date (jj-first if a local checkout is active).
   - Enforce CI gate (required checks only; see below).
   - If failing, run the surgical fix loop.
   - When green, auto-approve and squash-merge.
   - After a successful merge, run post-merge cleanup (mode-dependent).

## Local sync gate (required before CI)
If operating locally, ensure all local changes are in the PR:
1. Commit and push dirty changes on the PR branch:
   - `git add -A`
   - `git commit -m "chore: sync local changes"`
   - `git push`
   - If there is nothing to commit, continue.
2. Ensure OID parity with the PR head:
   - `pr_head=$(gh pr view <num> --json headRefOid --jq .headRefOid)`
   - `local_head=$(git rev-parse HEAD)`
   - If equal, continue.
   - If `git merge-base --is-ancestor "$local_head" "$pr_head"` (local behind): `git fetch origin` then `git rebase origin/<headRefName>`.
   - If `git merge-base --is-ancestor "$pr_head" "$local_head"` (local ahead): `git push`.
   - Else (diverged): apply `auto:hold` and comment (template below).

## CI gate (required checks only)
- Gate on required checks only (`gh pr checks --required`). Optional checks do not block merges.
- Detect “ungated” repos/PRs (no required checks):
  - If `gh pr checks <num> --required --json name` returns an empty list, treat CI as green and proceed to merge.
- Wait for required checks (blocking):
  - `gh pr checks <num> --required --watch --fail-fast`
  - This blocks until all required checks pass or the first required check fails.
- Stalled CI (10 minutes with no observable progress):
  - Define “progress” as any change in the required-check snapshot (`name`, `bucket`, `startedAt`, `completedAt`).
  - While waiting, periodically sample: `gh pr checks <num> --required --json name,bucket,startedAt,completedAt`.
  - If the snapshot does not change for 10 minutes while not all checks are `bucket=pass`, apply `auto:hold` and leave a summary comment with links to the stuck checks.
  - Treat `bucket=pending`, `bucket=skipping`, and `bucket=cancel` as “not green” (blocked) until resolved; do not merge through them.
- Drill into GitHub Actions when needed:
  - Identify check links: `gh pr checks <num> --required --json name,bucket,link,workflow`
  - Find likely runs: `gh run list --branch <headRefName> --limit 10`
  - Watch a run live: `gh run watch <run-id> --compact --exit-status`
  - Fetch failing step logs: `gh run view <run-id> --log-failed`

## Surgical fix loop
Smallest change that makes CI green:
1. Read the failure from CI logs.
2. Apply the minimal fix on the PR branch.
3. Commit with a terse message (e.g., `fix(ci): <cause>`).
4. Push and re-check.
5. Limit attempts (default 3). On exhaustion or hard conflicts:
   - Leave a summary comment.
   - Request changes as last resort.
   - Apply `auto:hold`.

## Branch updates (local VCS)
- Use the repository’s active VCS; avoid tooling switches mid-fix.
- Rebase onto the default branch; force-push only when required.
- If you need a concrete example, use git equivalents (e.g., `git fetch`, `git rebase`, `git push --force-with-lease`).

## Merge
- When required checks are green (or no required checks exist) and no hold:
  - Approve: `gh pr review <num> --approve`
  - Squash-merge: `gh pr merge <num> --squash`
- Policy:
  - Do not use `gh pr merge --admin` (not approved).
  - Do not use `--delete-branch` (leave remote branches intact).
- Confirm merge completion (merge queue friendly):
  - `gh pr view <num> --json state,mergedAt,mergeStateStatus`

## Post-merge cleanup (mode-dependent)
- Remote-only (`gh` only):
  - Always confirm merge: `gh pr view <num> --json state,mergedAt`.
  - If no local git worktree is present, stop after confirmation.
  - If a local worktree is present and clean, perform the local cleanup steps below (safe cleanup even when the PR was operated remotely).
- Local checkout (VCS):
  - Goal: leave the workspace on the default branch, synced to origin, with no PR branch checked out and no lingering local refs. Avoid destructive cleaning unless the default branch diverged; if it did, create a safety branch before resetting.
  - Example (git):
    - Ensure clean working tree: `git status --porcelain` (if dirty, stop; apply `auto:hold`).
    - Switch to default branch: `git checkout <default-branch>`
    - Fetch/prune: `git fetch --prune origin`
    - Sync default branch to origin (prevents ahead/behind after merge):
      - `local_default=$(git rev-parse <default-branch>)`
      - `remote_default=$(git rev-parse origin/<default-branch>)`
      - If equal, continue.
      - If `git merge-base --is-ancestor "$local_default" "$remote_default"` (local behind): `git merge --ff-only origin/<default-branch>`.
      - If `git merge-base --is-ancestor "$remote_default" "$local_default"` (local ahead): create a safety branch, then reset:
        - `git branch "backup/<default-branch>-$(date +%Y%m%d-%H%M%S)"`
        - `git reset --hard origin/<default-branch>`
      - Else (diverged): create a safety branch, then reset:
        - `git branch "backup/<default-branch>-$(date +%Y%m%d-%H%M%S)"`
        - `git reset --hard origin/<default-branch>`
    - If the local PR branch does not exist, skip deletion.
    - Delete the local PR branch only if it matches the PR head (or remote head):
      - `pr_head=$(gh pr view <num> --json headRefOid --jq .headRefOid)`
      - `local_head=$(git rev-parse <headRefName>)`
      - `remote_head=$(git rev-parse origin/<headRefName> 2>/dev/null || true)`
      - Delete only when `local_head == pr_head` or `local_head == remote_head`; otherwise apply `auto:hold` and comment (template below).

## Adaptive polling
- Poll under 60s unless CI is slow.
- Use recent CI duration to back off (cap at 120s).
- Exponential backoff on API errors.

## Status reporting
- Maintain a single PR comment/check-run named `AutoMerge Operator`.
- Update in place (avoid comment spam).

## Dirty local state comment template
```
AutoMerge Operator: local changes block checkout

PR branch is not checked out; worktree is dirty so checkout is unsafe.
Clean the workspace or move changes to the PR branch, then remove `auto:hold`.

Signal: `git status --porcelain` is empty.
```

## Local divergence comment template
```
AutoMerge Operator: local branch diverged

Local branch and PR head differ.
Push local commits into the PR or reset local to the PR head, then remove `auto:hold`.

Signal: `git rev-parse HEAD` equals PR `headRefOid`.
```

## Recipes
- Default branch: `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`
- Create: `gh pr create --fill --head <branch> --label auto:manage`
- PR head OID: `gh pr view <num> --json headRefOid --jq .headRefOid`
- Local branch exists: `git show-ref --verify --quiet refs/heads/<headRefName>`
- Required checks (summary): `gh pr checks <num> --required`
- Required checks (watch): `gh pr checks <num> --required --watch --fail-fast`
- Required checks (links/JSON): `gh pr checks <num> --required --json name,bucket,link,workflow`
- Actions runs (by branch): `gh run list --branch <branch> --limit 10`
- Actions run logs: `gh run view <run-id> --log-failed`
- Merge: `gh pr merge <num> --squash`

## Assets
- `assets/auto-merge.yml`
- `assets/pr-template.md`
