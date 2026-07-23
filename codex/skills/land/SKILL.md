---
name: land
description: "Safely finish an explicitly selected GitHub PR: bind exact repository/base/head identity, close review blockers, verify required checks, merge or wait for queue/auto-merge completion, prove live MERGED state, and then clean remote/local branches and associated worktrees. Use only for explicit `$land` or unmistakable merge/land intent. Do not use merely to watch CI, close an unmerged PR, delete a branch, sync local state, or open/update a PR."
---

# Land

## Purpose

Land one explicitly selected pull request as a fail-closed transaction.

Core rule:

```text
Mutation success is not landing success.
Do not clean branches or worktrees until live GitHub state proves the intended PR is MERGED.
```

`$ship` owns PR creation, proof publication, and draft-to-ready promotion. `$land`
consumes live state and may consume SHIP-v1 as a hint, but copied receipts are
never authoritative for merge readiness.

## Activation boundary

Use `$land` for explicit `$land`, merge, land, or finish-the-PR intent.

Do not use `$land` merely to:

- watch checks or workflow runs;
- close or abandon an unmerged PR;
- delete a branch or worktree without a merged-PR target;
- synchronize ordinary local state;
- open, update, or promote a PR; use `$ship`.

The skill is side-effecting and must remain explicit-invocation only.

## Input

Establish one immutable target before any mutation:

```yaml
land_input:
  repository: owner/name
  pr_number:
  pr_url:
  expected:
    base_ref:
    base_oid:
    head_repository: owner/name
    head_ref:
    head_oid:
  requested_merge_method: merge | squash | rebase | repo-policy
  cleanup:
    remote_branch: yes | no
    local_branch: yes | no
    associated_worktrees: yes | no
```

Resolve the repository and PR explicitly. Never infer an irreversible target
from a branch name alone. Require the live repository, PR number, base ref, head
repository, head ref, and head OID to match the target. Record the base OID as a
preflight fact; merge queues may legitimately advance the base before the PR
lands.

## State model

Choose exactly one mode:

```text
merge-now
queue-and-wait
auto-merge-and-wait
cleanup-only
blocked
```

- `merge-now`: every gate passes and the repository permits immediate merge.
- `queue-and-wait`: every admission gate passes and repository policy requires a merge queue.
- `auto-merge-and-wait`: every admission gate passes and explicit repository/user policy selects auto-merge.
- `cleanup-only`: the exact PR is already merged and only post-merge cleanup remains.
- `blocked`: target identity, evidence, policy, or authority is incomplete or inconsistent.

A draft PR, closed-unmerged PR, conflicting PR, changed head, active requested
changes, incomplete review inventory, missing approval, or non-green required
check is `blocked`. Do not silently reopen, promote, update, override, or retarget.

## Freshness invariant

Every push, branch update, review-thread resolution, approval change, or other
material PR mutation invalidates all cached landing evidence.

After the final mutation, rebuild one fresh snapshot containing:

- exact target identity and `headRefOid`;
- complete paginated review-thread inventory;
- structured review decision, latest reviews, and review requests;
- final required-check buckets;
- conflict, branch-freshness, merge-method, queue, and repository-policy state.

Run the pure evaluator:

```bash
uv run python3 codex/skills/land/scripts/evaluate_preflight.py <snapshot.json>
```

Proceed only when its route matches the intended mode. See
[references/landing-protocol.md](references/landing-protocol.md).

## Review gate

Fetch every review-thread page. Require the collected node count to equal
`totalCount`, the final `hasNextPage` to be false, and every page to report the
same expected head OID. API failure, missing counts, duplicate/partial pages, or
head drift blocks landing.

Every unresolved thread requires one explicit disposition:

```text
fixed-and-evidenced
obsolete-and-explicitly-withdrawn
resolve-only-with-user-authorization
still-blocking
needs-reviewer-clarification
```

Do not equate `isOutdated` with resolved. Resolve a GitHub thread only when the
concern is objectively fixed or explicitly withdrawn; ambiguous design concerns,
questions, and reviewer-owned blockers remain open. After any resolution,
rebuild the complete inventory.

