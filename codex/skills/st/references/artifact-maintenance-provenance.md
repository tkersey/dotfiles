# Artifact Maintenance Provenance

Artifact names are not workflow invocations.

A session can repair a file named `resolve-c3` without being governed by
`$resolve` or `resolve-c3`.

## AMR-v1

```yaml
st_artifact_maintenance_receipt:
  receipt_version: AMR-v1
  workspace:
  operation:
    inspect |
    migrate |
    repair |
    delete_sidecar |
    archive |
    validate
  governing_workflow: st
  artifact_paths: []
  mentioned_workflow_names: []
  activation_signal: no
  controller_invocation: no
  reason:
  evidence_refs: []
```

## Required use

Emit or report AMR-v1 when touching legacy, sidecar, or migration artifacts such
as:

```text
.step/st-plan.jsonl
.step/*st-plan*.jsonl
.step/resolve-c3-st-plan.jsonl
.ledger/st/migration/**
```

or any migrated workflow artifact whose path contains the name of another
workflow.

Do not require AMR-v1 for ordinary native `$st` controller writes under
`.ledger/st`, including workspace records, plan records, runtime claims, session
views, GCR receipts, proof receipts, changesets, integration receipts, locks, or
transactions. Those artifacts are workflow evidence only when controller-grade
evidence exists.

## Audit rule

`seq` and human reports should classify these as:

```text
artifact_under_repair
```

not as:

```text
workflow_entered
controller_invoked
true_c3
true_resolve
```

unless independent controller-grade evidence exists.

## Controller-grade evidence

Examples:

```text
actual controller command invocation
controller event/state file
explicit assistant/user workflow declaration
receipt emitted by the controller
```

Path names, patch hunks, `git add`, `jq`, `cat`, or deletion of an artifact are
not enough.
