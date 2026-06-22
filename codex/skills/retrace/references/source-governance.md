# Source Governance Gate

Historical replay can amplify an upstream classifier error.

Before a workflow-specific experiment, prove that the workflow actually governed the source.

## SGG-v1

```yaml
source_governance_gate:
  gate_version: SGG-v1
  gate_id:

  source:
    session_id:
    rollout_path:
    workflow:
    protocol:
    classifier_command:
    classifier_version:
    included_row_ref:

  evidence:
    governance:
      - evidence_id:
        present:
        source:
        timestamp:
        tool_name:
        executable:
        command:
        matched_field:
        matched_cue:
        excerpt:
        provenance_role:
    entry: []
    closure: []
    incidental: []

  classification:
    governance_provenance:
    closure_provenance:
    governing_evidence_refs: []
    incidental_evidence_refs: []
    absent_evidence_reasons: []

  verdict:
    state:
      authoritative |
      declared_uncontrolled |
      incidental |
      ambiguous |
      absent
    replay_allowed:
    allowed_modes: []
    reason:

  limitations: []
```

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
.step/resolve-c3-st-plan.jsonl
```

is `artifact_under_repair`.

It does not prove:

```text
resolve-c3 governed the session
```

Landing a PR does not prove:

```text
resolve-c3 closed a campaign
```
