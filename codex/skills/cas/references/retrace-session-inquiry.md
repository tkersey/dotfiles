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

Before CAS receives the inputs, validate the exact DCP-v2 and RIP-v1 bytes
through Retrace's canonical Ledger definitions:

```bash
ledger validate \
  --definition <retrace-skill-root>/definitions/ledger/decision-context-packet.json \
  --input packet=capsule.json \
  --format json > capsule.validation.json

ledger validate \
  --definition <retrace-skill-root>/definitions/ledger/retrace-inquiry-plan.json \
  --input plan=plan.json \
  --format json > plan.validation.json
```

Those passes establish structure only. CAS independently verifies the released
DCP identity and the exact carriers needed for inquiry.

Preferred command:

```bash
cas session_inquiry run \
  --capsule capsule.json \
  --capsule-validation capsule.validation.json \
  --plan plan.json \
  --plan-validation plan.validation.json \
  --receipt-dir .ledger/retrace/<inquiry-id> \
  --json
```

Before Retrace interprets a returned FIR:

```bash
ledger validate \
  --definition <cas-skill-root>/definitions/ledger/fork-inquiry-receipt.json \
  --input receipt=<fir.json> \
  --format json
```

Before execution:

```bash
cas --version
cas capabilities --json
cas session_inquiry preflight --json
```

FIR-v1 must preserve `lineage_mode`, source identity, anchor digests, workspace mode, model/provider, policy proof, terminal state, and cleanup.

`$cas` does not select the historical source and does not decide what the replay means.
