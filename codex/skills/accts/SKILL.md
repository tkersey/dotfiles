---
name: accts
description: Manage local Codex account switching with a metadata-only TOML config, safe auth.json vault backups, pending manual account activation, and weekly reset-cycle rotation. Use when the user asks to manage Codex accounts, switch Codex accounts, inspect account status, or rotate through accounts after weekly limits reset.
---

# Accts

## Purpose

Use `accts` to manage multiple local Codex accounts without putting OAuth secrets in prompts, TOML, logs, or skill instructions. The skill owns only Codex CLI auth at `~/.codex/auth.json`; do not extend it to Claude, Gemini, or unrelated agent CLIs.

The executable is:

```bash
python3 codex/skills/accts/scripts/accts.py --help
```

## Safety Rules

- Treat `auth.json` as secret OAuth material. Never print, summarize, paste, or store its contents outside the owner-only vault.
- Keep `accts.toml` metadata-only. If TOML contains token-like keys such as `access_token`, `refresh_token`, `api_key`, `secret`, or `password`, stop and fix the config rather than tolerating it.
- Use temp `CODEX_HOME` and `ACCTS_HOME` for tests, dry runs, or examples unless the user explicitly wants to mutate the live account setup.
- Do not install Codex lifecycle hooks for account switching. Use `queue`, `next`, and explicit `activate` commands so account changes are visible user-owned steps.
- A direct `activate` changes `auth.json`, but the running turn may already have loaded credentials. Prefer activating before starting the turn that should use the new account.

## Config

Default config location:

```bash
python3 codex/skills/accts/scripts/accts.py init --dry-run
python3 codex/skills/accts/scripts/accts.py init
```

Config schema:

```toml
[settings]
# codex_home = "~/.codex"
# vault_dir = "~/.local/share/accts/vault"
# state_dir = "~/.local/share/accts/state"
# cas_cwd = "/path/to/repo"

[accounts.personal]
label = "Personal"
enabled = true
reset_participates = true
vault = "personal/auth.json"
```

## Core Workflow

Back up each account once:

```bash
python3 codex/skills/accts/scripts/accts.py backup personal --label "Personal"
python3 codex/skills/accts/scripts/accts.py ls
python3 codex/skills/accts/scripts/accts.py status
```

Switch immediately when no current turn depends on the old account:

```bash
python3 codex/skills/accts/scripts/accts.py activate personal --backup-current
```

Queue a switch, inspect the pending account, then activate it manually before the turn that should use it:

```bash
python3 codex/skills/accts/scripts/accts.py queue personal
python3 codex/skills/accts/scripts/accts.py next
python3 codex/skills/accts/scripts/accts.py activate personal --backup-current
```

## Weekly Reset Rotation

Use reset-cycle rotation after the weekly Codex limit reset so each participating account receives one real turn near the same reset window.

```bash
python3 codex/skills/accts/scripts/accts.py reset-cycle status
python3 codex/skills/accts/scripts/accts.py reset-cycle start
python3 codex/skills/accts/scripts/accts.py next
```

`reset-cycle start` reads CAS account status and queues the first eligible vaulted account. Activate the account shown by `next` before using it. After that account has had a real turn, run `reset-cycle advance --account <name>` to mark it touched and queue the next untouched account. The cycle completes after every enabled `reset_participates = true` vaulted account has been marked touched.

If CAS is unavailable, do not invent reset timing. Use `reset-cycle status --state-only` to inspect local state, or ask the user before using an explicit offline `--resets-at` timestamp.

## Validation

Run the focused proof bundle after editing this skill:

```bash
python3 codex/skills/accts/scripts/accts.py --help
python3 -m unittest discover -s codex/skills/accts/tests -p 'test_*.py'
CODEX_HOME="$(mktemp -d)" ACCTS_HOME="$(mktemp -d)" python3 codex/skills/accts/scripts/accts.py init --dry-run
uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/accts
/Users/tk/workspace/tk/skills-zig/zig-out/bin/cas_account status --cwd /Users/tk/.dotfiles --json --usage --hooks off
codex debug prompt-input
git diff --check
```
