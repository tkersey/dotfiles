---
name: resolve
description: "Explicit repair loop for a branch diff, current branch, PR, or commit. Run fresh native `codex review` against one frozen local base branch or commit, hand actionable findings to `$fixed-point-driver`, validate, and repeat until native-review saturation is reached: two consecutive clean fresh native reviews on the unchanged artifact state with no seeded-finding recurrence."
---
# Resolve

## Intent
`$resolve` owns the **outer** loop only: `review -> repair -> validate -> re-review -> saturation confirmation`

Repeat until a **fresh native** `codex review` reaches **native-review saturation** on one frozen local review context.

Native-review saturation means:
- at least **two consecutive clean** fresh native `codex review` rounds
- both clean rounds run on the **unchanged artifact state**
- no actionable seeded finding recurs after remediation
- the latest reliable validation signal still passes

The first clean round after any remediation or actionable review is a **candidate clean**, not closure.
There is no wall-clock timeout and no cycle cap inside `$resolve`.
Long native review rounds, including 10m+ runs, are acceptable.
`$fixed-point-driver` remains unchanged and is the remediation engine inside each loop cycle.
Do not move the outer re-review loop into `$fixed-point-driver`.

The purpose of `$resolve` is exhaustive native-review discovery on a frozen scope: each remediation cycle should close the current seeded finding cluster tightly enough that the next fresh native review can spend its attention on **other** remaining issues rather than rediscovering the same one.

## Reporting
Keep user-facing output minimal.

During execution, emit at most one short line per cycle: `resolve C: review=; action=; validation=; clean_streak=`

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

## Internal saturation state
Track these internal fields across the run:
- `clean_streak`: consecutive clean fresh native review rounds on the unchanged artifact state
- `seeded_findings`: the latest actionable findings handed to `$fixed-point-driver`
- `seeded_finding_fingerprints`: stable normalized identities for the seeded findings
- `review_reconciliation`: for any reopening round, classify each actionable finding as `recurring_seeded`, `recurring_fix_discovered`, or `fresh_review`
- `last_material_change`: whether the latest remediation materially changed implicated code or materially improved validation evidence

Rules:
- any edit resets `clean_streak` to `0`
- any actionable finding resets `clean_streak` to `0`
- the first clean after an edit or actionable round sets `clean_streak=1` and is only a candidate clean
- closure requires `clean_streak >= 2`
- if a reopening round contains a `recurring_seeded` finding and the immediately preceding remediation did not materially change the implicated code or materially improve validation, stop blocked for non-convergence

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
6. If no suitable local primary branch exists, stop blocked and tell the user to create or fetch a local `main` or `master`, or pass `base_branch=` explicitly.
7. Read the current branch name with `git branch --show-current`.
8. If the resolved `base_branch` equals the current branch name, stop blocked. Do not compare a branch against itself.
9. For branch-backed runs, freeze `comparison_sha = git merge-base HEAD <base_branch>` before the first review.
10. Before the first branch-backed review, inspect `git status --porcelain --untracked-files=all`.
    - If the repo already contains unrelated or noisy untracked/modified files outside the requested scope, stop blocked and tell the user to clean or stash them or use a dedicated worktree.
    - Changes created by the current `$resolve` run are in-scope and do not count as contamination.
11. Before every branch-backed re-review or clean-confirmation review, recompute `git merge-base HEAD <base_branch>` and stop blocked if it no longer matches the frozen `comparison_sha`.

