# Memory extension templates

These files are templates only. They live in `.templates/` because read-only memory retrieval may list/read/search files under `~/.codex/memories`; hidden directories are skipped by the local memory backend, so templates here should not pollute memory search.

Do not place non-evidence templates in a visible directory such as `extensions/_templates/` under the live memory root. If an older visible `_templates/` directory exists, remove it or move it outside `~/.codex/memories`.

To create a real local digest, copy the relevant template into the matching extension's `resources/` directory and rename it with a timestamp prefix:

```text
~/.codex/memories/extensions/learnings/resources/2026-05-17T18-30-00-learnings-digest.md
~/.codex/memories/extensions/synesthesia/resources/2026-05-17T18-30-00-synesthesia-signals.md
~/.codex/memories/extensions/negative-ledger/resources/2026-05-17T18-30-00-negative-ledger-digest.md
```

Keep real resource digests local and uncommitted when they include private session details, local paths, repo state, or user-specific evidence.

Resource digests are short-lived consolidation inputs. Durable content should be promoted into `memory_summary.md`, `MEMORY.md`, or memory-root `skills/*`; do not rely on `extensions/*/resources/*.md` for long-term runtime retrieval.
