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
3. Determine `pr_decision` and build the complete managed proof block.
4. Push the exact intended committed head when required.
5. Create, update, or update then promote.
6. Read back repository, base/head refs and SHAs, URL, open/draft state, and the
   managed proof block.

A zero exit status is not publication proof. If mutation succeeds but readback
fails, report the partial public effect and block; re-read live state before
retrying.

Return immutable `SHIP-v1` for the exact publication epoch.
