# Pull-request route

## Pull-request route

Keep operation and final state separate:

```yaml
pr_decision:
  operation: create | update | update-and-promote | blocked
  final_state: ready | draft | preserve
```

Default to `ready` when validation is complete and no task remains blocked,
deferred, or open. Draft requires explicit user intent, incomplete or
accepted-caveat validation, open work, or repository policy.

For an existing exact repository/base/head PR, update rather than duplicate it.
Preserve its ready/draft state unless current authority permits a transition.
Promotion is `update-and-promote`: update proof first, then mark ready.

Read [pr-readiness-policy.md](references/pr-readiness-policy.md).

## New PR assignment

Every PR Ship creates, ready or draft, must be assigned to the authenticated
GitHub user. Before creation, resolve that user's login on the target host using
the same credentials as the PR operation; do not infer it from repository
ownership or Git authorship. With `gh`, include `--assignee @me` in
`gh pr create`. API/connector routes that cannot assign during creation must
add the resolved login immediately afterward.

Read back `assignees` and require that login before reporting success. If this
attempt created a PR but assignment is missing, repair that same PR with
`gh pr edit <pr-url> --add-assignee <login>` (or an additive provider call), then
read back again. Preserve other assignees and carry this requirement through
retries that discover the partially created PR. Do not reassign otherwise
pre-existing PRs during update or promotion.

If the identity cannot be resolved, block before creation. If assignment or its
readback fails, report the PR URL and incomplete assignment, and block rather
than claim success or create another PR.

## Managed body

Only replace content between:

```text
<!-- ship-proof:start -->
<!-- ship-proof:end -->
```

Preserve human-authored content outside the markers byte-for-byte. Duplicated,
nested, reversed, or unbalanced markers block mutation.

Read [pr-body-proof.md](references/pr-body-proof.md).

## Public mutation and readback

Before any PR effect:

1. Verify repository, remote, base/head branches and SHAs, worktree scope, task
   state, and validation.
2. Inspect live PRs for the exact repository/base/head tuple.
3. Determine `pr_decision` and build the complete managed proof block. For
   creation, resolve the required assignee as above.
4. Push the exact intended committed head when required.
5. Create and assign, update, or update then promote.
6. Read back repository, base/head refs and SHAs, URL, open/draft state, and the
   managed proof block; for new PRs, also verify the required assignee.

A zero exit status is not publication proof. If mutation succeeds but readback
fails, report the partial public effect and block; re-read live state before
retrying.

Return immutable `SHIP-v1` for the exact publication epoch.
