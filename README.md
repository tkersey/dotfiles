### Installation ###
```
git clone https://github.com/tkersey/dotfiles.git ~/.dotfiles && cd ~/.dotfiles && ./install
```

### Codex configuration

The two repository configs are installed as symlinks:

| Repository file | Symlink |
| --- | --- |
| `etc/codex/config.toml` | `/etc/codex/config.toml` |
| `home/.codex/config.toml` | `~/.codex/config.toml` |

Quit Codex/ChatGPT and running Codex CLI sessions, preserve any config edits
that should be kept, and update your checkout. Then run the existing installer
as your normal user:

```sh
cd ~/.dotfiles
./install --symlink
```

The default `./install` includes the same symlink step. The installer requests
`sudo` only when creating or replacing `/etc/codex/config.toml`. For an existing
config file or old symlink, choose `o` at that destination's overwrite prompt
to replace it with the new link. Overwrite removes the old file or link; keep
any needed contents before selecting it. Choose `s` to preserve an existing
file instead. The separate config-copying operation is removed.

Reopen Codex after installation. Shared defaults live in
`etc/codex/config.toml`; personal settings and the Developer Docs MCP server
live in `home/.codex/config.toml`. User values override system defaults.
Because the live files link into this checkout, edits and repository updates
are reflected through those links. Keep the checkout at a revision containing
both files.

### iCloud directory backups

Local directories that cannot be symlinked can be copied into iCloud Drive by the repository-managed rclone LaunchAgent. Configure [`backups/targets.conf`](backups/targets.conf), then follow [`backups/README.md`](backups/README.md).
