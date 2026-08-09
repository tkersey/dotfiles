---
name: memory-source-notes
description: "Safely transport accepted typed source evidence into immutable Codex memory-extension notes, inspect and reconcile that transport, and materialize bounded derived digests. Use only after a source-authorized handoff from learnings, negative-ledger, or synesthesia, or for explicit diagnostics and reconciliation. Never decide source eligibility or edit compiled memory."
metadata:
  version: "2.1.0"
---
# Memory Source Notes

## Mission

Provide append-only transport and read-only reconciliation between canonical
source domains and Phase 2 memory compilation.

```text
source-owned admission decision
-> validated immutable source note
-> extension interpretation
-> Phase 2 compilation
```

This skill owns transport, adapters, diagnostics, and derived digests. The
source skill owns meaning and eligibility. Phase 2 owns compiled memory.

## Allowed extensions

```text
learnings
negative-ledger
synesthesia
```

Refuse ad hoc memory and Chronicle routes.

## Common path

1. Require a source-authorized admission payload or an explicit read-only
   diagnostic/reconciliation request.
2. Bind the live memory root, extension, source identity, relationships, scope,
   and operation.
3. Validate paths, note shape, sensitive content, and source completeness.
4. Use the extension's dedicated adapter when one exists; otherwise use the
   generic writer.
5. Preserve immutable payload bytes and idempotent fingerprinting.
6. Capture the structured writer result.
7. Report exactly one transport proof line when persistence was attempted.
8. Keep canonical-source, immutable-note, derived-digest, and compiled-memory
   outcomes separate.
9. Never infer admission from reconciliation.

## Proof-line semantics

Use one of:

```text
created
duplicate-skip
not-attempted: source admission gate not met
not-attempted: cli unavailable
blocked
```

A digest refresh failure after a successful immutable note is a warning, not a
rollback of the note.

## Conditional disclosure

The complete pre-split contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it for one accepted generic
append or simple inspection.

Load it only for:

- writer discovery and exact CLI commands;
- Synesthesia or Negative Ledger adapter contracts;
- instruction deployment, current-state digest generation, and doctors;
- cross-source reconciliation and Phase 2 visibility diagnosis;
- proof-line interpretation, historical admission, supersession, or withdrawal;
- an unported edge route.

Its frontmatter is archived source, not a second skill definition.

## Guardrails

- Never edit `memory_summary.md`, `MEMORY.md`, or compiled memory skills.
- Never hand-author a note because the CLI is unavailable.
- Never let transport acquire semantic admission authority.
- Never deploy live extension instructions as symlinks.
- Never treat a derived digest as canonical source evidence.
