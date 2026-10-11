# Memory extension templates

These checked-in files under `codex/memories/extensions/.templates/` are source
templates only. Keep them outside the selected live memory root. The instruction
deployer copies only controlled `instructions.md` files; it does not install
templates. Do not rely on hidden-directory filtering to keep template prose out
of memory retrieval or consolidation.

Resolve a target extension through the native layout API before creating a real
resource digest:

```bash
memory-note path --extension <extension> --format json
```

Read `resources_dir`, `codex_home`, and `memory_version` from the returned
`memory-note-layout/v1` JSON. Use an explicit `--codex-home` and
`--memory-version v1|v2` on the path command when pinning a known active session.
Carry those resolved values to subsequent writer/reader commands, for example:

```bash
memory-note list --extension <extension> \
  --codex-home "<layout.codex_home>" \
  --memory-version "<layout.memory_version>"
```

Do not construct a root independently, fall back to an existing old directory,
or copy the source template directory into the live memory tree.

To create a real local digest, copy the relevant template into the matching extension's `resources/` directory and rename it with a timestamp prefix:

```text
<learnings-layout.resources_dir>/2026-05-17T18-30-00-learnings-digest.md
<synesthesia-layout.resources_dir>/2026-05-17T18-30-00-synesthesia-signals.md
<negative-ledger-layout.resources_dir>/2026-05-17T18-30-00-negative-ledger-digest.md
```

Keep real resource digests local and uncommitted when they include private session details, local paths, repo state, or user-specific evidence.

Resource digests are short-lived consolidation inputs. Phase 2 selects durable
content under its active artifact contract; v2 produces only compact
`memory_summary.md`. Do not rely on `extensions/*/resources/*.md` for long-term
runtime retrieval or edit compiled memory directly.
