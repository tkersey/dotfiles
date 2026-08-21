# Landing Protocol

This reference defines the operational details behind `$land`. The normative
order is:

```text
bind landing epoch
-> reconcile every review thread
-> bind any successor head as a new epoch
-> collect fresh merge admission
-> guarded merge mutation
-> live postcondition
-> cleanup
```

## 1. Bind the exact landing epoch

Use an explicit repository and PR selector for every GitHub command:

```bash
repo='owner/name'
pr='123'

gh pr view "$pr" --repo "$repo" \
  --json number,url,state,isDraft,baseRefName,baseRefOid,headRefName,headRefOid,headRepository,headRepositoryOwner,mergeable,mergeStateStatus,reviewDecision,reviewRequests,latestReviews,autoMergeRequest,mergeCommit,mergedAt
```

Retain:

```yaml
expected:
  repository:
  pr_number:
  base_ref:
  base_oid:
  head_repository:
  head_ref:
  head_oid:
```

Reject a mismatched repository, PR number, base ref, head repository, head ref,
or head OID. Branch names are not globally unique and are never sufficient by
themselves.

A SHIP receipt may identify the intended PR, but live GitHub state remains
authoritative.

## 2. Authorized branch updates

Do not update or rewrite the PR branch merely because it is behind. First read
live repository policy and select the authorized route.

When a direct branch update is required and permitted:

```bash
gh pr update-branch "$pr" --repo "$repo"
# or, only when policy explicitly selects it:
gh pr update-branch "$pr" --repo "$repo" --rebase
```

Any branch update publishes a new head. Close the current landing epoch as
superseded and bind a successor landing epoch before further review or merge
admission.

A merge queue synthesizes and validates a merge group against the current base;
it does not require the source branch to be updated merely because a direct
strict merge route would require freshness.

## 3. Complete review-thread inventory

Use GraphQL pagination with the CLI's recognized `$endCursor` variable:

```bash
read -r -d '' review_query <<'GRAPHQL' || true
query(
  $owner: String!
  $repo: String!
  $number: Int!
  $endCursor: String
) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      headRefOid
      reviewThreads(first: 100, after: $endCursor) {
        totalCount
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          comments(first: 100) {
            totalCount
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              author { login }
              body
              url
              createdAt
            }
          }
        }
      }
    }
  }
}
GRAPHQL

gh api graphql --paginate --slurp \
  -f owner='<owner>' \
  -f repo='<repo-name>' \
  -F number="$pr" \
  -f query="$review_query" \
  > review-pages.json
```

Require:

```text
first page contains totalCount
sum(thread nodes across pages) == totalCount
last thread page hasNextPage == false
all thread IDs are unique
all pages report the same headRefOid
that headRefOid == epoch head OID
complete conversation context is available for every unresolved thread
```

If conversation pagination is needed, fetch it before disposition. The latest
comment is an index, not necessarily the concern.

Incomplete inventory, API failure, missing counts, duplicate IDs, or head drift
is an obstruction. Do not fall back to the first 100 threads and do not treat
absence caused by an API failure as zero unresolved threads.

## 4. Review reconciliation loop

An unresolved thread blocks merge admission, but it is a nonterminal workflow
state whenever safe resolution work remains.

For every unresolved thread:

1. Preserve its complete concern and source URL as a witness.
2. Inspect the current head and determine current applicability.
3. Use `$review-fold` when law authority or applicability is not mechanically
   evident.
4. Choose one disposition:

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

5. Resolve only the first five dispositions. The final three preserve the thread
   and produce an exact obstruction.

### Directly repairable concerns

A current accepted concern that is safely repairable within the authorized PR
scope must not cause terminal obstruction before repair is attempted.

Use the existing semantic owners:

```text
Review Fold classification
-> Actuating review-closeout or isolated owner-local repair
-> strongest relevant validation
-> Ship publication
-> Land current-head discharge proof
-> Land thread resolution
```

