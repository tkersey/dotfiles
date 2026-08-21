---
name: land
description: "Safely finish an explicitly selected GitHub PR: reconcile every unresolved review thread, bind each successor head as a fresh landing epoch, verify merge admission, merge the exact approved head or wait for queue/auto-merge completion, prove live MERGED state, and then clean remote/local branches and associated worktrees. Use only for explicit `$land` or unmistakable merge/land intent. Do not use merely to watch CI, close an unmerged PR, delete a branch, sync local state, or open/update a PR."
---

# Land

## Purpose

Finish one explicitly selected pull request as a proof-preserving landing
protocol.

Core laws:

```text
An unresolved review thread means merge not ready, not workflow terminal.
Every unresolved review thread must reach a justified disposition before merge.
Thread resolution records proof; it never creates proof.
Mutation success is not landing success.
```

`$land` owns end-to-end completion: review-thread inventory, review closure,
fresh merge admission, exact-head merge, live terminal readback, and cleanup.
It does not duplicate semantic owners:

- `$review-fold` classifies a concern's authority and current applicability;
- `$actuating review-closeout` repairs accepted current concerns, with its direct
  owner-local repair path available for an isolated mistake;
- `$ship` publishes a validated successor head;
- `$land` proves the resulting disposition, resolves the GitHub thread, and
  restarts landing against the successor head.

Copied receipts and thread metadata are never authoritative for current merge
readiness.

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

Bind one immutable landing epoch before any mutation:

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

Never infer an irreversible target from a branch name alone. Require the live
repository, PR number, base ref, head repository, head ref, and head OID to match
the epoch. Record the base OID as an observation; a merge queue may legitimately
advance the base before the PR lands.

## State model

Choose exactly one route:

```text
reconcile-reviews
rebind-successor-head
merge-now
queue-and-wait
auto-merge-and-wait
cleanup-only
obstructed
```

- `reconcile-reviews`: merge is not ready, but review closure can progress.
- `rebind-successor-head`: a repair or authorized branch update published a new
  head; supersede the old epoch and rebuild all evidence.
- `merge-now`: every admission gate passes and immediate merge is permitted.
- `queue-and-wait`: every queue-admission gate passes; submit and wait for live
  merged state.
- `auto-merge-and-wait`: every admission gate passes and explicit policy selects
  auto-merge; enable it and wait for live merged state.
- `cleanup-only`: the exact PR/head is already merged.
- `obstructed`: no safe authorized successor action exists.

A repairable review concern is never `obstructed` before repair is attempted.
Reserve obstruction for missing mutation authority, an undecidable user-owned
requirement, required reviewer clarification, an unrepairable conflict, invalid
or unavailable evidence, or a repair whose strongest relevant validation fails.

## Landing epochs

A landing epoch is immutable in repository/PR/base/head identity. Any push,
branch update, review repair, or other head mutation supersedes the current
epoch rather than retargeting it.

After `$ship` publishes successor head `H[n+1]`:

```text
close epoch H[n] as superseded
bind H[n+1] as a new immutable target
discard every admission observation from H[n]
fetch the complete review inventory again
run complete fresh preflight
```

Do not carry approvals, checks, mergeability, thread counts, or resolution proof
across a head change without fresh current-head evidence.

## Review reconciliation

Every unresolved review thread is owned work for `$land`, not merely a reason to
stop. Land must drive every unresolved thread to a justified resolution before
merge or prove an exact obstruction.

For each unresolved thread:

1. Fetch enough of the complete conversation to understand the concern. A bare
   thread ID, latest-comment excerpt, `isOutdated`, or status count is
   insufficient.
2. Preserve the concern as a witness and ask `$review-fold` for law authority and
   current applicability when the disposition is not mechanically evident.
3. Choose exactly one disposition:

   ```text
   fixed-and-evidenced
   already-satisfied-and-evidenced
   obsolete-and-evidenced
   reviewer-withdrawn
   nonblocking-by-authority
   needs-authority
   needs-reviewer-clarification
   repair-failed
   ```

4. For a current accepted concern that is directly repairable, do not return
   terminal obstruction. Use the smallest authorized repair path:

   ```text
   patch -> validate -> publish successor head -> prove current-head discharge
   ```

   Then enter `rebind-successor-head` and restart complete preflight.
5. Resolve the GitHub thread only after the disposition is evidenced at the
   current head and live resolution readback succeeds.
6. Refetch every review-thread page after each resolution batch and require zero
   unresolved threads before merge admission.

`fixed-and-evidenced` requires a successor head distinct from the head on which
the current defect was observed. Use `already-satisfied-and-evidenced` when the
current head already falsifies the concern. `isOutdated` alone never proves
obsolescence.

A generic continuation instruction such as "continue", "finish it", or "do your
job" is not reviewer withdrawal, defect invalidation, new-requirement adoption,
or permission to dismiss a current substantive concern.

