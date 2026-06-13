# Review Adjudication Route Contract

`$resolve` consumes full `$review-adjudication` output. It must not flatten everything into `address`.

## Routes

- `address`
- `validate-only`
- `resolve-thread-only`
- `do-not-address`
- `delete-collapse-canonicalize`
- `blocked`

## Handling

| route | action |
|---|---|
| `address` | route receipt, compiler if triggered, fixed-point handoff |
| `delete-collapse-canonicalize` | compiler/fixed-point with ablation preferred |
| `validate-only` | add/run proof; reset streak if files change |
| `resolve-thread-only` | reply/resolve only when provider policy permits |
| `do-not-address` | record rationale; review run still not clean |
| `blocked` | stop before commit/push |
