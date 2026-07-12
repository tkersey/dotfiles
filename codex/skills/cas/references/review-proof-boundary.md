# CAS Review Transport Boundary

`$cas` starts, waits for, recovers, normalizes, and reports review attempts.
Its transport surface consists of attempt lifecycle, tuple identity, normalized
verdict facts, failure facts, and stable finding provenance.

CAS receipt normalization may expose `reviewAttemptPhase`,
`reviewAttemptExists`, `reviewThreadId`, `reviewTurnId`, `baseSha`, `headSha`,
`targetFingerprint`, `reviewVerdict.status`, `findingCount`, failure fields,
`findingId`, `findingFingerprint`, `reviewAttemptId`, `titleHash`, `bodyHash`,
and `normalizedLocation`.

CAS-RER-v1 may preserve an optional opaque `workflowBinding` containing only
`requestId` and `requestFingerprint`. CAS validates both as non-empty strings,
binds the complete object into lock and record identity, and returns it
unchanged. Unfiltered `current`/`list` preserves all same-artifact/thread
epochs; an explicitly supplied binding is an exact filter.

Pre-0.2.75 binding objects are accepted only when importing or reading
historical evidence. New review runs require the opaque two-field shape.

The canonical exhaustive workflow acquisition surface is:

```bash
cas review list --cwd <repo> --base <base> --codex-thread-id <id> --json
```

It returns one complete `CAS-LIST-v2` envelope whose `records` and `recordRefs`
cover the visible ledger set. Capability discovery prefers this surface and may
use `cas review_session list` only when the dispatcher explicitly advertises
that action. If neither list action is advertised, history acquisition fails;
it never falls back to `status --latest` or individually selected records.

`CAS-LIST-v2.recordRefs[].contextIdentityMatches` records whether the current
runtime, account, thread, tuple, and optional binding exactly match the record
context. Drift never hides the historical record.
