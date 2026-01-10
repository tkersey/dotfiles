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

## Monitor loop
Repeat with adaptive polling:
1. List open PRs: `gh pr list --state open --json number,title,headRefName,labels,isDraft`.
2. For each PR:
   - Skip if `auto:hold`.
   - Skip if not `auto:manage` and not agent-created.
   - If draft, mark ready: `gh pr ready`.
   - Ensure branch is up to date.
   - Enforce CI gate.
   - If failing, run the surgical fix loop.
   - When green, auto-approve and squash-merge.

## CI gate
- Treat any pending or failing check as a hard block.
- Use: `gh pr checks`, `gh run list`, `gh run watch`.

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

## Branch updates (jj-first)
- Prefer `jj` for writes; fall back to `git` only when needed.
- Rebase onto the default branch; force-push only when required.

## Merge
- When checks are green and no hold:
  - Approve: `gh pr review --approve`.
  - Squash-merge: `gh pr merge --squash`.

## Adaptive polling
- Poll under 60s unless CI is slow.
- Use recent CI duration to back off (cap at 120s).
- Exponential backoff on API errors.

## Status reporting
- Maintain a single PR comment/check-run named `AutoMerge Operator`.
- Update in place (avoid comment spam).

## Recipes
- Create: `gh pr create --fill --head <branch> --label auto:manage`
- Checks: `gh pr checks <num>`
- Merge: `gh pr merge <num> --squash`

## Assets
- `assets/auto-merge.yml`
- `assets/pr-template.md`