Use structured `reviewDecision`, `latestReviews`, and `reviewRequests` before
interpreting free-form top-level comments. An explicit unresolved human blocker
still blocks even when GitHub's normalized review decision appears permissive.

## Required-check gate

`gh pr checks --watch` is only a waiter. After it returns, read a structured
final snapshot with `name`, `state`, `bucket`, and `link`.

For required checks:

- `pass` is accepted;
- `fail`, `pending`, or `cancel` blocks;
- `skipping` blocks unless repository policy explicitly accepts that required context as skipped;
- an empty required-check set is accepted only after proving repository policy requires none.

Never interpret command exit zero alone as green.

## Merge mutation

Immediately before mutation, recapture the exact live `headRefOid`. Pass that
same OID to the merge command's exact-head guard.

- Never bundle cleanup into the merge command; do not use `--delete-branch`.
- Never use `--admin` unless the user explicitly authorizes a named protection bypass after seeing the exact blocked rule.
- Keep the merge method aligned with repository policy.
- A queue or auto-merge submission is nonterminal. Continue monitoring until live state is actually merged.

If the head OID changes, the merge must fail or stop. Do not retarget the attempt
to the new head automatically.

## Landing postcondition

Before reporting success or cleaning anything, read live PR state and prove:

```text
repository and PR still match the target
state == MERGED
mergedAt is non-null
mergeCommit OID is non-null
landed head OID == expected head OID
```

For queue and auto-merge modes, wait through all nonterminal states. A successful
submission, enabled auto-merge request, or queue admission is not a completed
landing.

## Cleanup transaction

Cleanup is post-merge and independently reported. A cleanup blocker does not
undo a successful merge; it produces a degraded cleanup result.

Order:

```text
associated worktrees
remote head branch
local head branch
final verification
```

### Associated worktrees

Discover records with:

```bash
git worktree list --porcelain -z
```

A worktree is associated only when its record contains the exact branch ref
`refs/heads/<head_ref>`. A detached worktree at the same commit is not associated
and must be preserved.

For every associated worktree:

- require its `HEAD` and branch ref to equal the landed head OID;
- require a clean tracked and untracked status;
- preserve and report locked worktrees, inaccessible paths, head drift, unique commits, or dirty state;
- never use `git worktree remove --force` and never delete the directory with `rm -rf`;
- if it is the primary worktree, switch it to the base branch and fast-forward rather than removing it;
- if it is a linked worktree, move the running shell outside that path, run `git worktree remove -- <path>`, and verify the record disappeared;
- prune only stale administrative metadata after path-safe removal and then refetch the full worktree inventory.

All associated worktrees must be removed or switched away from the head branch
before deleting the local branch. See the exact algorithm in
[references/landing-protocol.md](references/landing-protocol.md).

### Branches

Delete the remote branch only when the live remote ref still equals the landed
head OID and the head repository is the intended deletion target. Delete the
local branch only when its ref still equals the landed head OID, no worktree is associated with it, and the current worktree is on the updated base branch.
If requested cleanup observes that the exact local or remote branch ref is
already absent, report `already-absent` as a successful no-op; never claim that
the landing workflow deleted it.

Under squash merge, a force branch deletion may be necessary because the landed
commit is not an ancestor of the squash commit. Use it only after the OID and
worktree proofs above; never inherit an implicit force-delete from `gh pr merge`.

## Output

Emit one `LAND-v1` record after terminal readback and cleanup. Keep merge outcome,
remote cleanup, local cleanup, and per-worktree cleanup separate. Use
[references/land-record.md](references/land-record.md).

## Guardrails

- Never merge an ambiguous PR target.
- Never reuse evidence from before the final material mutation.
- Never merge with an unresolved or incompletely inventoried review thread.
- Never treat canceled required checks as green.
- Never bypass protections with `--admin` without explicit user authorization.
- Never report queued, auto-enabled, or command-success state as merged.
- Never clean a branch or worktree before a live `MERGED` postcondition.
- Never force-remove a dirty, locked, drifted, or unidentified worktree.
- If blocked, preserve state and report the exact failed gate and next safe action.

## Resources

- [landing-protocol.md](references/landing-protocol.md)
- [land-record.md](references/land-record.md)
- [decision-contract.yaml](references/decision-contract.yaml)
