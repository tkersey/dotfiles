# Retrace session inquiry through CAS

CAS owns the bounded replay transport for Retrace. Retrace owns source
selection, inquiry meaning, historical claims, and proof credit.

## Compatibility gate

```bash
cas app-server preflight \
  --cwd <repo> \
  --profile session-inquiry \
  --json
```

Require `status == "compatible"` for the exact resolved Codex runtime and all
required paginated-fork, ephemeral-fork, and inquiry-anchor probes passed.
Never silently change lineage after a transport or compatibility failure.

## Lineage modes

```text
thread_fork
  stored source thread -> exact completed boundary -> fork -> anchor proof

rollout_transcript
  verified rollout + retained-anchor digest -> fresh bounded transcript turn
```

A paginated source is supported when the profile's schema and live probes pass.
CAS selects an exact admissible completed boundary, verifies retained prefix
count and digest, and records fork identity. Interrupted or incomplete suffixes
are not completed history.

An ephemeral fork is pathless and absent from ordinary thread listing. A
successful fork proves neither live historical workspace reconstruction nor
the semantic truth of the replay.

Use `rollout_transcript` only when thread-fork lineage is unavailable for a
different evidenced reason. Its workspace policy remains:

```text
transcript_only
no current-checkout tools
read-only
network off
approvals denied
```

## Validation and execution

Validate DCP-v2 and RIP-v1 through Retrace's owning Ledger definitions before
CAS receives them. Then run:

```bash
cas session_inquiry run \
  --capsule capsule.json \
  --capsule-definition <retrace-root>/definitions/ledger/decision-context-packet.json \
  --capsule-validation capsule.validation.json \
  --plan plan.json \
  --plan-definition <retrace-root>/definitions/ledger/retrace-inquiry-plan.json \
  --plan-validation plan.validation.json \
  --receipt-dir .ledger/retrace/<inquiry-id> \
  --json
```

Validate the returned FIR through CAS's
`definitions/ledger/fork-inquiry-receipt.json` before Retrace interprets it.
FIR-v1 preserves exact lineage mode, source and fork identities, anchor
digests, workspace mode, runtime/provider, policy proof, terminal state, and
cleanup. Do not add undeclared durable fields to FIR-v1.
