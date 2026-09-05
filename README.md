### Installation ###
```
git clone https://github.com/tkersey/dotfiles.git ~/.dotfiles && cd ~/.dotfiles && ./install
```

### Codex configuration

**Existing installations: preserve the live `~/.codex/config.toml` before pulling
this split.** Follow the [migration instructions](codex/CONFIGURATION.md).

Shared defaults are deployed separately, with an explicit system-wide install:

```sh
./install --codex-config
```

This installs `codex/config.toml` into `/etc/codex/config.toml` and leaves
machine-local overrides and app-managed state in a regular user-owned config file.
It is opt-in, not part of the default `./install` tasks. Re-run it on each machine
after changing the shared baseline. Skills and agents keep their existing links.

### iCloud directory backups

Local directories that cannot be symlinked can be copied into iCloud Drive by the repository-managed rclone LaunchAgent. Configure [`backups/targets.conf`](backups/targets.conf), then follow [`backups/README.md`](backups/README.md).
