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

- operation-kind agreement;
- authority-kind agreement;
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
explicit-user-endorsement
explicit-user-rejection
source-skill
verified-artifact
```

`ledger-cli` is the retained writer/source-attestation label in existing
Learnings and Negative Ledger note envelopes. It does not grant the Ledger
runtime semantic authority; the enclosing Ledger result must still report
`authority_granted:false`.

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

## Managed reminder updates

After the source owner accepts withdrawal, identify the exact prior immutable
note and the evidence supporting the change:

```bash
uv run \
  "$memory_source_notes_root/scripts/source_memory_note.py" append \
  --source learnings --operation retract \
  --catalog-root "$ledger_home" --store-id "<context.store_id>" \
  --id lrn-... --prior-note-id MSN-... \
  --reason "The admitted reminder is no longer needed in its covered scope" \
  --evidence-ref "<inspectable source-approved evidence>"
```

Use `--source negative-ledger --id NEG-...` for that source. Use
`--operation supersede` for a supported replacement. The adapter derives the
logical kind, reads the prior note through the selected native layout, and
validates its source identity and scope against the canonical projection.
Supply additional `--evidence-ref` arguments when needed. Missing or conflicting
prior identity blocks the update; do not substitute a canonical ID or guess a
note ID. `inspect` previews the same validated envelope without writing.

Retraction targets the same canonical record and exact admitted scope. A
Learnings replacement with a different canonical ID must name the old record in
its canonical `supersedes_id`; its scope may narrow within the same repository.
Negative Ledger replacement through this adapter targets snapshots of the same
`NEG-*` record. For replacement by another `NEG-*`, first perform the justified
source-owned lifecycle change, then withdraw the old admission and separately
evaluate admission of the replacement. Neither memory operation performs that
canonical transition for the source owner.

For a Negative Ledger note older than the current snapshot or its immediate
predecessor, the adapter requires the selected managed store's exact repository
identity and unchanged complete capture evidence, with consistent nondecreasing
lifecycle counts. It does not reconstruct historical state from a label. Legacy
repository labels lack that stable store binding; an older unmatched legacy
snapshot stays blocked unless an exact supported custody witness is available.
This limit prevents retiring another store's note merely because its `NEG-*`
identifier and description match.

The source owner must preserve guidance still needed outside the repaired
domain. A partial repair is not grounds to withdraw an entire broad reminder;
select a supported replacement or leave the still-needed guidance in place.
No update command changes canonical history or an operational exclusion's
lifecycle. A redundant reminder can be withdrawn while its experiment remains
true and useful. Pin `--codex-home` and `--memory-version` when a selected layout
is already known, as for other admissions.

The writer appends an immutable note with a matching operation/kind and an exact
`MSN-*` relationship. Persistence, reader visibility, and observed downstream
consolidation remain separate facts. Do not claim compiled removal from a
successful append or edit compiled memory to manufacture it.

Reconciliation follows explicit note relationships across canonical IDs. Competing
replacement branches remain unresolved with their update IDs preserved; timestamps
and fingerprint suffixes do not decide which guidance is authoritative.

The adapter derives these operation/kind pairs:

| Source | Action | Kind | Operation |
|---|---|---|---|
| Learnings | Replace admitted guidance | `learning-supersession` | `supersede` |
| Learnings | Withdraw admitted guidance | `learning-withdrawal` | `retract` |
| Negative Ledger | Replace admitted guidance | `ledger-supersession` | `supersede` |
| Negative Ledger | Withdraw admitted guidance | `ledger-retraction` | `retract` |

Canonical `lrn-*` and `NEG-*` identities identify source evidence; only resolved
`MSN-*` identities establish note relationships. Retraction changes admission
support without changing canonical history or route state. A persisted update
does not establish that Phase 2 has consolidated it.

## Canonical versus admission authority

A note can be authoritative that Phase 2 must consider an event while remaining subordinate to its canonical domain source.

- a negative-ledger note is a projected snapshot; `$negative-ledger` and its passive Negative Evidence definition own current route state in the personal store selected through `$ledger`;
- a learnings note admits a row; `$learnings` owns the full event in its selected personal store;
- a Synesthesia note may itself be canonical when it records explicit endorsement, correction, rejection, retraction, reopening, or a durable boundary.

## Instruction deployment

Extension `instructions.md` files in the live memory root must be regular copied files. Do not symlink them. Copy only the instruction file; leave `notes/` and `resources/` as live private state.

Resolve `instructions_path`, `notes_dir`, and `resources_dir` through native
`memory-note path`, then pin its home/version for all operations. Do not inspect
both memory versions during normal work. Explicit native `migrate` copies
existing envelopes unchanged; it does not create new admissions or rewrite IDs,
fingerprints, timestamps, or scope. See [source-store-layout.md](source-store-layout.md).

## Derived Synesthesia digest

The Synesthesia adapter may derive a disposable current-state digest from immutable source notes. The digest is not a source event, is not compiled memory, and is never canonical. Its guarantees are:

- complete folding of `assert`, `confirm`, `supersede`, `reject`, `retract`, and `reopen` chains;
- deterministic ordering and source fingerprinting;
- every projected entry preserves immutable `source_note_ids`;
- unresolved, invalid, rejected, and retracted state remains visible;
- the default digest is a regular full projection, not a partial report;
- digest failure never rolls back an accepted source-note append.
