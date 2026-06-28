# Review-Compiler Provenance

## Session-level rule

Aggregate counters are discovery only.

Use:

```text
review_compiler_audit.denominator.included_sessions
```

before naming a session or explaining a count.

## Evidence roles

### Controller-grade governance

```text
controller_invocation
controller_event
controller_state
controller_receipt
```

### Declared but uncontrolled

```text
explicit_workflow_declaration
```

### Incidental

```text
artifact_under_repair
filename_or_path_mention
historical_reference
generic_prose
```

## Closure roles

Controller closure:

```text
controller_close
controller_receipt
campaign_bound_terminal
```

Not controller closure:

```text
generic delivery completion
PR merged
goal complete
tool exited zero
threads clean
```

## Required evidence ref

```yaml
evidence_ref:
  source:
  timestamp:
  tool_name:
  call_id:
  executable:
  command:
  working_directory:
  exit_status:
  matched_field:
  matched_cue:
  controller_campaign_id:
  excerpt:
  provenance_role:
```

Do not emit only:

```text
Exit code: 0
Chunk ID: ...
```

## Lifecycle consistency

Recommended states:

```text
valid
imported_state
partial_trace
orphan_close
contradictory
incidental
```

A close without begin is `orphan_close` only when controller-grade governance and closure evidence exist.

When the only workflow evidence is incidental, classify `incidental` and remove the row from the true workflow denominator.

## Regression case

Deleting or migrating:

```text
.step/review-workflow-st-plan.jsonl
```

must not create a true workflow run.

Expected:

```yaml
candidate_workflow: true
incidental_workflow: true
governance: incidental
workflow_required: false
workflow_entered: false
workflow_closed: false
included_in_workflow_denominator: false
closure_compression: NONE
```
