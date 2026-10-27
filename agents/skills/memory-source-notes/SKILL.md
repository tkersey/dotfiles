---
name: memory-source-notes
description: "Transport source-approved Learnings, Negative Ledger, and Synesthesia admissions through validated adapters to the native memory-note CLI; inspect selected memory layouts, copy extension instructions, and reconcile canonical records with immutable notes and compiled note references. Use for source handoffs or explicit memory transport, repair, or reconciliation requests. Never decides source eligibility or edits compiled memory."
metadata:
  version: "2.2.0"
---

# Memory Source Notes

## Mission

Provide one append-only transport path, bounded derived-digest tooling, and the
read-only cross-source reconciliation application for controlled custom memory
sources while preserving domain authority and Phase 2's compiler boundary.

Resolve the selected layout through `memory-note path --extension <name>
--format json`. The returned `notes_dir` owns immutable admissions; the
Synesthesia adapter may also regenerate its disposable `resources_dir` digest.
Do not derive these paths independently from `$HOME` or a config-file parser.

```text
<layout.notes_dir>/*.md
```

Phase 2 alone writes compiled memory. Version v2 produces only the compact
`memory_summary.md`; v1 may additionally produce `MEMORY.md` and `skills/*`.
Read only the selected version's artifacts when diagnosing compiled references:

