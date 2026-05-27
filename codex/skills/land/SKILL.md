---
name: land
description: "Land GitHub PRs end-to-end: update branch/PR, confirm reviews resolved, monitor CI until green, squash-merge, and clean local/remote state. Use for `$land`, finish/land/merge/close a PR, watch checks/runs, squash-merge, delete branch, or sync local state."
---

# Land

## Overview
Land a PR end-to-end: push updates, watch checks, squash-merge, and clean up state.

## Workflow
1) Identify the PR and target branch.
   - Use `gh pr view` (current branch) or `gh pr list` to locate it.

2) Update the PR.
   - Ensure the branch is up to date, run required checks, and push:
     - `git status`, fix issues, then `git push`.

3) Confirm and close review conversations before merge.
   - Fetch a complete review-thread inventory before merging. Include `totalCount`, `pageInfo{hasNextPage endCursor}`, thread `id`, `isResolved`, `isOutdated`, location, and latest comment URL/body. For example:
     - `gh api graphql -f owner='<owner>' -f repo='<repo>' -F number=<pr> -f query='query($owner:String!,$repo:String!,$number:Int!,$cursor:String){repository(owner:$owner,name:$repo){pullRequest(number:$number){reviewThreads(first:100,after:$cursor){totalCount pageInfo{hasNextPage endCursor} nodes{id isResolved isOutdated path line comments(last:1){nodes{author{login} body url}}}}}}}'`
   - If `pageInfo.hasNextPage` is true, page through every review thread until the collected node count equals `totalCount`; API failure, missing `totalCount`, or partial collection blocks the merge.
   - Do not merge while any review thread has `isResolved: false`, including outdated threads. For every unresolved thread, choose an explicit disposition first: address with code/docs, resolve-thread-only because it is obsolete/withdrawn, or block/defer with user approval.
   - If an unresolved thread was addressed by the PR changes, resolve the GitHub thread with `gh api graphql -f threadId='<thread-id>' -f query='mutation($threadId:ID!){resolveReviewThread(input:{threadId:$threadId}){thread{id isResolved}}}'`, then refetch the complete thread inventory.
   - Immediately before `gh pr merge`, rerun the complete paginated review-thread sweep and require `unresolved_count == 0`, `hasNextPage == false`, and the checked `headRefOid` to match the merge command's `--match-head-commit` value. A stale sweep from before the final push or before thread resolution does not count.
   - Also inspect `gh pr view --comments` and latest reviews for top-level comments or reviews that are not thread-resolvable; treat unresolved questions, requested changes, or explicit blockers as merge blockers until addressed or clearly withdrawn.

4) Monitor checks until green.
   - Use `gh pr checks --watch` or `gh run watch <run-id>`.
   - If checks fail, fix, push, and re-watch.

5) Squash-merge the PR.
   - Prefer `gh pr merge --squash --delete-branch` unless repo policy dictates otherwise.
   - If approvals are missing, request them before merging.

6) Clean up local state.
   - Fetch the updated mainline, switch to it, and delete the merged branch.

## Guardrails
- Do not merge if any review thread remains unresolved, the thread inventory was not fully paginated, requested changes are active, or required checks or approvals are missing.
- Treat addressed-but-unresolved GitHub review threads as still open; close them through GitHub and verify a fresh zero-unresolved sweep before merging.
- Keep the merge method aligned with repo policy.
- If any step is blocked, state the blocker and required next action.
