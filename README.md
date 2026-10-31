### Installation ###
```
git clone https://github.com/tkersey/dotfiles.git ~/.dotfiles && cd ~/.dotfiles && ./install
```

### Ghostty

See [Ghostty configuration](ghostty/README.md) for themes, agent-session shortcuts,
the one-time tip-cask migration, and local validation.

### Codex configuration

The shared Codex config is installed as a symlink:

| Repository file | Symlink |
| --- | --- |
| `codex/config.toml` | `/etc/codex/config.toml` |

The active user config (`$CODEX_HOME/config.toml`, normally
`~/.codex/config.toml`) remains a writable, machine-local file. It is not
installed or tracked by this repository.

Quit Codex/ChatGPT and running Codex CLI sessions and preserve any config edits
that should be kept. If an older installation linked the user config into the
repository, replace that symlink with a regular file preserving its contents
before updating your checkout. The installer no longer manages that destination.
Then update your checkout and run the existing installer as your normal user:

```sh
cd ~/.dotfiles
./install --symlink
```

The default `./install` includes the same symlink step. The installer requests
`sudo` only when creating or replacing `/etc/codex/config.toml`. For an existing
config file or old symlink, choose `o` at that destination's overwrite prompt
to replace it with the new link. Overwrite removes the old file or link; keep
any needed contents before selecting it. Choose `s` to preserve an existing
file instead.

Reopen Codex after installation. Reusable preferences, including TUI presets
(`tui.presets`), belong in `codex/config.toml`, even when Codex initially
saves them in the user file. Trust entries, installation-specific paths,
application state, and intentional local overrides stay in the user config.
User values override system defaults: when migrating reusable settings, remove
their superseded user entries once the shared file is installed and loads
successfully, then verify the affected settings resolve as intended.

The system config links into this checkout, so repository updates affect the
shared defaults. Keep the checkout at a revision containing
`codex/config.toml`.

### Ledger maintenance

After installing the qualified Homebrew Ledger 1.6.0 release, install the hourly
user LaunchAgent with `./install --ledger-maintenance`. This explicit option
activates `com.tkersey.ledger.maintenance`; ordinary dotfile linking does not.
The installer selects `tkersey/tap/ledger`, uses its stable executable path, and
pins the validated Python interpreter used during installation. It verifies
that launchd loaded the job.

The configuration is [maintenance.json](agents/skills/ledger/maintenance.json).
Each sweep selects at most 128 cataloged stores and runs for at most five minutes.
Native work per store is limited to 512 files, 256 MiB of preparation working
storage and 2 GiB of reads; a native call is limited to 30 seconds. An incomplete
sweep reports incomplete coverage. It does not claim that later sweeps inspect
the remaining stores.

Cleanup runs quietly. CLI results report failures, incomplete inspection, and
free space below the configured 5 GiB threshold. Only the latest bounded run
status is retained under `LEDGER_HOME/maintenance`, with a wrapper coordination
lock. No report history or payload archive is created.

`maintain_custody.py` inspects by default. Pass `--apply` for native housekeeping
and run-status updates. Routine `ensure_custody.py --ensure-owner` also
runs bounded housekeeping and reports a missing or stale scheduled-run receipt.
Normal access reads the installed LaunchAgent's configuration and cadence;
changing the cadence requires reinstalling the agent. A manual sweep does not
certify scheduled execution. Recorded execution does not prove the job remains
loaded or enabled.
`--read-only` and its `--no-maintenance` alias do neither. A healthy access does
not establish that idle-time scheduling is working.
