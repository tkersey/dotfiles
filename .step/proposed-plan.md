# Plan: Build `accts`, a Codex-Only Account Manager Skill

## Summary

Build `accts` as a repo-local Codex skill with a bundled Python CLI. The implementation must manage Codex account metadata in TOML, keep OAuth-bearing `auth.json` files in an owner-only vault, support safe backup/activation, apply queued account switches at the next Codex turn through Stop/SessionStart hooks, and rotate all enabled accounts after a weekly reset using `$cas` account status as the reset authority.

The first execution wave scaffolds `codex/skills/accts`, `agents/openai.yaml`, `scripts/accts.py`, and tests. The second wave implements config, state, vault, backup, status, and activate flows against temp `$CODEX_HOME`. The third wave adds queue/hook integration and hook merge/uninstall safety. The fourth wave adds CAS-backed reset-cycle logic and a turn-use ledger proving each account was actually used after a Codex turn.

## Implementation

- step=scaffold skill; owner=implementer; success_criteria=`codex/skills/accts` exists with `SKILL.md`, `agents/openai.yaml`, `scripts/accts.py`, and tests using skill-creator conventions.
- step=implement config/state/vault primitives; owner=implementer; success_criteria=TOML metadata parses, token-looking TOML keys are rejected, vault files are written atomically with mode `0600`, and state stores only labels/hashes/timestamps.
- step=implement backup/status/activate; owner=implementer; success_criteria=temp-home tests prove byte-identical backup/restore, unknown active auth is reported rather than overwritten, `--backup-current` works, and no token value is printed.
- step=implement queue and hooks; owner=implementer; success_criteria=`queue`, `hook print`, `hook install`, `hook uninstall`, `hook stop`, and `hook session-start` preserve existing hooks, apply pending switches exactly once, and return valid Codex hook JSON.
- step=implement CAS reset cycle; owner=implementer; success_criteria=adapter prefers `cas account status --json --usage --hooks off` when available, falls back to `$SKILLS_ZIG_REPO/zig-out/bin/cas_account`, fails closed on missing weekly fields, and reset-cycle fixture tests prove untouched-account advancement.
- step=write skill instructions and UI metadata; owner=implementer; success_criteria=`SKILL.md` documents the safety model and command workflow under 500 lines, `agents/openai.yaml` is generated/consistent, and no README/INSTALL/CHANGELOG-style extra docs are added.
- step=validate and close; owner=implementer; success_criteria=unit tests, temp-home integration, hook merge tests, quick validation, CLI help smoke, live redacted CAS status smoke, diff check, and projection checks pass.
- step=ship and land; owner=implementer; success_criteria=ready PR is opened/updated with proof, review threads and checks are clean, guarded squash merge uses `--match-head-commit`, and local/remote branch cleanup is verified.

## Locked Decisions

- Skill and CLI name is `accts`.
- Scope is Codex-only; do not modify or delete `codex/skills/caam`.
- Store human account metadata in `~/.codex/accts.toml`; store token-bearing `auth.json` copies under `~/.local/share/accts/vault/<account>/auth.json` with mode `0600`.
- Runtime state lives in `~/.local/state/accts/state.json` and contains only non-secret labels, hashes, pending account, reset-cycle metadata, and turn-use ledger rows.
- Next-turn handoff is `accts queue <account>` plus Codex Stop hook, with SessionStart as backup. Do not claim mid-response switching.
- Weekly reset detection uses CAS account status, specifically the weekly secondary window data when present. A CAS status read is observation, not proof that an account was used.
- Add a turn-use ledger: Stop hook marks the account just used in a real turn before queueing the next reset-cycle account.
- Preserve existing `hooks.json` entries through JSON merge and uninstall markers; never replace the full file.

## Validation

- `python3 codex/skills/accts/scripts/accts.py --help`
- `python3 -m unittest discover -s codex/skills/accts/tests -p 'test_*.py'`
- `CODEX_HOME="$(mktemp -d)" ACCTS_HOME="$(mktemp -d)" python3 codex/skills/accts/scripts/accts.py init --dry-run`
- `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/accts`
- `/Users/tk/workspace/tk/skills-zig/zig-out/bin/cas_account status --cwd /Users/tk/.dotfiles --json --usage --hooks off`
- `codex debug prompt-input`
- `git diff --check`
- `st doctor --file .step/st-plan.jsonl`
- `st assert-projection --file .step/st-plan.jsonl`
