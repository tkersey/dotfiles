# Migration From `.step/`

## Command

```bash
st workspace migrate \
  --from .step/st-plan.jsonl \
  --to .ledger/st \
  --plan-id default
```

## Preservation requirements

- task and intent IDs;
- statuses, priority, selection, dependencies, links;
- graph policy and lineage;
- waivers and graph debt;
- proof actions and proof receipts;
- comments and notes;
- runtime/claim history as historical records;
- polish passes and fingerprints;
- event/checkpoint sequence;
- source metadata;
- legacy projection membership.

## Migration outputs

```text
.ledger/st/migration/<migration-id>.json
.ledger/st/workspace.jsonl
.ledger/st/plans/default/plan.jsonl
.ledger/st/runtime/views/<initial-view>.json, when requested
```

## Atomicity

Migration is prepare/commit:

1. read and validate legacy source;
2. write all new artifacts under a transaction directory;
3. validate parity;
4. atomically publish workspace;
5. write migration receipt;
6. optionally remove or archive the legacy file.

If any step fails, the legacy source remains authoritative.

## After migration

No normal command writes to `.step/`.

Compatibility reads may be supported temporarily, but a write attempt must
return:

```text
legacy_artifact_root_read_only
```
