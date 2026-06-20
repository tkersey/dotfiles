# C³ Resolve Audit

Prefer:

```bash
seq review-compiler-audit --protocol c3 ...
```

when the installed `seq` supports it.

Until then, audit:

- `resolve-c3` lifecycle commands;
- `.ledger/c3/state.json`;
- `.ledger/c3/events.jsonl`;
- MRPC-v1 stages;
- direct delivery mutations between begin and close;
- candidate tournament size and route diversity;
- orphan edit atoms;
- controller-only commit/push.
