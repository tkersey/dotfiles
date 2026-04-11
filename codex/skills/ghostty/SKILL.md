---
name: ghostty
description: >-
  Control Ghostty terminal emulator via CLI. Use when managing windows, tabs,
  splits, fonts, or configuration for Ghostty.
---

<!-- TOC: Quick Start | THE EXACT PROMPT | Actions | Configuration | Troubleshooting | References -->

# Ghostty CLI

> **Core Capability:** Control and configure the Ghostty terminal emulator from the command line.

## Quick Start

```bash
# CLI location (or symlinked as `ghostty`)
/Applications/Ghostty.app/Contents/MacOS/ghostty

# List available actions
ghostty +list-actions

# Check version
ghostty --version
```

---

## THE EXACT PROMPT — Window/Tab Management

```
# New window
ghostty +new-window

# New tab
ghostty +new-tab

# Splits
ghostty +new-split:right
ghostty +new-split:down

# Navigate splits
ghostty +goto-split:up
ghostty +goto-split:down
ghostty +goto-split:left
ghostty +goto-split:right

# Close current surface
ghostty +close-surface

# Toggle fullscreen
ghostty +toggle-fullscreen
```

---

## THE EXACT PROMPT — Font Management

```
# Adjust font size
ghostty +increase-font-size:1
ghostty +decrease-font-size:1
ghostty +reset-font-size

# List available fonts
ghostty +list-fonts
```

---

## THE EXACT PROMPT — Configuration

```
# Config file: ~/.config/ghostty/config

# Show current config
ghostty +show-config

# Validate config
ghostty +validate-config

# Reload config (live)
ghostty +reload-config

# List themes/keybinds
ghostty +list-themes
ghostty +list-keybinds
```

---

## Launch Options

```bash
# Start with specific config
ghostty --config-file=/path/to/config

# Start with command
ghostty -e "htop"

# Start in directory
ghostty --working-directory=/path/to/dir
```

---

## Essential Commands

| Action | Command |
|--------|---------|
| New window | `ghostty +new-window` |
| New tab | `ghostty +new-tab` |
| Split right | `ghostty +new-split:right` |
| Split down | `ghostty +new-split:down` |
| Close | `ghostty +close-surface` |
| Reload config | `ghostty +reload-config` |

---

## Troubleshooting: Remote SSH

**Problem:** Seeing `[57414u` garbage when pressing numpad Enter over SSH.

**Quick fix:**

```bash
infocmp -x xterm-ghostty | ssh user@server 'mkdir -p ~/.terminfo && tic -x -o ~/.terminfo -'
```

**Fallback (no terminfo access):**

```bash
alias myserver='TERM=xterm-256color ssh user@myserver'
```

Full guide: [REMOTE-TERMINFO.md](references/REMOTE-TERMINFO.md)

---

## References

| Topic | Reference |
|-------|-----------|
| All commands | [COMMANDS.md](references/COMMANDS.md) |
| Remote terminfo setup | [REMOTE-TERMINFO.md](references/REMOTE-TERMINFO.md) |
