# Codex automations database

## Location
- Default database: `~/.codex/sqlite/codex-dev.db`
- Override path with `--db` in `scripts/cron.py` if needed.
- Filesystem automation configs: `~/.codex/automations/<automation-id>/automation.toml`
- `scripts/cron.py` keeps SQLite rows and filesystem configs in sync.

## Tables

### automations
Columns:
- `id` TEXT primary key
- `name` TEXT
- `prompt` TEXT
- `status` TEXT (defaults to `ACTIVE`)
- `next_run_at` INTEGER (unix milliseconds, nullable)
- `last_run_at` INTEGER (unix milliseconds, nullable)
- `cwds` TEXT (JSON array of strings)
- `rrule` TEXT (RFC5545 RRULE string; app stores with `RRULE:` prefix)
- `created_at` INTEGER (unix milliseconds)
- `updated_at` INTEGER (unix milliseconds)

## Filesystem config
Each automation also has a directory at:
- `~/.codex/automations/<id>/`

Files:
- `automation.toml` (primary config rendered from the `automations` row)
- `memory.md` (created if missing; updated by app runs)

### automation_runs
Columns:
- `thread_id` TEXT primary key
- `automation_id` TEXT
- `status` TEXT
- `read_at` INTEGER
- `thread_title` TEXT
- `source_cwd` TEXT
- `inbox_title` TEXT
- `inbox_summary` TEXT
- `created_at` INTEGER
- `updated_at` INTEGER
- `archived_user_message` TEXT
- `archived_assistant_message` TEXT
- `archived_reason` TEXT

### inbox_items
Columns:
- `id` TEXT primary key
- `title` TEXT
- `description` TEXT
- `thread_id` TEXT
- `read_at` INTEGER
- `created_at` INTEGER
