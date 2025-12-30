---
name: merge
description: Automated PR creation, monitoring, CI repair, review, and squash merging for a single repo using gh with jj-first/git-fallback workflows. Use when an agent must loop over PRs, enforce CI gates, auto-create PRs from branches, apply minimal fixes, and merge quickly with a compact label contract.
---

# Merge

## Overview
Enable a continuous PR autopilot: create PRs for every non-default branch, enforce CI gates, apply surgical fixes to get green, auto-review, and squash-merge via gh.

## Quick Start
1. Ensure `gh auth status` succeeds.
2. Ensure labels exist: `auto:manage`, `auto:hold` (create if missing).
3. Optionally add `.github/auto-merge.yml` from `assets/auto-merge.yml` to make defaults explicit.
4. Start the monitor loop (see “Monitor Loop”).

## Label Contract (Compact)
Use labels to express intent only; derive status from CI and agent logs.
- `auto:manage`: opt-in for full automation. Apply to all auto-created PRs.
- `auto:hold`: pause automation; do not update, review, or merge until removed.

Contributor guidance:
- If you want the agent to handle your PR, add `auto:manage`.
- If you want the agent to stop, add `auto:hold`.
- Document this in the PR template or CONTRIBUTING.md.

## PR Creation Policy (Moonshot)
- For every non-default branch without an open PR, create a PR.
- Use the repo PR template if present; otherwise use `assets/pr-template.md`.
- Set title/body from commits when possible (`gh pr create --fill`).
- Apply `auto:manage` immediately.
- Do not create drafts unless configured; default to ready-for-review.

## Monitor Loop
Repeat continuously with adaptive polling:
1. Fetch open PRs (`gh pr list --state open --json number,title,headRefName,labels,isDraft`).
2. For each PR:
   - Skip if `auto:hold` present.
   - If `auto:manage` absent and PR is not agent-created, skip.
   - If draft and auto-managed, mark ready (`gh pr ready`).
   - Ensure branch is up to date (see “Branch Update”).
   - Evaluate CI (see “CI Gate”).
   - Repair CI if failing (see “Surgical Fix Loop”).
   - When green, auto-approve and squash-merge.
3. Sleep for a computed interval (see “Adaptive Polling”).

## CI Gate (All Checks Mandatory)
- Treat any pending or failing check as a hard block.
- Use CI status from GitHub (`gh pr checks`, `gh run list`, `gh run watch`).
- Do not merge until all checks are successful.

## Surgical Fix Loop (Minimal Incision)
Apply the surgeon’s principle: smallest change that makes CI green.
1. Capture failure cause from check logs.
2. Apply the minimal fix on the PR branch.
3. Commit with a terse message (e.g., "fix(ci): <short cause>").
4. Push and re-check.
5. Limit attempts (default 3). On exhaustion or unresolved conflicts:
   - Leave a summary comment.
   - File “request changes” as last resort.
   - Apply `auto:hold` to prevent churn.

## Branch Update (JJ-First, Git-Fallback)
- Prefer `jj` for all write operations; fall back to git only when needed.
- Rebase PR branches onto the default branch, force-push if required.
- If conflicts cannot be resolved quickly, request changes and `auto:hold`.

## Review + Merge
- When all checks pass and no hold:
  - Auto-approve (`gh pr review --approve`) to satisfy any approval gates.
  - Squash-merge (`gh pr merge --squash`).
- Let repo settings handle branch deletion; do not force delete.

## Adaptive Polling
Keep polling under 60s unless CI is slow.
- Compute average CI duration from recent runs (last 5–10).
- If avg CI ≤ 10 minutes: poll every 30–55 seconds.
- If avg CI > 10 minutes: poll every min(120s, avg/5).
- On API errors, back off with exponential delay.

## Status Reporting
- Maintain a single PR comment or check-run named `AutoMerge Operator`.
- Update with: current state, last action, next action, and last error.
- Avoid noisy comment spam; edit in place when possible.

## Command Recipes (gh / jj / git)
- List PRs: `gh pr list --state open --json number,headRefName,labels,isDraft`
- Create PR: `gh pr create --fill --head <branch> --label auto:manage`
- Check status: `gh pr checks <num>` or `gh run list --branch <branch>`
- Approve: `gh pr review <num> --approve`
- Merge: `gh pr merge <num> --squash`
- JJ rebase (preferred): `jj rebase -b <branch> -o <default>`
- Git rebase (fallback): `git rebase <default>` then force-push

## Assets
- `assets/auto-merge.yml`: optional repo config template.
- `assets/pr-template.md`: default PR template if none exists.
