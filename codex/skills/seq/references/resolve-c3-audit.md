# C³ Resolve Audit

Prefer:

```bash
seq review-compiler-audit --protocol c3 ...
```

when the installed `seq` supports it.

Until then, audit:

- `review_compile.py` lifecycle commands;
- `.resolve-c3/state.json`;
- `.resolve-c3/events.jsonl`;
- MRPC-v1 stages;
- direct delivery mutations between begin and close;
- candidate tournament size and route diversity;
- orphan edit atoms;
- controller-only commit/push.
