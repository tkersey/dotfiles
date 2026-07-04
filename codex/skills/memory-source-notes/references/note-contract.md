# Memory Source Note Contract

## Core invariant

A note is an immutable source event, not compiled memory and not an instruction for normal agents.

## Generated envelope

The native writer creates one canonical envelope in a timestamped `.md` file:

```json
{
  "schema": "memory-source-note/v1",
  "id": "MSN-20260620T183000Z-a91f4e2c6b5d3f10",
  "captured_at": "2026-06-20T18:30:00Z",
  "extension": "synesthesia",
  "kind": "mapping-endorsement",
  "operation": "assert",
  "authority": "explicit-user-endorsement",
  "summary": "Endorse long corridor.",
  "scope": {
    "kind": "task-family",
    "repo": null,
    "paths": []
  },
  "source_refs": [
    {
      "kind": "user-endorsement",
      "ref": "rollout:019...",
      "summary": "User explicitly accepted the mapping"
    }
  ],
  "related_ids": [],
  "supersedes_id": null,
  "fingerprint": "a91f4e2c6b5d3f10...",
  "payload": {}
}
```

## Required guarantees

- one file per event;
- create-new semantics;
- no overwrite, mutation, or delete command;
- UTC timestamp filename;
- allowlisted extension and kind;
- non-empty authority, summary, source references, and payload;
- safe memory-root-relative destination;
- no symlink traversal;
- maximum input and output sizes;
- structured stdout and deterministic exit codes.

For Synesthesia writes, the extension adapter additionally guarantees:

- operation-kind compatibility;
- authority-kind compatibility;
- prior-note relationships for state-changing operations;
- required activation and non-activation boundaries;
- canonical key ordering and compact JSON before writer fingerprinting;
- envelope-owned authority and scope;
- deterministic mapping of logical confirmation to the current stored kind.

## Authority values

Recommended general values:

```text
explicit-user-correction
repeated-user-steering
ledger-cli
ledger-cli
explicit-user-endorsement
explicit-user-rejection
source-skill
verified-artifact
```

Synesthesia additionally uses:

```text
repeated-accepted-use
```

`assistant-inference` is never enough by itself for durable admission.

## Scope values

```text
global
repo
path-family
task-family
workflow
tool
```

Use the narrowest reusable scope.

## Synesthesia operation matrix

| Logical kind | Stored kind | Allowed operation | Required prior relationship |
|---|---|---|---|
| `mapping-endorsement` | `mapping-endorsement` | `assert` | no |
| `mapping-confirmation` | `mapping-endorsement` | `confirm` | `related_ids` |
| `mapping-correction` | `mapping-correction` | `supersede` | `supersedes_id` or `related_ids` |
| `mapping-rejection` | `mapping-rejection` | `reject` | `supersedes_id` or `related_ids` |
| `mapping-endorsement` reopening | `mapping-endorsement` | `reopen` | `supersedes_id` or `related_ids` |
| `activation-boundary` | `activation-boundary` | `assert` | no |
| `activation-boundary` confirmation | `activation-boundary` | `confirm` | `related_ids` |
| `activation-boundary` correction | `activation-boundary` | `supersede` | `supersedes_id` or `related_ids` |
| `activation-boundary` reopening | `activation-boundary` | `reopen` | `supersedes_id` or `related_ids` |
| `boundary-retraction` | `boundary-retraction` | `retract` | `supersedes_id` or `related_ids` |

## Supersession and retraction

A superseding, rejecting, retracting, confirming, or reopening note must include:

```text
operation
supersedes_id or related_ids
source_refs explaining the change
payload containing the replacement, confirmation, rejection, withdrawal, or reopening rule
```

Phase 2 updates compiled memory surgically. It never deletes source notes.

## Canonical versus admission authority

A note can be authoritative that Phase 2 must consider an event while remaining subordinate to its canonical domain source.

- a negative-ledger note is an exported snapshot; `.ledger/negative-ledger/events.jsonl` owns route state;
- a learnings note admits a row; `.ledger/learnings/events.jsonl` owns the full learning event;
- a Synesthesia note may itself be canonical when it records explicit endorsement, correction, rejection, retraction, reopening, or a durable boundary.

## Instruction deployment

Extension `instructions.md` files in the live memory root must be regular copied files. Do not symlink them. Copy only the instruction file; leave `notes/` and `resources/` as live private state.

## Derived Synesthesia digest

The Synesthesia adapter may derive a disposable current-state digest from immutable source notes. The digest is not a source event, is not compiled memory, and is never canonical. Its guarantees are:

- complete folding of `assert`, `confirm`, `supersede`, `reject`, `retract`, and `reopen` chains;
- deterministic ordering and source fingerprinting;
- every projected entry preserves immutable `source_note_ids`;
- unresolved, invalid, rejected, and retracted state remains visible;
- the default digest is a regular full projection, not a partial report;
- digest failure never rolls back an accepted source-note append.
