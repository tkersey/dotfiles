# Source Governance Gate

Historical replay can amplify an upstream classifier error.

Before a workflow-specific experiment, prove that the workflow actually governed the source.

## SGG-v1

The sole machine schema is
[`../definitions/ledger/source-governance-gate.json`](../definitions/ledger/source-governance-gate.json).
Author JSON, validate it with Ledger, and retain the returned definition digest.
This page owns interpretation, not a second field inventory.

## Governance provenance

Controller-grade:

```text
controller_invocation
controller_event
controller_state
controller_receipt
```

Potentially useful but not controller-authoritative:

```text
explicit_workflow_declaration
```

Incidental:

```text
artifact_under_repair
filename_or_path_mention
historical_reference
generic_prose
```

## Closure provenance

Controller-grade:

```text
controller_close
controller_receipt
campaign_bound_terminal
```

Not controller closure:

```text
generic_delivery_closure
tool_success_only
generic_prose
```

## Rules

### Authoritative

Requires at least one controller-grade governance item.

When the inquiry concerns closure, controller-grade closure evidence is also required.

### Declared uncontrolled

Requires an explicit workflow declaration but no controller-grade governance.

Replay may investigate why the controller was not used, but the limitation must remain visible.

### Incidental

Only artifact/path/history/generic references.

Replay is forbidden.

### Ambiguous

Conflicting or insufficient provenance.

Deterministic investigation only.

### Absent

No relevant evidence.

Replay is forbidden.

## Tool evidence

Preserve:

```text
tool kind
call id
executable
argv/command
working directory
exit status
matched field
matched cue
structured output/event
```

Do not reduce evidence to:

```text
Exit code: 0
Chunk ID: ...
```

## Anti-example

Deleting:

```text
.step/review-workflow-plan.jsonl
```

is `artifact_under_repair`.

It does not prove:

```text
the named review workflow governed the session
```

Landing a PR does not prove:

```text
the named review workflow closed a campaign
```
