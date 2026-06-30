# Synesthesia Memory Admission

## Boundary

Synesthesia owns the decision that a sensory mapping or activation boundary is durable enough to admit. `$memory-source-notes` owns validation, canonicalization, safe transport, copy-based adapter synchronization, diagnostics, and proof lines.

Ordinary sensory output is not persisted.

## Durable event classes

| Event | Logical kind | Stored kind | Operation | Prior note required |
|---|---|---|---|---|
| first explicit endorsement | `mapping-endorsement` | `mapping-endorsement` | `assert` | no |
| repeated explicit acceptance | `mapping-confirmation` | `mapping-endorsement` | `confirm` | yes, in `related_ids` |
| correction | `mapping-correction` | `mapping-correction` | `supersede` | yes |
| rejection | `mapping-rejection` | `mapping-rejection` | `reject` | yes |
| boundary assertion | `activation-boundary` | `activation-boundary` | `assert` | no |
| boundary confirmation | `activation-boundary` | `activation-boundary` | `confirm` | yes |
| boundary correction | `activation-boundary` | `activation-boundary` | `supersede` | yes |
| boundary reopening | `activation-boundary` | `activation-boundary` | `reopen` | yes |
| boundary withdrawal | `boundary-retraction` | `boundary-retraction` | `retract` | yes |
| mapping reopening | `mapping-endorsement` | `mapping-endorsement` | `reopen` | yes |

`mapping-confirmation` is a logical convenience. The current `memory-note` binary stores it as `kind=mapping-endorsement` plus `operation=confirm`.

## Authority matrix

Use the narrowest matching authority:

```text
mapping endorsement       explicit-user-endorsement | repeated-accepted-use
mapping confirmation      explicit-user-endorsement | repeated-accepted-use
mapping correction        explicit-user-correction
mapping rejection         explicit-user-rejection
activation boundary       explicit-user-endorsement | explicit-user-correction | repeated-accepted-use
boundary retraction       explicit-user-correction | explicit-user-rejection
```

Assistant inference is never sufficient.

## Lifecycle candidates

When `$learnings` lifecycle capture triggers Synesthesia evaluation and no
durable authority exists, useful mappings should become explicit candidates
rather than disappearing into a zero-row proof. Candidates are not adapter
payloads and must not be written to `.ledger/synesthesia/events.jsonl`.

Use this proof line shape:

```text
synesthesia: candidate: phrase="<sensory phrase>" translation="<engineering meaning>" needs=user-endorsement
```

Nearby context must include evidence, activation boundary, non-activation
boundary, verification or falsifier, and the missing authority. If the user
endorses, corrects, or rejects the candidate, convert that later event into the
appropriate durable operation.

## Canonical payload

Envelope fields own authority, scope, source references, and prior-note relationships. The payload owns only the sensory contract.

For endorsement, confirmation, or correction:

```json
{
  "operation": "assert",
  "authority": "explicit-user-endorsement",
  "summary": "Endorse long corridor as serialized-wait vocabulary.",
  "scope": {
    "kind": "task-family",
    "repo": null,
    "paths": []
  },
  "source_refs": [
    {
      "kind": "user-endorsement",
      "ref": "rollout:019...",
      "summary": "User explicitly accepted the mapping as reusable"
    }
  ],
  "related_ids": [],
  "supersedes_id": null,
  "payload": {
    "sensory_phrase": "long corridor",
    "engineering_translation": "serialized waits, chatty calls, or amplified dependency latency",
    "activation_boundary": "performance and dependency-chain diagnosis",
    "non_activation_boundary": "exact syntax or literal-only requests",
    "verification": "Every use names the concrete wait or latency mechanism and evidence"
  }
}
```

The adapter generates legacy compatibility fields required by the current writer. Do not manually make payload scope or endorsement type a second authority.

For rejection, replace `engineering_translation` with:

```json
"rejection_reason": "The phrase repeatedly implied the wrong failure family"
```

For a pure activation boundary, the payload contains:

```json
{
  "activation_boundary": "Use for explicit compare-by-feel requests",
  "non_activation_boundary": "Do not activate for ordinary architecture review",
  "verification": "Future use must name the representational ambiguity or explicit sensory request"
}
```

For boundary retraction:

```json
{
  "retracted_boundary": "Implicitly use for every performance task",
  "reason": "Performance alone does not establish representational need",
  "verification": "Future activation requires explicit sensory language or a documented handoff"
}
```

