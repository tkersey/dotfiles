# iCloud directory backups

This subsystem copies local directories into the macOS iCloud Drive filesystem. `rclone` uses ordinary local paths; Apple authentication remains owned by macOS and no rclone credentials are committed.

## Configure

Choose a stable logical machine identity in `profile`, then add each directory to `targets.conf`:

```text
some-application:$HOME/Library/Application Support/Some Application
some-tool-state:$HOME/.some-tool-state
```

Logical names must match `[A-Za-z0-9._-]+`. Source paths must be absolute or start with a literal `$HOME`. Sources inside iCloud Drive are rejected.

Backups are written beneath:

```text
~/Library/Mobile Documents/com~apple~CloudDocs/backups/macos/<profile>/
├── current/
└── history/
```

Scheduled runs use `rclone copy`, so locally deleted files remain in `current` until an explicit `prune`. Replaced files are moved into timestamped `history` directories. Symlinks and local metadata are preserved using rclone's `--links` and `--metadata` modes.

## Install and authorize

The root installer provisions the hourly LaunchAgent at minute 17:

```sh
./install --icloud-backup
./backups/backup run --dry-run
./backups/backup arm
```

Cloning the repository or installing the LaunchAgent does not authorize writes. The machine-local arm marker is stored outside Git at `~/.local/state/dotfiles-icloud-backup/armed`.

Useful commands:

```sh
./backups/backup status
./backups/backup run --dry-run
./backups/backup run
./backups/backup restore all
./backups/backup restore all --apply
./backups/backup prune all
./backups/backup prune all --apply
./backups/backup disarm
```

`restore` and `prune` are dry-run operations unless `--apply` is supplied. Applied restores preserve overwritten local files under `~/.local/state/dotfiles-icloud-backup/restore-history/`.

## Replace or reset a Mac

1. Sign into the Apple Account and enable iCloud Drive.
2. Clone the dotfiles repository and run `./install`.
3. Run `./backups/backup status`.
4. Preview and apply restoration with `restore all`, then `restore all --apply`.
5. Inspect the restored applications and files.
6. Run `./backups/backup arm` only after the replacement machine is ready to become authoritative.

Do not arm two simultaneously active Macs with the same profile. History is intentionally retained until manually reviewed and removed. Close applications that maintain live databases before backing them up when a transactionally consistent snapshot matters. macOS privacy controls may also require user approval for protected source directories.
