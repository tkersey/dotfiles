# Landing Protocol

This reference defines the operational details behind `$land`. The order is
normative: target binding, fresh evidence, guarded mutation, live postcondition,
then cleanup.

## 1. Bind the exact target

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

A SHIP-v1 receipt may identify the intended PR, but live GitHub state remains
authoritative.

## 2. Update policy and evidence invalidation

Do not update or rewrite the PR branch merely because it is behind. First read
repository policy and select the authorized update method.

When an update is permitted:

```bash
gh pr update-branch "$pr" --repo "$repo"
# or, only when policy explicitly selects it:
gh pr update-branch "$pr" --repo "$repo" --rebase
```

Any push, branch update, review-thread resolution, approval change, or other
material mutation invalidates every prior review, check, mergeability, and
head-OID observation. Rebuild the complete snapshot after the final mutation.

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
          comments(last: 1) {
            totalCount
            nodes {
              author { login }
              body
              url
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

Require all of the following:

```text
first page contains totalCount
sum(nodes across pages) == totalCount
last page pageInfo.hasNextPage == false
all pages report the same headRefOid
that headRefOid == expected head OID
all thread IDs are unique
unresolved thread count == 0
```

If any invariant fails, block. Do not fall back to the first 100 threads.

For an unresolved thread, retrieve enough of the conversation to understand the
concern before choosing its disposition. The latest comment alone is an index,
not always sufficient evidence.

Resolve an objectively addressed or explicitly withdrawn thread with:

```bash
gh api graphql \
  -f threadId='<thread-node-id>' \
  -f query='mutation($threadId:ID!){resolveReviewThread(input:{threadId:$threadId}){thread{id isResolved}}}'
```

Then discard the old inventory and fetch every page again.

## 4. Structured review and blocker state

Read structured review state:

```bash
gh pr view "$pr" --repo "$repo" \
  --json reviewDecision,latestReviews,reviewRequests,comments,headRefOid
```

Repository policy determines whether an approval is required. Active
`CHANGES_REQUESTED`, pending required review, unanswered material questions, or
an explicit top-level blocker prevents landing. Do not infer approval solely
from free-form prose when `reviewDecision` and latest review states are
available.

## 5. Required checks

Wait, then read a separate structured terminal snapshot:

```bash
gh pr checks "$pr" --repo "$repo" --required --watch

gh pr checks "$pr" --repo "$repo" --required \
  --json name,state,bucket,link \
  > required-checks.json
```

The waiter cannot be the final proof because canceled checks are not equivalent
to passed checks.

Default policy:

| Bucket | Disposition |
|---|---|
| `pass` | accept |
| `fail` | block |
| `pending` | block |
| `cancel` | block |
| `skipping` | block unless repository policy explicitly accepts the skipped required context |

If no required checks are returned, prove that the base-branch policy requires
none. An API error or unknown policy is not an empty passing set.

## 6. Preflight snapshot

Normalize live observations into the evaluator input:

```json
{
  "expected": {
    "repository": "owner/name",
    "pr_number": 123,
    "base_ref": "main",
    "head_repository": "owner/name",
    "head_ref": "feature",
    "head_oid": "0123456789abcdef"
  },
  "observed": {
    "repository": "owner/name",
    "pr_number": 123,
    "state": "OPEN",
    "is_draft": false,
    "base_ref": "main",
    "head_repository": "owner/name",
    "head_ref": "feature",
    "head_oid": "0123456789abcdef"
  },
  "reviews": {
    "inventory_complete": true,
    "unresolved_threads": 0,
    "review_decision": "APPROVED",
    "requested_changes_active": false,
    "explicit_blockers": 0
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

`merge.delivery_mode` is one of `immediate`, `queue`, or `auto`.

Evaluate:

```bash
uv run python3 codex/skills/land/scripts/evaluate_preflight.py snapshot.json
```

The evaluator is pure: it performs no network, Git, filesystem, merge, or cleanup
mutation. It returns one route and an explicit blocker list.

## 7. Final exact-head recapture

Immediately before the merge mutation, reread live state and recapture the head:

```bash
head_oid="$({
  gh pr view "$pr" --repo "$repo" --json headRefOid --jq .headRefOid
})"
```

Require `head_oid` to equal the evaluator's expected head. If it differs, stop,
discard every gate, and restart preflight against the newly authorized target.

## 8. Merge actions

Never pass `--delete-branch` here.

Immediate merge, using the repository-approved method:

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

Substitute `--merge` or `--rebase` only when repository policy selects that
method. Never use `--admin` as a retry mechanism. An administrator bypass
requires a new explicit user authorization naming the rule that would be
bypassed.

## 9. Wait for the terminal postcondition

After any merge, queue, or auto-merge command, repeatedly read live PR state:

```bash
gh pr view "$pr" --repo "$repo" \
  --json number,url,state,headRefOid,mergedAt,mergeCommit,autoMergeRequest