## Canonical append

After the gate passes, write the repo-local canonical event first:

```bash
ledger capture --source synesthesia \
  --kind mapping-endorsement \
  --json -
```

For confirmation:

```bash
ledger capture --source synesthesia \
  --kind mapping-confirmation \
  --json -
```

The ledger source validates the operation-kind matrix, prior relationship,
scope, authority, payload, and source references before appending to:

```text
.ledger/synesthesia/events.jsonl
```

## Same-turn memory-source admission

After the canonical append succeeds, load `$memory-source-notes` only when
global memory admission is warranted. Export the memory-note adapter envelope:

```bash
ledger export --source synesthesia \
  --format memory-note \
  --id SYN-...
```

Then pass that envelope to the Synesthesia source-note adapter:

```bash
uv run python \
  codex/skills/memory-source-notes/scripts/synesthesia_memory_note.py \
  append \
  --kind <logical-kind> \
  --json -
```

The adapter injects writer-compatibility fields, canonicalizes JSON before
fingerprinting, invokes `memory-note`, and emits the writer result. A failed
memory admission must never roll back a successful ledger append.

## Copy-based adapter synchronization

Memory extension instructions must be regular copied files, not symlinks.

From the dotfiles repository root:

```bash
uv run python \
  codex/skills/memory-source-notes/scripts/synesthesia_memory_note.py \
  sync-instructions
```

This copies:

```text
codex/memories/extensions/synesthesia/instructions.md
```

into:

```text
${CODEX_HOME:-$HOME/.codex}/memories/extensions/synesthesia/instructions.md
```

It refuses a symlinked destination or symlinked destination component.

## Doctor workflow

```bash
uv run python \
  codex/skills/memory-source-notes/scripts/synesthesia_memory_note.py \
  doctor \
  --format text
```

The doctor distinguishes:

```text
no source notes
adapter missing, stale, or symlinked
digest missing, stale, invalid, or current
source notes and digest present but not compiled
compiled memory mentions present
writer unavailable or writer doctor failure
```

## Generated current-state digest

Every successful non-dry-run Synesthesia append refreshes:

```text
${CODEX_HOME:-$HOME/.codex}/memories/extensions/synesthesia/resources/latest_synesthesia_digest.md
```

Manual refresh:

```bash
uv run python \
  codex/skills/memory-source-notes/scripts/synesthesia_memory_note.py \
  memory-digest
```

The generator reads the complete immutable note history, validates stored envelopes, and folds event chains in captured-time and note-ID order:

```text
assert     -> create an active mapping or boundary
confirm    -> add support to the referenced active lineage
supersede  -> replace the referenced current rule
reject     -> make the referenced mapping inactive
retract    -> make the referenced mapping or boundary inactive
reopen     -> restore an inactive referenced lineage with new evidence
```

Dangling, forward, cross-lineage, category-mismatched, or content-mismatched events remain under `Unresolved event chains` and never become active implicitly. Invalid source notes remain visible under `Invalid source notes`.

The default digest is always complete: active mappings, active boundaries, rejected/retracted entries, unresolved chains, and invalid notes. Partial human reports require an explicit `--output`; they must not overwrite the default `latest_synesthesia_digest.md`.

The digest embeds a deterministic source fingerprint over note IDs, note fingerprints, kinds, operations, and source-file hashes. Re-running without source changes returns `current` and does not rewrite the file. Digest failure is reported as a warning and never rolls back a successful source-note append.

## Phase 2 promotion

Explicit durable user endorsement, correction, rejection, retraction, or boundary instruction is sufficient evidence of intended persistence when the mapping is concrete, scoped, reversible, and future behavior would change.

Do not impose a repetition requirement on explicit durable authority.

Without explicit durability, require repeated accepted operational use across at least two independent contexts.

Resource digests are only staging artifacts. Every promotable resource entry must cite one or more immutable `source_note_ids`. Resource-only prose is not admitted evidence.

## Proof lines

Emit a proof line only when persistence was requested or the admission gate passed:

```text
memory-note: id=MSN-... extension=synesthesia kind=<kind> status=created
memory-note: duplicate-skip: extension=synesthesia fingerprint=<fingerprint>
memory-note: not-attempted: cli unavailable
memory-note: failed: <concise reason>
```

Do not emit routine `not-attempted` lines for ordinary diagnostic use.
