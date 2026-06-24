# Memory Source Note Contract

## Core invariant

A note is an immutable source event, not compiled memory and not an instruction for normal agents.

## Generated envelope

The CLI writes a canonical note envelope to a timestamped `.md` file:

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

## Required guarantees

- one file per event;
- create-new semantics;
- no overwrite, mutation, or delete command;
- UTC timestamp filename;
- allowlisted extension and kind;
- stable fingerprint input for semantically equivalent source events;
- non-empty authority, summary, source references, and payload;
- safe memory-root-relative destination;
- no symlink traversal;
- maximum input and output sizes;
- structured stdout and deterministic exit codes.

## Canonical caller input

The writer's generated envelope is canonical. Source-specific callers are also responsible for passing a stable source-event representation when duplicate detection depends on input bytes.

For Synesthesia, the accepted writer input is the canonical stdout of:

```bash
uv run --with pyyaml python \
  codex/skills/synesthesia/scripts/validate_synesthesia.py \
  memory-file proposed.json --kind <kind> --emit-canonical
```

Do not reformat or augment the canonical JSON before handing it to `memory-note`.

## Authority values

Recommended values:

```text
explicit-user-correction
repeated-user-steering
learnings-cli
ledger-cli
explicit-user-endorsement
explicit-user-rejection
explicit-user-retraction
explicit-user-remember-request
repeated-accepted-use
verified-artifact
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

## Supersession and retraction

A superseding, rejecting, retracting, confirming, or reopening event that acts on an admitted prior state must include:

```text
operation
supersedes_id or related_ids
source_refs explaining the change
payload containing the replacement, confirmation, rejection, or withdrawal semantics
```

Phase 2 updates compiled memory surgically. It must not delete source notes.

## Synesthesia kind-operation compatibility

| Kind | Allowed operations | Prior note requirement |
|---|---|---|
| `mapping-endorsement` | `assert`, `confirm`, `reopen` | confirmation and reopening require prior linkage |
| `mapping-correction` | `supersede` | required |
| `mapping-rejection` | `reject` | required for an already admitted mapping |
| `activation-boundary` | `assert`, `confirm`, `supersede`, `reopen` | all except initial assertion require prior linkage |
| `boundary-retraction` | `retract` | required |

The Synesthesia package preflight enforces this matrix before handoff.

## Canonical versus admission authority

A note can be authoritative that Phase 2 must consider an event while remaining subordinate to its canonical domain source.

- A negative-ledger note is authoritative as an exported snapshot, but `.ledger/negative-ledger.jsonl` owns route state.
- A learnings admission note is authoritative that a row should be considered, but `.learnings.jsonl` owns the full learning record.
- A harness note may itself be canonical when it records an explicit user correction with evidence.
- A Synesthesia note may itself be canonical when it records explicit user endorsement, correction, rejection, retraction, or a directly requested durable boundary.
