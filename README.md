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

Native Ledger writes report validation, publication, and storage errors in their
normal results. Preparation uses native transaction finalization, leaving no
second payload archive. No scheduler, background status worker, or desktop
notification is installed.

For a separate bounded storage inspection, use `ledger maintain` with an explicit
managed store. It reports incomplete inspection and unresolved native work without
changing history. See [storage maintenance](agents/skills/ledger/references/storage-maintenance.md).
