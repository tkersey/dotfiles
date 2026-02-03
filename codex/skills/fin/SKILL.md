---
name: fin
description: "Finalize GitHub PRs: update the branch/PR, monitor CI until green, squash-merge, and clean up local/remote state. Use for requests like finish/land/close a PR, monitor checks, squash and cleanup."
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

3) Monitor checks until green.
   - Use `gh pr checks --watch` or `gh run watch <run-id>`.
   - If checks fail, fix, push, and re-watch.

4) Squash-merge the PR.
   - Prefer `gh pr merge --squash --delete-branch` unless repo policy dictates otherwise.
   - If approvals are missing, request them before merging.

5) Clean up local state.
   - Fetch the updated mainline, switch to it, and delete the merged branch.

## Guardrails
- Do not merge if required checks or approvals are missing.
- Keep the merge method aligned with repo policy.
- If any step is blocked, state the blocker and required next action.
