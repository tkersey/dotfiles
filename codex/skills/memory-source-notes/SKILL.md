---
name: memory-source-notes
description: "Transport source-approved Learnings, Negative Ledger, and Synesthesia admissions through validated adapters to the `memory-note` CLI; inspect, reconcile, and diagnose immutable-note, digest, and Phase 2 visibility gaps. Never decides source eligibility or edits compiled memory."
metadata:
  version: "2.1.1"
---

# Memory Source Notes

## Mission

Provide one append-only transport path, bounded derived-digest tooling, and the
read-only cross-source reconciliation application for controlled custom memory
sources while preserving domain authority and Phase 2's compiler boundary.

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

- `$learnings` owns the passive Learnings protocol, `.ledger/learnings/events.jsonl`, and learning admission semantics.
- `$negative-ledger` owns the passive Negative Evidence protocol, `.ledger/negative-ledger/events.jsonl`, and route-state admission semantics.
- `$synesthesia` owns the passive `synesthesia/protocol` definition, `.ledger/synesthesia/events.jsonl`, sensory mapping semantics, and the admission decision.
- The `memory-note` CLI owns the final immutable note write.
- `$memory-source-notes` owns command syntax, extension-specific adapters, derived digest generation, copy-based instruction deployment, diagnostics, proof-line interpretation, and read-only reconciliation across canonical sources, immutable admissions, and Phase 2 visibility.
- Phase 2 owns promotion, deduplication, supersession, and compiled-memory updates.

Reconciliation diagnoses transport and visibility state. It does not infer source
eligibility, append canonical rows, write notes, or grant authority.

## Allowed extensions

```text
learnings
negative-ledger
synesthesia
```

Refuse `ad_hoc` and Chronicle. Native remember/forget/update requests belong to Codex's native ad-hoc path. Chronicle is upstream-owned.

## Trigger cues

- explicit `$memory-source-notes`;
- documented handoff from `$learnings`, `$negative-ledger`, or `$synesthesia`;
- explicit request to inspect or repair a custom memory-source layout;
- explicit request to synchronize extension instructions into the live memory root;
- explicit request to diagnose why admitted notes are not reaching compiled memory;
- explicit request to reconcile canonical source records with immutable notes or Phase 2 visibility;
- explicit source-authorized historical admission or harvest request.

Do not trigger merely because a task produced history. The owning skill must first establish a source-specific admission event, unless the request is explicitly read-only reconciliation or diagnostics.

## CLI discovery

Before the first native Ledger command in an admission, reconciliation, or
diagnostic workflow, load `$ledger` and complete `$ledger ensure` once.

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
uv run \
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

- performs deterministic writer-transport normalization;
- delegates operation-kind, authority-kind, relationship, boundary, scope, source-reference, sensitive-key, and payload validation to `ledger validate` with the passive Synesthesia memory-note definition;
- treats Ledger's result as the sole structural decision without granting semantic authority;
- preserves the envelope as the authority for scope and authority;
- injects deterministic transport fields required by the current `memory-note` writer;
- serializes canonical JSON before writer fingerprinting;
- maps logical `mapping-confirmation` to stored `mapping-endorsement` with `operation=confirm`;
- invokes `memory-note` without hand-authoring notes;
- refreshes the generated Synesthesia current-state digest after every successful non-dry-run append;
- treats digest failure as a non-rollback warning, never as failure of the immutable source-note write.

Do not bypass this adapter for new Synesthesia writes.

## Negative Ledger validated adapter

After `$negative-ledger` accepts a complete current projection for admission,
use:

```bash
uv run \
  codex/skills/memory-source-notes/scripts/negative_ledger_memory_note.py \
  admit \
  --id NEG-... \
  --kind ledger-projection
```

Use `ledger-status-transition`, `ledger-supersession`, or `ledger-retraction`
only when the source owner classifies that event. The adapter runs
definition-bound `ledger doctor`, obtains the authoritative `memory-note`
projection, validates identity and projection completeness, preserves
the deterministic export bytes, and invokes `memory-note` idempotently. It
rejects `need-evidence`, `capture_candidate`, `unknown`, and incomplete active
projections.

The adapter is transport, not admission authority. It must be called only after
Negative Ledger decides recurrence and utility. Inspect without writing via:

```bash
uv run \
  codex/skills/memory-source-notes/scripts/negative_ledger_memory_note.py \
  inspect \
  --id NEG-...
```

