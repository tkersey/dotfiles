---
name: fix
description: Explicit repair loop for a branch diff, current branch, PR, or commit. Run native `codex review` against a frozen local base branch or commit, hand actionable findings to `$fixed-point-driver`, validate, and repeat until a fresh native review is clean. Use when prompts say "$fix this PR", "fix current branch", "fix this diff", "address review comments", or "repair this branch to review-clean closure".
---

# Fix

## Intent
`$fix` owns the **outer** loop only:

`review -> repair -> validate -> re-review`

Repeat until a **fresh native** `codex review` returns no actionable findings.

There is no wall-clock timeout and no cycle cap inside `$fix`. Long native review rounds, including 10m+ runs, are acceptable.

`$fixed-point-driver` remains unchanged and is the remediation engine inside each loop cycle. Do not move the outer re-review loop into `$fixed-point-driver`.

## Reporting
Keep user-facing output minimal.

During execution, emit at most one short line per cycle:

`fix C<n>: review=<clean|blocked|N actionable>; action=<repair|stop>; validation=<pass|fail|n/a>`

Final output must contain exactly these sections and nothing else:

- `**Status**`
- `**Review**`
- `**Validation**`
- `**Do Next**`

## Actionable finding bar
Treat a review comment as actionable only when it is a concrete, author-fix-worthy issue on the in-scope change set.

Actionable findings are:
- correctness, crash, corruption, security, reliability, or meaningful maintainability regressions
- concrete compatibility or validation gaps tied to changed code
- issues with a clear implicated file, symbol, scenario, or diff hunk

Not actionable by default:
- style-only nits
- broad redesign requests without a concrete bug or regression
- comments already disproven by current code and validation
- comments clearly unrelated to the frozen review scope

If review output is ambiguous, be conservative and do not claim clean unless the round is clearly clean.

## Scope selection
1. If the user explicitly requests a commit review, use commit scope.
2. Otherwise use branch-backed review.
3. Resolve `base_branch` as a **local primary branch** in this order:
   - explicit user-supplied local `base_branch`
   - the branch name from `git symbolic-ref --quiet --short refs/remotes/origin/HEAD`, with the `origin/` prefix stripped, but only if the same-named local branch exists
   - `main` if the local branch exists
   - `master` if the local branch exists
4. Never use `@{upstream}` or the current branch's tracking branch as the default `base_branch`.
5. Never pass remote-tracking refs like `origin/main` or `origin/master` to `codex review --base`; pass a local branch name only.
6. If no suitable local primary branch exists, stop blocked and tell the user to create or fetch a local `main` or `master`, or pass `base_branch=<local-branch>` explicitly.
7. Read the current branch name with `git branch --show-current`.
8. If the resolved `base_branch` equals the current branch name, stop blocked. Do not compare a branch against itself.
9. For branch-backed runs, freeze `comparison_sha = git merge-base HEAD <base_branch>` before the first review.
10. Before the first branch-backed review, inspect `git status --porcelain --untracked-files=all`.
    - If the repo already contains unrelated or noisy untracked/modified files outside the requested scope, stop blocked and tell the user to clean or stash them or use a dedicated worktree.
    - Changes created by the current `$fix` run are in-scope and do not count as contamination.
11. Before every branch-backed re-review, recompute `git merge-base HEAD <base_branch>` and stop blocked if it no longer matches the frozen `comparison_sha`.

