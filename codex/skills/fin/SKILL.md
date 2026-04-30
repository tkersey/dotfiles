---
name: fin
description: "Finalize GitHub PRs end-to-end: update branch/PR, confirm review conversations are resolved, monitor CI until green, squash-merge, and clean up local/remote state. Use when asked to $fin or to finish/land/merge/close a PR, watch checks or runs, squash-merge, delete the branch, and sync local state."
---

# Fin

## Overview
Finish a PR end-to-end: push updates, watch checks, squash-merge, and clean up state.

## Workflow
1) Identify the PR and target branch.
   - Use `gh pr view` (current branch) or `gh pr list` to locate it.

2) Update the PR.
   - Ensure the branch is up to date, run required checks, and push:
     - `git status`, fix issues, then `git push`.

3) Confirm review conversations are resolved.
   - Fetch review threads before merging. For example:
     - `gh api graphql -f owner='<owner>' -f repo='<repo>' -F number=<pr> -f query='query($owner:String!,$repo:String!,$number:Int!){repository(owner:$owner,name:$repo){pullRequest(number:$number){reviewThreads(first:100){pageInfo{hasNextPage} nodes{isResolved path line comments(last:1){nodes{author{login} body url}}}}}}}'`
   - Do not merge while any review thread has `isResolved: false`.
   - If `pageInfo.hasNextPage` is true, page through all review threads or block the merge until the full thread set has been checked.
   - Also inspect `gh pr view --comments` for top-level comments or reviews that are not thread-resolvable; treat unresolved questions, requested changes, or explicit blockers as merge blockers until addressed or clearly withdrawn.

4) Monitor checks until green.
   - Use `gh pr checks --watch` or `gh run watch <run-id>`.
   - If checks fail, fix, push, and re-watch.

5) Squash-merge the PR.
   - Prefer `gh pr merge --squash --delete-branch` unless repo policy dictates otherwise.
   - If approvals are missing, request them before merging.

6) Clean up local state.
   - Fetch the updated mainline, switch to it, and delete the merged branch.

## Guardrails
- Do not merge if review comments are unresolved, requested changes are active, or required checks or approvals are missing.
- Keep the merge method aligned with repo policy.
- If any step is blocked, state the blocker and required next action.