Never bulk-resolve from bare thread IDs. Batch execution is permitted only after
each thread is bound to an individual evidence-bearing disposition. Preserve a
current substantive concern at an unchanged head; do not resolve or merge it.

See [landing-protocol.md](references/landing-protocol.md).

## Merge admission

After review reconciliation is complete, rebuild one current-head snapshot with:

- exact target identity and `headRefOid`;
- complete paginated review-thread inventory and unresolved thread IDs;
- per-thread reconciliation records for every thread resolved by this landing;
- structured review decision, latest reviews, and review requests;
- final required-check buckets;
- conflict, branch-freshness, merge-method, queue, and repository-policy state.

Run the pure evaluator:

```bash
uv run python3 codex/skills/land/scripts/evaluate_preflight.py <snapshot.json>
```

Interpret its result:

```text
exit 0 / verdict pass      merge admission is ready
exit 3 / verdict continue  follow the returned nonterminal route
exit 2 / verdict block     preserve state and report the exact obstruction
```

`REVIEW_THREADS_UNRESOLVED` routes to `reconcile-reviews`; it is never by itself
a terminal workflow result.

## Required-check gate

`gh pr checks --watch` is only a waiter. After it returns, read a structured
final snapshot with `name`, `state`, `bucket`, and `link`.

For required checks:

- `pass` is accepted;
- `fail`, `pending`, or `cancel` obstructs merge admission;
- `skipping` obstructs unless live repository policy explicitly accepts it;
- an empty required-check set is accepted only after proving policy requires
  none.

Never interpret command exit zero alone as green.

## Merge mutation

Immediately before mutation, repeat the complete current-head review sweep and
merge-admission readback, then recapture `headRefOid`. Pass that same OID to the
merge command's exact-head guard.

- Never bundle cleanup into the merge command; do not use `--delete-branch`.
- Ordinary `$land` never performs an administrator protection bypass.
- Keep the merge method aligned with live repository policy.
- Queue and auto-merge submission are nonterminal; continue until live state is
  actually merged.
- A merge queue does not require the source branch to be current merely because
  direct strict merging would; derive branch freshness from the selected route
  and live policy.

If the head changes, stop the mutation, supersede the epoch, and restart against
the newly authorized head. Never retarget an in-flight merge attempt.

## Landing postcondition

Before reporting success or cleaning anything, prove from live state:

```text
repository and PR still match the target
state == MERGED
mergedAt is non-null
mergeCommit OID is non-null
landed head OID == expected head OID
```

A successful command, queue admission, or enabled auto-merge request is not a
completed landing.

## Cleanup transaction

Cleanup is post-merge and independently reported. A cleanup obstruction does not
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
- preserve and report locked worktrees, inaccessible paths, head drift, unique
  commits, or dirty state;
- never use `git worktree remove --force` and never delete the directory with
  `rm -rf`;
- switch the primary worktree to the base branch and fast-forward it rather than
  removing it;
- move the running shell outside a linked worktree, run
  `git worktree remove -- <path>`, and verify the record disappeared;
- prune only stale administrative metadata after path-safe removal and refetch
  the complete worktree inventory.

All associated worktrees must be removed or switched away before deleting the
local branch.

### Branches

Delete the remote branch only when its live ref still equals the landed head OID
and the head repository is the intended deletion target. Delete the local branch
only when its ref still equals the landed head OID, no worktree is associated,
and the current worktree is on the updated base branch.

If an exact requested ref is already absent, report `already-absent` as a
successful no-op; never claim that this landing deleted it.

Under squash or rebase merge, local branch deletion may require force because the
landed commit is rewritten. Use it only after exact-OID and worktree proof; never
inherit implicit force deletion from `gh pr merge`.

## Output

Emit one `LAND-v2` record after terminal readback and cleanup attempts. Preserve
landing epochs, per-thread review dispositions, merge admission, postcondition,
remote cleanup, local cleanup, per-worktree cleanup, and plural obstructions as
separate facts. See [land-record.md](references/land-record.md).

## Guardrails

- Never merge an ambiguous PR target.
- Never treat unresolved review threads as terminal when safe repair can progress.
- Never resolve a current substantive concern without current-head discharge
  evidence.
- Never resolve threads from bare IDs or generic user encouragement.
- Never reuse evidence across a material head mutation.
- Never merge with an unresolved or incompletely inventoried review thread.
- Never treat canceled required checks as green.
- Never use `--admin` in ordinary `$land`.
- Never report queued, auto-enabled, or command-success state as merged.
- Never clean a branch or worktree before a live `MERGED` postcondition.
- Never force-remove a dirty, locked, drifted, or unidentified worktree.
- If obstructed, preserve state and report every exact obstruction and next safe
  action.

## Resources

- [landing-protocol.md](references/landing-protocol.md)
- [land-record.md](references/land-record.md)
- [decision-contract.json](references/decision-contract.json)
