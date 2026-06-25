# `$retrace` Session Inquiry

`$cas` owns safe replay lifecycle for `$retrace`.

Current supported lineage modes:

```text
thread_fork
  stored source thread -> thread/fork -> rollback -> anchor verification

rollout_transcript
  verified rollout + retained-anchor digest -> fresh thread -> bounded
  transcript-context turn
```

Rollout-transcript replay requires:

```text
workspace_policy = transcript_only
no current-checkout tools
read-only
network off
approvals denied
```

It is not live historical workspace reconstruction.

Preferred command:

```bash
cas session_inquiry run \
  --capsule capsule.json \
  --plan plan.json \
  --receipt-dir .ledger/retrace/<inquiry-id> \
  --json
```

Before execution:

```bash
cas --version
cas capabilities --json
cas session_inquiry preflight --json
```

FIR-v1 must preserve `lineage_mode`, source identity, anchor digests, workspace mode, model/provider, policy proof, terminal state, and cleanup.

`$cas` does not select the historical source and does not decide what the replay means.
