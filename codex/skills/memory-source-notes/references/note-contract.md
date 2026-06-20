# Memory Source Note Contract

## Core Invariant

A note is an immutable source event, not compiled memory and not an instruction for normal agents.

## Generated Envelope

The CLI writes a canonical JSON object to a timestamped `.md` file:

```json
{
  "schema": "memory-source-note/v1",
  "id": "MSN-20260620T183000Z-a91f4e2c6b5d3f10",
  "captured_at": "2026-06-20T18:30:00Z",
  "extension": "negative-ledger",
  "kind": "ledger-projection",
  "operation": "assert",
  "authority": "ledger-cli",
  "summary": "NEG-000001 active exclusion projection",
  "scope": {
    "kind": "repo",
    "repo": "owner/repo",
    "paths": ["src/mvcc"]
  },
  "source_refs": [
    {
      "kind": "negative-ledger",
      "ref": ".ledger/negative-ledger.jsonl#NEG-000001",
      "summary": "Full exported current projection"
    }
  ],
  "related_ids": [],
  "supersedes_id": null,
  "fingerprint": "a91f4e2c6b5d3f10...",
  "payload": {}
}
```

## Required Guarantees

- one file per event;
- create-new semantics;
- no overwrite, mutation, or delete command;
- UTC timestamp filename;
- allowlisted extension and kind;
- canonical fingerprint excluding generated ID/timestamp;
- non-empty authority, summary, source references, and payload;
- safe memory-root-relative destination;
- no symlink traversal;
- maximum input and output sizes;
- structured stdout and deterministic exit codes.

## Authority Values

Recommended values:

```text
explicit-user-correction
repeated-user-steering
learnings-cli
ledger-cli
explicit-user-endorsement
explicit-user-rejection
source-skill
verified-artifact
```

`assistant-inference` is never enough by itself for durable admission.

## Scope Values

```text
global
repo
path-family
task-family
workflow
tool
```

Use the narrowest reusable scope.

## Supersession and Retraction

A superseding/retracting note must include:

```text
operation
supersedes_id or related_ids
source_refs explaining the change
payload containing the replacement or withdrawal rationale
```

Phase 2 should update compiled memory surgically. It must not delete source notes.

## Canonical Versus Admission Authority

A note can be authoritative that Phase 2 must consider an event while remaining subordinate to its canonical domain source.

- A negative-ledger note is authoritative as an exported snapshot, but `.ledger/negative-ledger.jsonl` owns route state.
- A learnings admission note is authoritative that a row should be considered, but `.learnings.jsonl` owns the full learning record.
- A harness note may itself be canonical when it records an explicit user correction with evidence.
- A synesthesia note may itself be canonical when it records explicit endorsement/rejection.