The minimum behavioral trace is:

```text
patch -> validate -> publish successor head
-> prove current-head discharge
-> resolve thread
-> complete fresh preflight
```

If repair changes the head from `H0` to `H1`:

```text
close H0 epoch as superseded
bind H1 as the successor landing epoch
discard every admission observation from H0
refetch every review thread at H1
reclassify any still-current concerns
rebuild required checks and repository policy at H1
```

Do not automatically retarget the old epoch. The PR identity persists; the head
identity does not.

### Evidence-bearing resolution record

Before resolving a thread, retain:

```yaml
review_resolution:
  thread_id:
  concern_ref:
  observed_head_oid:
  resolved_head_oid:
  law_authority: entailed | strengthening | preference |
    new-requirement | underdetermined
  current_applicability: still-present | transformed-applicable |
    already-excluded | not-comparable | unknown
  disposition: fixed-and-evidenced | already-satisfied-and-evidenced |
    obsolete-and-evidenced | reviewer-withdrawn | nonblocking-by-authority
  evidence_refs: []
  resolution_readback: true
```

Requirements:

- `fixed-and-evidenced` requires `resolved_head_oid != observed_head_oid` and
  validation or proof against `resolved_head_oid`;
- `already-satisfied-and-evidenced` requires current-head source or test evidence
  that the alleged defect is absent;
- `obsolete-and-evidenced` requires objective current-head evidence; GitHub
  `isOutdated` alone is insufficient;
- `reviewer-withdrawn` requires the reviewer's explicit withdrawal;
- `nonblocking-by-authority` requires the accepted Goal or public-contract basis
  showing the requested property is not a current merge obligation;
- every record requires live GitHub resolution readback;
- all evidence must be current at the final epoch head.

A generic continuation instruction such as "continue", "finish it", or "do your
job" is not withdrawal, defect invalidation, or authority to dismiss a concern.

### Prohibited resolution behavior

Never:

- resolve from bare thread IDs;
- convert `isOutdated` directly into `obsolete`;
- bulk-resolve before assigning an individual disposition to every thread;
- call a current substantive defect fixed at an unchanged head;
- modify a temporary preflight count to simulate resolution;
- resolve a concern merely because the user asked Land to finish the PR.

Batching is permitted only after every member is bound to a valid individual
record. Review Fold may quotient duplicate witnesses into a shared semantic
class, but every original thread must retain its own evidence binding and live
resolution readback.

### Resolution mutation

For an evidenced resolvable disposition:

```bash
gh api graphql \
  -f threadId='<thread-node-id>' \
  -f query='mutation($threadId:ID!){resolveReviewThread(input:{threadId:$threadId}){thread{id isResolved}}}'
```

Require the returned thread ID to match and `isResolved` to be true. Then discard
the previous inventory and refetch every page.

The reconciliation loop reaches its fixed point only when:

```text
complete current-head inventory
unresolved thread IDs == []
all threads resolved by this landing have complete current-head records
no active requested changes
no explicit unresolved material blocker
```

## 5. Structured review and approval state

Read structured review state after the final resolution mutation:

```bash
gh pr view "$pr" --repo "$repo" \
  --json reviewDecision,latestReviews,reviewRequests,comments,headRefOid
```

Active `CHANGES_REQUESTED`, unanswered material questions, or an explicit
current blocker routes back to `reconcile-reviews`. A required approval that is
simply absent and cannot be supplied by Land is an obstruction with the exact
required next action.

Do not infer approval solely from free-form prose when structured review state is
available.

## 6. Required checks

Wait, then read a separate structured terminal snapshot:

```bash
gh pr checks "$pr" --repo "$repo" --required --watch

gh pr checks "$pr" --repo "$repo" --required \
  --json name,state,bucket,link \
  > required-checks.json
```

The waiter is not final proof.