## Hard rules
- MUST use native `codex review` for every review round.
- MUST use `codex review --commit <commit_sha>` for explicit commit scope.
- MUST use `codex review --base <base_branch>` for branch-backed scope.
- MUST keep one frozen review context for the whole run.
- MUST rerun a fresh native review after every remediation cycle.
- MUST pass the latest actionable review findings into `$fixed-point-driver` and instruct it to resolve those findings on the current artifact state.
- MUST let `$fixed-point-driver` do the remediation work; `$fix` owns orchestration.
- MUST require a passing validation signal after each remediation cycle.
- MUST stop only when a fresh native review is clean or a real blocker prevents forward progress.
- MUST stop blocked if there is no reliable validation signal.
- MUST stop blocked on review-scope contamination or merge-base drift.
- MUST stop blocked when the only resolved default base would compare the branch against itself.
- MUST detect non-convergence: if two consecutive review rounds produce the same normalized actionable findings and the immediately preceding remediation did not materially change the implicated code or improve validation, stop blocked.
- MUST keep user-facing reporting to the required minimal format.
- MUST wait for each native `codex review` process to complete unless the process itself fails, the environment terminates it, or the user interrupts.
- MUST NOT impose a wall-clock timeout or cycle cap.
- MUST NOT stop, skip, downgrade, or truncate a review round just because it is taking a long time.
- MUST NOT treat elapsed time, patience limits, or long review duration as a blocker.
- MUST NOT narrow or otherwise change review scope mid-run.
- MUST NOT claim success based on a stale pre-repair review.
- MUST NOT replace native review with a custom review prompt.
- MUST NOT use `@{upstream}` or a remote-tracking ref as the default `base_branch`.
- MUST assume wrappers may need both stdout and stderr from `codex review`.

## Native review commands
Prefer concrete shell commands over vague intent.

### Commit scope
- Verify the commit exists with:
  - `git rev-parse --verify <commit_sha>^{commit}`
- Review with:
  - `codex review --commit <commit_sha>`

### Branch-backed scope
- Read the current branch name with:
  - `git branch --show-current`
- If needed, resolve the repo default branch name with:
  - `git symbolic-ref --quiet --short refs/remotes/origin/HEAD`
- Verify the local base branch exists with:
  - `git show-ref --verify --quiet refs/heads/<base_branch>`
- Freeze and verify `comparison_sha` with:
  - `git merge-base HEAD <base_branch>`
  - `git rev-parse --verify <comparison_sha>^{commit}`
- Review with:
  - `codex review --base <base_branch>`

## Loop
1. **Preflight**
   - Resolve scope.
   - Resolve a local primary `base_branch` for branch-backed runs.
   - Freeze review context.
   - Check contamination for the initial branch-backed run.
2. **Review**
   - Run fresh native review on the frozen scope.
   - Wait for the review command to finish; long-running review rounds are acceptable.
   - Normalize the results into `clean`, `blocked`, or a short actionable findings set.
3. **Stop if clean**
   - If the review is clean, finish.
4. **Repair**
   - Invoke `$fixed-point-driver` with the latest actionable findings.
   - Instruct it to:
     - resolve exactly those findings on the current artifact state
     - keep changes narrow and evidence-backed
     - run the smallest sufficient validation
     - return control after remediation and validation
   - Do not let `$fixed-point-driver` own the outer re-review loop.
5. **Validation gate**
   - Confirm the post-remediation validation signal passes.
   - If it fails or no reliable signal exists, stop blocked.
6. **Re-review**
   - Re-run fresh native review on the same frozen scope.
7. **Repeat**
   - Continue until the review is clean or blocked.

## How to invoke `$fixed-point-driver`
When handing off to `$fixed-point-driver`, pass all of the following:

- the frozen review scope (`base_branch` + `comparison_sha`, or `commit_sha`)
- the latest actionable findings from the most recent native review
- the instruction that the goal is to resolve those findings to closure on the current artifact state
- the instruction to keep remediation narrow, validated, and ready for another fresh native review round

Use `$fixed-point-driver` as an internal repair phase. Do not mirror its full ledgers back to the user unless the run is blocked and the ledger is the only way to explain the blocker.

## Minimal final response
Final output must use exactly this shape:

**Status**
`done` or `blocked`; `cycles=<n>`

**Review**
`scope=<base ...|commit ...>; last_review=<clean|blocked|N actionable>; last_action=<stop|repaired>`

**Validation**
`<command/result>` or `blocked: no reliable validation signal`

**Do Next**
`none` when done; otherwise one exact next step
