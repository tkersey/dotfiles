# CAS automation state

CAS preserves the existing Codex automation store and files. No migration or
second durable store is required.

## Default locations

```text
~/.codex/sqlite/codex-dev.db
~/.codex/automations/<automation-id>/automation.toml
~/.codex/automations/<automation-id>/memory.md
```

`--db <path>` overrides only the SQLite database selected by the command. The
default state root remains derived from `HOME` for parity with the absorbed
native automation product.

## `automations`

Required fields:

- `id` TEXT primary key
- `name` TEXT
- `prompt` TEXT
- `status` TEXT: `ACTIVE` or `PAUSED`
- `next_run_at`, `last_run_at` INTEGER nullable, Unix milliseconds
- `cwds` TEXT containing a JSON array of strings
- `rrule` TEXT containing an RFC5545 rule
- `created_at`, `updated_at` INTEGER, Unix milliseconds

Additive columns are allowed. Missing or incompatible required columns block
mutation.

## Files

`automation.toml` is rendered from the row. `memory.md` is created if absent
and otherwise preserved; successful bounded run summaries are appended through
the native runner. Doctor detects missing, stale, malformed, unsafe, or
row-divergent file state.

## `automation_runs`

Run rows preserve thread and automation identity, status, timestamps, cwd,
inbox title/summary, and app-side archival fields. Current statuses include
`RUNNING`, `PENDING_REVIEW`, `FAILED`, and `ARCHIVED`.

## `inbox_items`

Inbox rows preserve item ID, title, description, thread ID, read timestamp, and
creation timestamp.

CAS never fabricates a successful rollback after a committed database change.
A file-sync failure is a distinct observable result and leaves an actionable
doctor diagnostic.
