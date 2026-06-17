# Negative Ledger Integration

Run negative-ledger query/map when:

- same cluster reappears after repair;
- prior selected route is falsified;
- prior universalist not-needed is falsified;
- add-surface route failed or became unsound;
- public bypass / compatibility / tolerance path was introduced then rejected;
- one-change candidate resembles prior failed route;
- Review Distillation Mode is active.

The next packet must avoid active excluded routes, prove evidence stale/superseded/reopened, or block.

Operational source:

```bash
ledger map --route "<selected-route>" --cluster "<cluster-id>" --artifact "<artifact-state-id>"
```

Use `.ledger/negative-ledger.jsonl` through the `ledger` CLI. Do not treat prose or `.learnings.jsonl` recall as an operational route gate.
