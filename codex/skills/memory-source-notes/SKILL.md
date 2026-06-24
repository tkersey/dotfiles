---
name: memory-source-notes
description: "Safely append, inspect, validate, and deploy typed source-evidence notes for controlled Codex memory extensions. Use only after a handoff from harness-memory, learnings, negative-ledger, or synesthesia, or an explicit custom source capture request. Never edits compiled memory."
metadata:
  version: "1.1.0"
---

# Memory Source Notes

## Mission

Provide one append-only transport path for controlled custom memory sources while preserving domain authority and Phase 2's compiler boundary.

This skill writes source evidence only:

```text
~/.codex/memories/extensions/<extension>/notes/*.md
```

It never writes:

```text
~/.codex/memories/memory_summary.md
~/.codex/memories/MEMORY.md
~/.codex/memories/skills/*
```

## Authority model

```text
source skill or canonical domain store
-> source-specific admission decision
-> validated immutable memory-source note
-> extension instructions.md interpretation
-> Phase 2 consolidation
-> compiled memory
```

- `learnings` owns `.learnings.jsonl` and the admission gate for learning snapshots.
- `ledger` owns `.ledger/negative-ledger.jsonl` and the admission gate for route state.
- `harness-memory` owns durable operating-correction admission.
- `synesthesia` owns sensory mapping and activation-boundary admission.
- `memory-note` owns safe immutable transport.
- this skill owns command syntax, extension-specific adapters, copy-based instruction deployment, diagnostics, and proof-line interpretation;
- Phase 2 owns promotion, deduplication, supersession, and compiled-memory updates.

## Allowed extensions

```text
harness
learnings
negative-ledger
synesthesia
```

Refuse `ad_hoc` and Chronicle. Native remember/forget/update requests belong to Codex's native ad-hoc path. Chronicle is upstream-owned.

## Trigger cues

- explicit `$memory-source-notes`;
- documented handoff from `$harness-memory`, `$learnings`, `$negative-ledger`, or `$synesthesia`;
- explicit request to inspect or repair a custom memory-source layout;
- explicit request to synchronize extension instructions into the live memory root;
- explicit request to diagnose why admitted notes are not reaching compiled memory.

Do not trigger merely because a task produced history. The owning skill must first establish a source-specific admission event.

## CLI discovery

For general extensions, resolve the writer in this order:

```bash
run_memory_note_tool() {
  if [ -n "${MEMORY_NOTE_BIN:-}" ] && [ -x "$MEMORY_NOTE_BIN" ]; then
    "$MEMORY_NOTE_BIN" "$@"
    return
  fi

  if command -v memory-note >/dev/null 2>&1; then
    memory-note "$@"
    return
  fi

  local repo="${SKILLS_ZIG_REPO:-$HOME/workspace/tk/skills-zig}"
  if [ -x "$repo/zig-out/bin/memory-note" ]; then
    "$repo/zig-out/bin/memory-note" "$@"
    return
  fi

  echo "memory-note: not-attempted: cli unavailable" >&2
  return 127
}
```

Do not silently install unreleased tooling. Never hand-author a note as a fallback for a missing CLI.

## General append workflow

1. Receive an accepted payload from the owning skill.
2. Confirm the live memory root and extension directory are real directories, not symlinks.
3. Remove secrets, unnecessary local paths, raw transcript chronology, and unsupported inference.
4. Ensure authority, scope, source references, relationships, operation, and payload are complete.
5. Run the extension's validated append path.
6. Capture the structured result.
7. Emit exactly one proof line when persistence was attempted.

## Synesthesia validated adapter

Synesthesia uses:

```bash
uv run python \
  codex/skills/memory-source-notes/scripts/synesthesia_memory_note.py \
  append \
  --kind <logical-kind> \
  --json -
```

Logical kinds:

```text
mapping-endorsement
mapping-confirmation
mapping-correction
mapping-rejection
activation-boundary
boundary-retraction
```

The adapter:

