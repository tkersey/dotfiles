---
name: cron
description: Create and manage Codex app automations stored in the local SQLite database (~/.codex/sqlite/codex-dev.db). Use when you need to add, list, update, enable/disable, delete, or run scheduled automations; edit automation prompts, RRULE schedules, or cwd scopes; or inspect automation records for the Codex app.
---

# Cron

## Overview
Use this skill to manage Codex automations by editing the local SQLite database and synced filesystem automation configs. Operate through the bundled `scripts/cron.py` and keep changes minimal and explicit.

## Quick Start
- List automations: `uv run python scripts/cron.py list`
- Create an automation: `uv run python scripts/cron.py create --name "Weekly release notes" --prompt-file /path/to/prompt.md --rrule "RRULE:FREQ=WEEKLY;BYDAY=FR;BYHOUR=9;BYMINUTE=0"`
- Update an automation: `uv run python scripts/cron.py update --id <id> --rrule "RRULE:FREQ=DAILY;BYHOUR=9;BYMINUTE=0"`
- Enable or disable: `uv run python scripts/cron.py enable --id <id>` or `uv run python scripts/cron.py disable --id <id>`
- Run immediately: `uv run python scripts/cron.py run-now --id <id>`
- Delete: `uv run python scripts/cron.py delete --id <id>`

## Workflow
1. Choose the working directories (`cwds`). Default to the current repo if not specified.
2. Write the automation prompt. Use `--prompt-file` for multi-line prompts.
3. Provide an RFC5545 RRULE string (see schedule guidance below).
4. Create or update the automation with `scripts/cron.py`.

## Clarify When Ambiguous
Ask questions only when the request is ambiguous or when the user explicitly asks for guidance. Do not block otherwise.

Essential elements to confirm or infer:
1. Automation name.
2. Prompt content (single line or file path).
3. Schedule as an RFC5545 RRULE string (include `RRULE:` prefix).
4. Working directories (`cwds`), default to the current repo if not specified.
5. Status if explicitly requested; otherwise default to `ACTIVE`.

When ambiguous, ask for the missing details. Examples:
- If the user says “daily” or “weekly” without a time, ask for time and day-of-week when relevant.
- If the user says “run it for this repo” but does not specify paths, confirm the repo root as the only `cwd`.
- If the user asks “set it up like the app” without a schedule, ask for the RRULE or offer a concrete example to confirm.

## Schedule (RRULE)
- Accept only RFC5545 RRULE strings. Cron expressions are not supported.
- The app stores `RRULE:`-prefixed strings; include the prefix to match existing records. Both forms are accepted.
- Prefer explicit `BYHOUR`/`BYMINUTE` for stable schedules.

Example rules:
- Daily at 09:00: `RRULE:FREQ=DAILY;BYHOUR=9;BYMINUTE=0`
- Weekly on Friday at 09:00: `RRULE:FREQ=WEEKLY;BYDAY=FR;BYHOUR=9;BYMINUTE=0`
- Every 24 hours: `RRULE:FREQ=HOURLY;INTERVAL=24;BYMINUTE=0`

## Task Examples
### Daily standup summary
Name: `Summarize yesterday's git activity`
Prompt: Summarize yesterday's git activity for standup. Include notable commits, files touched, and any risks or follow-ups.
Schedule: `RRULE:FREQ=DAILY;BYHOUR=9;BYMINUTE=0`

### Weekly release notes
Name: `Draft weekly release notes`
Prompt: Draft weekly release notes from merged PRs. Include links when available and group by area.
Schedule: `RRULE:FREQ=WEEKLY;BYDAY=FR;BYHOUR=9;BYMINUTE=0`

### CI failure triage
Name: `Summarize CI failures`
Prompt: Summarize CI failures and flaky tests from the last CI window, group by root cause, and suggest minimal fixes.
Schedule: `RRULE:FREQ=DAILY;BYHOUR=8;BYMINUTE=30`

## Data Model Reference
See `references/db.md` for the database schema and field notes.