## Synesthesia current-state digest

Manual refresh:

```bash
uv run \
  codex/skills/memory-source-notes/scripts/synesthesia_memory_note.py \
  memory-digest
```

Default output:

```text
${CODEX_HOME:-$HOME/.codex}/memories/extensions/synesthesia/resources/latest_synesthesia_digest.md
```

The generator validates all stored Synesthesia notes and folds `assert`, `confirm`, `supersede`, `reject`, `retract`, and `reopen` into a deterministic current-state projection. It preserves active mappings, active boundaries, inactive entries, unresolved event chains, invalid-note diagnostics, source-note provenance, and a source fingerprint.

The default digest is a complete materialized view and must remain a regular file. Partial or active-only reports require an explicit `--output` and must not replace the default digest. The digest never replaces immutable source notes or compiled memory.

## Copy-based extension instruction deployment

Live memory extension instructions must be regular copied files. Do not deploy them as symlinks.

Synchronize Synesthesia instructions from the dotfiles repository into the live memory root:

```bash
uv run \
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
uv run \
  codex/skills/memory-source-notes/scripts/synesthesia_memory_note.py \
  doctor \
  --repo <repo> \
  --format text
```

The doctor reports:

- live adapter status and source/live hashes;
- source-note count, kinds, operations, parse failures, and latest note IDs;
- digest status (`missing`, `current`, `stale`, `invalid`,
  `insecure-permissions`, or unsafe path);
- current active/inactive/unresolved projection counts;
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

Do not emit memory proof lines during ordinary work when no durable event or persistence request exists. Digest refresh is silent on successful automatic runs; only manual `memory-digest` calls print a digest summary.

A source-note failure must not undo a successful canonical learning, negative-ledger, or Synesthesia write. Report canonical and admission outcomes separately.

## Source-specific kinds

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

## Read-only reconciliation

Reconciliation compares canonical source records, immutable source notes, and
Phase 2 provenance without writing or deciding eligibility.

```bash
memory_source_notes_root="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/memory-source-notes")"
uv run python \
  "$memory_source_notes_root/scripts/source-memory-reconcile.py" \
  --repo "$(git rev-parse --show-toplevel)" \
  --format text
```

The report may classify a canonical record as:

```text
admitted
eligible-unadmitted
not-eligible
needs-source-review
incomplete-projection
stale-note
```

Phase 2 visibility is reported separately as `visible`, `lag`, or `unknown`.
Exact source or note IDs must appear as bounded provenance tokens; a substring
is not evidence. Unreadable Phase 2 files produce `unknown`, never a false claim
of absence.

Repository-scoped notes match only the canonical normalized origin identity
when one is available. Basename aliases do not establish repository identity.
Unscoped notes remain unscoped; they are not silently rebound to the current
repository.

When source owners have reviewed historical rows, pass an explicit
`source-memory-eligibility/v1` JSON file via `--eligibility`. Each decision must
name one canonical ID, `eligible|not-eligible`, and a non-empty source-owned
reason. The reconciler uses that input only to distinguish a real admission gap
from an ineligible or unreviewed record.

After an owning source explicitly accepts a candidate, use its documented
adapter or exact native `memory-note` projection. Keep backfill bounded and
auditable; never bulk-admit every source row.

See [source-store-layout.md](references/source-store-layout.md) and
[harvest-workflow.md](references/harvest-workflow.md).

## General read and doctor workflow

```bash
run_memory_note_tool doctor
run_memory_note_tool doctor --extension negative-ledger
run_memory_note_tool list --extension learnings
run_memory_note_tool show --extension negative-ledger --id MSN-...
```

Use source-specific doctors for canonical stores and this skill's reconciler
for historical cross-source gaps.

## Privacy and retrieval

Source notes may be exposed by broad read-only memory search even though normal runtime retrieval should route through compiled outputs. Never store credentials, tokens, private keys, raw chat logs, or long tool outputs.

## Non-goals

Do not use this skill to:

- bypass native ad-hoc remember/forget/update behavior;
- write compiled memory directly;
- replace canonical repo-local source stores;
- decide whether negative evidence blocks a route;
- decide whether a learning, negative projection, or sensory mapping is eligible;
- infer durable user preferences from assistant prose alone;
- capture ordinary chronology;
- write into Chronicle;
- delete or mutate source notes;
- symlink live memory extension instructions;
- convert a reconciliation report into automatic bulk admission.
