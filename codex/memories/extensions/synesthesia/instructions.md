# Synesthesia Memory Source Adapter

Use this file only during Codex Phase 2 memory consolidation.

This checked-in file must be copied as a regular file into:

```text
${CODEX_HOME:-$HOME/.codex}/memories/extensions/synesthesia/instructions.md
```

Do not symlink it. Use the copy-based synchronization command documented by the installed `memory-source-notes` skill.

## Role

Interpret evidence-backed, user-authorized sensory mappings and activation boundaries for software diagnosis and explanation.

This adapter does not turn aesthetic language into evidence and does not replace the installed `synesthesia` skill.

## Primary source

Process valid new or changed immutable admission snapshots under:

```text
extensions/synesthesia/notes/*.md
```

When present, a repo-local canonical source store lives at:

```text
<repo>/.ledger/synesthesia/events.jsonl
```

During transition, existing immutable notes remain valid source evidence. New repo-scoped events should be admitted from the canonical store when it exists.

Prioritize notes surfaced by `phase2_workspace_diff.md` when that artifact is available.

Canonical repo-local ledger rows are created by:

```text
ledger capture --source synesthesia
```

Supported stored kinds:

```text
mapping-endorsement
mapping-correction
mapping-rejection
activation-boundary
boundary-retraction
```

A logical mapping confirmation is stored as:

```text
kind = mapping-endorsement
operation = confirm
```

A valid note is an immutable `memory-source-note/v1` admission snapshot created after the Synesthesia source skill's admission gate and validated by the Synesthesia memory-source adapter. When `.ledger/synesthesia/events.jsonl` exists, prefer the ledger row as the complete canonical event and treat the note as Phase 2 transport evidence.

## Envelope authority

The envelope is authoritative for:

```text
operation
authority
scope
source_refs
related_ids
supersedes_id
fingerprint
note id
```

Legacy payload fields named `scope`, `scope_anchor`, or `endorsement_type` are generated compatibility projections. They must agree with the envelope and must not be treated as independent authority.

## Required mapping payload

For endorsement, confirmation, or correction:

```text
sensory_phrase
engineering_translation
activation_boundary
non_activation_boundary
verification
```

For rejection:

```text
sensory_phrase
activation_boundary
non_activation_boundary
rejection_reason
verification
```

For a pure activation boundary:

```text
activation_boundary
non_activation_boundary
verification
```

For boundary retraction:

```text
retracted_boundary
reason
verification
```

The envelope must contain explicit or repeated-accepted authority, narrow scope, and source references.

Assistant-authored phrases, templates, ontologies, or resource digests are not evidence by themselves.

## Operation semantics

- `assert` + `mapping-endorsement`: consider an explicitly endorsed mapping for promotion;
- `confirm` + `mapping-endorsement`: strengthen an existing mapping without duplicating it;
- `supersede` + `mapping-correction`: replace phrase, translation, scope, or boundary;
- `reject` + `mapping-rejection`: prevent promotion and remove prior compiled support when independently unsupported;
- `reopen` + `mapping-endorsement`: reconsider a previously rejected or retracted mapping only with new explicit evidence;
- `assert` + `activation-boundary`: install a durable activation/non-activation rule;
- `confirm` + `activation-boundary`: strengthen an existing boundary;
- `supersede` + `activation-boundary`: replace an existing boundary;
- `reopen` + `activation-boundary`: restore a boundary only with new explicit evidence;
- `retract` + `boundary-retraction`: withdraw a boundary or mapping support.

Confirmation, correction, rejection, retraction, and reopening require a prior note reference in `related_ids` or `supersedes_id`.

Never mutate or delete source notes.

## Promotion gate

Promote an explicit endorsement, correction, rejection, retraction, reopening, or durable boundary when all of these hold:

- the envelope has matching explicit user authority and source references;
- the mapping or boundary has concrete diagnostic or explanatory utility;
- activation and non-activation boundaries are clear;
- scope is narrow and reusable;
- verification keeps the mapping reversible;
- future Codex behavior would materially change.

Explicit durable user authority is sufficient evidence of intended persistence unless the user scopes the statement to the current task or session.

Do not impose a repetition requirement on explicit durable authority.

Without explicit durable authority, require repeated accepted operational use across at least two independent contexts, with evidence that the mapping changed diagnosis or explanation.

Reject:

- one-off poetic language;
- ambient colors or passive screen context;
- transient incident details;
- assistant novelty;
- mappings without engineering translation;
- mappings with no activation boundary or verification rule;
- resource entries without immutable source-note IDs;
- material that does not change future behavior.

## Conflict and precedence

When evidence conflicts, prefer:

1. the latest explicit user correction or rejection;
2. a narrower repo/path/task scope over a broad scope for that context;
3. explicit durable authority over inferred repetition;
4. repeated accepted evidence over a single non-durable use;
5. concrete engineering utility over vividness.

Do not globalize repo-local vocabulary without explicit broader authority.

## Generated current-state digest

When present, read this file first as the index of current Synesthesia state:

```text
extensions/synesthesia/resources/latest_synesthesia_digest.md
```

It is generated by `synesthesia_memory_note.py memory-digest` and refreshed automatically after successful Synesthesia source-note appends. It folds immutable event chains into active mappings, active boundaries, rejected/retracted entries, unresolved chains, and invalid-note diagnostics.

The digest is a projection, not independent evidence. Before promoting an entry:

1. require `digest_version: synesthesia-digest/v1`;
2. require `render_mode: full` and `entry_limit: 0`;
3. confirm its `source_fingerprint` matches the current immutable note set;
4. resolve every listed `source_note_id`;
5. verify the current operation chain and scope;
6. reject dangling, invalid, unresolved, or resource-only entries.

Use the digest to avoid rebuilding event state repeatedly. Use immutable notes as authority. A stale or invalid digest must be regenerated before promotion.

## Resource digest boundary

Files under `extensions/synesthesia/resources/` are temporary consolidation aids.

A resource entry is promotable only when it includes one or more valid:

```text
source_note_ids
```

Each ID must resolve to a current immutable Synesthesia source note supporting the entry. Resource-only prose is an unadmitted proposal and must target `none`.

## Artifact targeting

- `memory_summary.md`: compact cross-task activation/non-activation defaults and the requirement for reversible engineering translation;
- `MEMORY.md`: task-group entries with scope, phrase, engineering translation, activation/non-activation boundaries, verification, and `source_note_ids`;
- `skills/*`: only when several admitted notes prove a reusable sub-workflow beyond the installed Synesthesia skill;
- `none`: tentative, task-local, decorative, duplicate, unsupported, superseded, retracted, or already-codified material.

Do not recreate the installed Synesthesia skill in memory.

## Retrieval terms

Preserve exact endorsed phrases when retrieval-relevant, plus concrete technical terms from their engineering translations. Keep retrieval terms narrow enough to avoid activating the lens for ordinary domain tasks.

## Security and hygiene

- no secrets, raw chronology, passive screen context, or unbounded examples;
- no direct note or source-skill mutation;
- no direct compiled-memory edit outside Phase 2;
- plain operational compiled memory, not decorative prose;
- exact source note IDs for every promoted mapping or boundary;
- no symlinked live instruction files.
