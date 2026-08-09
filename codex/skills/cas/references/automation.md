# CAS automation

Use only `cas automation`. It adapts the existing local Codex automation state;
there is no app-server automation API and no second store.

## Safety gate

When compatibility is uncertain, before troubleshooting, or before mutation
that depends on store/scheduler assumptions, run:

```bash
cas automation doctor --json
```

Do not perform row or file mutations when `safeToMutate` is false. Doctor
checks database existence, required tables and columns, row values, cwd JSON,
RRULEs, row/file agreement, filesystem safety, resolved Codex, and the selected
scheduler label and loaded arguments.

One narrow exception is the exact doctor-directed same-label scheduler
adoption: when the only actionable incompatibility is the recognized
predecessor scheduler and `migrationRequired` is true, the authorized repair is
`cas automation scheduler install --replace`, followed immediately by another
doctor and scheduler-status check. This does not authorize automation row or
file mutation.

## Commands

```text
cas automation [--db <path>] doctor [--json]
cas automation [--db <path>] list [--status ACTIVE|PAUSED] [--json]
cas automation [--db <path>] show (--id <id> | --name <name>) [--json]

cas automation [--db <path>] create
  --name <name> (--prompt <text> | --prompt-file <path>) --rrule <RRULE>
  [--status ACTIVE|PAUSED] [--cwd <path>]...
  [--cwds-json <json> | --clear-cwds] [--next-run-at <timestamp>]

cas automation [--db <path>] update (--id <id> | --name <name>)
  [--new-name <name>] [--prompt <text> | --prompt-file <path>]
  [--rrule <RRULE>] [--status ACTIVE|PAUSED] [--cwd <path>]...
  [--cwds-json <json> | --clear-cwds]
  [--next-run-at <timestamp> | --clear-next-run-at]

cas automation [--db <path>] <enable|disable|run-now|delete>
  (--id <id> | --name <name>)

cas automation [--db <path>] run-due
  [--id <id>] [--limit <positive-integer>] [--dry-run]
  [--codex-bin <path-or-name>] [--lock-label <label>]

cas automation scheduler install
  [--label <label>] [--interval-seconds <positive-integer>]
  [--path <PATH>] [--codex-bin <path-or-name>] [--replace]

cas automation scheduler <uninstall|status> [--label <label>] [--json]
```

Validate all inputs before the first write. Target selectors must resolve
exactly one row. Database changes use SQLite transactions; a later file-sync
failure is reported separately and remains visible to doctor.

## Schedule

Use RFC5545 RRULEs, not cron expressions. Canonical writes include `RRULE:`;
existing non-prefixed rows remain readable.

- `HOURLY` requires `BYMINUTE`.
- `DAILY` requires `BYHOUR` and `BYMINUTE`.
- `WEEKLY` requires `BYDAY`, `BYHOUR`, and `BYMINUTE`.
- `BYHOUR` and `BYMINUTE` are interpreted in UTC.

Examples:

```text
RRULE:FREQ=DAILY;BYHOUR=9;BYMINUTE=0
RRULE:FREQ=WEEKLY;BYDAY=FR;BYHOUR=9;BYMINUTE=0
RRULE:FREQ=HOURLY;INTERVAL=24;BYMINUTE=0
```

## Runner

`run-due` launches `codex exec`, records bounded output and exit status, and
updates `last_run_at`, `next_run_at`, and `automation_runs`. Default limit is
10. `--dry-run` is strictly read-only across rows, run records, files, and
memory. Locking is label-scoped and fail-closed. Labels accept only
`[A-Za-z0-9._-]`.

`CODEX_BIN` selects the Codex executable. Scheduler environment names are
`CAS_AUTOMATION_LAUNCHD_LABEL`, `CAS_AUTOMATION_LAUNCHD_INTERVAL_SECONDS`, and
`CAS_AUTOMATION_LAUNCHD_PATH`.

## Scheduler

The default label remains `com.openai.codex.automation-runner`; log paths remain
under `~/Library/Logs/codex-automation-runner/`. The loaded program arguments
must invoke `cas automation run-due`.

Inspect first:

```bash
cas automation scheduler status --json
```

If `migrationRequired` is true for the same-label predecessor job, adopt it in
place:

```bash
cas automation scheduler install --replace
cas automation scheduler status --json
```

Never install a second label for migration.
