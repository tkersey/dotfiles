# Mutation Permit Gate

Validate permit files with:

```bash
resolve-c3 legacy-gate --file <permit.yml>
```

This legacy gate surface is retired. Current mutation authority comes from controller-emitted MRPC-v1 via `resolve-c3 mrpc-gate --file <mrpc.json>`.

The gate checks the literal `RGR-V2-MUTATION-PERMIT:` key and rejects:

- selected_route: mutate-existing-owner;
- positive production net without warrant;
- continue_owner when owner is too coarse or unknown;
- negative-ledger query_or_map: no;
- missing `ledger_cli: ledger`, `.ledger/negative-ledger/events.jsonl` store, or `ledger map` exit code;
- `ledger_available: no` or `exit_code: 3`;
- one-test-per-wound without a family matrix;
- handoff_allowed: no.
