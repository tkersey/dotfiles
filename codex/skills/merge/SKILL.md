---
name: merge
description: "PR autopilot: create/manage PRs, enforce CI gates, apply surgical fixes, and squash-merge via `gh`."
---

# Merge

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
Pick the least-privileged mode that can succeed:
- Remote-only (`gh` only): create/manage PRs, monitor checks, review, merge, label, comment; do not checkout code locally.
- Local checkout (VCS): only when a surgical fix is needed; checkout the PR branch, apply minimal changes, push, then clean up local state after merge.

## Monitor loop
Process PRs sequentially (blocking per PR on CI):
1. List open PRs: `gh pr list --state open --json number,title,headRefName,labels,isDraft`.
2. For each PR:
   - Skip if `auto:hold`.
   - Skip if not `auto:manage` and not agent-created.
   - If draft, mark ready: `gh pr ready <num>`.
   - Ensure branch is up to date (jj-first if a local checkout is active).
   - Enforce CI gate (required checks only; see below).
   - If failing, run the surgical fix loop.
   - When green, auto-approve and squash-merge.
   - After a successful merge, run post-merge cleanup (mode-dependent).

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
  - No local checkout means no local cleanup. Ensure the PR is merged via `gh pr view <num> --json state,mergedAt`.
- Local checkout (VCS):
  - Goal: leave the workspace on the default branch, with no PR branch checked out and no lingering local refs. Avoid destructive cleaning.
  - Example (git):
    - Ensure clean working tree: `git status --porcelain` (if dirty, stop; apply `auto:hold`).
    - Switch to default branch: `git checkout <default-branch>`
    - Delete local PR branch if present: `git branch -D <headRefName>`
    - Prune deleted remotes: `git fetch --prune`

## Adaptive polling
- Poll under 60s unless CI is slow.
- Use recent CI duration to back off (cap at 120s).
- Exponential backoff on API errors.

## Status reporting
- Maintain a single PR comment/check-run named `AutoMerge Operator`.
- Update in place (avoid comment spam).

## Recipes
- Default branch: `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`
- Create: `gh pr create --fill --head <branch> --label auto:manage`
- Required checks (summary): `gh pr checks <num> --required`
- Required checks (watch): `gh pr checks <num> --required --watch --fail-fast`
- Required checks (links/JSON): `gh pr checks <num> --required --json name,bucket,link,workflow`
- Actions runs (by branch): `gh run list --branch <branch> --limit 10`
- Actions run logs: `gh run view <run-id> --log-failed`
- Merge: `gh pr merge <num> --squash`

## Assets
- `assets/auto-merge.yml`
- `assets/pr-template.md`
