---
name: cron
description: Create and manage Codex app automations stored in the local SQLite database (~/.codex/sqlite/codex-dev.db). Use when you need to add, list, update, enable/disable, delete, or run-now automations; edit automation names, prompts, RRULE schedules, or cwd scopes; or inspect automation records while troubleshooting app automation behavior.
---

# Cron

## Overview
Use this skill to manage Codex automations by editing the local SQLite database and synced filesystem automation configs. Use `run_cron_tool` to prefer the Zig CLI with script fallback and keep changes minimal and explicit.

## Quick Start
```bash
CODEX_SKILLS_HOME="${CODEX_HOME:-$HOME/.codex}"
CLAUDE_SKILLS_HOME="${CLAUDE_HOME:-$HOME/.claude}"
CRON_SCRIPT="$CODEX_SKILLS_HOME/skills/cron/scripts/cron.py"
[ -f "$CRON_SCRIPT" ] || CRON_SCRIPT="$CLAUDE_SKILLS_HOME/skills/cron/scripts/cron.py"

run_cron_tool() {
  if command -v cron >/dev/null 2>&1 && cron --help 2>&1 | grep -q "cron.zig"; then
    cron "$@"
    return
  fi
  if [ "$(uname -s)" = "Darwin" ] && command -v brew >/dev/null 2>&1; then
    if ! brew install tkersey/tap/cron; then
      echo "brew install tkersey/tap/cron failed; refusing silent fallback." >&2
      return 1
    fi
    if command -v cron >/dev/null 2>&1 && cron --help 2>&1 | grep -q "cron.zig"; then
      cron "$@"
      return
    fi
    echo "brew install tkersey/tap/cron did not produce a compatible cron binary." >&2
    return 1
  fi
  if [ -f "$CRON_SCRIPT" ]; then
    uv run python "$CRON_SCRIPT" "$@"
    return
  fi
  echo "cron binary missing and fallback script not found: $CRON_SCRIPT" >&2
  return 1
}
```

- List automations: `run_cron_tool list`
- Create an automation: `run_cron_tool create --name "Weekly release notes" --prompt-file /path/to/prompt.md --rrule "RRULE:FREQ=WEEKLY;BYDAY=FR;BYHOUR=9;BYMINUTE=0"`
- Update an automation: `run_cron_tool update --id <id> --rrule "RRULE:FREQ=DAILY;BYHOUR=9;BYMINUTE=0"`
- Enable or disable: `run_cron_tool enable --id <id>` or `run_cron_tool disable --id <id>`
- Run immediately: `run_cron_tool run-now --id <id>`
- Delete: `run_cron_tool delete --id <id>`
- Run due automations once (headless): `scripts/automation_runner.py --once`
- Install and start user LaunchAgent scheduler: `scripts/install_launch_agent.sh`
- Stop and remove scheduler: `scripts/uninstall_launch_agent.sh`

Runtime bootstrap policy for `cron` mirrors `seq`/`cas`/`lift`: prefer the Zig `cron` binary; on macOS with `brew`, treat `brew install tkersey/tap/cron` failure (or incompatible binary) as a hard error; otherwise fallback to `uv run python "$CRON_SCRIPT"`.

## Workflow
1. Choose the working directories (`cwds`). Default to the current repo if not specified.
2. Write the automation prompt. Use `--prompt-file` for multi-line prompts.
3. Provide an RFC5545 RRULE string (see schedule guidance below).
4. Create or update the automation with `run_cron_tool`.
5. If you want hands-off execution without the desktop app, install the LaunchAgent with `scripts/install_launch_agent.sh`.

## Headless Runner
- `scripts/automation_runner.py` executes due automations by calling `codex exec` and updates:
  - `automations.last_run_at`
  - `automations.next_run_at`
  - `automation_runs` rows for each execution
- The runner uses `python-dateutil` via `uv` in the shebang and does not require a persistent venv.
- `--codex-bin` accepts either an absolute path or executable name; default resolves `$CODEX_BIN` or `codex` from `PATH`.
- `scripts/launchd_wrapper.sh` uses `lockf` to prevent overlapping runs.
- `scripts/install_launch_agent.sh` is idempotent and installs `~/Library/LaunchAgents/com.openai.codex.automation-runner.plist` with a 60-second interval by default.
  - Optional overrides:
    - `--label <reverse-dns-label>` (or env `CRON_LAUNCHD_LABEL`)
    - `--interval-seconds <n>` (or env `CRON_LAUNCHD_INTERVAL_SECONDS`)
    - `--path <PATH>` (or env `CRON_LAUNCHD_PATH`)
- `scripts/uninstall_launch_agent.sh` is idempotent and accepts optional `--label`.
- Logs: `~/Library/Logs/codex-automation-runner/out.log` and `~/Library/Logs/codex-automation-runner/err.log`.
- Service status:
  - `launchctl print gui/$(id -u)/com.openai.codex.automation-runner`

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
