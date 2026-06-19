# Governor Tooling

Available local validators:

```bash
resolve-c3 legacy-gate --file <legacy-governor-artifact.yml>
resolve-c3 mrpc-gate --file <mrpc.json>
resolve-c3 rdr-gate --file <record.yml>
```

The Python governor validators are retired. Current C3 closure uses `resolve-c3` gate subcommands and controller state under `.ledger/c3/`.
