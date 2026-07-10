# CAS Review Transport Boundary

`$cas` is review transport. It can start, wait for, normalize, and report review attempts and review verdict facts. It must not own closure approval, enforce clean-review streaks, or reject review execution because of evidence-tracking metadata.

Callers that need repeated clean reviews own that policy outside CAS. They may request additional independent attempts with `--fresh-attempt REASON`, then count and evaluate the resulting review verdicts themselves.

CAS receipt normalization may expose transport facts such as `reviewAttemptPhase`, `reviewAttemptExists`, `reviewThreadId`, `reviewTurnId`, `baseSha`, `headSha`, `targetFingerprint`, `reviewVerdict.status`, `findingCount`, and failure fields. It may also expose per-finding identity fields such as `findingId`, `findingFingerprint`, `reviewAttemptId`, `laneRole`, `titleHash`, `bodyHash`, and `normalizedLocation` so downstream receipts can cite the exact review row.

These fields are observational and are not guarantees. Per-finding identity is
not acceptance, rejection, repair-mode selection, clean-streak authority, or
mutation authority.

CAS-RER-v1 may additionally preserve an optional `workflowBinding` containing
`actuationRunId`, `artifactStateFingerprint`, `reviewContractFingerprint`,
`resolutionDigest`, a canonical `selectedLenses` set, `reviewLane`, and
`lensContract`. The live-state fingerprint is distinct from CAS's opaque
`targetFingerprint`. The producer uses it for lock and record identity.
Unfiltered `current`/`list` preserves all same-artifact/thread epochs so prior
findings remain visible; an explicitly supplied binding is an exact filter.

The canonical exhaustive workflow acquisition surface is:

```bash
cas review list --cwd <repo> --base <base> --codex-thread-id <id> --json
```

It returns one complete `CAS-LIST-v1` envelope whose `records` and `recordRefs`
cover the visible ledger set. Capability discovery prefers this surface and may
use `cas review_session list` only when the dispatcher explicitly advertises
that action. If neither list action is advertised, closeout fails; it never
falls back to `status --latest` or individually selected records.

`CAS-LIST-v1.recordRefs[].proofCreditEligible` is current-context metadata.
Runtime or account drift may make a record ineligible for clean credit without
changing the immutable record-time `principal.proofUsable` fact or hiding the
record from history.

The binding remains transport identity, not semantic approval. Missing binding
must not stop CAS from running, but actuation closure that requires a bound
record must reject it as `workflow-unbound`. Import must preserve rather than
invent the binding.
