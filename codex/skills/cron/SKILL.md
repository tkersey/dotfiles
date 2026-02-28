---
name: cron
description: Create and manage Codex app automations stored in the local SQLite database (~/.codex/sqlite/codex-dev.db). Use when you need to add, list, update, enable/disable, delete, or run-now automations; edit automation names, prompts, RRULE schedules, or cwd scopes; or inspect automation records while troubleshooting app automation behavior.
---

# Cron

## Overview
Use this skill to manage Codex automations through the native Zig `cron` CLI. Runtime paths are Zig-only (no Python fallback, no shell launchd wrappers).

## Zig CLI Iteration Repos

When iterating on `cron`, use these two repos:

- `skills-zig` (`/Users/tk/workspace/tk/skills-zig`): source for the `cron` binary, build/test wiring, release tags.
- `homebrew-tap` (`/Users/tk/workspace/tk/homebrew-tap`): formula/checksum updates for released binaries.

## Quick Start
```bash
run_cron_tool() {
  if command -v cron >/dev/null 2>&1 && cron --help 2>&1 | grep -q "cron.zig"; then
    cron "$@"
    return
  fi
  if [ "$(uname -s)" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
    if ! brew install tkersey/tap/cron; then
      echo "brew install tkersey/tap/cron failed." >&2
      return 1
    fi
    if command -v cron >/dev/null 2>&1 && cron --help 2>&1 | grep -q "cron.zig"; then
      cron "$@"
      return
    fi
    echo "brew install tkersey/tap/cron did not produce a compatible cron binary." >&2
    return 1
  fi
  echo "cron binary missing; install tkersey/tap/cron." >&2
  return 1
}
```

- List automations: `run_cron_tool list`
- Create an automation: `run_cron_tool create --name "Weekly release notes" --prompt-file /path/to/prompt.md --rrule "RRULE:FREQ=WEEKLY;BYDAY=FR;BYHOUR=9;BYMINUTE=0"`
- Update an automation: `run_cron_tool update --id <id> --rrule "RRULE:FREQ=DAILY;BYHOUR=9;BYMINUTE=0"`
- Enable or disable: `run_cron_tool enable --id <id>` or `run_cron_tool disable --id <id>`
- Run immediately: `run_cron_tool run-now --id <id>`
- Delete: `run_cron_tool delete --id <id>`
- Run due automations once: `run_cron_tool run-due`
- Run due automations dry-run: `run_cron_tool run-due --dry-run`
- Install/start launchd scheduler (macOS): `run_cron_tool scheduler install`
- Stop/remove launchd scheduler (macOS): `run_cron_tool scheduler uninstall`
- Show scheduler status (macOS): `run_cron_tool scheduler status`

Runtime bootstrap policy mirrors `seq`/`cas`/`lift`: prefer the Zig binary and fail closed when missing/incompatible.

## Workflow
1. Choose working directories (`cwds`). Default is current repo if omitted on `create`.
2. Write the automation prompt (use `--prompt-file` for multi-line prompts).
3. Provide an RFC5545 RRULE string.
4. Create or update with `cron`.
5. For unattended execution, install scheduler via `cron scheduler install`.

## Headless Runner
- `cron run-due` executes due automations by calling `codex exec` and updates:
  - `automations.last_run_at`
  - `automations.next_run_at`
  - `automation_runs` rows
- `--codex-bin` accepts executable name or absolute path (default resolves `$CODEX_BIN` or `codex` in `PATH`).
- Locking is label-scoped and fail-closed (`--lock-label`, or env `CRON_LAUNCHD_LABEL`).
- Scheduler commands are macOS-only and manage `~/Library/LaunchAgents/<label>.plist` directly from Zig.
- Logs: `~/Library/Logs/codex-automation-runner/out.log` and `~/Library/Logs/codex-automation-runner/err.log`.

## Clarify When Ambiguous
Ask questions only when the request is ambiguous or when the user explicitly asks for guidance. Do not block otherwise.

Essential elements to confirm or infer:
1. Automation name.
2. Prompt content (single line or file path).
3. Schedule as an RFC5545 RRULE string (include `RRULE:` prefix).
4. Working directories (`cwds`), default to current repo if not specified.
5. Status if explicitly requested; otherwise default to `ACTIVE`.

When ambiguous, ask for missing details. Examples:
- If user says “daily”/“weekly” without time, ask for required time/day fields.
- If user says “run it for this repo” without paths, confirm repo root as `cwd`.

## Schedule (RRULE)
- Accept only RFC5545 RRULE strings. Cron expressions are unsupported.
- Rules are canonicalized to `RRULE:`-prefixed form.
- Validation is fail-closed.
- Supported frequencies:
  - `HOURLY` requires `BYMINUTE`
  - `DAILY` requires `BYHOUR` and `BYMINUTE`
  - `WEEKLY` requires `BYDAY`, `BYHOUR`, and `BYMINUTE`

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
See `references/db.md` for schema and field notes.
