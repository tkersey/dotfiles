# Post-Push PR Sweep Contract

`$resolve` may not claim PR-comment-reviewed completion until visible PR comments and review threads are swept against the latest pushed commit.

## PR discovery

Prefer provider-native tooling. For GitHub, `gh pr view --json number,url,state,headRefName,baseRefName,headRefOid,baseRefOid,reviewDecision` is acceptable for discovery, but not sufficient for complete thread inventory.

If no PR exists, report `inventory_status: no_pr`.

If multiple PRs are associated and ambiguous, block.

## Complete review-thread inventory

For GitHub PRs, collect a complete paginated review-thread inventory when possible:

- `totalCount`
- `pageInfo.hasNextPage`
- `pageInfo.endCursor`
- thread `id`
- `isResolved`
- `isOutdated`
- path and line
- latest comment author/body/url
- associated commit/head when available

If pagination fails, totalCount is missing, or collected nodes < totalCount, mark inventory incomplete.

Do not claim complete PR sweep on incomplete inventory unless the final status is downgraded or blocked.

## In-scope items

- inline review comments;
- unresolved review threads;
- PR conversation comments with concrete feedback;
- requested-changes summaries;
- actionable bot/automation comments.

## Out-of-scope items

- approvals, acknowledgements, emoji-only comments, status chatter;
- comments authored by this agent as status/reply;
- already resolved/dismissed/obsolete comments unless they still describe current defects;
- unrelated comments.

## Processing

For every in-scope unprocessed item, invoke `$review-adjudication` and consume full route/warrant output.

Mutation-capable routes go through the Review-Closure Abstraction Ladder before `$fixed-point-driver`.

If PR handling changes branch state, reset review streak and repeat local review, full validation, commit, push, and PR sweep.
