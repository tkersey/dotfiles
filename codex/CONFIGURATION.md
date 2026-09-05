# Codex configuration

`codex/config.toml` is the portable baseline, installed as a **root-owned regular
file** at `/etc/codex/config.toml`. It is not linked into the user configuration.
Codex loads system defaults below `$CODEX_HOME/config.toml` (normally
`~/.codex/config.toml`); user, profile, trusted project and CLI overrides still win.
This is ordinary configuration, not `managed_config.toml` or `requirements.toml`.
See [OpenAI's configuration precedence](https://developers.openai.com/codex/config-basic).

The baseline retains the existing model/reasoning values, features, agent limits,
app defaults, realtime preferences, memory settings, TUI preferences and developer
docs MCP server. Trust entries, notices/onboarding state, desktop settings,
notifications, installed marketplaces/plugins, app-provisioned MCP servers and
path/hash-specific environment values stay local. Unknown local keys also survive.
Skills (`~/.agents/skills`) and agents (`~/.codex/agents`) keep their existing links.

## Existing installation: before pulling this change

**Close all Codex/ChatGPT clients first. Detach the live config before checking out
or pulling the split.** The old symlink points at the tracked file that this change
reduces; an installer run after checkout cannot recover the overwritten live bytes.
Run this from any shell, including fish; it keeps a private backup and atomically
replaces only the symlink, leaving the old repository file untouched:

```sh
bash -c '
set -eu
config="${CODEX_HOME:-$HOME/.codex}/config.toml"
if [ -L "$config" ]; then
  backup=$(mktemp "$config.pre-system-split.XXXXXX")
  cp -L "$config" "$backup"
  stage=$(mktemp "$config.local.XXXXXX")
  cp "$backup" "$stage"
  chmod 600 "$stage" "$backup"
  mv -f "$stage" "$config"
  printf "Preserved live config; backup: %s\n" "$backup"
fi
'
```

Then pull/checkout the change. Do not discard unrelated working-tree changes.
A separate worktree is also supported: running its installer can detach a live
symlink pointing to the **old** checkout, without changing that checkout's file.

## Install or update

From the repository root, as your normal user (not `sudo ./install`):

```sh
uv run --script codex/install-config.py --dry-run
./install --codex-config
```

Requires `uv` (already in the Brewfile), Python 3.11+ and the script-pinned TOML Kit;
uv resolves the script environment. The first run may need network access. This
installer targets macOS/Linux; it does not configure native Windows installations.
`--codex-config` is opt-in and is not part of the default `./install` tasks.

The installer validates both TOML files, backs up the exact live user config with
mode `0600`, deploys the baseline with `sudo` as mode `0644`, then atomically writes
the user file with mode `0600`. Existing dotfiles-managed system files are backed
up before replacement. Other system configurations and system symlinks are refused
rather than overwritten. Only filesystem installation commands run under sudo.

Matching local values are removed so they inherit future baseline changes.
**Differing overrides are preserved**, including a different model or feature flag.
Local-only settings retain their TOML formatting/comments. Re-running is a no-op
when neither layer needs changing; each run removes values equal to the baseline,
so an explicitly duplicated local value is not treated as a permanent pin.

Run the installer on each machine after changing the baseline; Git alone does not
update `/etc`. Restart Codex and inspect `/debug-config` and `/status` to confirm
layer provenance and effective settings. Settings support still depends on the
installed client version; this split intentionally does not change feature values.
The system file applies to every local user and every `CODEX_HOME` on the machine.
Never put secrets or installation-specific paths in the shared baseline.

## Recovery

If the reduced file was already pulled while the old link was active, the installer
refuses that link. Restore the live pre-pull backup into a **regular** user file
before retrying; do not copy through the old symlink. Without a live backup, Git
can recover only a committed snapshot, not uncommitted installation state. The
last pre-split snapshot is available with:

```sh
git show 4c6443f29c71d35826f9bc58acbc34f0040b41a2:codex/config.toml
```

For rollback, close clients, restore the printed local backup as a regular file,
and restore the printed system backup with sudo. If no system file existed before
installation, remove only the newly installed `/etc/codex/config.toml`. Keep backups
until startup is verified. A sudo/install failure leaves the live user config
unpruned. If a concurrent edit is detected after system deployment, the system
baseline may already be updated, but the live user file is not overwritten; close
clients and retry. Do not run installers concurrently.

## Tests

```sh
uv run --script codex/tests/test_install_config.py
bash -n install
```

Tests use temporary directories and replace the sudo boundary; they never touch
real `/etc`, a real user config, or a running Codex client. They cover value
preservation, dotted/inline tables, overrides, backups/modes, idempotence, failures,
concurrent edits, fresh installs, pre-pull detachment and installer integration.
