# Synesthesia Memory Admission

## Boundary

Synesthesia owns the decision that a mapping or activation boundary is admissible. `$memory-source-notes` owns safe transport and proof lines. Phase 2 owns compiled memory.

No ordinary Synesthesia answer creates a durable note.

## Admissible events

A note is allowed only for one of these witnessed events:

- explicit user endorsement;
- explicit user correction;
- explicit user rejection;
- explicit retraction;
- explicit request to remember the mapping or boundary;
- repeated accepted operational use with independent source references.

Assistant-authored novelty, inferred taste, one-off poetic language, and task-local incident descriptions are not sufficient.

## Supported kinds and operations

| Kind | Allowed operation | Prior note required |
|---|---|---|
| `mapping-endorsement` | `assert`, `confirm`, `reopen` | for `confirm` and `reopen` |
| `mapping-correction` | `supersede` | yes |
| `mapping-rejection` | `reject` | yes unless rejecting a newly proposed unrecorded mapping |
| `activation-boundary` | `assert`, `confirm`, `supersede`, `reopen` | except initial `assert` |
| `boundary-retraction` | `retract` | yes |

A required prior note must appear in `supersedes_id` or `related_ids`.

## Envelope authority

The source-note envelope exclusively owns:

- `operation`;
- `authority`;
- `scope`;
- `source_refs`;
- `related_ids`;
- `supersedes_id`.

Do not duplicate those concepts in the payload.

Allowed Synesthesia authorities are:

```text
explicit-user-endorsement
explicit-user-correction
explicit-user-rejection
explicit-user-retraction
explicit-user-remember-request
repeated-accepted-use
```

`assistant-inference` and `source-skill` alone are insufficient.

## Payload

For an accepted mapping:

```json
{
  "sensory_phrase": "long corridor",
  "engineering_translation": "serialized waits or amplified dependency latency",
  "activation_boundary": "performance and dependency-chain diagnosis",
  "non_activation_boundary": "literal-only or exact syntax work",
  "verification": "Every use identifies the concrete latency mechanism and evidence"
}
```

Allowed payload fields:

```text
sensory_phrase
engineering_translation
activation_boundary
non_activation_boundary
verification
```

A `mapping-rejection` may omit `engineering_translation` only when the rejected mapping has no accepted translation.

## Scope

Use the envelope's canonical scope values:

```text
global
repo
path-family
task-family
workflow
tool
```

Use the narrowest reusable scope. Repo-local vocabulary remains repo-local until separately endorsed at broader scope.

## Preflight and canonicalization

Write the proposed envelope to a temporary JSON file, then run:

```bash
uv run --with pyyaml python \
  codex/skills/synesthesia/scripts/validate_synesthesia.py \
  memory-file proposed.json --kind mapping-endorsement --emit-canonical \
  > proposed.canonical.json
```

Pass **the canonical file** to `$memory-source-notes`. The canonicalizer sorts object keys and removes insignificant JSON formatting differences so equivalent Synesthesia calls produce identical input bytes for the current `memory-note` fingerprinting behavior.

Do not hand-author a note if the CLI is unavailable.

## Resource-digest provenance

A Synesthesia resource digest is only a temporary consolidation aid. Every promotable mapping, boundary, rejection, or failure shield in a resource digest must include:

```text
source_note_ids: [MSN-...]
```

An entry with no valid source-note ID is an unadmitted proposal and must target `none`.

## Proof-line discipline

Only `$memory-source-notes` emits the final proof line. Synesthesia should mention no memory result unless:

- the user requested capture;
- an admissible event occurred;
- preflight or writing was attempted.

Do not add routine “not attempted” lines to ordinary diagnostic answers.