## Hard rules
- MUST use native `codex review` for every review round.
- MUST use `codex review --commit <commit_sha>` for explicit commit scope.
- MUST use `codex review --base <base_branch>` for branch-backed scope.
- MUST keep one frozen review context for the whole run.
- MUST rerun a fresh native review after every remediation cycle.
- MUST rerun a fresh native review after every candidate clean.
- MUST treat the first clean after any remediation or actionable round as `candidate_clean` only.
- MUST require at least two consecutive clean fresh native reviews on the unchanged artifact state before done.
- MUST pass the latest actionable review findings into `$fixed-point-driver` and instruct it to resolve the seeded findings to non-recurrence on the current artifact state.
- MUST allow `$fixed-point-driver` to close directly exposed proof-hook or adjacent-seam issues when needed to keep the seeded findings closed.
- MUST require `$fixed-point-driver` to return review reconciliation with seeded-finding status, any fix-discovered findings, and per-finding provenance.
- MUST let `$fixed-point-driver` do the remediation work; `$resolve` owns orchestration.
- MUST require a passing validation signal after each remediation cycle.
- MUST stop only when a fresh native review is saturated or a real blocker prevents forward progress.
- MUST stop blocked if there is no reliable validation signal.
- MUST stop blocked on review-scope contamination or merge-base drift.
- MUST stop blocked when the only resolved default base would compare the branch against itself.
- MUST detect non-convergence: if two consecutive actionable review rounds produce the same normalized actionable findings and the immediately preceding remediation did not materially change the implicated code or materially improve validation, stop blocked.
- MUST keep user-facing reporting to the required minimal format.
- MUST wait for each native `codex review` process to complete unless the process itself fails, the environment terminates it, or the user interrupts.
- MUST NOT impose a wall-clock timeout or cycle cap.
- MUST NOT stop, skip, downgrade, or truncate a review round just because it is taking a long time.
- MUST NOT treat elapsed time, patience limits, or long review duration as a blocker.
- MUST NOT stop on the first clean.
- MUST NOT claim saturation based on a stale pre-repair review.
- MUST NOT claim success based on only one clean review.
- MUST NOT narrow or otherwise change review scope mid-run.
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
   - Normalize the results into `clean`, `blocked`, or a short actionable findings set with stable fingerprints.
3. **Candidate clean**
   - If the review is clean and `clean_streak == 0`, mark `candidate_clean`, set `clean_streak=1`, and immediately run another fresh native review on the unchanged artifact state.
   - Do not finish on this first clean.
4. **Saturation confirmation**
   - If the clean-confirmation review is also clean on the unchanged artifact state, set `clean_streak=2` and finish.
   - If the clean-confirmation review returns actionable findings, reset `clean_streak=0`, record `review_reconciliation`, and continue to repair.
5. **Repair**
   - Invoke `$fixed-point-driver` with the latest actionable findings and the current finding ledger.
   - Instruct it to:
     - resolve the seeded findings to non-recurrence on the current artifact state
     - close any directly exposed proof-hook or adjacent-seam issue needed to keep the seeded findings closed
     - keep changes narrow and evidence-backed
     - run the smallest sufficient validation
     - return control after remediation and validation with seeded-finding status, `fix_discovered_count`, and per-finding provenance
   - Do not let `$fixed-point-driver` own the outer re-review loop.
6. **Validation gate**
   - Confirm the post-remediation validation signal passes.
   - If it fails or no reliable signal exists, stop blocked.
   - Any edit resets `clean_streak=0`.
7. **Re-review**
   - Re-run fresh native review on the same frozen scope.
   - If findings recur, reconcile them against the seeded-finding ledger before the next repair.
8. **Repeat**
   - Continue until native-review saturation is reached or the run is blocked.

## How to invoke `$fixed-point-driver`
When handing off to `$fixed-point-driver`, pass all of the following:
- the frozen review scope (`base_branch` + `comparison_sha`, or `commit_sha`)
- the latest actionable findings from the most recent native review
- the current seeded finding ledger, including `seeded_finding_fingerprints`
- any reopening-round `review_reconciliation`
- the instruction that the goal is to resolve the seeded findings to non-recurrence on the current artifact state so the next fresh native review can focus on different remaining issues
- the instruction that it may close directly exposed proof-hook or adjacent-seam issues needed to keep the seeded findings closed, but must not widen into unrelated redesign
- the instruction to keep remediation narrow, validated, and ready for another fresh native review round
- the instruction to return `seeded_findings_closed`, `seeded_findings_still_open`, `fix_discovered_count`, and per-finding provenance in the form `Origin=review_seed|proof_hook|adjacent_seam|validation_gap`

Use `$fixed-point-driver` as an internal repair phase.
Do not mirror its full ledgers back to the user unless the run is blocked and the ledger is the only way to explain the blocker.

## Minimal final response
Final output must use exactly this shape:

**Status**
`done` or `blocked`; `cycles=`; `clean_streak=`

**Review**
`scope=; last_review=; last_action=`

**Validation**
`<signal>` or `blocked: no reliable validation signal`

**Do Next**
`none` when done; otherwise one exact next step
