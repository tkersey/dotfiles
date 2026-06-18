# Lint Contract

Pre-governance lint checks the spec before SGR-v2 exists.

Final handoff lint may require SGR-v2.

Use:

```bash
python tools/spec_lint.py --phase pre-governance --strict-receipts <spec>
python tools/spec_lint.py --phase handoff --strict-receipts <spec>
```

A script pass is structural evidence, not semantic proof.
