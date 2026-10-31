# Review

## Invocation and runtime

Use `run` for a standalone one-off review. Use one owner-lived
`start --wait` process for workflow-bound or Actuating review. Use `wait` only
to recover or inspect an already-started admissible attempt.

Inspect `cas capabilities --json` for the installed build, or reuse its unchanged
result. Require `cas_structured_review_v1: true`; workflow-bound starts also
require `cas_workflow_bound_owner_lived_review_v1: true`.
Both `run` and `start` execute the exact-binary `review`/`managed-ws` live gate
internally. Require its compatible result; do not run a duplicate standalone
probe unless diagnosing or qualifying the runtime. A failed gate creates no
review attempt and never permits a transport fallback.

Preserve the caller's rubric, including intentional absence. Native/default
standard review uses no `--custom-instructions` argument; do not add an empty
argument, wrapper, or substitute prompt. Select one invocation, not both:

```bash
# Standalone native/default review.
cas review run --cwd <repo> --base <base> \
  --timeout-ms 2700000 --json

# Workflow-bound native/default alternative.
cas review start --wait --cwd <repo> --base <base> \
  --workflow-binding-json @<binding.json> \
  --timeout-ms 2700000 --json
```

Only a caller-selected custom rubric, such as an auxiliary or focused review,
adds `--custom-instructions @<instructions>` to the chosen invocation. Preserve
those exact bytes. A custom review does not acquire native-standard credit
merely because CAS executed it successfully.

## Evidence and recovery

A process is not a review. An attempt exists only after `reviewThreadId`; a
semantic verdict exists only when the structured verdict binds the exact
target tuple. CAS reports the backend; the caller decides credit and finding
disposition. For post-publication review, retain the exact bound base/head
selector; a clean checkout is not a reason to use `--uncommitted`.

Recover a live or pending exact handle with `wait`, not a replacement attempt.
When the caller admits a distinct same-target attempt after terminal evidence,
pass `--fresh-attempt <source-bound-reason>`. CAS records the reason; it does not
decide whether the new attempt is permitted. Missing output or an unsuccessful
wait alone does not establish that another attempt is safe.

## Receipt interpretation

For workflow-bound/Actuating review, consume the exact owner-issued CAS receipt
directly. Require:

- receipt and verdict target tuples agree;
- expected base, head, and target fingerprint;
- exact workflow-binding echo;
- structured semantic status;
- strong principal and no reduced protection;
- backend class `cas-start-wait`;
- exact current runtime compatibility facts.

Do not pass the receipt through Ledger or copy it into an Actuating event log.
Structural parsing is not review credit; Actuating evaluates the exact fields
under its static Review Contract. Missing structured output, provider failure,
account exhaustion, fallback, transport loss, stale tuple, or mismatched binding
earns no semantic credit. Standalone `run` is not a workflow-bound
`cas-start-wait` receipt.

A binding echo or digest identifies supplied context; it does not deliver that
context or prove the reviewer saw it. Preserve material access limitations.
See [review-proof-boundary.md](references/review-proof-boundary.md) for ownership,
premise visibility, illustrative receipt limits, and interrupted-campaign recovery.

## Caller-selected configuration

With CAS `0.7.1` or newer, pass any caller-required thread configuration through
one `--thread-start-params-json JSON|@file` object on `run` or `start`:

```bash
cas review start --wait --cwd <repo> --base <base> \
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

Use `--cwd` for the CAS-owned repository and, only for a caller-supplied rubric,
`--custom-instructions`; JSON keys `cwd` and `developerInstructions` are rejected.
Keep the review thread durable: `ephemeral: true` is rejected. CAS also owns `review/start`'s
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
effective-permissions receipt or effective-repository attestation. The controlled
preflight establishes protocol compatibility; the actual thread start admits
caller configuration, and successful review execution remains the evidence for
filesystem access.

Reported `cwd` does not attest the repository used by every reviewer command.
Caller configuration such as `GIT_DIR` or `GIT_WORK_TREE` can redirect Git even
when the reported directory matches. Do not introduce redirection incidentally.
When selected configuration can redirect repository resolution, establish its
consistency with the intended subject from relevant execution evidence before
accepting subject-dependent claims; otherwise retain that limitation and withhold
unsupported credit. Do not silently rewrite settings or widen permissions.
