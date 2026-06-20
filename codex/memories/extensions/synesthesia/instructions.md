# Synesthesia Memory Source Adapter

Use this file only during Codex Phase 2 memory consolidation.

## Role

This extension interprets evidence-backed, user-endorsed sensory mappings and activation boundaries for software diagnosis.

It does not turn aesthetic language into evidence and does not replace the installed `synesthesia` skill.

## Primary Source

```text
extensions/synesthesia/notes/*.md
```

Supported kinds:

```text
mapping-endorsement
mapping-correction
mapping-rejection
activation-boundary
boundary-retraction
```

A valid note is an immutable `memory-source-note/v1` event created after the source skill's endorsement gate.

## Required Payload

For mappings:

```text
sensory_phrase
engineering_translation
activation_boundary
non_activation_boundary when relevant
scope
scope_anchor
endorsement_type
verification
```

The envelope must contain explicit authority and source references.

Assistant-authored phrases, templates, or mapping ontologies are not evidence by themselves.

## Operation Semantics

- `assert`/endorsement: current accepted mapping or boundary;
- `confirm`: repeated accepted use raises confidence;
- `supersede`/correction: replace phrase, translation, or scope;
- `reject`: prevent promotion and remove prior compiled mapping if independently unsupported;
- `retract`: withdraw a boundary/mapping;
- `reopen`: restore only with new explicit evidence.

Never edit/delete source notes.

## Promotion Gate

Require explicit endorsement/correction/rejection or repeated accepted use, likely stability beyond one session, concrete diagnostic utility, reversible engineering translation, narrow scope, and future behavior delta.

Reject one-off poetic language, ambient colors, transient incident details, and mappings that do not change engineering reasoning.

## Artifact Targeting

- `memory_summary.md`: compact activation/non-activation defaults and translation requirements.
- `MEMORY.md`: use task-group structure with scope, phrase, engineering translation, activation/non-activation boundaries, `source_note_ids`, and retrieval terms.
- `skills/*`: only for a repeated sub-workflow beyond the installed source skill.
- `none`: tentative, unendorsed, retracted, duplicate, decorative, or task-local phrases.

## Cross-Extension Ownership

- operating behavior about when to use the lens -> synesthesia owns the sensory boundary;
- general evidence-backed technical lesson -> learnings;
- failed route constraint -> negative-ledger;
- sensory phrase plus engineering translation -> synesthesia.

## Security and Hygiene

- no secrets, raw chronology, passive screen context, or unbounded examples;
- plain operational compiled memory, not decorative prose;
- exact endorsed phrases when retrieval-relevant;
- no direct note or source-skill mutation;
- no direct compiled-memory edit outside Phase 2.
