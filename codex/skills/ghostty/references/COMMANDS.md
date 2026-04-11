# Ghostty Commands — Complete Reference

## Table of Contents
- [Actions (IPC)](#actions-ipc)
- [Navigation](#navigation)
- [Font Commands](#font-commands)
- [Configuration](#configuration)
- [Launch Options](#launch-options)
- [Debugging](#debugging)

---

## Actions (IPC)

Actions control a running Ghostty instance via `+action` flag.

```bash
# List all available actions
ghostty +list-actions

# Window management
ghostty +new-window
ghostty +new-tab
ghostty +close-surface
ghostty +toggle-fullscreen

# Splits
ghostty +new-split:right
ghostty +new-split:down
ghostty +new-split:left
ghostty +new-split:up
```

---

## Navigation

```bash
# Navigate between splits
ghostty +goto-split:previous
ghostty +goto-split:next
ghostty +goto-split:up
ghostty +goto-split:down
ghostty +goto-split:left
ghostty +goto-split:right

# Tab navigation
ghostty +goto-tab:1
ghostty +goto-tab:2
ghostty +goto-tab:previous
ghostty +goto-tab:next
```

---

## Font Commands

```bash
# Adjust font size (amount as parameter)
ghostty +increase-font-size:1
ghostty +decrease-font-size:1
ghostty +increase-font-size:2

# Reset to default
ghostty +reset-font-size

# List available fonts
ghostty +list-fonts
```

---

## Configuration

Config file location: `~/.config/ghostty/config`

```bash
# Show current configuration
ghostty +show-config

# Validate configuration
ghostty +validate-config

# Reload config without restart
ghostty +reload-config

# List themes
ghostty +list-themes

# List keybinds
ghostty +list-keybinds
```

---

## Launch Options

```bash
# Start with specific config file
ghostty --config-file=/path/to/config

# Execute command on startup
ghostty -e "htop"
ghostty -e "ssh user@host"

# Start in specific directory
ghostty --working-directory=/path/to/dir

# Combine options
ghostty --working-directory=/projects -e "git status"
```

---

## Debugging

```bash
# Check version
ghostty --version

# Validate configuration
ghostty +validate-config

# Show all configuration options
ghostty +show-config

# List available actions
ghostty +list-actions
```

---

## Quick Reference

| Category | Command | Description |
|----------|---------|-------------|
| Window | `+new-window` | Create new window |
| Tab | `+new-tab` | Create new tab |
| Split | `+new-split:right` | Split pane right |
| Split | `+new-split:down` | Split pane down |
| Navigate | `+goto-split:next` | Next split |
| Font | `+increase-font-size:1` | Increase font |
| Font | `+reset-font-size` | Reset font |
| Config | `+reload-config` | Reload config |
| Config | `+validate-config` | Validate config |
| Info | `+list-actions` | List all actions |
