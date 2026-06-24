# Synesthesia Memory Source Adapter

Use this file only during Codex Phase 2 memory consolidation.

## Role

This extension interprets immutable, evidence-backed source notes for user-endorsed sensory mappings and activation boundaries used in software diagnosis.

It does not:

- turn aesthetic language into evidence;
- replace the installed `synesthesia` skill;
- infer preferences from assistant-authored prose;
- promote unadmitted resource-digest entries;
- write or mutate source notes.

## Primary source

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

A valid note is an immutable `memory-source-note/v1` event that passed the Synesthesia skill's admission preflight before `$memory-source-notes` wrote it.

## Required envelope authority

The note envelope owns:

```text
operation
authority
scope
source_refs
related_ids
supersedes_id
```

Do not reconstruct or override those fields from payload prose.

Accept only explicit user endorsement, correction, rejection, retraction, direct remember requests, or independently evidenced repeated accepted use.

`assistant-inference` is never sufficient.

## Mapping payload

Promotable mapping payloads contain:

```text
sensory_phrase
engineering_translation when the mapping has one
activation_boundary
non_activation_boundary
verification
```

Do not promote payloads that duplicate envelope scope or authority through fields such as `scope`, `scope_anchor`, or `endorsement_type`.

## Operation semantics

- `assert`: establish a newly accepted mapping or boundary;
- `confirm`: strengthen a prior accepted mapping through repeated accepted use;
- `supersede`: replace a prior phrase, translation, or boundary;
- `reject`: record explicit rejection and prevent unsupported promotion;
- `retract`: withdraw a prior mapping or boundary;
- `reopen`: restore a prior mapping only after fresh accepted evidence.

Corrections, confirmations, retractions, and reopenings require prior-note linkage. Rejections require prior-note linkage when rejecting an already admitted mapping.

Never edit or delete source notes. Resolve current state from the immutable event history.

## Promotion gate

Require all of:

- accepted authority;
- concrete future diagnostic or routing utility;
- reversible engineering translation;
- explicit activation and non-activation boundaries;
- narrow scope;
- verification rule;
- likely stability beyond the originating task;
- a future behavior delta.

Reject:

- one-off poetic language;
- assistant novelty;
- ambient UI colors or passive Chronicle context;
- transient incident details;
- mappings with no engineering translation or decision value;
- generic technical facts better owned by learnings;
- failed-route evidence better owned by the negative ledger.

## Resource digests

Files under:

```text
extensions/synesthesia/resources/*.md
```

are temporary consolidation aids, not independent evidence.

Every promotable mapping, boundary, rejection, or failure shield in a resource digest must cite one or more valid immutable note IDs:

```text
source_note_ids: [MSN-...]
```

An entry without source-note IDs is an unadmitted proposal. Its target is `none`.

## Conflict and precedence

Prefer, in order:

1. latest explicit user correction or retraction;
2. narrower applicable scope;
3. repeated accepted use over a single endorsement;
4. concrete engineering utility over aesthetic vividness.

Do not globalize repo-local vocabulary without separate broader authority.

## Artifact targeting

- `memory_summary.md`: compact activation/non-activation defaults and the requirement for literal engineering translation.
- `MEMORY.md`: scoped mappings, verification rules, source note IDs, and retrieval terms.
- `skills/*`: only for a repeated sub-workflow beyond the installed Synesthesia skill.
- `none`: tentative, decorative, duplicate, retracted, unendorsed, or task-local material.

Do not reproduce the full Synesthesia workflow in compiled memory.

## Security and hygiene

- no secrets, credentials, raw transcripts, or long tool outputs;
- no raw chronology;
- no private local paths unless essential and safely scoped;
- plain operational compiled memory, not decorative prose;
- exact endorsed phrase only when retrieval depends on it;
- no direct source-skill or compiled-memory mutation outside the owning phase.
