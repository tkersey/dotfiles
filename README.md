### Installation ###
```
git clone https://github.com/tkersey/dotfiles.git ~/.dotfiles && cd ~/.dotfiles && ./install
```

### Codex configuration

The installer copies the two repository configs into regular files:

| Repository file | Installed file |
| --- | --- |
| `etc/codex/config.toml` | `/etc/codex/config.toml` |
| `home/.codex/config.toml` | `~/.codex/config.toml` |

To migrate, quit Codex/ChatGPT and running Codex CLI sessions, preserve any
uncommitted config changes, and check out the revision containing the split.
Then run the repository installer as your normal user:

```sh
cd ~/.dotfiles
./install --codex-config
```

The installer requests `sudo` only for the system file. It replaces existing
config symlinks with regular files without changing their targets, and saves
readable previous contents beside each destination as `config.toml.backup.*`.
An old link whose target was removed by checkout is replaced directly.
Identical regular files are left alone. The system file is installed with mode
644 and the user file with mode 600. The default `./install` also includes this
step; `--symlink` handles the remaining links only.

Reopen Codex and check that your model, plugins, and MCP tools load. User config
values override system defaults. Installed files are independent of the
checkout: pulling repository changes does not update them. Run
`./install --codex-config` again to apply the repository versions; differing
live settings are backed up before replacement.

For an isolated installation check, the following prefixes both destinations
with the staging path and does not use `sudo`. `DESTDIR` is supported only for
this operation.

```sh
DESTDIR=/absolute/staging/path ./install --codex-config
```

### iCloud directory backups

Local directories that cannot be symlinked can be copied into iCloud Drive by the repository-managed rclone LaunchAgent. Configure [`backups/targets.conf`](backups/targets.conf), then follow [`backups/README.md`](backups/README.md).