```

Continue waiting while the exact PR remains open and legitimately queued or
auto-enabled. Stop and report a blocker when it is closed without merge, removed
from the expected flow, or its head changes.

Landing is proven only when:

```text
state == MERGED
mergedAt != null
mergeCommit.oid != null
headRefOid == expected head OID
```

Record the merge commit OID and timestamp before cleanup.

## 10. Worktree cleanup

Worktree cleanup precedes local branch deletion because Git refuses ordinary
branch deletion while a worktree uses the branch, and because force deletion can
hide unique local state.

### Inventory

From a surviving repository context:

```bash
git worktree list --porcelain -z > worktrees.before
```

Parse NUL-delimited records. Relevant fields include:

```text
worktree <absolute-path>
HEAD <oid>
branch refs/heads/<branch>
locked [reason]
prunable <reason>
```

Select only records whose branch field is exactly:

```text
refs/heads/<head_ref>
```

Do not select detached records merely because their `HEAD` equals the landed
head OID.

### Per-worktree gates

For each selected record:

1. Require the record's `HEAD` to equal the landed head OID.
2. Require `git rev-parse refs/heads/<head_ref>` to equal the landed head OID.
3. Require the path to be accessible, unless the record is explicitly stale and prunable.
4. Require no `locked` marker.
5. Require clean tracked and untracked state:

   ```bash
   git -C "$worktree_path" status --porcelain=v1 -uall
   ```

6. Detect whether the running process's current directory is the worktree path or a descendant. Move to a different surviving worktree or other safe repository context before removal.

Any failed gate preserves the worktree and records an exact blocker. Never use
`--force` to convert uncertainty into deletion.

### Primary worktree

The primary worktree is not removable with `git worktree remove`. If it uses the
head branch:

```bash
git -C "$primary_path" fetch <base-remote> <base-ref>
git -C "$primary_path" switch <base-ref>
git -C "$primary_path" merge --ff-only <base-remote>/<base-ref>
```

If the switch or fast-forward fails, preserve the worktree and branch. Successful
switching removes the association without deleting the primary checkout.

### Linked worktree

For a clean, unlocked linked worktree whose `HEAD` equals the landed head OID:

```bash
cd "$safe_surviving_context"
git worktree remove -- "$worktree_path"
```

Do not use:

```text
git worktree remove --force
rm -rf <worktree-path>
```

After removal, refetch the inventory and prove that the exact path and branch
association are gone.

For a stale `prunable` record whose directory is already absent, run:

```bash
git worktree prune --verbose
```

Then refetch and verify. Pruning is administrative cleanup, not permission to
delete a live directory.

### Completion condition

Worktree cleanup is complete only when no inventory record contains
`branch refs/heads/<head_ref>`. Detached worktrees remain untouched.

## 11. Branch cleanup

Remote branch deletion requires:

```text
head repository is the intended repository
remote ref exists
remote ref OID == landed head OID
cleanup policy requests deletion
```

Local branch deletion requires:

```text
local ref OID == landed head OID
no associated worktree remains
current worktree is on the updated base branch
cleanup policy requests deletion
```

Under squash merge, use a force delete only after those proofs:

```bash
git branch -D -- "$head_ref"
```

For a merge commit or rebase merge, prefer ordinary safe deletion when possible:

```bash
git branch -d -- "$head_ref"
```

Never rely on `gh pr merge --delete-branch` for these decisions.

## 12. Final verification

Read back:

```text
PR remains MERGED at the expected head
remote branch deletion result
local branch deletion result
full worktree inventory
updated base branch OID
```

Emit LAND-v1 even when cleanup is partially blocked. The merge result and each
cleanup surface are independent facts.
