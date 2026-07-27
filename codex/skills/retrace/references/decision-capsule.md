# Decision Context Packet: DCP-v2

Retrace authors DCP-v2 from the ordered evidence returned by
[`../definitions/seq/decision-capsule.json`](../definitions/seq/decision-capsule.json).
Seq neither selects the episode nor authors the packet.

The sole machine schema and identity law are in
[`../definitions/ledger/decision-context-packet.json`](../definitions/ledger/decision-context-packet.json).
Ledger materializes a null `packet_id` to the released `DCP-<sha256>` identity
and rejects a mismatched claim. This page retains the temporal and epistemic
laws only.

## Determinism

The capsule may classify visible text and structured receipts, but it must not ask a model to invent hidden alternatives or rationale.

## Anchor calculation

For each horizon, calculate:

```text
source total turns
desired final retained turn
last N turns to drop
digest of retained turn identities/content metadata
```

CAS verifies the fork after rollback against the anchor digest or equivalent turn list.

## Outcome horizon

The first outcome turn is the earliest turn containing evidence unavailable at the decision point that would materially inform evaluation, such as:

```text
test result
review finding
user correction
commit outcome
deployment/merge result
later failure
```

When ambiguous, mark the post-decision/pre-outcome anchor unavailable.

## Source identity

Prefer thread ID.

Use rollout path only when thread identity cannot be recovered.

Record whether source thread is stored, archived, or only file-backed.
