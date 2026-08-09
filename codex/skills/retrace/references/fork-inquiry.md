# Fork Inquiry Receipt: FIR-v1

A FIR is controller evidence, not merely a model answer.

## Lineage modes

### `thread_fork`

```text
stored source thread
-> read paginated source turns when applicable
-> select an exact admissible completed boundary
-> verify retained prefix count and digest
-> thread/fork at that boundary
-> bind forked_from_id and anchor proof
```

Requires source thread identity, matching `forked_from_id`, the exact selected
boundary, and matching retained-prefix count and digest. Interrupted or
incomplete suffixes are not admissible completed boundaries. The fork itself is
not proof of historical workspace reconstruction.

### `rollout_transcript`

```text
verified source rollout
-> retained transcript prefix
-> fresh thread/start
-> bounded transcript-context turn/start
```

Requires:

- source rollout path;
- source and anchor digest verification;
- `workspace_reconstruction.mode = transcript_only`;
- no live historical workspace claim;
- fresh inquiry thread identity.

It is not a live fork of the source thread.

## Machine shape

CAS owns the sole machine definition:
[`../../cas/definitions/ledger/fork-inquiry-receipt.json`](../../cas/definitions/ledger/fork-inquiry-receipt.json).
Do not duplicate its field tree in Retrace documentation or fixtures. Validate
the exact CAS receipt with Ledger and retain the returned definition digest.

## Validity

A valid FIR requires:

- source and replay lineage;
- exact outcome-blind anchor;
- requested hindsight horizon;
- read-only/no-network policy;
- terminal turn;
- structured answer;
- cleanup state.

Invalid receipts remain audit evidence but do not contribute to route distributions or consensus.
