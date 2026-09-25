# Review

Use `run` for a standalone one-off review. Use one owner-lived
`start --wait` process for workflow-bound or Actuating review. Use `wait` only
to recover or inspect an already-started admissible attempt.

Both `run` and `start` execute the required exact-binary `review`/`managed-ws`
live preflight before starting. Do not run a duplicate standalone probe unless
diagnosing or qualifying the runtime. Select one review invocation, not both:

```bash
# Standalone review.
cas review run --cwd <repo> --base <base> \
  --custom-instructions @<instructions> \
  --timeout-ms 2700000 --json

# Workflow-bound alternative, with one owner-lived notification channel.
cas review start --wait --cwd <repo> --base <base> \
  --custom-instructions @<instructions> \
  --workflow-binding-json @<binding.json> \
  --timeout-ms 2700000 --json
```

A process is not a review. An attempt exists only after `reviewThreadId`; a
semantic verdict exists only when the structured verdict binds the exact
target tuple. CAS reports the backend. The caller decides credit and finding
disposition. A failed compatibility gate blocks the route before an attempt
exists; it is never a clean review. See
[review-proof-boundary.md](references/review-proof-boundary.md).

When the caller admits a new same-target attempt after terminal evidence, pass
`--fresh-attempt <source-bound-reason>`. CAS records the reason; it does not
decide whether the new attempt is permitted.
