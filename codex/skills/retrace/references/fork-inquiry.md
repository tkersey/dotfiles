# Fork Inquiry Receipt: FIR-v1

A FIR is controller evidence, not merely a model answer.

## Lineage modes

### `thread_fork`

```text
stored source thread
-> thread/fork
-> thread/rollback
-> retained-anchor verification
```

Requires source thread identity and matching `forked_from_id`.

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
