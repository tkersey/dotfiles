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

## Caller-selected configuration

With CAS `0.7.1` or newer, pass any caller-required thread configuration through
one `--thread-start-params-json JSON|@file` object on `run` or `start`:

```bash
cas review start --wait --cwd <repo> --base <base> \
  --custom-instructions @<instructions> \
  --thread-start-params-json @<runtime-options.json> \
  --workflow-binding-json @<binding.json> \
  --timeout-ms 2700000 --json
```

Use native app-server names such as `model`, `modelProvider`, `sandbox`,
`permissions`, `approvalPolicy`, `environments`, `runtimeWorkspaceRoots`, and
`config`. CAS admits top-level names from the selected executable's generated
experimental `ThreadStartParams` schema and preserves nested values, explicit
nulls, false, empty arrays, and exact numbers. Let Codex validate setting values
and combinations; keep `config` open and use the installed runtime's semantics.
Omit settings the caller has not selected. A file is loaded once before preflight;
`wait` observes the already-configured attempt and rejects new launch options.

Use `--cwd` and `--custom-instructions` for the CAS-owned repository and exact
rubric; JSON keys `cwd` and `developerInstructions` are rejected. Keep the review
thread durable: `ephemeral: true` is rejected. CAS also owns `review/start`'s
thread, target, and inline delivery. Other schema-advertised options, including
paginated history, remain caller-selectable.

Keep language-specific settings with the caller. For Zig, an applicable caller
may supply `config["shell_environment_policy.set"]` containing
`ZIG_LOCAL_CACHE_DIR` and `ZIG_GLOBAL_CACHE_DIR`. Select paths inside the actual
permitted write area; setting cache variables alone does not grant access or
establish the cause of `PermissionDenied`. Do not widen permissions by default.

Distinguish supplied thread settings from the reviewer's effective policy.
Released Codex `0.162.1` forces inline-review approvals to `Never`, replaces base
instructions, and prefers `config.review_model` over the ordinary model. These
are app-server behaviors, not values CAS should silently compensate for. Inspect
the installed runtime when diagnosing a policy or propagation discrepancy.

Use `threadStartParamsDigest` and the bound target fingerprint to identify the
selected configuration. Different settings get distinct reuse identities; key
order and whitespace do not. CAS records the digest and redacts configured
thread-start event bodies; do not treat it as a replayable configuration or
effective-permissions receipt. The controlled preflight establishes protocol
compatibility; the actual thread start admits caller configuration, and successful
review execution remains the evidence for filesystem access.
