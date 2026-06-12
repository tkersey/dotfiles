# Review Adjudication Route Contract

`$resolve` must consume full `$review-adjudication` output. Do not reduce review items to only `address` / `do-not-address`.

## Input context to provide

For each review or PR item, provide:

- exact item text;
- source and provider identity;
- file path and line range when available;
- relevant code/diff context;
- selected base ref/SHA and current `HEAD` SHA;
- project conventions and tests bearing on the item;
- proposed consequence of each route.

## Routes to consume

Expected `$review-adjudication` routes:

- `address`
- `validate-only`
- `resolve-thread-only`
- `do-not-address`
- `delete-collapse-canonicalize`
- `blocked`

Expected permitted actions:

- `mutate-code`
- `add-validation-only`
- `resolve-thread`
- `draft-reply`
- `defer`
- `none`

## Route handling

| route | permitted action | `$resolve` handling |
|---|---|---|
| `address` | `mutate-code` | run Review-Closure Abstraction Ladder; route surviving mutation to `$fixed-point-driver` |
| `delete-collapse-canonicalize` | `mutate-code` | run ladder with isomorphic/refactor/fixed-point ablation preferred |
| `validate-only` | `add-validation-only` | run/add proof only; if files change, reset review streak |
| `resolve-thread-only` | `resolve-thread` | resolve/reply only if provider policy permits and proof is current |
| `do-not-address` | `draft-reply` / `defer` / `none` | record rationale; review run still not clean |
| `blocked` | `none` | stop before commit/push |

## Counting

Every review run with any comment/finding resets the streak even if all items later route to no-change/do-not-address/resolve-thread-only.

Final report should include route counts separately for local review items and PR items.