```text
<layout.memory_root>/memory_summary.md
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

- `$learnings` owns the passive Learnings protocol and learning admission semantics.
- `$negative-ledger` owns the passive Negative Evidence protocol and route-state admission semantics.
- `$ledger` owns canonical custody and personal store selection for these managed sources. Use its returned `native_args` and stable `repository_id`; a workspace is an optional cataloged alias, and Git is unnecessary for direct `--store-id` selection.
- `$synesthesia` owns the passive `synesthesia/protocol` definition, `.ledger/synesthesia/events.jsonl`, sensory mapping semantics, and the admission decision.
- The `memory-note` CLI owns effective memory-root resolution and every immutable note write or version migration.
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

Do not trigger merely because a task produced history. The owning skill must first establish a source-specific admission event, unless the request is explicitly read-only reconciliation or diagnostics.

## CLI discovery

Load `$ledger` for canonical context and operation selection. Resolve a managed
source once using its selected store ID or registered workspace. Read-only
transport and diagnostics do not initialize stores, scan worktrees, or run
custody maintenance. Synesthesia retains its explicitly selected unmanaged root.

For general extensions, resolve the writer in this order:

```bash
run_memory_note_tool() {
  if [ -n "${MEMORY_NOTE_BIN:-}" ]; then
    if [ ! -x "$MEMORY_NOTE_BIN" ]; then
      echo "memory-note: failed: selected CLI unavailable" >&2
      return 127
    fi
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

## Select one memory layout

The native writer asks Codex's effective configuration through local app-server
`config/read` when `--memory-version` is omitted. Explicit `--codex-home` and
`--memory-version v1|v2` pin a known active session. The native path response uses
schema `memory-note-layout/v1` and names `codex_home`, `memory_version`,
`memory_root`, `extension_root`, `notes_dir`, `instructions_path`, and
`resources_dir`.

Resolve once and pass the returned home/version to every append, list, show,
doctor, digest, and instruction-copy operation in that workflow. The bundled
adapters share `scripts/memory_layout.py` for this. A resolver failure is a
diagnostic error; never fall back to an old directory because it exists.
After a config-version change, verify reader access in a fresh Codex session.
Ordinary operations never search or write both versions.

## General append workflow

1. Receive an accepted payload from the owning skill.
2. Resolve and pin the memory layout; confirm existing path components are real directories, not symlinks.
3. Remove secrets, unnecessary local paths, raw transcript chronology, and unsupported inference.
4. Ensure authority, scope, source references, relationships, operation, and payload are complete.
5. Run the extension's validated append path.
6. Capture the structured result.
7. Retain the writer proof and report any transport degradation separately from canonical success.

Resolve adapter paths once from the installed skill, independently of the target
repository's working directory:

```bash
memory_source_notes_root="$(realpath "$HOME/.agents/skills/memory-source-notes")"
```

## Synesthesia validated adapter

After Synesthesia accepts a canonical event for global memory admission, use
its exact canonical identity and the same explicit custody root used for capture:

```bash
uv run \
  "$memory_source_notes_root/scripts/synesthesia_memory_note.py" \
  admit \
  --repo "<canonical-custody-root>" \
  --id SYN-...
```

Use `inspect-admission` with the same arguments for a read-only projection.
The adapter derives the kind from the canonical event, checks the selected
Ledger definition and immutable note inventory, and resolves canonical `SYN-*`
relationships to exact already-admitted `MSN-*` identities. It preserves the
canonical identities in derived source references; it never edits canonical
rows or invents note IDs. Missing, ambiguous, or unresolved prior admissions
block this admission without rolling back capture or automatically backfilling
history. Existing exact snapshots retain their bytes and fingerprints.

Transport reserves source-reference kinds `synesthesia-canonical-event` for the
snapshot's own canonical ID and `synesthesia-canonical-relationship` for its
canonical predecessors. These are provenance, not new user authority. Canonical
source submissions must not prepopulate them. Read-only reconciliation uses the
same resolver and fingerprint construction, rather than comparing canonical and
transport envelopes as though their identities were interchangeable.

Synesthesia retains explicit unmanaged custody in this revision. This adapter
does not discover or migrate another worktree's history. Use the source owner's
selected root consistently; storage-location or migration changes remain owned
by `$ledger` and require a separate custody decision.

The lower-level `append --kind <logical-kind> --json -` path remains for
source-approved note envelopes whose relationships are already `MSN-*` IDs.
It rejects canonical relationship IDs; use `admit` for canonical events instead
of hand-editing projected relationships.

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
  "$memory_source_notes_root/scripts/negative_ledger_memory_note.py" \
  admit \
  --store-id "<context.store_id>" \
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
  "$memory_source_notes_root/scripts/negative_ledger_memory_note.py" \
  inspect \
  --store-id "<context.store_id>" \
  --id NEG-...
```

## Synesthesia current-state digest

Manual refresh:

```bash
uv run \
  "$memory_source_notes_root/scripts/synesthesia_memory_note.py" \
  memory-digest
```

The default output is in the same selected layout as admission:

```text
<layout.resources_dir>/latest_synesthesia_digest.md
```

The generator validates all stored Synesthesia notes and folds `assert`, `confirm`, `supersede`, `reject`, `retract`, and `reopen` into a deterministic current-state projection. It preserves active mappings, active boundaries, inactive entries, unresolved event chains, invalid-note diagnostics, source-note provenance, and a source fingerprint.

The default digest is a complete materialized view and must remain a regular file. Partial or active-only reports require an explicit `--output` and must not replace the default digest. The digest never replaces immutable source notes or compiled memory.

## Copy-based extension instruction deployment

Live memory extension instructions must be regular copied files. Do not deploy them as symlinks.

Synchronize all three controlled extensions from the tracked source files into
the selected memory root:

```bash
uv run \
  "$memory_source_notes_root/scripts/memory_source_layout.py" \
  sync-instructions
```

The command:

- copies only `instructions.md`;
- leaves live `notes/` and `resources/` untouched;
- uses an atomic regular-file replacement;
- reports `current` when no copy is needed;
- refuses a symlinked destination or symlinked destination component.

Use `--extension <name>` to select one extension, `--source-root <directory>`
when the checked-in instruction source is elsewhere, and `--memory-version`
with `--codex-home` to pin a reviewed layout. `doctor` on the same script reports
selected paths and source/live hashes without creating directories. The
repository wrapper `scripts/doctor-memory-source-layout.sh` delegates to it.
The Synesthesia-specific `sync-instructions` command remains supported.

## Synesthesia doctor

```bash
uv run \
  "$memory_source_notes_root/scripts/synesthesia_memory_note.py" \
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
- exact source-note IDs observed in the selected compiled artifacts;
- the likely failing stage and next action.

## General writer command

For extensions without a dedicated adapter:

```bash
run_memory_note_tool append \
  --extension <extension> \
  --kind <kind> \
  --codex-home "<layout.codex_home>" \
  --memory-version "<layout.memory_version>" \
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

Unavailable CLI:

```text
memory-note: not-attempted: cli unavailable
```

Unsafe topology or validation failure:

```text
memory-note: failed: <concise reason>
```

Keep no-ops internal unless the user asks for their evidence. Do not emit memory proof lines during ordinary work when no durable event or persistence request exists. Digest refresh is silent on successful automatic runs; only manual `memory-digest` calls print a digest summary.

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
memory_source_notes_root="$(realpath "$HOME/.agents/skills/memory-source-notes")"
uv run python \
  "$memory_source_notes_root/scripts/source-memory-reconcile.py" \
  --store-id "<context.store_id>" \
  --source learnings --source negative-ledger \
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

The `source-memory-reconciliation/v3` report separates compiled references as
`note-id-observed`, `not-observed`, `unknown`, or `not-applicable`. Only the exact
immutable note ID is an observed link. A bare `NEG-*` or learning ID can collide
across stores and does not attribute admission. Missing or unreadable required
compiled files produce `unknown`. A readable summary without a literal note ID
does not establish compiler lag, rejection, paraphrase, or decision impact.

Managed notes use `ledger-repository:<store_id>`. A historical scope can match
only through the same source's exact native exported bytes and writer
fingerprint, without rewriting the note or inventing Git remote/basename
aliases. Notes lacking that witness remain foreign or unresolved. Per-source
context, inventory, or projection errors preserve unrelated healthy results.

Use `--repo <registered-workspace>` as a managed store alias if no store ID is
selected. For Synesthesia include `--source synesthesia --repo
<explicit-unmanaged-root>`; the default source set includes all three. Use
`--source` to avoid diagnosing a source that is outside the intended task.

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

For an explicit root-version cutover, use native `memory-note migrate` as
documented in [source-store-layout.md](references/source-store-layout.md).
Migrate only existing admitted immutable envelopes. Migration is separate from
source eligibility and does not authorize historical bulk admission.

## General read and doctor workflow

```bash
run_memory_note_tool path --extension learnings --format json
run_memory_note_tool doctor --extension learnings --codex-home "<layout.codex_home>" --memory-version "<layout.memory_version>"
run_memory_note_tool list --extension learnings --codex-home "<layout.codex_home>" --memory-version "<layout.memory_version>"
run_memory_note_tool show --extension learnings --id MSN-... --codex-home "<layout.codex_home>" --memory-version "<layout.memory_version>"
```

Use source-specific doctors for canonical stores and this skill's reconciler
for historical cross-source gaps.

## Privacy and retrieval

Source notes may be exposed by broad read-only memory search even though normal runtime retrieval should route through compiled outputs. Never store credentials, tokens, private keys, raw chat logs, or long tool outputs.

## Non-goals

Do not use this skill to:

- bypass native ad-hoc remember/forget/update behavior;
- write compiled memory directly;
- replace canonical source stores or choose custody outside `$ledger`;
- decide whether negative evidence blocks a route;
- decide whether a learning, negative projection, or sensory mapping is eligible;
- infer durable user preferences from assistant prose alone;
- capture ordinary chronology;
- write into Chronicle;
- delete or mutate source notes;
- symlink live memory extension instructions;
- convert a reconciliation report into automatic bulk admission.