- enforces operation-kind and authority-kind matrices;
- requires prior note relationships for confirmation, correction, rejection, retraction, and reopening;
- requires activation and non-activation boundaries;
- validates source references and narrow scope;
- rejects sensitive keys;
- makes the envelope authoritative for scope and authority;
- injects compatibility fields required by the current `memory-note` writer;
- serializes canonical JSON before writer fingerprinting;
- maps logical `mapping-confirmation` to stored `mapping-endorsement` with `operation=confirm`;
- invokes `memory-note` without hand-authoring notes.

Do not bypass this adapter for new Synesthesia writes.

## Copy-based extension instruction deployment

Live memory extension instructions must be regular copied files. Do not deploy them as symlinks.

Synchronize Synesthesia instructions from the dotfiles repository into the live memory root:

```bash
uv run python \
  codex/skills/memory-source-notes/scripts/synesthesia_memory_note.py \
  sync-instructions
```

The command:

- copies only `instructions.md`;
- leaves live `notes/` and `resources/` untouched;
- uses an atomic regular-file replacement;
- reports `current` when no copy is needed;
- refuses a symlinked destination or symlinked destination component.

## Synesthesia doctor

```bash
uv run python \
  codex/skills/memory-source-notes/scripts/synesthesia_memory_note.py \
  doctor \
  --format text
```

The doctor reports:

- live adapter status and source/live hashes;
- source-note count, kinds, operations, parse failures, and latest note IDs;
- `memory-note` availability and doctor output;
- compiled-memory mentions of Synesthesia or source-note IDs;
- the likely failing stage and next action.

## General writer command

For extensions without a dedicated adapter:

```bash
run_memory_note_tool append \
  --extension <extension> \
  --kind <kind> \
  --json -
```

## Proof lines

Successful append:

```text
memory-note: id=MSN-... extension=<name> kind=<kind> status=created
```

Duplicate accepted as no-op:

```text
memory-note: duplicate-skip: extension=<name> fingerprint=<fingerprint>
```

No qualifying event, but only when the gate was materially evaluated:

```text
memory-note: not-attempted: source admission gate not met
```

Unavailable CLI:

```text
memory-note: not-attempted: cli unavailable
```

Unsafe topology or validation failure:

```text
memory-note: failed: <concise reason>
```

Do not emit memory proof lines during ordinary work when no durable event or persistence request exists.

A source-note failure must not undo a successful canonical learning or negative-ledger write. Report canonical and admission outcomes separately.

## Source-specific kinds

Harness:

```text
harness-rule
harness-confirmation
harness-supersession
harness-retraction
```

Learnings:

```text
learning-admission
learning-confirmation
learning-supersession
learning-withdrawal
```

Negative ledger:

```text
ledger-projection
ledger-status-transition
ledger-supersession
ledger-retraction
```

Synesthesia stored kinds:

```text
mapping-endorsement
mapping-correction
mapping-rejection
activation-boundary
boundary-retraction
```

Synesthesia logical `mapping-confirmation` is stored as `mapping-endorsement` with `operation=confirm` until the native writer adds a distinct kind.

See [note-contract.md](references/note-contract.md) and [extension-payloads.md](references/extension-payloads.md).

## Read and doctor workflow

General read-only commands:

```bash
run_memory_note_tool doctor
run_memory_note_tool doctor --extension negative-ledger
run_memory_note_tool list --extension harness
run_memory_note_tool show --extension negative-ledger --id MSN-...
```

## Privacy and retrieval

Source notes may be exposed by broad read-only memory search even though normal runtime retrieval should route through compiled outputs. Never store credentials, tokens, private keys, raw chat logs, or long tool outputs.

## Non-goals

Do not use this skill to:

- bypass native ad-hoc remember/forget/update behavior;
- write compiled memory directly;
- replace `.learnings.jsonl` or `.ledger/negative-ledger.jsonl`;
- decide whether negative evidence blocks a route;
- infer durable user preferences from assistant prose alone;
- capture ordinary chronology;
- write into Chronicle;
- delete or mutate source notes;
- symlink live memory extension instructions.