| Bucket | Disposition |
|---|---|
| `pass` | accept |
| `fail` | obstruct |
| `pending` | wait, then reread |
| `cancel` | obstruct |
| `skipping` | obstruct unless live policy explicitly accepts the skipped required context |

If no required checks are returned, prove that current base-branch policy
requires none. An API error or unknown policy is not an empty passing set.

## 7. LAND-PREFLIGHT-v2 snapshot

Normalize current observations without erasing unresolved thread identities:

```json
{
  "expected": {
    "repository": "owner/name",
    "pr_number": 123,
    "base_ref": "main",
    "head_repository": "owner/name",
    "head_ref": "feature",
    "head_oid": "1111111111111111111111111111111111111111"
  },
  "observed": {
    "repository": "owner/name",
    "pr_number": 123,
    "state": "OPEN",
    "is_draft": false,
    "base_ref": "main",
    "head_repository": "owner/name",
    "head_ref": "feature",
    "head_oid": "1111111111111111111111111111111111111111"
  },
  "reviews": {
    "inventory_complete": true,
    "unresolved_thread_ids": [],
    "review_decision": "APPROVED",
    "requested_changes_active": false,
    "explicit_blockers": 0,
    "reconciliation": {
      "initial_unresolved_thread_ids": ["PRRT_thread_1"],
      "records": [
        {
          "thread_id": "PRRT_thread_1",
          "concern_ref": "https://github.com/owner/name/pull/123#discussion_r1",
          "observed_head_oid": "0000000000000000000000000000000000000000",
          "resolved_head_oid": "1111111111111111111111111111111111111111",
          "law_authority": "entailed",
          "current_applicability": "already-excluded",
          "disposition": "fixed-and-evidenced",
          "evidence_refs": [
            "commit:1111111111111111111111111111111111111111",
            "test:uv run python3 -m unittest"
          ],
          "resolution_readback": true
        }
      ]
    }
  },
  "checks": {
    "required_expected": true,
    "items": [
      {"name": "test", "required": true, "bucket": "pass"}
    ]
  },
  "merge": {
    "delivery_mode": "immediate",
    "conflict_free": true,
    "branch_up_to_date": true,
    "strict_freshness_required": true,
    "policy_satisfied": true,
    "method_allowed": true,
    "admin_override": false
  },
  "policy": {
    "approvals_required": true,
    "allow_required_skipping": false
  }
}
```

`merge.delivery_mode` is `immediate`, `queue`, or `auto`.

Evaluate:

```bash
uv run python3 codex/skills/land/scripts/evaluate_preflight.py snapshot.json
```

The evaluator is pure. It performs no network, Git, filesystem, merge, thread
resolution, or cleanup mutation.

Result semantics:

```text
verdict pass / exit 0
  merge admission ready or cleanup-only

verdict continue / exit 3
  workflow can progress through reconcile-reviews

verdict block / exit 2
  evidence or authority is unsound or unavailable; preserve state
```

An unresolved thread ID produces `continue`, `merge_admission: not-ready`, and
`mode: reconcile-reviews`. It does not produce terminal obstruction merely for
being unresolved.

## 8. Final current-head recapture

Immediately before merge mutation:

1. refetch the complete review-thread inventory;
2. require zero unresolved IDs;
3. reread structured review and required checks;
4. reevaluate the current snapshot;
5. recapture `headRefOid`:

   ```bash
   head_oid="$({
     gh pr view "$pr" --repo "$repo" --json headRefOid --jq .headRefOid
   })"
   ```

Require `head_oid` to equal the evaluator's expected head. If it differs, stop,
supersede the epoch, and restart complete preflight.

## 9. Merge actions

Never pass `--delete-branch` here. Never use `--admin` in ordinary `$land`.

Immediate merge using the repository-approved method:

```bash
gh pr merge "$pr" --repo "$repo" \
  --squash \
  --match-head-commit "$head_oid"
```

Merge queue submission:

