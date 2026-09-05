### Installation ###
```
git clone https://github.com/tkersey/dotfiles.git ~/.dotfiles && cd ~/.dotfiles && ./install
```

### iCloud directory backups

Local directories that cannot be symlinked can be copied into iCloud Drive by the repository-managed rclone LaunchAgent. Configure [`backups/targets.conf`](backups/targets.conf), then follow [`backups/README.md`](backups/README.md).
