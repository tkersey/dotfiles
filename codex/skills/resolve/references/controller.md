# Controller

Canonical command:

```bash
resolve-c3 --help
```

The controller stores local state under `.ledger/c3/`, manages the lab worktree, registers candidates, selects the lexicographic winner, emits MRPC, applies the exact patch, and gates commit/push.

The existing configured `$st` hooks delegate to the controller when C³ state is active.