```bash
gh pr merge "$pr" --repo "$repo" \
  --match-head-commit "$head_oid"
```

Explicit auto-merge submission:

```bash
gh pr merge "$pr" --repo "$repo" \
  --auto \
  --squash \
  --match-head-commit "$head_oid"
```

Substitute `--merge` or `--rebase` only when live repository policy selects that
method.

## 10. Wait for the terminal postcondition

After any merge, queue, or auto-merge command, repeatedly read live PR state:

```bash
gh pr view "$pr" --repo "$repo" \
  --json number,url,state,headRefOid,mergedAt,mergeCommit,autoMergeRequest
```

Continue waiting while the exact PR remains open and legitimately queued or
auto-enabled. Stop when it is closed without merge, removed from the expected
flow, or its head changes.

Landing is proven only when:

```text
state == MERGED
mergedAt != null
mergeCommit.oid != null
headRefOid == expected head OID
```

Record the merge commit OID and timestamp before cleanup.

## 11. Worktree cleanup

Worktree cleanup precedes local branch deletion because worktrees can hold unique
local state.

### Inventory

From a surviving repository context:

```bash
git worktree list --porcelain -z > worktrees.before
```

Select only records whose branch field is exactly:

```text
refs/heads/<head_ref>
```

Do not select detached records merely because their `HEAD` equals the landed
head OID.

### Per-worktree gates

For each selected record:

1. Require the record `HEAD` to equal the landed head OID.
2. Require `refs/heads/<head_ref>` to equal the landed head OID.
3. Require the path to be accessible unless explicitly stale and prunable.
4. Require no `locked` marker.
5. Require clean tracked and untracked state:

   ```bash
   git -C "$worktree_path" status --porcelain=v1 -uall
   ```

6. Move the running process outside a linked worktree before removal.

Any failed gate preserves the worktree and reports an exact cleanup obstruction.
Never use `--force` to convert uncertainty into deletion.

### Primary worktree

If the primary worktree uses the head branch:

```bash
git -C "$primary_path" fetch <base-remote> <base-ref>
git -C "$primary_path" switch <base-ref>
git -C "$primary_path" merge --ff-only <base-remote>/<base-ref>
```

Preserve it if switching or fast-forwarding fails.

### Linked worktree

For a clean, unlocked linked worktree at the landed head:

```bash
cd "$safe_surviving_context"
git worktree remove -- "$worktree_path"
```

Do not use:

```text
git worktree remove --force
rm -rf <worktree-path>
```

Refetch inventory and prove the exact association disappeared.

For an absent stale `prunable` path, `git worktree prune --verbose` may remove
administrative metadata. Inventory before and after, and report every removed
record.

Completion requires no record with `branch refs/heads/<head_ref>`. Detached
worktrees remain untouched.

## 12. Branch cleanup

If an exact requested local or remote ref is already absent, record
`already-absent` as a successful no-op. API failure or ambiguous lookup is an
obstruction, not absence.

Remote deletion requires:

```text
head repository is the intended repository
remote ref exists
remote ref OID == landed head OID
cleanup policy requests deletion
```

Local deletion requires:

```text
local ref OID == landed head OID
no associated worktree remains
current worktree is on the updated base branch
cleanup policy requests deletion
```

Under squash or rebase merge, force deletion may be necessary after those exact
proofs:

```bash
git branch -D -- "$head_ref"
```

For a merge commit, prefer ordinary safe deletion when possible:

```bash
git branch -d -- "$head_ref"
```

Never rely on `gh pr merge --delete-branch` for these decisions.

## 13. Final verification

Read back:

```text
PR remains MERGED at the expected head
review unresolved IDs remain empty
remote branch deletion result
local branch deletion result
full worktree inventory
updated base branch OID
```

Emit `LAND-v2` even when cleanup is partially obstructed. Merge, review
reconciliation, remote cleanup, local cleanup, and each worktree remain
independent facts.
