# Capability and Legacy Mode

The skill contract may be newer than the installed `st` binary.

Do not pretend future commands exist.

## Native mode

Native workspace mode requires:

```text
workspace_v1
plan_namespace_v1
qualified_refs_v1
workspace_claim_v1
fencing_token_v1
session_view_v1
branch_epoch_v1
changeset_v1
serialized_integration_v1
gcr_v2
graph_intelligence_receipt_v1
graph_repair_receipt_v1
st_artifact_maintenance_receipt_v1
ledger_artifact_root_v1
```

## Missing native capabilities

Allowed:

```text
read current legacy graph
analyze graph health
write migration/spec recommendations
prepare CLI implementation specs
block material mutation
```

Forbidden:

```text
inventing .ledger/st state by hand
using multiple unmanaged --file paths as a substitute
calling non-existent workspace commands
claiming GCR-v2 authority from GCR-v1 output
material concurrent mutation
```

## Legacy single-plan compatibility

Legacy `.step/st-plan.jsonl` may be read for explicit compatibility or migration.

After a repository is migrated to `.ledger/st`, legacy writes fail closed.

If the installed CLI cannot support `.ledger/st`, the correct next step is a CLI
implementation or migration plan, not a partial emulation in prose.
